from fastapi import APIRouter, HTTPException
from typing import Dict
from models.common.http_result import HttpResult
from config.log_config import get_logger
from manager import SYSTEM_CONFIG_DATA_MANAGER
from utils.decorators.skip_auth import skip_auth

system_config_router = APIRouter()
logger = get_logger()

@system_config_router.get("/api/deploy-center/system-config/list", summary="获取所有配置项")
async def get_config_list():
    """
    获取所有系统配置列表
    """
    try:
        config_list = SYSTEM_CONFIG_DATA_MANAGER.list_configs()
        return HttpResult.ok(data=config_list)
    except Exception as e:
        logger.error(f"获取系统配置列表失败: {e}")
        return HttpResult.fail(msg=str(e))

@skip_auth
@system_config_router.get("/api/deploy-center/system-config/{config_key}", summary="获取配置项详情")
async def get_config(config_key: str):
    """
    根据键获取系统配置
    """
    try:
        config_value = SYSTEM_CONFIG_DATA_MANAGER.get_config(config_key)
        if config_value is None:
            return HttpResult.fail(code=404, msg="Config not found")
        return HttpResult.ok(data=config_value)
    except Exception as e:
        logger.error(f"获取系统配置失败: {e}")
        return HttpResult.fail(msg=str(e))
        

@system_config_router.put("/api/deploy-center/system-config/{config_key}", summary="更新配置项")
async def update_config(config_key: str, updated_data: dict):
    """
    更新系统配置
    """
    try:
        SYSTEM_CONFIG_DATA_MANAGER.update_config(config_key, updated_data)
        return HttpResult.ok()
    except Exception as e:
        logger.error(f"更新系统配置失败: {e}")
        return HttpResult.fail(msg=str(e))

@system_config_router.delete("/api/deploy-center/system-config/{config_key}", summary="删除配置项")
async def delete_config(config_key: str):
    """
    删除系统配置
    """
    try:
        SYSTEM_CONFIG_DATA_MANAGER.delete_config(config_key)
        return HttpResult.ok()
    except Exception as e:
        logger.error(f"删除配置项失败: {e}")
        return HttpResult.fail(msg=str(e))