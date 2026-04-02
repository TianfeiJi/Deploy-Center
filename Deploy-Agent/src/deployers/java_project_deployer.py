import os
import re
import shutil
import subprocess
from datetime import datetime
from typing import Optional

from loguru import logger

from context.deploy_context import DeployContext
from manager import PROJECT_DATA_MANAGER
from models.entity.deploy_task import DeployTask
from models.enum.deploy_strategy_enum import DeployStrategyEnum
from utils.deploy_validator import DeployValidator


class JavaProjectDeployer:
    """
    Java 项目部署执行器。

    基于 DeployTask 执行部署流程，负责构建镜像并启动容器。
    仅处理部署逻辑，不涉及任务调度与状态管理。
    """

    def __init__(self):
        self.java_project = None
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
            2. 将任务输入中的 JAR 文件复制到部署目录
            3. 准备并校验 Dockerfile
            4. 写入或覆盖 .dockerignore
            5. 清理旧容器与镜像
            6. 构建 Docker 镜像
            7. 启动 Docker 容器
            8. 更新部署记录与项目信息
        """
        strategy = DeployStrategyEnum.RECREATE.value

        self.java_project = PROJECT_DATA_MANAGER.get_project(deploy_task.project_id)
        if self.java_project is None:
            raise ValueError(f"没有 id 为 {deploy_task.project_id} 的 Java 项目")

        project_id = deploy_task.project_id
        project_code = self.java_project.get("project_code")
        project_name = self.java_project.get("project_name")

        ctx = DeployContext()
        ctx.container_name = deploy_task.container_name or self.java_project.get("container_name") or project_code

        logger.info(f"[{deploy_task.id}][{strategy}] START - {project_code} ({project_name})")
        logger.info(
            f"[{deploy_task.id}][{strategy}][OPERATOR] - "
            f"id={deploy_task.operator_id}, name={deploy_task.operator_name}"
        )

        steps = [
            ("DIR", "准备部署目录", lambda: self._ensure_project_directory(ctx)),
            ("PREPARE_JAR", "准备 JAR 到部署目录", lambda: self._prepare_jar_file(ctx, deploy_task)),
            ("DOCKERFILE", "准备并校验 Dockerfile", lambda: self._prepare_and_validate_dockerfile(ctx, deploy_task)),
            ("IGNORE", "生成 .dockerignore", lambda: self._create_dockerignore(ctx)),
            ("CLEAN", "清理旧容器与镜像", lambda: self._cleanup_old_container_and_image(ctx, deploy_task)),
            ("BUILD", "构建镜像", lambda: self._build_image(ctx, deploy_task)),
            ("RUN", "启动容器", lambda: self._start_container(ctx, deploy_task)),
            ("UPDATE", "更新部署记录", lambda: self._update_java_project_data(project_id)),
        ]

        try:
            self._execute_steps(deploy_task.id, steps, strategy, ctx)
            logger.info(f"[{deploy_task.id}][{strategy}] SUCCESS - {project_code}")
        except Exception:
            logger.error(f"[{deploy_task.id}][{strategy}] FAILED")
            raise

        image_name = deploy_task.build_image_name or self.java_project.get("docker_image_name")
        image_tag = deploy_task.build_image_tag or self.java_project.get("docker_image_tag")
        container_name = ctx.container_name

        return (
            f"项目 {project_code}（{project_name}）部署成功，"
            f"容器 {container_name} 已启动（基于镜像 {image_name}:{image_tag}）"
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
        base = self.java_project.get("container_project_path")
        logs_dir = os.path.join(base, "logs")
        jars_dir = os.path.join(base, "jars")

        if not os.path.exists(base):
            os.makedirs(base)
            logger.info(f"创建项目目录: {base}")

        os.makedirs(logs_dir, exist_ok=True)
        os.makedirs(jars_dir, exist_ok=True)

        logger.info(f"部署目录已就绪: jars={jars_dir}, logs={logs_dir}")

    def _prepare_jar_file(self, ctx: DeployContext, deploy_task: DeployTask):
        """
        将任务中的上传 JAR 文件准备到部署目录。
        """
        if not deploy_task.upload_file_path:
            raise RuntimeError("deploy_task.upload_file_path 为空，无法继续部署")

        source_jar_path = deploy_task.upload_file_path
        if not os.path.isfile(source_jar_path):
            raise RuntimeError(f"上传文件不存在: {source_jar_path}")

        target_jar_path = os.path.join(
            self.java_project.get("container_project_path"),
            "jars",
            f"{self.java_project.get('project_code')}.jar"
        )

        shutil.copy2(source_jar_path, target_jar_path)
        ctx.artifact_path = target_jar_path

        logger.info(f"JAR 已准备到部署目录: {target_jar_path}")

    def _prepare_and_validate_dockerfile(self, ctx: DeployContext, deploy_task: DeployTask):
        """
        准备并校验 Dockerfile。

        规则：
            - Java 项目要求 deploy_task.dockerfile_content 必须存在
            - 写入到项目根目录 Dockerfile
        """
        project_root_path = self.java_project.get("container_project_path")
        if not project_root_path:
            raise RuntimeError("container_project_path 缺失，无法准备 Dockerfile")

        dockerfile_path = os.path.join(project_root_path, "Dockerfile")

        if not deploy_task.dockerfile_content:
            raise RuntimeError("deploy_task.dockerfile_content 为空，Java 项目无法继续部署")

        with open(dockerfile_path, "w", encoding="utf-8") as f:
            f.write(deploy_task.dockerfile_content)

        try:
            with open(dockerfile_path, "r", encoding="utf-8") as f:
                dockerfile_content = f.read()
            DeployValidator.validate_dockerfile(dockerfile_content)
        except Exception as e:
            raise RuntimeError(f"Dockerfile 校验失败: {e}")

        ctx.project_root_path = project_root_path
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
            ".DS_Store",
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

    def _update_java_project_data(self, project_id: str):
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
        image_name = deploy_task.build_image_name or self.java_project.get("docker_image_name")
        image_tag = deploy_task.build_image_tag or self.java_project.get("docker_image_tag")

        if not image_name or not image_tag:
            raise RuntimeError("镜像名称或标签缺失，无法继续部署")

        return f"{image_name}:{image_tag}"