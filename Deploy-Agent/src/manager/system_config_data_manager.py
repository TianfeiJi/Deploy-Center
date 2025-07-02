import json
import os
from typing import List, Optional
from datetime import datetime
from models.entity.system_config import SystemConfig


class SystemConfigDataManager:
    _instance = None
    _data_file_path = os.path.join(
        os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
        "data", "system_config_data.json"
    )

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(SystemConfigDataManager, cls).__new__(cls)
        return cls._instance

    def _load_configs(self) -> List[SystemConfig]:
        try:
            with open(self._data_file_path, "r", encoding="utf-8") as file:
                raw_data = json.load(file)
                return [SystemConfig(**item) for item in raw_data]
        except FileNotFoundError:
            return []

    def _save_configs(self, configs: List[SystemConfig]):
        with open(self._data_file_path, "w", encoding="utf-8") as file:
            json.dump(
                [cfg.model_dump() for cfg in configs],
                file,
                indent=4,
                ensure_ascii=False,
                default=str  # 避免 datetime 报错
            )

    def create_config(self, config_data: dict) -> SystemConfig:
        configs = self._load_configs()
        new_id = 1 if not configs else max(cfg.id for cfg in configs) + 1
        now = datetime.now()
        config = SystemConfig(
            id=new_id,
            config_name=config_data.get("config_name"),
            config_key=config_data.get("config_key"),
            config_value=config_data.get("config_value"),
            config_remark=config_data.get("config_remark", ""),
            config_group=config_data.get("config_group", ""),
            created_at=now,
            updated_at=now
        )
        configs.append(config)
        self._save_configs(configs)
        return config

    def get_config(self, config_key: str) -> Optional[SystemConfig]:
        configs = self._load_configs()
        for config in configs:
            if config.config_key == config_key:
                return config
        return None

    def update_config(self, config_key: str, updated_data: dict):
        configs = self._load_configs()
        for config in configs:
            if config.config_key == config_key:
                if "config_name" in updated_data:
                    config.config_name = updated_data["config_name"]
                if "config_value" in updated_data:
                    config.config_value = updated_data["config_value"]
                if "config_remark" in updated_data:
                    config.config_remark = updated_data["config_remark"]
                if "config_group" in updated_data:
                    config.config_group = updated_data["config_group"]
                config.updated_at = datetime.now()
                self._save_configs(configs)
                return
        raise ValueError(f"Config with key {config_key} not found.")

    def delete_config(self, config_key: str):
        configs = self._load_configs()
        configs = [cfg for cfg in configs if cfg.config_key != config_key]
        self._save_configs(configs)

    def list_configs(self) -> List[SystemConfig]:
        return self._load_configs()

    @classmethod
    def get_instance(cls):
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance
