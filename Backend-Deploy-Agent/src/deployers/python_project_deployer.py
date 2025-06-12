"""
@File    : python_project_deployer.py
@Author  : Tianfei Ji
@Date    : 2025-06-11
@Desc    : Python项目部署器
"""
import os
import re
import shutil
import subprocess
import zipfile
from datetime import datetime
import uuid
from fastapi import UploadFile
from models.common.http_result import HttpResult
from manager.project_data_manager import ProjectDataManager
from manager.deploy_history_data_manager import DeployHistoryDataManager
from manager.template_manager import TemplateManager
from config.log_config import get_logger


class PythonProjectDeployer:
    """
    PythonProjectDeployer

    用于部署 Python 项目。

    部署流程如下：
        1. 接收上传的 zip 压缩包与 dockerfile 内容（可选）
        2. 解压 zip 至项目目录 -> 判断是否存在根层级 Dockerfile：
            - 若存在则使用解压包中的 Dockerfile
            - 若不存在，则使用传入的 dockerfile_content 内容生成 Dockerfile
            - 若两者都无，则报错退出
        3. 构建 Docker 镜像
        4. 若容器已存在则删除旧容器
        5. 启动新容器（根据模板指令）
        6. 更新部署状态及项目记录（含部署历史）
    """
    
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(PythonProjectDeployer, cls).__new__(cls)
        return cls._instance

    def __init__(self):
        self.logger = get_logger()
        self.project_data_manager = ProjectDataManager().get_instance()
        self.deploy_history_manager = DeployHistoryDataManager().get_instance()
        self.template_manager = TemplateManager().get_instance()
        self.python_project = None
        self.dockerfile_path = None

    def deploy(self, id: str, zip_file: UploadFile, dockerfile_content: str = None, dockercommand_content: str = None):
        self.logger.info("==================== Python Project Deploy : Start ====================")
        self.deploy_status = "START"
        self.python_project = self.project_data_manager.get_project(id)
        if self.python_project is None:
            return HttpResult[None](code=400, status="failed", msg=f"没有id为{id}的Python项目", data=None)

        self.deploy_history_id = str(uuid.uuid4()).replace("-", "")[:8]

        self._create_project_directory()
        zip_path = self._save_zip_file(zip_file)
        self._extract_zip_file(zip_path)
        self._delete_zip_file(zip_path)

        if not self._detect_or_create_dockerfile(dockerfile_content):
            msg = "未检测到 Dockerfile，且未提供 dockerfile_content 参数"
            self.logger.error(msg)
            return HttpResult[None](code=400, status="failed", msg=msg, data=None)

        self._build_image(id, self.dockerfile_path)
        self._start_container(id, dockercommand_content)
        self._update_python_project_data(id)

        self.logger.info("==================== Python Project Deploy : Finish ====================")
        return HttpResult[None](code=200, status="success", msg=f"{self.python_project.get('project_name')} 部署成功", data=None)

    def _create_project_directory(self):
        container_project_path = self.python_project.get('container_project_path')
        os.makedirs(container_project_path, exist_ok=True)
        self.logger.info(f"1 - Success - 创建项目目录: {container_project_path}")

    def _save_zip_file(self, zip_file: UploadFile) -> str:
        zip_path = os.path.join(self.python_project.get('container_project_path'), f"{self.python_project.get('project_code')}.zip")
        with open(zip_path, "wb") as buffer:
            shutil.copyfileobj(zip_file.file, buffer)
        self.logger.debug(f"ZIP 文件保存到: {zip_path}")
        return zip_path

    def _extract_zip_file(self, zip_path: str):
        extract_path = self.python_project.get('container_project_path')
        with zipfile.ZipFile(zip_path, "r") as zip_ref:
            zip_ref.extractall(extract_path)
        self.logger.debug(f"ZIP 文件解压到: {extract_path}")

    def _delete_zip_file(self, zip_path: str):
        os.remove(zip_path)
        self.logger.debug(f"临时 ZIP 文件已删除: {zip_path}")

    def _detect_or_create_dockerfile(self, dockerfile_content: str) -> bool:
        container_project_path = self.python_project.get('container_project_path')
        dockerfile_path = os.path.join(container_project_path, "Dockerfile")

        # 判断顶层是否已有 Dockerfile
        files_in_root = os.listdir(container_project_path)
        if "Dockerfile" in files_in_root:
            self.dockerfile_path = dockerfile_path
            self.logger.info("检测到解压目录下已有 Dockerfile")
            return True

        # 若参数中有 dockerfile_content 则写入
        if dockerfile_content:
            with open(dockerfile_path, "w") as f:
                f.write(dockerfile_content)
            self.dockerfile_path = dockerfile_path
            self.logger.info("根据传入内容创建 Dockerfile")
            return True

        return False

    def _build_image(self, id, dockerfile_path: str):
        dockerfile_folder = os.path.dirname(dockerfile_path)
        os.chdir(dockerfile_folder)
        command = [
            "docker", "build", "-t",
            f"{self.python_project.get('docker_image_name')}:{self.python_project.get('docker_image_tag')}", "."
        ]
        try:
            subprocess.run(command, check=True)
            self.logger.info(f"镜像 {self.python_project.get('docker_image_name')}:{self.python_project.get('docker_image_tag')} 构建成功")
        except subprocess.CalledProcessError as e:
            self.deploy_status = "FAILED"
            err_msg = f"镜像构建失败: {e}"
            self.logger.error(err_msg)
            self.deploy_history_manager.log_deploy_result(self.deploy_history_id, id, "failed", err_msg)
            raise RuntimeError(err_msg)  # 抛出异常，阻止继续执行

    def _start_container(self, id: str, dockercommand_content: str):
        container_name = self.python_project.get('project_code')
        try:
            check_result = subprocess.run(
                f"docker ps -a --format '{{{{.Names}}}}' | grep -w {container_name}",
                shell=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )
            if check_result.returncode == 0:
                subprocess.run(f"docker rm -f {container_name}", shell=True, check=False)

            dockercommand_content = re.sub(r'\\\s*\r?\n', ' ', dockercommand_content).strip()
            subprocess.run(dockercommand_content, shell=True, check=True)
            self.logger.info(f"容器 {container_name} 启动成功")
        except Exception as e:
            self.deploy_status = "FAILED"
            err_msg = f"容器启动失败: {e}"
            self.logger.error(err_msg)
            self.deploy_history_manager.log_deploy_result(self.deploy_history_id, id, "failed", err_msg)
            raise RuntimeError(err_msg)  # 抛出异常，阻止继续执行

    def _update_python_project_data(self, id):
        updated_data = {
            "status": "running",
            "updated_at": datetime.now().strftime("%Y-%m-%dT%H:%M:%S"),
            "last_deployed_at": datetime.now().strftime("%Y-%m-%dT%H:%M:%S")
        }
        self.project_data_manager.update_project(id, updated_data)
        self.logger.info("项目数据已更新")
        self.deploy_history_manager.log_deploy_result(self.deploy_history_id, id, self.deploy_status, None)
