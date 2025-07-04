from models.entity.user import User
from fastapi import APIRouter, Body, HTTPException
from typing import List, Dict
from models.common.http_result import HttpResult
from manager import USER_DATA_MANAGER
from utils.user_context import get_current_user
from config.log_config import get_logger


user_router = APIRouter()
logger = get_logger()


@user_router.get("/api/deploy-center/user/list", summary="获取用户列表")
async def get_user_list():
    """
    获取所有用户信息
    """
    try:
        user_list: List[User] = USER_DATA_MANAGER.list_users()
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
        user: User = USER_DATA_MANAGER.get_user(user_id)
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
        USER_DATA_MANAGER.create_user(user_info)
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
        USER_DATA_MANAGER.update_user(user_id, updated_info)
        return HttpResult[Dict](code=200, status="success", msg=None, data=None)
    except ValueError as ve:
        logger.error(f"更新用户信息失败: {ve}")
        return HttpResult[Dict](code=404, status="failed", msg=str(ve), data=None)
    except Exception as e:
        logger.error(f"更新用户信息失败: {e}")
        return HttpResult[Dict](code=500, status="failed", msg=str(e), data=None)

@user_router.put("/api/deploy-center/user/{user_id}/change-status", summary="变更用户状态")
async def change_user_status(user_id: int, status: str = Body(..., embed=True)):
    """
    禁用 / 启用 指定用户
    """
    try:
        current_user: User = get_current_user()
        if current_user.id == user_id:
            return HttpResult.failed(msg="禁止修改自己的账号状态", code=400)

        user = USER_DATA_MANAGER.get_user(user_id)
        if not user:
            return HttpResult.failed(msg="用户不存在", code=404)

        # 更新状态
        USER_DATA_MANAGER.update_user(user_id, {"status": status})

        # 日志记录（如写入 DB 或打印）
        logger.info(f"[用户状态变更] 操作人: {current_user.username}，目标用户: {user.username}，新状态: {status}")

        return HttpResult.success(msg="状态变更成功")
    except Exception as e:
        logger.error(f"用户状态变更失败: {e}")
        return HttpResult.failed(msg="服务器异常", code=500)
    
@user_router.delete("/api/deploy-center/user/{user_id}", summary="删除用户")
async def delete_user(user_id: int):
    """
    删除用户
    """
    try:
        USER_DATA_MANAGER.delete_user(user_id)
        return HttpResult[Dict](code=200, status="success", msg=None, data=None)
    except Exception as e:
        logger.error(f"删除用户失败: {e}")
        return HttpResult[Dict](code=500, status="failed", msg=str(e), data=None)