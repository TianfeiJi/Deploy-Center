"""
@File           : java_project_deployer.py
@Author         : Tianfei Ji
@Description    :  Java 项目部署器，用于将上传的 JAR 包构建为 Docker 镜像并部署为服务容器。
"""
import os
import re
import shutil
import subprocess
from datetime import datetime
import uuid
from fastapi import UploadFile
from models.common.http_result import HttpResult
from models.enum.status_enum import StatusEnum
from manager.project_data_manager import ProjectDataManager
from manager.deploy_history_data_manager import DeployHistoryDataManager
from manager.template_manager import TemplateManager
from config.log_config import get_logger
from utils.user_context import get_current_user


class JavaProjectDeployer:
    """
    JavaProjectDeployer

    执行 Java 项目从构建到部署的完整流程，包含以下步骤：
        1. 准备部署目录
        2. 写入或覆盖 Dockerfile 文件
        3. 拷贝Jar包
        4. 清理同名旧容器与旧镜像（如存在）
        5. 构建 Docker 镜像
        6. 启动 Docker 容器
        7. 更新部署记录、项目信息

    支持异常处理、部署状态记录、日志输出，适用于后端自动化部署系统。
    """

    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(JavaProjectDeployer, cls).__new__(cls)
        return cls._instance

    def __init__(self):
        self.logger = get_logger()
        self.project_data_manager = ProjectDataManager().get_instance()
        self.deploy_history_manager = DeployHistoryDataManager().get_instance()
        self.template_manager = TemplateManager().get_instance()

        self.java_project = None
        self.dockerfile_path = None

    def deploy(self, id: str, jar_file: UploadFile, dockerfile_content: str, dockercommand_content: str):
        """
        部署 Java 项目主流程。
        """
        self.logger.info("==================== Java 项目部署：开始 ====================")
        self.user = get_current_user()
        self.logger.info(f"当前用户：{self.user}")
        
        self.deploy_status = StatusEnum.START
        self.java_project = self.project_data_manager.get_project(id)
        if self.java_project is None:
            return HttpResult[None](code=400, status="failed", msg=f"没有 id 为 {id} 的 Java 项目", data=None)

        self.logger.info(f"开始部署项目：{self.java_project}")
        # 生成部署历史id
        self.deploy_history_id = str(uuid.uuid4()).replace("-", "")[:8]

        self._create_project_directory()
        self._create_dockerfile(dockerfile_content)
        self._copy_jar_to_directory(jar_file)
        self._cleanup_old_container_and_image()
        self._build_image(id, self.dockerfile_path)
        self._start_container(id, dockercommand_content)
        self._update_java_project_data(id)

        self.logger.info("==================== Java 项目部署：完成 ====================")
        success_msg = (
            f"项目 {self.java_project.get('project_code')}（{self.java_project.get('project_name')}）部署成功，"
            f"容器 {self.java_project.get('container_name')} 已启动（基于镜像 {self.java_project.get('docker_image_name')}:{self.java_project.get('docker_image_tag')}）"
        )
        return success_msg

    def _create_project_directory(self):
        """
        1 - 准备项目目录

        创建项目所需的基础目录结构。
        如果项目目录已存在，则提示继续使用原目录；
        logs 子目录永远保留，jars 子目录若不存在则创建。
        """
        self.logger.info("1 - START - 准备项目目录")
        container_project_path = self.java_project.get('container_project_path')

        if os.path.exists(container_project_path):
            self.logger.info(f"1 - PROCESS - 检测到项目目录已存在，将继续使用原目录: {container_project_path}")
        else:
            os.makedirs(container_project_path)
            self.logger.info(f"1 - PROCESS - 已创建新的项目目录: {container_project_path}")

        os.makedirs(f"{container_project_path}/logs", exist_ok=True)
        os.makedirs(f"{container_project_path}/jars", exist_ok=True)
        self.logger.info(f"1 - FINISH - 项目目录结构已准备完成: {container_project_path}")

    def _create_dockerfile(self, dockerfile_content) -> str:
        """
        2 - 写入 Dockerfile

        写入或替换 Dockerfile。
        如果已存在旧版本，会打印替换提示。
        """
        self.logger.info("2 - START - 写入 Dockerfile")
        dockerfile_path = os.path.join(self.java_project.get('container_project_path'), "Dockerfile")
        if os.path.exists(dockerfile_path):
            self.logger.warning(f"2 - PROCESS - 检测到已存在 Dockerfile，将进行覆盖: {dockerfile_path}")
        with open(dockerfile_path, "w") as f:
            f.write(dockerfile_content)
        self.logger.info(f"2 - FINISH - Dockerfile 写入完成: {dockerfile_path}")
        self.dockerfile_path = dockerfile_path
        return dockerfile_path

    def _copy_jar_to_directory(self, jar_file: UploadFile):
        """
        3 - 拷贝 JAR 包

        拷贝上传的 JAR 文件到目标目录。
        """
        self.logger.info("3 - START - 拷贝 JAR 包")
        target_path = f"{self.java_project.get('container_project_path')}/jars/{self.java_project.get('project_code')}.jar"
        if os.path.exists(target_path):
            self.logger.warning(f"3 - PROCESS - 检测到旧 JAR 文件，将进行覆盖: {target_path}")
        with open(target_path, "wb") as buffer:
            shutil.copyfileobj(jar_file.file, buffer)
        self.logger.info(f"3 - FINISH - JAR 文件已拷贝至: {target_path}")

    def _cleanup_old_container_and_image(self):
        """
        4 - 检测并删除旧容器与镜像
        """
        container_name = self.java_project.get('project_code')
        image_name = f"{self.java_project.get('docker_image_name')}:{self.java_project.get('docker_image_tag')}"

        self.logger.info(f"4 - START - 检测并删除旧容器与镜像: {container_name} / {image_name}")

        # 清理旧容器
        try:
            check_container = subprocess.run(
                f"docker ps -a --format '{{{{.Names}}}}' | grep -w {container_name}",
                shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE
            )
            if check_container.returncode == 0:
                self.logger.info(f"4.1 - PROCESS - 检测到旧容器 {container_name}，执行删除...")
                subprocess.run(f"docker rm -f {container_name}", shell=True, check=False)
                self.logger.info(f"4.1 - FINISH - 旧容器已删除: {container_name}")
            else:
                self.logger.info(f"4.1 - SKIP - 未检测到旧容器: {container_name}")
        except Exception as e:
            self.logger.warning(f"4.1 - ERROR - 清理容器异常: {e}")
        
        # 清理旧镜像
        try:
            check_image = subprocess.run(
                f"docker images -q {image_name}",
                shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE
            )
            image_id = check_image.stdout.decode().strip()
            if image_id:
                self.logger.info(f"4.2 - PROCESS - 检测到旧镜像 {image_name}，执行删除...")
                subprocess.run(f"docker rmi -f {image_name}", shell=True, check=False)
                self.logger.info(f"4.2 - SUCCESS - 旧镜像已删除: {image_name}")
            else:
                self.logger.info(f"4.2 - SKIP - 未检测到旧镜像: {image_name}")
        except Exception as e:
            self.logger.warning(f"4.2 - ERROR - 清理镜像异常: {e}")
        self.logger.info("4 - FINISH - 旧容器与镜像检测与清理流程完成")
        
    def _build_image(self, id, dockerfile_path: str):
        """
        5 - 构建镜像

        执行镜像构建。
        """
        self.logger.info("5 - START - 构建镜像")
        dockerfile_folder = os.path.dirname(dockerfile_path)
        os.chdir(dockerfile_folder)
        image_name = f"{self.java_project.get('docker_image_name')}:{self.java_project.get('docker_image_tag')}"
        command = ["docker", "build", "-t", image_name, "."]
        try:
            self.logger.info(f"5 - PROCESS - 执行构建命令: {' '.join(command)}")
            subprocess.run(command, check=True)
            self.logger.info(f"5 - FINISH - 镜像构建成功: {image_name}")
        except subprocess.CalledProcessError as e:
            self.deploy_status = StatusEnum.FAILED
            err_msg = f"5 - ERROR - 镜像构建失败: {image_name}, 错误: {e}"
            self.logger.error(err_msg)
            self.deploy_history_manager.log_deploy_result(self.deploy_history_id, id, "failed", err_msg, self.user)
            raise RuntimeError(err_msg)

    def _start_container(self, id: str, dockercommand_content: str):
        """
        6 - 启动容器

        启动 Docker 容器。
        """
        self.logger.info("6 - START - 启动容器")
        container_name = self.java_project.get('project_code')
        try:
            dockercommand_content = re.sub(r'\\\s*\r?\n', ' ', dockercommand_content).strip()
            subprocess.run(dockercommand_content, shell=True, check=True)
            self.logger.info(f"6 - FINISH - 容器启动成功: {container_name}")
        except Exception as e:
            self.deploy_status = StatusEnum.FAILED
            err_msg = f"6 - ERROR - 容器启动失败: {container_name}, 错误: {e}"
            self.logger.error(err_msg)
            self.deploy_history_manager.log_deploy_result(self.deploy_history_id, id, self.deploy_status, err_msg, self.user)
            raise RuntimeError(err_msg)

    def _update_java_project_data(self, id):
        """
        7 - 更新部署记录和项目状态

        更新部署成功后的项目状态和时间戳。
        """
        self.logger.info("7 - START - 更新部署记录和项目状态")
        updated_data = {
            "status": "running",
            "updated_at": datetime.now().strftime("%Y-%m-%dT%H:%M:%S"),
            "last_deployed_at": datetime.now().strftime("%Y-%m-%dT%H:%M:%S")
        }
        try:
            self.project_data_manager.update_project(id, updated_data)
            self.logger.info("7.1 - FINISH - 项目状态更新成功")
        except Exception as e:
            self.deploy_status = StatusEnum.FAILED
            err_msg = f"7.1 - ERROR - 项目状态更新失败: {e}"
            self.logger.error(err_msg)

        try:
            self.deploy_status = StatusEnum.SUCCESS
            self.deploy_history_manager.log_deploy_result(self.deploy_history_id, id, self.deploy_status, None, self.user)
            self.logger.info("7.2 - FINISH - 部署记录更新成功")
        except Exception as e:
            self.deploy_status = StatusEnum.FAILED
            err_msg = f"7.2 - ERROR - 部署记录更新失败: {e}"
            self.logger.error(err_msg)
        self.logger.info("7 - FINISH - 更新部署记录和项目状态完成")
        
        