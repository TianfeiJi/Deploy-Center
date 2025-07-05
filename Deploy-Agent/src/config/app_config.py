# config/app_config.py
import os
import yaml
from dataclasses import dataclass

CONFIG_PATH = os.path.join(os.path.dirname(__file__), "config.yaml")

@dataclass
class AppConfig:
    name: str
    version: str
    logging: dict

    @classmethod
    def load(cls, path: str = CONFIG_PATH) -> "AppConfig":
        with open(path, "r") as f:
            config_dict = yaml.safe_load(f)
        app_config = config_dict.get("app", {})
        return cls(
            name=app_config.get("name", "Deploy Agent"),
            version=app_config.get("version", "v1.0.8"),
            logging=app_config.get("logging", {}),
        )

# 模块级单例
app_config = AppConfig.load()