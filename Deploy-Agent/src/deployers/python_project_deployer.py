import os
import re
import shutil
import subprocess
import zipfile
from datetime import datetime
from typing import Optional

from loguru import logger

from context.deploy_context import DeployContext
from manager import PROJECT_DATA_MANAGER
from models.entity.deploy_task import DeployTask
from models.enum.deploy_strategy_enum import DeployStrategyEnum
from utils.deploy_validator import DeployValidator


class PythonProjectDeployer:
    """
    Python 项目部署执行器。

    基于 DeployTask 执行部署流程，负责构建镜像并启动容器。
    仅处理部署逻辑，不涉及任务调度与状态管理。
    """

    def __init__(self):
        self.python_project = None
        self.deploy_task: Optional[DeployTask] = None

    def deploy(
        self,
        deploy_task: DeployTask,
        strategy: str = DeployStrategyEnum.default()
    ):
        """
        部署入口。

        参数说明：
            deploy_task:
                当前部署任务对象，包含 project_id、upload_file_path、
                dockerfile_content、dockercommand_content 等任务输入。
            strategy:
                部署策略，默认使用系统默认值。
        """
        self.deploy_task = deploy_task

        if strategy == DeployStrategyEnum.RECREATE:
            return self._recreate_deploy(deploy_task)

        if strategy == DeployStrategyEnum.BLUE_GREEN:
            return self._blue_green_deploy(deploy_task)

        raise ValueError(f"不支持的部署策略: {strategy}")

    def _recreate_deploy(self, deploy_task: DeployTask):
        """
        单实例重建式部署（Recreate Deployment）

        流程说明：
            1. 准备部署目录
            2. 将任务输入中的 ZIP 文件复制到部署目录
            3. 解压 ZIP 包
            4. 识别项目根目录
            5. 校验并处理 Dockerfile
            6. 写入或覆盖 .dockerignore
            7. 清理旧容器与镜像
            8. 构建 Docker 镜像
            9. 启动 Docker 容器
            10. 更新部署记录与项目信息
        """
        strategy = DeployStrategyEnum.RECREATE.value

        self.python_project = PROJECT_DATA_MANAGER.get_project(deploy_task.project_id)
        if self.python_project is None:
            raise ValueError(f"没有 id 为 {deploy_task.project_id} 的 Python 项目")

        project_id = deploy_task.project_id
        project_code = self.python_project.get("project_code")
        project_name = self.python_project.get("project_name")

        ctx = DeployContext()
        ctx.container_name = deploy_task.container_name or project_code

        logger.info(f"[{deploy_task.id}][{strategy}] START - {project_code} ({project_name})")
        logger.info(
            f"[{deploy_task.id}][{strategy}][OPERATOR] - "
            f"id={deploy_task.operator_id}, name={deploy_task.operator_name}"
        )

        steps = [
            ("DIR", "准备部署目录", lambda: self._ensure_project_directory(ctx)),
            ("PREPARE_ZIP", "准备 ZIP 到部署目录", lambda: self._prepare_zip_file(ctx, deploy_task)),
            ("UNZIP", "解压 ZIP", lambda: self._unzip_project(ctx)),
            ("DETECT", "识别项目结构", lambda: self._detect_project_root(ctx)),
            ("DOCKERFILE", "校验并处理 Dockerfile", lambda: self._prepare_and_validate_dockerfile(ctx, deploy_task)),
            ("IGNORE", "生成 .dockerignore", lambda: self._create_dockerignore(ctx)),
            ("CLEAN", "清理旧容器与镜像", lambda: self._cleanup_old_container_and_image(ctx, deploy_task)),
            ("BUILD", "构建镜像", lambda: self._build_image(ctx, deploy_task)),
            ("RUN", "启动容器", lambda: self._start_container(ctx, deploy_task)),
            ("UPDATE", "更新部署记录", lambda: self._update_python_project_data(project_id)),
        ]

        try:
            self._execute_steps(deploy_task.id, steps, strategy, ctx)
            logger.info(f"[{deploy_task.id}][{strategy}] SUCCESS - {project_code}")
        except Exception:
            logger.error(f"[{deploy_task.id}][{strategy}] FAILED")
            raise

        image_name = deploy_task.build_image_name or self.python_project.get("docker_image_name")
        image_tag = deploy_task.build_image_tag or self.python_project.get("docker_image_tag")

        return (
            f"项目 {project_code}（{project_name}）部署成功，"
            f"镜像 {image_name}:{image_tag} 已启动"
        )

    def _blue_green_deploy(self, deploy_task: DeployTask):
        """蓝绿部署"""
        raise NotImplementedError("blue_green strategy is not implemented yet")

    def _execute_steps(self, deploy_task_id, steps, strategy, ctx: DeployContext):
        total = len(steps)

        for idx, (code, desc, func) in enumerate(steps, 1):
            ctx.current_step = code
            prefix = f"[{idx}/{total}][{code}]"

            logger.info(f"[{deploy_task_id}][{strategy}]{prefix} START - {desc}")

            try:
                func()
                logger.info(f"[{deploy_task_id}][{strategy}]{prefix} SUCCESS")
            except Exception:
                logger.exception(f"[{deploy_task_id}][{strategy}]{prefix} FAILED - {desc}")
                raise

    # ==============================
    # STEPS
    # ==============================

    def _ensure_project_directory(self, ctx: DeployContext):
        """
        确保项目部署目录存在。
        """
        base = self.python_project.get("container_project_path")
        logs_dir = os.path.join(base, "logs")
        app_dir = os.path.join(base, "app")

        if not os.path.exists(base):
            os.makedirs(base)
            logger.info(f"创建项目目录: {base}")

        os.makedirs(logs_dir, exist_ok=True)
        os.makedirs(app_dir, exist_ok=True)

        logger.info(f"部署目录已就绪: app={app_dir}, logs={logs_dir}")

    def _prepare_zip_file(self, ctx: DeployContext, deploy_task: DeployTask):
        """
        将任务中的上传 ZIP 文件准备到部署目录。

        说明：
            - DeployTask 中只保存 upload_file_path
            - 真正部署时再复制到项目 app 目录
        """
        if not deploy_task.upload_file_path:
            raise RuntimeError("deploy_task.upload_file_path 为空，无法继续部署")

        source_zip_path = deploy_task.upload_file_path
        if not os.path.isfile(source_zip_path):
            raise RuntimeError(f"上传文件不存在: {source_zip_path}")

        target_zip_path = os.path.join(
            self.python_project.get("container_project_path"),
            "app",
            "project.zip"
        )

        shutil.copy2(source_zip_path, target_zip_path)
        ctx.artifact_path = target_zip_path

        logger.info(f"ZIP 已准备到部署目录: {target_zip_path}")

    def _unzip_project(self, ctx: DeployContext):
        """
        解压项目 ZIP，并清理旧文件。
        """
        if not ctx.artifact_path:
            raise RuntimeError("zip_path 未初始化")

        app_dir = os.path.dirname(ctx.artifact_path)

        for name in os.listdir(app_dir):
            path = os.path.join(app_dir, name)

            if path == ctx.artifact_path:
                continue

            if os.path.isfile(path) or os.path.islink(path):
                os.remove(path)
            else:
                shutil.rmtree(path)

        try:
            with zipfile.ZipFile(ctx.artifact_path, "r") as z:
                z.extractall(app_dir)
        except zipfile.BadZipFile as e:
            raise RuntimeError(f"ZIP 文件无效: {e}")
        except Exception as e:
            raise RuntimeError(f"解压失败: {e}")

        os.remove(ctx.artifact_path)
        logger.info("项目解压完成")
        logger.debug(f"解压目录: {app_dir}")

    def _detect_project_root(self, ctx: DeployContext):
        """
        识别项目根目录。

        支持两种结构：
            1. 根目录直接包含 Dockerfile
            2. 根目录仅有一个子目录，且该子目录中包含 Dockerfile
        """
        app_dir = os.path.join(self.python_project.get("container_project_path"), "app")

        root_dockerfile = os.path.join(app_dir, "Dockerfile")
        if os.path.isfile(root_dockerfile):
            ctx.project_root_path = app_dir
            logger.info("项目根目录识别完成")
            logger.debug(f"项目根目录: {ctx.project_root_path}")
            return

        logger.info("根目录未检测到 Dockerfile，尝试识别唯一子目录项目结构")

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

    def _prepare_and_validate_dockerfile(self, ctx: DeployContext, deploy_task: DeployTask):
        """
        准备并校验 Dockerfile。

        规则：
            - 若 deploy_task.dockerfile_content 有值，则覆盖写入 Dockerfile
            - 否则使用项目压缩包中的 Dockerfile
        """
        if not ctx.project_root_path:
            raise RuntimeError("内部错误：缺少 project_root_path（依赖步骤 DETECT 未执行或失败）")

        dockerfile_path = os.path.join(ctx.project_root_path, "Dockerfile")

        if deploy_task.dockerfile_content:
            with open(dockerfile_path, "w", encoding="utf-8") as f:
                f.write(deploy_task.dockerfile_content)
            logger.info(f"已使用任务输入覆盖 Dockerfile: {dockerfile_path}")

        if not os.path.isfile(dockerfile_path):
            raise RuntimeError(f"Dockerfile 不存在: {dockerfile_path}")

        try:
            with open(dockerfile_path, "r", encoding="utf-8") as f:
                dockerfile_content = f.read()
            DeployValidator.validate_dockerfile(dockerfile_content)
        except Exception as e:
            raise RuntimeError(f"Dockerfile 校验失败: {e}")

        ctx.dockerfile_path = dockerfile_path
        logger.info(f"Dockerfile 校验通过: {dockerfile_path}")

    def _create_dockerignore(self, ctx: DeployContext):
        """
        创建默认的 .dockerignore。
        """
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

    def _cleanup_old_container_and_image(self, ctx: DeployContext, deploy_task: DeployTask):
        """
        删除旧容器和旧镜像。
        """
        container_name = ctx.container_name
        if not container_name:
            raise RuntimeError("container_name 未初始化")

        image_name = self._resolve_image_name(deploy_task)

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

    def _build_image(self, ctx: DeployContext, deploy_task: DeployTask):
        """
        构建 Docker 镜像。
        """
        if not ctx.project_root_path:
            raise RuntimeError("project_root_path 未初始化，无法构建镜像")

        image = self._resolve_image_name(deploy_task)
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

    def _start_container(self, ctx: DeployContext, deploy_task: DeployTask):
        """
        启动 Docker 容器。
        """
        if not ctx.container_name:
            raise RuntimeError("container_name 未初始化")

        if not deploy_task.dockercommand_content:
            raise RuntimeError("deploy_task.dockercommand_content 为空，无法启动容器")

        cmd = re.sub(r'\\\s*\r?\n', ' ', deploy_task.dockercommand_content).strip()

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

    def _update_python_project_data(self, project_id: str):
        """
        更新项目部署时间。
        """
        updated_data = {
            "last_deployed_at": datetime.now().strftime("%Y-%m-%dT%H:%M:%S")
        }

        PROJECT_DATA_MANAGER.update_project(project_id, updated_data)

        logger.info("项目部署记录已更新")

    def _resolve_image_name(self, deploy_task: DeployTask) -> str:
        """
        解析本次任务最终要使用的镜像名:标签。

        优先级：
            1. deploy_task.build_image_name/build_image_tag
            2. project 静态配置中的 docker_image_name/docker_image_tag
        """
        image_name = deploy_task.build_image_name or self.python_project.get("docker_image_name")
        image_tag = deploy_task.build_image_tag or self.python_project.get("docker_image_tag")

        if not image_name or not image_tag:
            raise RuntimeError("镜像名称或标签缺失，无法继续部署")

        return f"{image_name}:{image_tag}"