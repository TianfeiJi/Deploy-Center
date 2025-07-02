# manager/__init__.py
"""
manager 包统一暴露全局单例管理器实例。

本模块作为统一导入入口，提供系统中的DataManager 单例对象，方便调用方直接使用，提升可读性与一致性。

暴露内容：
- PROJECT_DATA_MANAGER: 管理项目数据
- DEPLOY_HISTORY_DATA_MANAGER: 管理部署历史记录数据
- SYSTEM_CONFIG_DATA_MANAGER: 管理系统配置项数据
- TEMPLATE_MANAGER: 管理部署模板及其内容
"""
from .deploy_history_data_manager import DeployHistoryDataManager
from .project_data_manager import ProjectDataManager
from .system_config_data_manager import SystemConfigDataManager
from .template_manager import TemplateManager


PROJECT_DATA_MANAGER = ProjectDataManager().get_instance()
DEPLOY_HISTORY_DATA_MANAGER = DeployHistoryDataManager().get_instance()
SYSTEM_CONFIG_DATA_MANAGER = SystemConfigDataManager().get_instance()
TEMPLATE_MANAGER = TemplateManager().get_instance()