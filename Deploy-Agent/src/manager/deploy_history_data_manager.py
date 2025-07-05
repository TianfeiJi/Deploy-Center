import json
import os
from typing import Dict, List, Optional
from datetime import datetime
from models.entity.deploy_history import DeployHistory


class DeployHistoryDataManager:
    _instance = None
    _data_file_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "data", "deploy_history_data.json")

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(DeployHistoryDataManager, cls).__new__(cls)
        return cls._instance
    
    @classmethod
    def get_instance(cls):
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance
    
    def log_deploy_result(
        self,
        deploy_history_id: str,
        project_id: str,
        status: str,
        failed_reason: Optional[str] = None,
        user: Optional[Dict] = None
    ):
        deploy_history = self.get_deploy_history(deploy_history_id)
        # 如果已存在就更新
        if deploy_history:
            self.update_deploy_history(deploy_history_id, {
                "status": status,
                "failed_reason": failed_reason
            })
        else:   # 如果不存在就新增
            deploy_history = DeployHistory(
                id=deploy_history_id,
                project_id=project_id,
                status=status,
                failed_reason=failed_reason,
                operator_name=user.get("nickname") if user else None,
                created_by=user.get("id") if user else None,
                created_at=datetime.now().isoformat(),
                updated_by=None,
                updated_at=None
            )
            self.create_deploy_history(deploy_history)

    def create_deploy_history(self, deploy_history: DeployHistory):
        deploy_history_list = self._load_deploy_historys()
        deploy_history_list.append(deploy_history)
        self._save_deploy_historys(deploy_history_list)

    def get_deploy_history(self, deploy_history_id: str) -> Optional[DeployHistory]:
        deploy_history_list = self._load_deploy_historys()
        for record in deploy_history_list:
            if record.id == deploy_history_id:
                return record
        return None
    def update_deploy_history(self, deploy_history_id: str, updated_data: dict):
        deploy_history_list: List[DeployHistory] = self._load_deploy_historys()
        for history in deploy_history_list:
            if history.id == deploy_history_id:
                for key, value in updated_data.items():
                    if hasattr(history, key):
                        setattr(history, key, value)
                history.updated_at = datetime.now().isoformat()
                self._save_deploy_historys(deploy_history_list)
                return
        raise ValueError(f"Deploy record with ID {deploy_history_id} not found.")

    def delete_deploy_history(self, deploy_history_id: str):
        deploy_history_list = self._load_deploy_historys()
        deploy_history_list = [record for record in deploy_history_list if record.id != deploy_history_id]
        self._save_deploy_historys(deploy_history_list)

    def list_deploy_historys(self) -> List[DeployHistory]:
        return self._load_deploy_historys()
    
    def _load_deploy_historys(self) -> List[DeployHistory]:
        try:
            with open(self._data_file_path, "r", encoding="utf-8") as file:
                raw_data = json.load(file)
                return [DeployHistory(**item) for item in raw_data]
        except (FileNotFoundError, json.JSONDecodeError):
            return []

    def _save_deploy_historys(self, deploy_historys: List[DeployHistory]):
        def default_serializer(obj):
            if isinstance(obj, datetime):
                return obj.isoformat()
            raise TypeError(f"Unserializable object {obj} of type {type(obj)}")

        with open(self._data_file_path, "w", encoding="utf-8") as file:
            json.dump(
                [record.model_dump() for record in deploy_historys],
                file,
                indent=4,
                ensure_ascii=False,
                default=default_serializer
            )