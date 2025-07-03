# manager/__init__.py
"""
manager 包统一暴露全局单例管理器实例。

本模块作为统一导入入口，提供系统中的DataManager 单例对象，方便调用方直接使用，提升可读性与一致性。
"""
from .agent_data_manager import AgentDataManager
from .system_config_data_manager import SystemConfigDataManager
from .user_data_manager import UserDataManager


AGENT_DATA_MANAGER = AgentDataManager().get_instance()
SYSTEM_CONFIG_DATA_MANAGER = SystemConfigDataManager().get_instance()
USER_DATA_MANAGER = UserDataManager().get_instance()