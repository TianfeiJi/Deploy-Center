# middleware/verify_token_middleware.py
import re
from fastapi import Request, status
from starlette.middleware.base import BaseHTTPMiddleware
from models.common.http_result import HttpResult
from utils.jwt_util import JWTUtil

# 定义静态路径白名单（完全匹配或前缀匹配）
STATIC_SKIP_AUTH_PATHS = [
    "/docs",
    "/redoc",
    "/openapi.json"
]

class VerifyTokenMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        path = request.url.path
        method = request.method

        # Step 1: 判断是否在静态白名单
        if any(path == p or path.startswith(p + "/") for p in STATIC_SKIP_AUTH_PATHS):
            return await call_next(request)

        # Step 2: 判断当前请求是否带有 @skip_auth 装饰器
        for route in request.app.routes:
            if hasattr(route, "endpoint") and method in route.methods:
                if route.path == path or re.fullmatch(route.path.replace("{", "(?P<").replace("}", ">[^/]+)"), path):
                    if getattr(route.endpoint, "_skip_auth", False):
                        return await call_next(request)

        # Step 3: 验证 Token
        token = request.headers.get("Authorization")
        if not token:
            return HttpResult.failed(msg="Token is missing", code=403).json_response()

        token = token.replace("Bearer ", "")
        user = JWTUtil.get_user_from_token(token)
        if not user:
            return HttpResult.failed(msg="Invalid or expired token", code=403).json_response()

        return await call_next(request)
