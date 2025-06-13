from models.entity.user import User
from fastapi import APIRouter, HTTPException
from typing import List, Dict
from models.common.http_result import HttpResult
from manager.user_data_manager import UserDataManager
from config.log_config import get_logger

user_router = APIRouter()
logger = get_logger()


@user_router.get("/api/deploy-center/user/list", summary="获取用户列表")
async def get_user_list():
    """
    获取所有用户信息
    """
    try:
        user_data_manager = UserDataManager.get_instance()
        user_list: List[User] = user_data_manager.list_users()
        return HttpResult[List[User]](code=200, status="success", msg=None, data=[user for user in user_list])
    except Exception as e:
        logger.error(f"获取用户列表失败: {e}")
        return HttpResult[None](code=500, status="failed", msg=str(e), data=None)

@user_router.get("/api/deploy-center/user/{user_id}", summary="获取用户详情")
async def get_user(user_id: int):
    """
    根据用户ID获取用户详情
    """
    try:
        user_data_manager = UserDataManager.get_instance()
        user: User = user_data_manager.get_user(user_id)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        user_info_dict = user.model_dump(exclude={"password", "two_factor_secret", "created_at", "created_by", "updated_at", "updated_by"})
        
        return HttpResult[dict](code=200, status="success", msg=None, data=user_info_dict)
    except Exception as e:
        logger.error(f"获取用户详情失败: {e}")
        return HttpResult[None](code=500, status="failed", msg=str(e), data=None)

@user_router.post("/api/deploy-center/user/create", summary="新增用户")
async def create_user(user_info: Dict):
    """
    新增用户
    """
    try:
        user_data_manager = UserDataManager.get_instance()
        user_data_manager.create_user(user_info)
        return HttpResult[None](code=200, status="success", msg="用户创建成功", data=None)
    except Exception as e:
        logger.error(f"创建用户失败: {e}")
        return HttpResult[None](code=500, status="failed", msg=str(e), data=None)

@user_router.put("/api/deploy-center/user/{user_id}", summary="更新用户信息")
async def update_user(user_id: int, updated_info: Dict):
    """
    更新用户信息
    """
    try:
        user_data_manager = UserDataManager.get_instance()
        user_data_manager.update_user(user_id, updated_info)
        return HttpResult[Dict](code=200, status="success", msg=None, data=None)
    except ValueError as ve:
        logger.error(f"更新用户信息失败: {ve}")
        return HttpResult[Dict](code=404, status="failed", msg=str(ve), data=None)
    except Exception as e:
        logger.error(f"更新用户信息失败: {e}")
        return HttpResult[Dict](code=500, status="failed", msg=str(e), data=None)

@user_router.delete("/api/deploy-center/user/{user_id}", summary="删除用户")
async def delete_user(user_id: int):
    """
    删除用户
    """
    try:
        user_data_manager = UserDataManager.get_instance()
        user_data_manager.delete_user(user_id)
        return HttpResult[Dict](code=200, status="success", msg=None, data=None)
    except Exception as e:
        logger.error(f"删除用户失败: {e}")
        return HttpResult[Dict](code=500, status="failed", msg=str(e), data=None)