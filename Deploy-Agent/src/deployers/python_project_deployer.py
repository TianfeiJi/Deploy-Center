import os
import re
import shutil
import subprocess
import zipfile
from datetime import datetime
import uuid
from loguru import logger
from fastapi import UploadFile
from models.common.http_result import HttpResult
from models.enum.status_enum import StatusEnum
from manager import PROJECT_DATA_MANAGER, DEPLOY_HISTORY_DATA_MANAGER
from utils.user_context import get_current_user
from utils.deploy_validator import DeployValidator


class PythonProjectDeployer:
    """
    PythonProjectDeployer

    执行 Python 项目从构建到部署的完整流程，包含以下步骤：
        1. 准备部署目录
        2. 保存上传的 ZIP 包
        3. 解压 ZIP 包
        4. 删除临时 ZIP 文件
        5. 识别项目根目录
        6. 校验项目 Dockerfile
        7. 写入或覆盖 Dockerignore
        8. 清理旧容器与镜像（如存在）
        9. 构建 Docker 镜像
        10. 启动 Docker 容器
        11. 更新部署记录与项目信息

    ZIP 包支持两种结构：
        1. 解压后根目录直接包含 Dockerfile
        2. 解压后根目录仅包含一个一级子目录，且该子目录下包含 Dockerfile
    """

    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(PythonProjectDeployer, cls).__new__(cls)
        return cls._instance

    def __init__(self):
        self.python_project = None
        self.dockerfile_path = None
        self.build_context_path = None

    def deploy(self, id: str, zip_file: UploadFile, dockercommand_content: str):
        logger.info("==================== Python 项目部署：开始 ====================")

        self.user = get_current_user()
        user_brief = {
            "id": self.user.get("id"),
            "username": self.user.get("username"),
            "nickname": self.user.get("nickname")
        }
        logger.info(f"操作用户：{user_brief}")

        self.deploy_status = StatusEnum.START
        self.python_project = PROJECT_DATA_MANAGER.get_project(id)
        if self.python_project is None:
            return HttpResult[None](code=400, status="failed", msg=f"没有 id 为 {id} 的 Python 项目", data=None)

        project_brief = {
            "id": self.python_project.get("id"),
            "project_code": self.python_project.get("project_code"),
            "project_name": self.python_project.get("project_name"),
        }
        logger.info(f"开始部署项目：{project_brief}")
        self.deploy_history_id = str(uuid.uuid4()).replace("-", "")[:8]

        self._create_project_directory()
        zip_path = self._save_zip_file(zip_file)
        self._unzip_project(zip_path)
        self._delete_zip_file(zip_path)

        self.build_context_path = self._detect_project_root()
        self._validate_project_dockerfile()
        self._create_dockerignore()

        self._cleanup_old_container_and_image()
        self._build_image(id)
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
        container_project_path = self.python_project.get("container_project_path")

        if os.path.exists(container_project_path):
            logger.info(f"1 - PROCESS - 检测到目录已存在，将继续使用: {container_project_path}")
        else:
            os.makedirs(container_project_path)
            logger.info(f"1 - PROCESS - 创建新部署目录: {container_project_path}")

        os.makedirs(os.path.join(container_project_path, "logs"), exist_ok=True)
        os.makedirs(os.path.join(container_project_path, "app"), exist_ok=True)
        logger.info("1 - FINISH - 部署目录准备完成")

    def _save_zip_file(self, zip_file: UploadFile) -> str:
        logger.info("2 - START - 保存上传的 ZIP 包")
        zip_path = os.path.join(self.python_project.get("container_project_path"), "app", "project.zip")
        with open(zip_path, "wb") as f:
            shutil.copyfileobj(zip_file.file, f)
        logger.info(f"2 - FINISH - ZIP 文件保存成功: {zip_path}")
        return zip_path

    def _unzip_project(self, zip_path: str):
        logger.info("3 - START - 清理目录并解压 ZIP 包")

        app_dir = os.path.dirname(zip_path)

        try:
            logger.info(f"3.1 - PROCESS - 清理目录: {app_dir}")
            for filename in os.listdir(app_dir):
                file_path = os.path.join(app_dir, filename)

                if file_path == zip_path:
                    continue

                if os.path.isfile(file_path) or os.path.islink(file_path):
                    os.remove(file_path)
                elif os.path.isdir(file_path):
                    shutil.rmtree(file_path)

            logger.info("3.1 - FINISH - 目录清理完成")
        except Exception as e:
            err_msg = f"3.1 - ERROR - 清理目录失败: {e}"
            logger.error(err_msg)
            raise RuntimeError(err_msg)

        try:
            logger.info("3.2 - PROCESS - 开始解压 ZIP 文件")
            with zipfile.ZipFile(zip_path, "r") as zip_ref:
                zip_ref.extractall(app_dir)
            logger.info("3.2 - FINISH - ZIP 解压完成")
        except zipfile.BadZipFile as e:
            err_msg = f"3.2 - ERROR - ZIP 文件无效: {e}"
            logger.error(err_msg)
            raise RuntimeError(err_msg)
        except Exception as e:
            err_msg = f"3.2 - ERROR - 解压失败: {e}"
            logger.error(err_msg)
            raise RuntimeError(err_msg)

        logger.info("3 - FINISH - 解压流程完成")

    def _delete_zip_file(self, zip_path: str):
        logger.info("4 - START - 删除临时 ZIP 文件")
        os.remove(zip_path)
        logger.info("4 - FINISH - ZIP 文件已删除")

    def _detect_project_root(self) -> str:
        """
        5 - 识别项目根目录

        支持两种结构：
            1. app 根目录直接包含 Dockerfile
            2. app 根目录仅包含一个一级子目录，且该子目录下包含 Dockerfile
        """
        logger.info("5 - START - 识别项目根目录")
        app_dir = os.path.join(self.python_project.get("container_project_path"), "app")

        root_dockerfile = os.path.join(app_dir, "Dockerfile")
        if os.path.isfile(root_dockerfile):
            logger.info(f"5.1 - FINISH - 检测到根目录 Dockerfile，项目根目录为: {app_dir}")
            return app_dir

        try:
            entries = os.listdir(app_dir)
            visible_entries = [name for name in entries if name not in ["__MACOSX", ".DS_Store"]]
            subdirs = [
                os.path.join(app_dir, name)
                for name in visible_entries
                if os.path.isdir(os.path.join(app_dir, name))
            ]
            files = [
                os.path.join(app_dir, name)
                for name in visible_entries
                if os.path.isfile(os.path.join(app_dir, name))
            ]
        except Exception as e:
            err_msg = f"5.1 - ERROR - 读取解压目录失败: {e}"
            logger.error(err_msg)
            raise RuntimeError(err_msg)

        if len(subdirs) == 1 and len(files) == 0:
            candidate_dir = subdirs[0]
            candidate_dockerfile = os.path.join(candidate_dir, "Dockerfile")
            if os.path.isfile(candidate_dockerfile):
                logger.info(f"5.2 - FINISH - 检测到唯一一级子目录 Dockerfile，项目根目录为: {candidate_dir}")
                return candidate_dir

        err_msg = (
            "5 - ERROR - 未检测到可用的项目根目录。"
            "请确保 ZIP 解压后满足以下之一："
            "1）根目录直接包含 Dockerfile；"
            "2）根目录仅包含一个项目目录，且该目录下包含 Dockerfile。"
        )
        logger.error(err_msg)
        raise RuntimeError(err_msg)

    def _validate_project_dockerfile(self) -> str:
        """
        6 - 校验项目 Dockerfile
        """
        logger.info("6 - START - 校验项目 Dockerfile")

        if not self.build_context_path:
            raise RuntimeError("6 - ERROR - build_context_path 未初始化，无法校验 Dockerfile")

        dockerfile_path = os.path.join(self.build_context_path, "Dockerfile")
        if not os.path.isfile(dockerfile_path):
            err_msg = f"6 - ERROR - 未找到 Dockerfile: {dockerfile_path}"
            logger.error(err_msg)
            raise RuntimeError(err_msg)

        try:
            logger.info(f"6.1 - PROCESS - 读取 Dockerfile: {dockerfile_path}")
            with open(dockerfile_path, "r", encoding="utf-8") as f:
                dockerfile_content = f.read()

            logger.info("6.2 - PROCESS - 开始校验 Dockerfile 内容")
            DeployValidator.validate_dockerfile(dockerfile_content)
            logger.info("6.2 - FINISH - Dockerfile 内容校验通过")
        except Exception as e:
            err_msg = f"6 - ERROR - Dockerfile 校验失败: {e}"
            logger.error(err_msg)
            raise RuntimeError(err_msg)

        self.dockerfile_path = dockerfile_path
        logger.info(f"6 - FINISH - Dockerfile 校验完成: {dockerfile_path}")
        return dockerfile_path

    def _create_dockerignore(self):
        """
        7 - 写入 .dockerignore

        以识别出的 build_context_path 为准创建或保留 .dockerignore。
        """
        logger.info("7 - START - 写入 .dockerignore")

        if not self.build_context_path:
            raise RuntimeError("7 - ERROR - build_context_path 未初始化，无法写入 .dockerignore")

        dockerignore_path = os.path.join(self.build_context_path, ".dockerignore")
        ignore_rules = [
            "logs/",
            "*.log",
            "*.tmp",
            "__pycache__/",
            ".DS_Store",
            "__MACOSX/",
            "*.zip"
        ]

        try:
            if os.path.exists(dockerignore_path):
                logger.info(f"7 - PROCESS - 检测到已有 .dockerignore 文件，跳过创建: {dockerignore_path}")
            else:
                logger.info("7 - PROCESS - 未检测到 .dockerignore 文件，准备创建")
                with open(dockerignore_path, "w", encoding="utf-8") as f:
                    f.write("\n".join(ignore_rules) + "\n")
                logger.info(f"7 - PROCESS - 创建并写入 .dockerignore 完成: {dockerignore_path}")
            logger.info("7 - FINISH - .dockerignore 检查与写入流程完成")
        except Exception as e:
            logger.warning(f"7 - ERROR - 写入 .dockerignore 失败: {e}")

    def _cleanup_old_container_and_image(self):
        logger.info("8 - START - 清理旧容器与镜像")
        container_name = self.python_project.get("project_code")
        image_name = f"{self.python_project.get('docker_image_name')}:{self.python_project.get('docker_image_tag')}"

        try:
            check_container = subprocess.run(
                f"docker ps -a --format '{{{{.Names}}}}' | grep -w {container_name}",
                shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE
            )
            if check_container.returncode == 0:
                logger.info(f"8.1 - PROCESS - 发现旧容器，删除中: {container_name}")
                subprocess.run(f"docker rm -f {container_name}", shell=True, check=False)
            else:
                logger.info(f"8.1 - SKIP - 未检测到旧容器: {container_name}")
        except Exception as e:
            logger.warning(f"8.1 - ERROR - 删除容器异常: {e}")

        try:
            check_image = subprocess.run(
                f"docker images -q {image_name}",
                shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE
            )
            image_id = check_image.stdout.decode().strip()
            if image_id:
                logger.info(f"8.2 - PROCESS - 发现旧镜像，删除中: {image_name}")
                subprocess.run(f"docker rmi -f {image_name}", shell=True, check=False)
            else:
                logger.info(f"8.2 - SKIP - 未检测到旧镜像: {image_name}")
        except Exception as e:
            logger.warning(f"8.2 - ERROR - 删除镜像异常: {e}")
        logger.info("8 - FINISH - 清理完成")

    def _build_image(self, id: str):
        logger.info("9 - START - 构建 Docker 镜像")

        if not self.build_context_path:
            raise RuntimeError("9 - ERROR - build_context_path 未初始化，无法构建镜像")

        image_name = f"{self.python_project.get('docker_image_name')}:{self.python_project.get('docker_image_tag')}"
        command = ["docker", "build", "-t", image_name, "."]

        try:
            logger.info(f"9 - PROCESS - 执行构建命令: {' '.join(command)}")
            logger.info(f"9 - PROCESS - 构建上下文目录: {self.build_context_path}")
            subprocess.run(command, check=True, cwd=self.build_context_path)
            logger.info(f"9 - FINISH - 镜像构建成功: {image_name}")
        except subprocess.CalledProcessError as e:
            self.deploy_status = StatusEnum.FAILED
            err_msg = f"9 - ERROR - 镜像构建失败: {image_name}, 错误: {e}"
            logger.error(err_msg)
            DEPLOY_HISTORY_DATA_MANAGER.log_deploy_result(self.deploy_history_id, id, "failed", err_msg, self.user)
            raise RuntimeError(err_msg)

    def _start_container(self, id: str, dockercommand_content: str):
        logger.info("10 - START - 校验启动命令并启动容器")
        container_name = self.python_project.get("project_code")

        dockercommand_content = re.sub(r'\\\s*\r?\n', ' ', dockercommand_content).strip()

        try:
            logger.info("10.1 - PROCESS - 开始校验 docker run 命令")
            DeployValidator.validate_docker_command(dockercommand_content)
            logger.info("10.1 - FINISH - docker run 命令校验通过")
        except Exception as e:
            err_msg = f"10.1 - ERROR - docker run 命令校验失败: {e}"
            logger.error(err_msg)
            raise RuntimeError(err_msg)

        try:
            subprocess.run(dockercommand_content, shell=True, check=True)
            logger.info(f"10 - FINISH - 容器启动成功: {container_name}")
        except Exception as e:
            self.deploy_status = StatusEnum.FAILED
            err_msg = f"10 - ERROR - 容器启动失败: {container_name}, 错误: {e}"
            logger.error(err_msg)
            DEPLOY_HISTORY_DATA_MANAGER.log_deploy_result(self.deploy_history_id, id, self.deploy_status, err_msg, self.user)
            raise RuntimeError(err_msg)

    def _update_python_project_data(self, id: str):
        logger.info("11 - START - 更新部署时间与部署记录数据")
        updated_data = {
            "last_deployed_at": datetime.now().strftime("%Y-%m-%dT%H:%M:%S")
        }
        try:
            PROJECT_DATA_MANAGER.update_project(id, updated_data)
            logger.info("11.1 - FINISH - 部署时间更新成功")
        except Exception as e:
            self.deploy_status = StatusEnum.FAILED
            logger.error(f"11.1 - ERROR - 部署时间更新失败: {e}")

        try:
            self.deploy_status = StatusEnum.SUCCESS
            DEPLOY_HISTORY_DATA_MANAGER.log_deploy_result(self.deploy_history_id, id, self.deploy_status, None, self.user)
            logger.info("11.2 - FINISH - 部署记录更新成功")
        except Exception as e:
            self.deploy_status = StatusEnum.FAILED
            logger.error(f"11.2 - ERROR - 更新部署记录失败: {e}")

        logger.info("11 - FINISH - 部署记录与项目状态更新完成")