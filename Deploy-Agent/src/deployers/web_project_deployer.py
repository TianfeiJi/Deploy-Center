import os
import shutil
import zipfile
from datetime import datetime
from typing import Optional

from loguru import logger

from context.deploy_context import DeployContext
from manager import PROJECT_DATA_MANAGER
from models.entity.deploy_task import DeployTask


class WebProjectDeployer:
    """
    Web 项目部署执行器。

    基于 DeployTask 执行前端静态资源部署流程。
    """

    def __init__(self):
        self.web_project = None
        self.deploy_task: Optional[DeployTask] = None

    def deploy(self, deploy_task: DeployTask):
        """
        部署入口。

        当前流程较简单：
            1. 准备项目目录
            2. 将上传的 ZIP 包复制到部署目录
            3. 解压 ZIP 包
            4. 删除临时 ZIP 包
            5. 更新项目最近部署时间
        """
        self.deploy_task = deploy_task
        self.web_project = PROJECT_DATA_MANAGER.get_project(deploy_task.project_id)

        if self.web_project is None:
            raise ValueError(f"没有 id 为 {deploy_task.project_id} 的 Web 项目")

        project_id = deploy_task.project_id
        project_code = self.web_project.get("project_code")
        project_name = self.web_project.get("project_name")
        strategy = "static_deploy"

        ctx = DeployContext()

        logger.info(f"[{deploy_task.id}][{strategy}] START - {project_code} ({project_name})")
        logger.info(
            f"[{deploy_task.id}][{strategy}][OPERATOR] - "
            f"id={deploy_task.operator_id}, name={deploy_task.operator_name}"
        )

        steps = [
            ("DIR", "准备项目目录", lambda: self._ensure_project_directory(ctx)),
            ("PREPARE_ARTIFACT", "准备 ZIP 到部署目录", lambda: self._prepare_artifact(ctx, deploy_task)),
            ("UNZIP", "解压 ZIP 文件", lambda: self._unzip_artifact(ctx, deploy_task)),
            ("CLEAN", "删除临时 ZIP 文件", lambda: self._delete_artifact(ctx, deploy_task)),
            ("UPDATE", "更新项目最近部署时间", lambda: self._update_project_last_deployed_at(project_id)),
        ]

        try:
            self._execute_steps(steps, deploy_task, strategy, ctx)
            logger.info(f"[{deploy_task.id}][{strategy}] SUCCESS - {project_code}")
        except Exception:
            logger.error(f"[{deploy_task.id}][{strategy}] FAILED - {project_code}")
            raise

        return f"{project_name} 项目部署成功"

    def _execute_steps(self, steps, deploy_task: DeployTask, strategy: str, ctx: DeployContext):
        total = len(steps)
        task_id = deploy_task.id

        for idx, (code, desc, func) in enumerate(steps, 1):
            ctx.current_step = code
            prefix = f"[{idx}/{total}][{code}]"

            logger.info(f"[{task_id}][{strategy}]{prefix} START - {desc}")
            try:
                func()
                logger.info(f"[{task_id}][{strategy}]{prefix} SUCCESS")
            except Exception:
                logger.exception(f"[{task_id}][{strategy}]{prefix} FAILED - {desc}")
                raise

    def _ensure_project_directory(self, ctx: DeployContext):
        """
        创建项目目录。
        """
        project_root_path = self.web_project.get("container_project_path")
        if not project_root_path:
            raise RuntimeError("container_project_path 为空，无法继续部署")

        os.makedirs(project_root_path, exist_ok=True)
        ctx.project_root_path = project_root_path

        logger.info(f"项目目录已就绪: {project_root_path}")

    def _prepare_artifact(self, ctx: DeployContext, deploy_task: DeployTask):
        """
        将上传的 ZIP 包复制到部署目录。
        """
        if not deploy_task.upload_file_path:
            raise RuntimeError("deploy_task.upload_file_path 为空，无法继续部署")

        source_path = deploy_task.upload_file_path
        if not os.path.isfile(source_path):
            raise RuntimeError(f"上传文件不存在: {source_path}")

        if not ctx.project_root_path:
            raise RuntimeError("project_root_path 未初始化")

        target_path = os.path.join(
            ctx.project_root_path,
            f"{self.web_project.get('project_code')}.zip"
        )

        shutil.copy2(source_path, target_path)
        ctx.artifact_path = target_path

        logger.info(f"ZIP 已准备到部署目录: {target_path}")

    def _unzip_artifact(self, ctx: DeployContext, deploy_task: DeployTask):
        """
        解压 ZIP 文件，并清理旧文件。
        """
        if not ctx.artifact_path:
            raise RuntimeError("artifact_path 未初始化")

        extract_path = ctx.project_root_path
        if not extract_path:
            raise RuntimeError("project_root_path 未初始化")

        logger.info(f"[{deploy_task.id}][{ctx.current_step}] PROCESS - 开始清理旧文件: {extract_path}")

        for name in os.listdir(extract_path):
            path = os.path.join(extract_path, name)

            if path == ctx.artifact_path:
                continue

            if os.path.isfile(path) or os.path.islink(path):
                os.remove(path)
            else:
                shutil.rmtree(path)

        try:
            logger.info(f"[{deploy_task.id}][{ctx.current_step}] PROCESS - 开始解压 ZIP: {ctx.artifact_path}")
            with zipfile.ZipFile(ctx.artifact_path, "r") as zip_ref:
                zip_ref.extractall(extract_path)
        except zipfile.BadZipFile as e:
            raise RuntimeError(f"ZIP 文件无效: {e}")
        except Exception as e:
            raise RuntimeError(f"解压 ZIP 文件失败: {e}")

        logger.info(f"ZIP 文件已解压到: {extract_path}")

    def _delete_artifact(self, ctx: DeployContext, deploy_task: DeployTask):
        """
        删除临时 ZIP 文件。
        """
        if not ctx.artifact_path:
            raise RuntimeError("artifact_path 未初始化")

        if os.path.exists(ctx.artifact_path):
            os.remove(ctx.artifact_path)
            logger.info(f"临时 ZIP 文件已删除: {ctx.artifact_path}")
        else:
            logger.warning(f"[{deploy_task.id}][{ctx.current_step}] 临时 ZIP 文件不存在，跳过删除")

    def _update_project_last_deployed_at(self, project_id: str):
        """
        更新项目最近一次成功部署时间。
        """
        updated_data = {
            "last_deployed_at": datetime.now().strftime("%Y-%m-%dT%H:%M:%S")
        }

        PROJECT_DATA_MANAGER.update_project(project_id, updated_data)
        logger.info("项目最近部署时间已更新")