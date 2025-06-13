from fastapi import APIRouter, HTTPException
from typing import Dict, Optional, Union
from models.common.http_result import HttpResult
from config.log_config import get_logger
from manager.system_config_data_manager import SystemConfigManager
from utils.decorators.skip_auth import skip_auth

system_config_router = APIRouter()
logger = get_logger()

@system_config_router.get("/api/deploy-center/system-config/list", summary="获取所有配置项")
async def get_config_list():
    """
    获取所有系统配置列表
    """
    try:
        config_manager = SystemConfigManager.get_instance()
        config_list = config_manager.list_configs()
        return HttpResult[object](code=200, status="success", msg=None, data=config_list)
    except Exception as e:
        logger.error(f"获取系统配置列表失败: {e}")
        return HttpResult[None](code=500, status="failed", msg=str(e), data=None)

@skip_auth
@system_config_router.get("/api/deploy-center/system-config/{config_key}", summary="获取配置项详情")
async def get_config(config_key: str):
    """
    根据键获取系统配置
    """
    try:
        config_manager = SystemConfigManager.get_instance()
        config_value = config_manager.get_config(config_key)
        if config_value is None:
            raise HTTPException(status_code=404, detail="Config not found")
        return HttpResult[object](code=200, status="success", msg=None, data=config_value)
    except Exception as e:
        logger.error(f"获取系统配置失败: {e}")
        return HttpResult[None](code=500, status="failed", msg=str(e), data=None)

@system_config_router.put("/api/deploy-center/system-config/{config_key}", summary="更新配置项")
async def update_config(config_key: str, updated_data: dict):
    """
    更新系统配置
    """
    try:
        config_manager = SystemConfigManager.get_instance()
        config_manager.update_config(config_key, updated_data)
        return HttpResult[None](code=200, status="success", msg=None, data=None)
    except Exception as e:
        logger.error(f"更新系统配置失败: {e}")
        return HttpResult[None](code=500, status="failed", msg=str(e), data=None)

@system_config_router.delete("/api/deploy-center/system-config/{config_key}", summary="删除配置项")
async def delete_config(config_key: str):
    """
    删除系统配置
    """
    try:
        config_manager = SystemConfigManager.get_instance()
        config_manager.delete_config(config_key)
        return HttpResult[Dict[str, str]](code=200, status="success", msg=None, data=None)
    except Exception as e:
        logger.error(f"删除配置项失败: {e}")
        return HttpResult[Dict[str, str]](code=500, status="failed", msg=str(e), data=None)