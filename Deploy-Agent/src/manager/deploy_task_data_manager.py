import json
import os
from typing import List, Optional
from datetime import datetime

from models.entity.deploy_task import DeployTask


class DeployTaskDataManager:
    """
    DeployTaskDataManager

    仅负责 DeployTask 的持久化存取，不处理任务业务逻辑。
    """

    _instance = None
    _data_file_path = os.path.join(
        os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
        "data",
        "deploy_task_data.json"
    )

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(DeployTaskDataManager, cls).__new__(cls)
        return cls._instance

    @classmethod
    def get_instance(cls):
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    def save_deploy_task(self, deploy_task: DeployTask):
        """
        保存一个新的 DeployTask。
        """
        deploy_task_list = self._load_deploy_tasks()
        deploy_task_list.append(deploy_task)
        self._save_deploy_tasks(deploy_task_list)

    def get_deploy_task(self, deploy_task_id: str) -> Optional[DeployTask]:
        """
        根据任务 ID 获取 DeployTask。
        """
        deploy_task_list = self._load_deploy_tasks()
        for task in deploy_task_list:
            if task.id == deploy_task_id:
                return task
        return None

    def update_deploy_task_fields(self, deploy_task_id: str, updated_data: dict):
        """
        按字段更新指定任务。
        """
        deploy_task_list = self._load_deploy_tasks()

        for task in deploy_task_list:
            if task.id == deploy_task_id:
                for key, value in updated_data.items():
                    if hasattr(task, key):
                        setattr(task, key, value)

                if hasattr(task, "updated_at"):
                    task.updated_at = datetime.now()

                self._save_deploy_tasks(deploy_task_list)
                return

        raise ValueError(f"DeployTask not found: {deploy_task_id}")

    def delete_deploy_task(self, deploy_task_id: str):
        """
        删除指定任务。
        """
        deploy_task_list = self._load_deploy_tasks()
        new_task_list = [task for task in deploy_task_list if task.id != deploy_task_id]
        self._save_deploy_tasks(new_task_list)

    def list_deploy_tasks(self) -> List[DeployTask]:
        """
        返回所有任务。
        """
        return self._load_deploy_tasks()

    def list_deploy_tasks_by_project_id(self, project_id: str) -> List[DeployTask]:
        """
        根据 project_id 查询任务列表。
        """
        deploy_task_list = self._load_deploy_tasks()
        return [task for task in deploy_task_list if task.project_id == project_id]

    def replace_all_deploy_tasks(self, deploy_tasks: List[DeployTask]):
        """
        用新的任务列表整体覆盖存储内容。
        """
        self._save_deploy_tasks(deploy_tasks)

    def _load_deploy_tasks(self) -> List[DeployTask]:
        try:
            with open(self._data_file_path, "r", encoding="utf-8") as file:
                raw_data = json.load(file)
                return [DeployTask(**item) for item in raw_data]
        except (FileNotFoundError, json.JSONDecodeError):
            return []

    def _save_deploy_tasks(self, deploy_tasks: List[DeployTask]):
        def default_serializer(obj):
            if isinstance(obj, datetime):
                return obj.isoformat()
            raise TypeError(f"Unserializable object {obj} of type {type(obj)}")

        os.makedirs(os.path.dirname(self._data_file_path), exist_ok=True)

        with open(self._data_file_path, "w", encoding="utf-8") as file:
            json.dump(
                [task.model_dump() for task in deploy_tasks],
                file,
                indent=4,
                ensure_ascii=False,
                default=default_serializer
            )