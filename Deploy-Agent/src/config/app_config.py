# config/app_config.py
from pathlib import Path
import yaml
from dataclasses import dataclass

CONFIG_PATH = Path(__file__).resolve().parents[2] / "config.yaml"

@dataclass
class LoggingConfig:
    file: bool
    level: str


@dataclass
class AppConfig:
    name: str
    version: str
    logging: LoggingConfig

    @classmethod
    def load(cls, path: str = CONFIG_PATH) -> "AppConfig":
        with open(path, "r", encoding="utf-8") as f:
            config_dict = yaml.safe_load(f) or {}

        app_dict = config_dict.get("app", {}) or {}
        logging_dict = app_dict.get("logging", {}) or {}

        return cls(
            name=app_dict.get("name", "Deploy Agent"),
            version=app_dict.get("version", "v1.0.8"),
            logging=LoggingConfig(
                file=logging_dict.get("file", False),
                level=logging_dict.get("level", "DEBUG").upper(),
            ),
        )
        
# 模块级单例
app_config = AppConfig.load()