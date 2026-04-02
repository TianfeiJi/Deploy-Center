import uuid
from datetime import datetime
from threading import Lock, Thread
from typing import List, Optional, Set

from loguru import logger

from manager import PROJECT_DATA_MANAGER, DEPLOY_TASK_DATA_MANAGER
from models.entity.deploy_task import DeployTask
from deployers.python_project_deployer import PythonProjectDeployer
from deployers.java_project_deployer import JavaProjectDeployer
from deployers.web_project_deployer import WebProjectDeployer


class DeployTaskService:
    """
    DeployTaskService

    职责：
        1. 生成并提交部署任务
        2. 控制全局并发数量
        3. 保证同一个 project_id 不会同时执行多个部署任务
        4. 更新任务状态与执行时间
        5. 在任务完成后继续调度等待中的任务

    说明：
        - DeployTaskDataManager 只负责 DeployTask 的持久化存取
        - DeployTaskService 负责任务业务逻辑与调度逻辑
    """

    def __init__(self):
        # 全局最大并发任务数
        self.max_concurrent_task = 1

        # 当前运行中的任务 ID 集合
        self.running_task_ids: Set[str] = set()

        # 当前正在部署中的项目 ID 集合
        # 用于限制同一个 project_id 不能同时执行多个部署任务
        self.deploying_project_ids: Set[str] = set()

        # 等待中的任务队列
        self.pending_task_queue: List[DeployTask] = []

        # 线程锁，保证提交/完成/调度任务时状态一致
        self._lock = Lock()

        logger.info(
            f"DeployTaskService initialized, max_concurrent_task={self.max_concurrent_task}"
        )

    def submit_task(
        self,
        project_id: str,
        task_name: Optional[str] = None,
        trigger_type: str = "MANUAL",
        deploy_mechanism: str = "UPLOAD",
        upload_file_name: Optional[str] = None,
        upload_file_path: Optional[str] = None,
        build_image_name: Optional[str] = None,
        build_image_tag: Optional[str] = None,
        container_name: Optional[str] = None,
        dockerfile_content: Optional[str] = None,
        dockercommand_content: Optional[str] = None,
        operator_id: Optional[int] = None,
        operator_name: Optional[str] = None,
    ) -> DeployTask:
        """
        提交一个新的部署任务。

        流程：
            1. 由 Manager 生成任务 ID
            2. 构造 DeployTask 对象
            3. 保存任务
            4. 判断是立即执行还是进入等待队列
        """
        with self._lock:
            task_id = str(uuid.uuid4()).replace("-", "")[:8]
            now = datetime.now()

            task = DeployTask(
                id=task_id,
                project_id=project_id,
                task_name=task_name,
                status="PENDING",
                trigger_type=trigger_type,
                deploy_mechanism=deploy_mechanism,
                upload_file_name=upload_file_name,
                upload_file_path=upload_file_path,
                build_image_name=build_image_name,
                build_image_tag=build_image_tag,
                container_name=container_name,
                dockerfile_content=dockerfile_content,
                dockercommand_content=dockercommand_content,
                operator_name=operator_name,
                operator_id=operator_id,
                created_at=now,
                updated_at=None,
            )

            logger.info(
                f"[TASK:{task.id}] submit task, project_id={task.project_id}, "
                f"task_name={task.task_name}, trigger_type={task.trigger_type}, "
                f"deploy_mechanism={task.deploy_mechanism}"
            )

            DEPLOY_TASK_DATA_MANAGER.save_deploy_task(task)
            logger.info(f"[TASK:{task.id}] task saved successfully")

            if self.can_run(task):
                self._start_task(task)
            else:
                self.pending_task_queue.append(task)
                logger.info(
                    f"[TASK:{task.id}] task added to pending queue, "
                    f"pending_count={len(self.pending_task_queue)}"
                )

            return task

    def can_run(self, task: DeployTask) -> bool:
        """
        判断任务当前是否可以执行。

        规则：
            1. 全局并发数不能超过限制
            2. 同一个 project_id 不能同时运行多个部署任务
        """
        if len(self.running_task_ids) >= self.max_concurrent_task:
            logger.debug(
                f"[TASK:{task.id}] cannot run: running_task_count="
                f"{len(self.running_task_ids)}, max={self.max_concurrent_task}"
            )
            return False

        if task.project_id in self.deploying_project_ids:
            logger.debug(
                f"[TASK:{task.id}] cannot run: project_id={task.project_id} is already deploying"
            )
            return False

        return True

    def _start_task(self, task: DeployTask):
        """
        启动任务执行。
        """
        self.running_task_ids.add(task.id)
        self.deploying_project_ids.add(task.project_id)

        logger.info(
            f"[TASK:{task.id}] start task, project_id={task.project_id}, "
            f"running_task_count={len(self.running_task_ids)}, "
            f"deploying_project_count={len(self.deploying_project_ids)}"
        )

        thread = Thread(target=self._run_task, args=(task,), daemon=True)
        thread.start()

    def _run_task(self, task: DeployTask):
        """
        后台线程中的任务执行入口。
        """
        try:
            project = PROJECT_DATA_MANAGER.get_project(task.project_id)
            if project is None:
                raise ValueError(f"Project not found: {task.project_id}")

            project_type = (project.get("project_type") or "").upper()

            if project_type == "PYTHON":
                logger.info(f"[TASK:{task.id}] dispatch to PythonProjectDeployer")
                self.update_task_status(task.id, "RUNNING")
                deployer = PythonProjectDeployer()
            elif project_type == "JAVA":
                logger.info(f"[TASK:{task.id}] dispatch to JavaProjectDeployer")
                self.update_task_status(task.id, "RUNNING")
                deployer = JavaProjectDeployer()
            elif project_type == "WEB":
                logger.info(f"[TASK:{task.id}] dispatch to WebProjectDeployer")
                self.update_task_status(task.id, "RUNNING")
                deployer = WebProjectDeployer()
            else:
                raise ValueError(f"Unsupported project type: {project_type}")

            deploy_result = deployer.deploy(task)

            logger.info(
                f"[TASK:{task.id}] deploy finished successfully, result={deploy_result}"
            )
            
            self.finish_task(task, success=True)
        except Exception as e:
            logger.exception(f"[TASK:{task.id}] task execution failed: {e}")
            self.finish_task(task, success=False, failed_reason=str(e))

    def update_task_status(
        self,
        task_id: str,
        status: str,
        failed_reason: Optional[str] = None,
    ):
        """
        更新任务状态。

        规则：
            - 进入 RUNNING 时，如果 started_at 为空，则写入开始时间
            - 进入 SUCCESS / FAILED / CANCELLED 时，写入结束时间
            - 若 started_at 存在，则自动计算 duration_ms
        """
        task = DEPLOY_TASK_DATA_MANAGER.get_deploy_task(task_id)
        if task is None:
            raise ValueError(f"DeployTask not found: {task_id}")

        now = datetime.now()
        updated_data = {
            "status": status,
            "failed_reason": failed_reason,
        }

        if status == "RUNNING" and not task.started_at:
            updated_data["started_at"] = now

        if status in ["SUCCESS", "FAILED", "CANCELLED"]:
            updated_data["finished_at"] = now

            if task.started_at:
                try:
                    started_at = task.started_at
                    if isinstance(started_at, str):
                        started_at = datetime.fromisoformat(started_at)

                    updated_data["duration_ms"] = int(
                        (now - started_at).total_seconds() * 1000
                    )
                except ValueError:
                    logger.warning(
                        f"[TASK:{task_id}] invalid started_at format: {task.started_at}"
                    )

        DEPLOY_TASK_DATA_MANAGER.update_deploy_task_fields(task_id, updated_data)

        if status in ["SUCCESS", "FAILED", "CANCELLED"]:
            logger.info(
                f"[TASK:{task_id}] status updated to {status}, failed_reason={failed_reason}"
            )
        else:
            logger.debug(
                f"[TASK:{task_id}] status updated to {status}, failed_reason={failed_reason}"
            )

    def update_task_runtime_info(
        self,
        task_id: str,
        build_image_name: Optional[str] = None,
        build_image_tag: Optional[str] = None,
        container_name: Optional[str] = None,
    ):
        """
        更新任务运行时信息。
        """
        updated_data = {}

        if build_image_name is not None:
            updated_data["build_image_name"] = build_image_name
        if build_image_tag is not None:
            updated_data["build_image_tag"] = build_image_tag
        if container_name is not None:
            updated_data["container_name"] = container_name

        if not updated_data:
            logger.debug(f"[TASK:{task_id}] skip runtime info update: empty updated_data")
            return

        DEPLOY_TASK_DATA_MANAGER.update_deploy_task_fields(task_id, updated_data)

        logger.info(
            f"[TASK:{task_id}] runtime info updated, "
            f"build_image_name={build_image_name}, build_image_tag={build_image_tag}, "
            f"container_name={container_name}"
        )

    def finish_task(
        self,
        task: DeployTask,
        success: bool,
        failed_reason: Optional[str] = None,
    ):
        """
        结束任务。

        流程：
            1. 从运行中集合移除
            2. 更新最终状态
            3. 调度等待中的后续任务
        """
        with self._lock:
            logger.info(
                f"[TASK:{task.id}] finish task, success={success}, "
                f"project_id={task.project_id}"
            )

            self.running_task_ids.discard(task.id)
            self.deploying_project_ids.discard(task.project_id)

            final_status = "SUCCESS" if success else "FAILED"
            self.update_task_status(task.id, final_status, failed_reason)

            logger.info(
                f"[TASK:{task.id}] runtime state cleared, "
                f"running_task_count={len(self.running_task_ids)}, "
                f"deploying_project_count={len(self.deploying_project_ids)}, "
                f"pending_count={len(self.pending_task_queue)}"
            )

            self.dispatch_pending_tasks()

    def dispatch_pending_tasks(self):
        """
        调度等待队列中的任务。

        规则：
            - 顺序扫描等待队列
            - 找到可执行任务后立即启动
            - 达到全局并发上限后停止继续调度
        """
        if not self.pending_task_queue:
            return

        for task in list(self.pending_task_queue):
            if not self.can_run(task):
                continue

            self.pending_task_queue.remove(task)
            self._start_task(task)

            logger.info(
                f"[TASK:{task.id}] dequeued and started, "
                f"project_id={task.project_id}, "
                f"remaining_pending_count={len(self.pending_task_queue)}"
            )

            if len(self.running_task_ids) >= self.max_concurrent_task:
                break