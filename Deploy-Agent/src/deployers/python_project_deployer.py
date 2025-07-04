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
from datetime import datetime
import uuid
from loguru import logger
from fastapi import UploadFile
from models.common.http_result import HttpResult
from models.enum.status_enum import StatusEnum
from manager import PROJECT_DATA_MANAGER, DEPLOY_HISTORY_DATA_MANAGER
from utils.user_context import get_current_user


class PythonProjectDeployer:
    """
    PythonProjectDeployer

    执行 Python 项目从构建到部署的完整流程，包含以下步骤：
        1. 准备部署目录
        2. 保存上传的 ZIP 包
        3. 解压 ZIP 包
        4. 删除临时 ZIP 文件
        5. 写入或覆盖 Dockerfile
        6. 清理旧容器与镜像（如存在）
        7. 构建 Docker 镜像
        8. 启动 Docker 容器
        9. 更新部署记录与项目信息

    支持异常处理、部署状态记录、日志输出，适用于后端自动化部署系统。
    """

    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(PythonProjectDeployer, cls).__new__(cls)
        return cls._instance

    def __init__(self):
        self.python_project = None
        self.dockerfile_path = None

    def deploy(self, id: str, zip_file: UploadFile, dockerfile_content: str, dockercommand_content: str):
        logger.info("==================== Python 项目部署：开始 ====================")
        self.user = get_current_user()
        safe_user_info = {
            "id": self.user.get("id"),
            "username": self.user.get("username"),
            "nickname": self.user.get("nickname")
        }
        logger.info(f"当前用户（简要）：{safe_user_info}")
        
        self.deploy_status = StatusEnum.START
        self.python_project = PROJECT_DATA_MANAGER.get_project(id)
        if self.python_project is None:
            return HttpResult[None](code=400, status="failed", msg=f"没有 id 为 {id} 的 Python 项目", data=None)

        logger.info(f"开始部署项目：{self.python_project}")
        self.deploy_history_id = str(uuid.uuid4()).replace("-", "")[:8]

        self._create_project_directory()
        zip_path = self._save_zip_file(zip_file)
        self._unzip_project(zip_path)
        self._delete_zip_file(zip_path)
        self._create_dockerfile(dockerfile_content)
        self._cleanup_old_container_and_image()
        self._build_image(id, self.dockerfile_path)
        self._start_container(id, dockercommand_content)
        self._update_python_project_data(id)

        logger.info("==================== Python 项目部署：完成 ====================")
        success_msg = (
            f"项目 {self.python_project.get('project_code')}（{self.python_project.get('project_name')}）部署成功，"
            f"镜像 {self.python_project.get('docker_image_name')}:{self.python_project.get('docker_image_tag')} 已启动"
        )
        return success_msg

    def _create_project_directory(self):
        logger.info("1 - START - 准备部署目录")
        container_project_path = self.python_project.get('container_project_path')

        if os.path.exists(container_project_path):
            logger.info(f"1 - PROCESS - 检测到目录已存在，将继续使用: {container_project_path}")
        else:
            os.makedirs(container_project_path)
            logger.info(f"1 - PROCESS - 创建新部署目录: {container_project_path}")

        os.makedirs(f"{container_project_path}/logs", exist_ok=True)
        os.makedirs(f"{container_project_path}/app", exist_ok=True)
        logger.info("1 - FINISH - 部署目录准备完成")

    def _save_zip_file(self, zip_file: UploadFile) -> str:
        logger.info("2 - START - 保存上传的 ZIP 包")
        zip_path = os.path.join(self.python_project.get('container_project_path'), "app/project.zip")
        with open(zip_path, "wb") as f:
            shutil.copyfileobj(zip_file.file, f)
        logger.info(f"2 - FINISH - ZIP 文件保存成功: {zip_path}")
        return zip_path

    def _unzip_project(self, zip_path: str):
        logger.info("3 - START - 解压 ZIP 包")
        unzip_command = f"unzip -o {zip_path} -d {os.path.dirname(zip_path)}"
        try:
            subprocess.run(unzip_command, shell=True, check=True)
            logger.info("3 - FINISH - ZIP 解压完成")
        except Exception as e:
            raise RuntimeError(f"3 - ERROR - 解压失败: {e}")

    def _delete_zip_file(self, zip_path: str):
        logger.info("4 - START - 删除临时 ZIP 文件")
        os.remove(zip_path)
        logger.info("4 - FINISH - ZIP 文件已删除")

    def _create_dockerfile(self, dockerfile_content: str):
        logger.info("5 - START - 写入 Dockerfile")
        dockerfile_path = os.path.join(self.python_project.get('container_project_path'), "Dockerfile")
        if os.path.exists(dockerfile_path):
            logger.warning(f"5 - PROCESS - 检测到已存在 Dockerfile，将进行覆盖: {dockerfile_path}")
        with open(dockerfile_path, "w") as f:
            f.write(dockerfile_content)
        logger.info(f"5 - FINISH - Dockerfile 写入完成: {dockerfile_path}")
        self.dockerfile_path = dockerfile_path

    def _cleanup_old_container_and_image(self):
        logger.info("6 - START - 清理旧容器与镜像")
        container_name = self.python_project.get('project_code')
        image_name = f"{self.python_project.get('docker_image_name')}:{self.python_project.get('docker_image_tag')}"

        try:
            check_container = subprocess.run(
                f"docker ps -a --format '{{{{.Names}}}}' | grep -w {container_name}",
                shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE
            )
            if check_container.returncode == 0:
                logger.info(f"6.1 - PROCESS - 发现旧容器，删除中: {container_name}")
                subprocess.run(f"docker rm -f {container_name}", shell=True, check=False)
            else:
                logger.info(f"6.1 - SKIP - 未检测到旧容器: {container_name}")
        except Exception as e:
            logger.warning(f"6.1 - ERROR - 删除容器异常: {e}")

        try:
            check_image = subprocess.run(
                f"docker images -q {image_name}",
                shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE
            )
            image_id = check_image.stdout.decode().strip()
            if image_id:
                logger.info(f"6.2 - PROCESS - 发现旧镜像，删除中: {image_name}")
                subprocess.run(f"docker rmi -f {image_name}", shell=True, check=False)
            else:
                logger.info(f"6.2 - SKIP - 未检测到旧镜像: {image_name}")
        except Exception as e:
            logger.warning(f"6.2 - ERROR - 删除镜像异常: {e}")
        logger.info("6 - FINISH - 清理完成")

    def _build_image(self, id: str, dockerfile_path: str):
        logger.info("7 - START - 构建 Docker 镜像")
        image_name = f"{self.python_project.get('docker_image_name')}:{self.python_project.get('docker_image_tag')}"
        os.chdir(os.path.dirname(dockerfile_path))
        command = ["docker", "build", "-t", image_name, "."]
        try:
            logger.info(f"7 - PROCESS - 执行构建命令: {' '.join(command)}")
            subprocess.run(command, check=True)
            logger.info(f"7 - FINISH - 镜像构建成功: {image_name}")
        except subprocess.CalledProcessError as e:
            self.deploy_status = StatusEnum.FAILED
            err_msg = f"7 - ERROR - 镜像构建失败: {image_name}, 错误: {e}"
            logger.error(err_msg)
            DEPLOY_HISTORY_DATA_MANAGER.log_deploy_result(self.deploy_history_id, id, "failed", err_msg, self.user)
            raise RuntimeError(err_msg)

    def _start_container(self, id: str, dockercommand_content: str):
        logger.info("8 - START - 启动容器")
        container_name = self.python_project.get('project_code')
        try:
            dockercommand_content = re.sub(r'\\\s*\r?\n', ' ', dockercommand_content).strip()
            subprocess.run(dockercommand_content, shell=True, check=True)
            logger.info(f"8 - FINISH - 容器启动成功: {container_name}")
        except Exception as e:
            self.deploy_status = StatusEnum.FAILED
            err_msg = f"8 - ERROR - 容器启动失败: {container_name}, 错误: {e}"
            logger.error(err_msg)
            DEPLOY_HISTORY_DATA_MANAGER.log_deploy_result(self.deploy_history_id, id, self.deploy_status, err_msg, self.user)
            raise RuntimeError(err_msg)

    def _update_python_project_data(self, id: str):
        logger.info("9 - START - 更新部署时间与部署记录数据")
        updated_data = {
            "last_deployed_at": datetime.now().strftime("%Y-%m-%dT%H:%M:%S")
        }
        try:
            PROJECT_DATA_MANAGER.update_project(id, updated_data)
            logger.info("9.1 - FINISH - 部署时间更新成功")
        except Exception as e:
            self.deploy_status = StatusEnum.FAILED
            logger.error(f"9.1 - ERROR - 部署时间更新失败: {e}")

        try:
            self.deploy_status = StatusEnum.SUCCESS
            DEPLOY_HISTORY_DATA_MANAGER.log_deploy_result(self.deploy_history_id, id, self.deploy_status, None, self.user)
            logger.info("9.2 - FINISH - 部署记录更新成功")
        except Exception as e:
            self.deploy_status = StatusEnum.FAILED
            logger.error(f"9.2 - ERROR - 更新部署记录失败: {e}")

        logger.info("9 - FINISH - 部署记录与项目状态更新完成")