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
from models.enum.deploy_strategy_enum import DeployStrategyEnum
from manager import PROJECT_DATA_MANAGER, DEPLOY_HISTORY_DATA_MANAGER
from utils.user_context import get_current_user
from utils.deploy_validator import DeployValidator
from context.deploy_context import DeployContext


class PythonProjectDeployer:
    """
    PythonProjectDeployer

    Python 项目部署执行器（Deployment Executor）。

    职责说明：
        负责根据不同部署策略（如 RECREATE、BLUE_GREEN 等），
        执行 Python 项目的构建、部署与运行流程。

    核心能力：
        - 接收上传的项目 ZIP 包
        - 解析并识别项目结构
        - 校验 Dockerfile 与启动命令
        - 构建 Docker 镜像
        - 启动或切换容器实例
        - 记录部署结果与状态

    设计说明：
        - deploy(...) 为统一入口，根据 strategy 分发不同部署策略
        - 各部署策略实现为独立方法（如 _recreate_deploy / _blue_green_deploy）

    ZIP 包结构支持：
        1. 根目录直接包含 Dockerfile
        2. 根目录仅包含一个子目录，且该子目录包含 Dockerfile
    """
    def __init__(self):
        self.python_project = None

    def deploy(self, id: str, zip_file: UploadFile, dockercommand_content: str,
               strategy: str = DeployStrategyEnum.default()):

        if strategy == DeployStrategyEnum.RECREATE:
            return self._recreate_deploy(id, zip_file, dockercommand_content)

        if strategy == DeployStrategyEnum.BLUE_GREEN:
            return self._blue_green_deploy(id, zip_file, dockercommand_content)

        raise ValueError(f"不支持的部署策略: {strategy}")

    def _recreate_deploy(self, id: str, zip_file: UploadFile, dockercommand_content: str):
        """
        单实例重建式部署（Recreate Deployment）

        流程说明：
            1. 准备部署目录
            2. 保存上传的 ZIP 包
            3. 解压 ZIP 包
            4. 删除临时 ZIP 文件
            5. 识别项目根目录
            6. 校验项目 Dockerfile
            7. 写入或覆盖 .dockerignore
            8. 清理旧容器与镜像（如存在）
            9. 构建 Docker 镜像
            10. 启动 Docker 容器
            11. 更新部署记录与项目信息

        特点：
            - 实现简单
            - 存在短暂服务中断
            - 不支持无感更新
            - 适用于开发环境或低可用性要求场景
        """
        # ===== 初始化 =====
        self.deploy_history_id = str(uuid.uuid4()).replace("-", "")[:8]
        strategy = DeployStrategyEnum.RECREATE.value

        self.user = get_current_user()

        self.python_project = PROJECT_DATA_MANAGER.get_project(id)
        if self.python_project is None:
            return HttpResult[None](code=400, status="failed", msg=f"没有 id 为 {id} 的 Python 项目", data=None)

        project_code = self.python_project.get("project_code")
        project_name = self.python_project.get("project_name")

        # ===== context =====
        ctx = DeployContext()
        ctx.container_name = project_code

        # ===== 开始日志 =====
        logger.info(f"[{self.deploy_history_id}][{strategy}] START - {project_code} ({project_name})")
        logger.info(
            f"[{self.deploy_history_id}][{strategy}][USER] - "
            f"id={self.user.get('id')}, username={self.user.get('username')}, nickname={self.user.get('nickname')}"
        )

        # ===== 定义步骤 =====
        steps = [
            ("DIR", "准备部署目录", lambda: self._ensure_project_directory(ctx)),
            ("SAVE_ZIP", "保存 ZIP 到部署目录", lambda: self._save_zip_file(ctx, zip_file)),
            ("UNZIP", "解压ZIP", lambda: self._unzip_project(ctx)),
            ("DETECT", "识别项目结构", lambda: self._detect_project_root(ctx)),
            ("DOCKERFILE", "校验 Dockerfile", lambda: self._validate_project_dockerfile(ctx)),
            ("IGNORE", "生成 .dockerignore", lambda: self._create_dockerignore(ctx)),
            ("CLEAN", "清理旧容器与镜像", lambda: self._cleanup_old_container_and_image(ctx)),
            ("BUILD", "构建镜像", lambda: self._build_image(ctx)),
            ("RUN", "启动容器", lambda: self._start_container(ctx, dockercommand_content)),
            ("UPDATE", "更新部署记录", lambda: self._update_python_project_data(ctx, id)),
        ]

        try:
            self._execute_steps(steps, strategy, ctx)
            logger.info(f"[{self.deploy_history_id}][{strategy}] SUCCESS - {project_code}")
        except Exception as e:
            logger.error(f"[{self.deploy_history_id}][{strategy}] FAILED")
            raise

        return (
            f"项目 {project_code}（{project_name}）部署成功，"
            f"镜像 {self.python_project.get('docker_image_name')}:{self.python_project.get('docker_image_tag')} 已启动"
        )

    def _blue_green_deploy(self, id: str, zip_file: UploadFile, dockercommand_content: str):
        """蓝绿部署"""
        raise NotImplementedError("blue_green strategy is not implemented yet")

    def _execute_steps(self, steps, strategy, ctx: DeployContext):
        total = len(steps)

        for idx, (code, desc, func) in enumerate(steps, 1):
            ctx.current_step = code

            prefix = f"[{idx}/{total}][{code}]"

            logger.info(f"[{self.deploy_history_id}][{strategy}]{prefix} START - {desc}")

            try:
                func()
                logger.info(f"[{self.deploy_history_id}][{strategy}]{prefix} SUCCESS")
            except Exception:
                logger.exception(
                    f"[{self.deploy_history_id}][{strategy}]{prefix} FAILED - {desc}"
                )
                raise

    # ==============================
    # STEPS
    # ==============================
    def _ensure_project_directory(self, ctx: DeployContext):
        base = self.python_project.get("container_project_path")
        logs_dir = os.path.join(base, "logs")
        app_dir = os.path.join(base, "app")

        if not os.path.exists(base):
            os.makedirs(base)
            logger.info(f"创建项目目录: {base}")

        os.makedirs(logs_dir, exist_ok=True)
        os.makedirs(app_dir, exist_ok=True)

        logger.info(f"部署目录已就绪: app={app_dir}, logs={logs_dir}")

    def _save_zip_file(self, ctx: DeployContext, zip_file: UploadFile):
        path = os.path.join(
            self.python_project.get("container_project_path"),
            "app",
            "project.zip"
        )

        with open(path, "wb") as f:
            shutil.copyfileobj(zip_file.file, f)

        ctx.zip_path = path
        logger.info(f"ZIP 已保存: {path}")

    def _unzip_project(self, ctx: DeployContext):
        if not ctx.zip_path:
            raise RuntimeError("zip_path 未初始化")

        app_dir = os.path.dirname(ctx.zip_path)

        # 清理旧文件
        for name in os.listdir(app_dir):
            path = os.path.join(app_dir, name)

            if path == ctx.zip_path:
                continue

            if os.path.isfile(path) or os.path.islink(path):
                os.remove(path)
            else:
                shutil.rmtree(path)

        # 解压新包
        try:
            with zipfile.ZipFile(ctx.zip_path, "r") as z:
                z.extractall(app_dir)
        except zipfile.BadZipFile as e:
            raise RuntimeError(f"ZIP 文件无效: {e}")
        except Exception as e:
            raise RuntimeError(f"解压失败: {e}")

        os.remove(ctx.zip_path)
        logger.info("项目解压完成")
        logger.debug(f"解压目录: {app_dir}")

    def _detect_project_root(self, ctx: DeployContext):
        app_dir = os.path.join(self.python_project.get("container_project_path"), "app")

        root_dockerfile = os.path.join(app_dir, "Dockerfile")
        if os.path.isfile(root_dockerfile):
            ctx.project_root_path = app_dir
            logger.info("项目根目录识别完成")
            logger.debug(f"项目根目录: {ctx.project_root_path}")
            return
        
        logger.info("根目录未检测到 Dockerfile，尝试识别唯一子目录项目结构")

        # 过滤掉Mac系统打包文件夹时自动生成的垃圾文件
        visible_entries = [
            name for name in os.listdir(app_dir)
            if name not in ["__MACOSX", ".DS_Store"]
        ]

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

        if len(subdirs) == 1 and len(files) == 0:
            candidate = subdirs[0]
            if os.path.isfile(os.path.join(candidate, "Dockerfile")):
                ctx.project_root_path = candidate
                logger.info("项目根目录识别完成")
                logger.debug(f"项目根目录: {ctx.project_root_path}")
                return

        raise RuntimeError("未检测到可用的项目根目录，请确保 ZIP 结构中包含 Dockerfile")

    def _validate_project_dockerfile(self, ctx: DeployContext):
        if not ctx.project_root_path:
            raise RuntimeError("内部错误：缺少 project_root_path（依赖步骤 DETECT 未执行或失败）")

        path = os.path.join(ctx.project_root_path, "Dockerfile")

        if not os.path.isfile(path):
            raise RuntimeError(f"Dockerfile 不存在: {path}")

        try:
            with open(path, "r", encoding="utf-8") as f:
                dockerfile_content = f.read()
            DeployValidator.validate_dockerfile(dockerfile_content)
        except Exception as e:
            raise RuntimeError(f"Dockerfile 校验失败: {e}")

        ctx.dockerfile_path = path
        logger.info(f"Dockerfile 校验通过: {path}")

    def _create_dockerignore(self, ctx: DeployContext):
        if not ctx.project_root_path:
            raise RuntimeError("project_root_path 未初始化")

        path = os.path.join(ctx.project_root_path, ".dockerignore")

        if os.path.exists(path):
            logger.info(f".dockerignore 已存在: {path}")
            return

        ignore_rules = [
            "logs/",
            "*.log",
            "*.tmp",
            "__pycache__/",
            ".DS_Store",
            "__MACOSX/",
            "*.zip",
        ]

        with open(path, "w", encoding="utf-8") as f:
            f.write("\n".join(ignore_rules) + "\n")

        logger.info(f"已创建 .dockerignore: {path}")

    def _cleanup_old_container_and_image(self, ctx: DeployContext):
        if not ctx.container_name:
            raise RuntimeError("container_name 未初始化")

        container_name = ctx.container_name
        image_name = f"{self.python_project.get('docker_image_name')}:{self.python_project.get('docker_image_tag')}"

        # ===== 删除容器 =====
        check_container_cmd = [
            "docker", "ps", "-a",
            "--filter", f"name={container_name}",
            "--format", "{{.Names}}"
        ]

        result = subprocess.run(
            check_container_cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )

        if container_name in result.stdout:
            logger.info(f"[CMD] docker rm -f {container_name}")

            subprocess.run(
                ["docker", "rm", "-f", container_name],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                check=False
            )

            logger.info(f"已删除旧容器: {container_name}")

        # ===== 删除镜像 =====
        check_image_cmd = ["docker", "images", "-q", image_name]

        result = subprocess.run(
            check_image_cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )

        if result.stdout.strip():
            logger.info(f"[CMD] docker rmi -f {image_name}")

            subprocess.run(
                ["docker", "rmi", "-f", image_name],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                check=False
            )

            logger.info(f"已删除旧镜像: {image_name}")

    def _build_image(self, ctx: DeployContext):
        if not ctx.project_root_path:
            raise RuntimeError("project_root_path 未初始化，无法构建镜像")

        image = f"{self.python_project.get('docker_image_name')}:{self.python_project.get('docker_image_tag')}"
        ctx.image_name = image

        command = ["docker", "build", "-t", image, "."]
        logger.info(f"开始构建镜像: {image}")
        logger.debug(f"构建目录: {ctx.project_root_path}")
        logger.info(f"[CMD] {' '.join(command)}")
        try:
            subprocess.run(
                command,
                cwd=ctx.project_root_path,
                check=True
            )
        except subprocess.CalledProcessError as e:
            raise RuntimeError(f"镜像构建失败: {image}, 错误: {e}")

        logger.info(f"镜像构建完成: {image}")

    def _start_container(self, ctx: DeployContext, dockercommand_content: str):
        if not ctx.container_name:
            raise RuntimeError("container_name 未初始化")

        cmd = re.sub(r'\\\s*\r?\n', ' ', dockercommand_content).strip()

        try:
            DeployValidator.validate_docker_command(cmd)
        except Exception as e:
            raise RuntimeError(f"docker run 命令校验失败: {e}")

        logger.info(f"开始启动容器: {ctx.container_name}")
        logger.info(f"[CMD] {cmd}")
        try:
            subprocess.run(cmd, shell=True, check=True)
        except Exception as e:
            raise RuntimeError(f"容器启动失败: {ctx.container_name}, 错误: {e}")

        logger.info(f"容器启动完成: {ctx.container_name}")

    def _update_python_project_data(self, ctx: DeployContext, id: str):
        updated_data = {
            "last_deployed_at": datetime.now().strftime("%Y-%m-%dT%H:%M:%S")
        }

        PROJECT_DATA_MANAGER.update_project(id, updated_data)

        DEPLOY_HISTORY_DATA_MANAGER.log_deploy_result(
            self.deploy_history_id,
            id,
            StatusEnum.SUCCESS,
            None,
            self.user
        )

        logger.info("项目部署记录已更新")