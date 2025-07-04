# middlewares/user_injection.py
from starlette.middleware.base import BaseHTTPMiddleware
from fastapi import Request
from utils.user_context import set_current_user
from utils.jwt_util import JWTUtil
from manager import USER_DATA_MANAGER


class UserInjectionMiddleware(BaseHTTPMiddleware):
     async def dispatch(self, request: Request, call_next):
        try:
            auth_header = request.headers.get("Authorization", "")
            if auth_header.startswith("Bearer "):
                token = auth_header.removeprefix("Bearer ").strip()
                user = JWTUtil.get_user_from_token(token)
                if user:
                    user_id = user.get("user_id")
                    set_current_user(USER_DATA_MANAGER.get_user(user_id))
        except Exception as e:
            print(f"[UserInjectionMiddleware] 注入用户失败: {e}")

        response = await call_next(request)
        return response