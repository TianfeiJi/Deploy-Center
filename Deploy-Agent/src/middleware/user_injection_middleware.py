# middlewares/user_injection.py
from starlette.middleware.base import BaseHTTPMiddleware
from fastapi import Request
import json
from config.log_config import get_logger
from utils.user_context import set_current_user

logger = get_logger()

class UserInjectionMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        user_info = request.headers.get("X-User")
        try:
            user = json.loads(user_info) if user_info else None
        except Exception as e:
            logger.warning(f"X-User 解析失败：{e}")
            user = None

        # 设置全局用户上下文
        set_current_user(user)

        response = await call_next(request)
        return response