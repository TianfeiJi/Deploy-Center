import os
import re
import shutil
import subprocess
from datetime import datetime
import uuid
from fastapi import UploadFile
from models.common.http_result import HttpResult
from manager.project_data_manager import ProjectDataManager
from manager.deploy_history_data_manager import DeployHistoryDataManager
from manager.template_manager import TemplateManager
from config.log_config import get_logger


class JavaProjectDeployer:
    _instance = None

    def __new__(cls):
        """
        确保只创建一个实例。
        """
        if cls._instance is None:
            cls._instance = super(JavaProjectDeployer, cls).__new__(cls)
        return cls._instance
    
    def __init__(self):
        # 使用全局 logger
        self.logger = get_logger()
        self.project_data_manager = ProjectDataManager().get_instance()
        self.deploy_history_manager = DeployHistoryDataManager().get_instance()
        self.template_manager = TemplateManager().get_instance()

        self.java_project = None
        self.dockerfile_path = None
    
    def deploy(self, id: str, jar_file: UploadFile, dockerfile_content: str, dockercommand_content: str):
        """部署 Java 项目"""
        self.logger.info("==================== Java Project Deploy : Start ====================")
        self.deploy_status = "START"
        self.java_project = self.project_data_manager.get_project(id)
        if (self.java_project is None):
            return HttpResult[None](code=400, status="failed", msg=f"没有id为{id}的Java项目", data=None)
        self.logger.info(f"开始部署项目：{self.java_project}")
        # 部署历史ID
        self.deploy_history_id = str(uuid.uuid4()).replace("-", "")[:8]
        # 创建项目文件夹
        self._create_project_directory()
        # 创建Dockerfile
        self.dockerfile_path = self._create_dockerfile(dockerfile_content)
        # 将jar包移动到目标文件夹
        self._copy_jar_to_directory(jar_file)
        # 构建镜像
        self._build_image(id, self.dockerfile_path)
        # 启动容器
        self._start_container(id, dockercommand_content)
        # 更新项目信息
        self._update_java_project_data(id)
       
        self.logger.info("==================== Java Project Deploy : Finish ====================")
        sussess_msg = f"项目 {self.java_project.get('project_code')}（{self.java_project.get('project_name')}） 部署成功, {self.java_project.get('docker_image_name')}:{self.java_project.get('docker_image_tag')}已启动"
        return sussess_msg

    def _create_project_directory(self):
        """创建项目目录"""
        self.logger.info(f"1 - Start - 创建容器卷目录")
        container_project_path = self.java_project.get('container_project_path')
        # os.makedirs(f"{container_project_path}/config", exist_ok=True)  # 配置文件目录
        os.makedirs(f"{container_project_path}/logs", exist_ok=True)    # 日志目录
        os.makedirs(f"{container_project_path}/jars", exist_ok=True)    # JAR 包目录
        self.logger.info(f"1 - Success - 项目目录已创建: {container_project_path}")

    def _create_dockerfile(self, dockerfile_content) -> str:
        """创建 Dockerfile"""
        self.logger.info(f"2 - Start - 创建Dockerfile")
        dockerfile_path = os.path.join(self.java_project.get('container_project_path'), "Dockerfile")
        with open(dockerfile_path, "w") as f:
            f.write(dockerfile_content)
        self.logger.info(f"2 - Success - Dockerfile 已创建: {dockerfile_path}")
        return dockerfile_path

    def _copy_jar_to_directory(self, jar_file: UploadFile):
        """复制 JAR 文件"""
        self.logger.info(f"3 - Start - 拷贝Jar包")
        target_path = f"{self.java_project.get('container_project_path')}/jars/{self.java_project.get('project_code')}.jar"

        # 将 JAR 文件直接拷贝到目标路径
        with open(target_path, "wb") as buffer:
            shutil.copyfileobj(jar_file.file, buffer)

        self.logger.info(f"3 - Success - JAR 文件已拷贝到: {target_path}")

    def _build_image(self, id, dockerfile_path: str):
        """构建 Docker 镜像"""
        self.logger.info("4 - Start - 构建镜像")

        # 获取 Dockerfile 所在的文件夹路径
        dockerfile_folder = os.path.dirname(dockerfile_path)
        self.logger.info(f"5 - Process - 进入Dockerfile所在目录：{dockerfile_folder}")
        # 确保构建镜像时，Docker 的上下文路径是 Dockerfile 所在的目录
        os.chdir(dockerfile_folder)  # 进入 Dockerfile 所在目录

        command = [
            "docker", "build", "-t", f"{self.java_project.get('docker_image_name')}:{self.java_project.get('docker_image_tag')}", "."
        ]
        try:
            self.logger.info(f"4 - Process - 构建镜像, 执行命令：{' '.join(command)}")
            subprocess.run(command, check=True)
            self.logger.info(
                f"4 - Success - 镜像 {self.java_project.get('docker_image_name')}:{self.java_project.get('docker_image_tag')} 构建成功")
        except subprocess.CalledProcessError as e:
            self.deploy_status = "FAILED"
            err_msg = f"4 - Failed - 镜像 {self.java_project.get('docker_image_name')}:{self.java_project.get('docker_image_tag')} 构建失败: {e}"
            self.logger.error(err_msg)
            # 更新部署历史
            self.deploy_history_manager.log_deploy_result(self.deploy_history_id, id, "failed", err_msg)
            raise RuntimeError(err_msg)  # 抛出异常，阻止继续执行

    def _start_container(self, id: str, dockercommand_content: str):
        """启动容器"""
        self.logger.info(f"5 - Start - 启动容器")
        container_name = self.java_project.get('project_code')
        try:
            # 判断容器是否存在
            check_result = subprocess.run(
                f"docker ps -a --format '{{{{.Names}}}}' | grep -w {container_name}",
                shell=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )
            # 如果存在，则删除旧的
            if check_result.returncode == 0:
                self.logger.info(f"5 - Process - 检测到旧容器: {container_name}")
                subprocess.run(f"docker rm -f {container_name}", shell=True, check=False)
                self.logger.info(f"5 - Process - 已清理旧容器: {container_name}")

            #  替换 \ 以及 换行符 为 空格
            dockercommand_content = re.sub(r'\\\s*\r?\n', ' ', dockercommand_content).strip()
            subprocess.run(dockercommand_content, shell=True, check=True)
            self.logger.info(f"5 - Success - {container_name} 容器启动成功")
        except Exception as e:
            self.deploy_status = "FAILED"
            err_msg =  f"5 - Failed - {container_name} 容器启动失败: {e}"
            self.logger.error(err_msg)
            # 更新部署历史
            self.deploy_history_manager.log_deploy_result(self.deploy_history_id, id, self.deploy_status, err_msg)
            raise RuntimeError(err_msg)  # 抛出异常，阻止继续执行

    def _update_java_project_data(self, id):
        """更新项目数据"""
        self.logger.info(f"6 - Start - 更新项目数据")
        updated_data = {
            "status": "running",
            "updated_at": datetime.now().strftime("%Y-%m-%dT%H:%M:%S"),
            "last_deployed_at": datetime.now().strftime("%Y-%m-%dT%H:%M:%S")
        }
        self.project_data_manager.update_project(id, updated_data)
        self.logger.info(f"6 - Success - 更新项目数据成功")
        # 更新部署历史
        self.deploy_history_manager.log_deploy_result(self.deploy_history_id, id, self.deploy_status, None)