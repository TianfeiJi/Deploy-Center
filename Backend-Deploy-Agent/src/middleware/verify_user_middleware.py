# middleware/verify_user_middleware.py
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse
from starlette import status

# WARNING：当前逻辑仅检查 X-User 请求头是否存在，尚未验证用户的合法性
# TODO：后续应接入用户合法性验证
class VerifyUserMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        path = request.url.path

        user = request.headers.get("X-User")
        # 检查是否携带 X-User 且用户合法（暂时只判断是否存在）
        if not user or not self.is_valid_user(user):
            return JSONResponse(
                status_code=status.HTTP_401_UNAUTHORIZED,
                content={"detail": "Invalid Request"},
                headers={"WWW-Authenticate": "Bearer"}
            )

        return await call_next(request)
    
    def is_valid_user(self, user: str) -> bool:
        # TODO: 实现真正的用户校验逻辑
        # 比如校验 user 是否在白名单、是否 token 签名合法等
        return bool(user)  # 临时占位，始终为 True
