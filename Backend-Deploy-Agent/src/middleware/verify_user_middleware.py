# middleware/verify_user_middleware.py
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse
from starlette import status


class VerifyUserMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        path = request.url.path

        user = request.headers.get("X-User")
        # TODO：现在只是监测有没有携带X-User 没有对拿到的user信息进行验证！
        if not user:
            return JSONResponse(
                status_code=status.HTTP_401_UNAUTHORIZED,
                content={"detail": "Invalid Request"},
                headers={"WWW-Authenticate": "Bearer"}
            )

        return await call_next(request)
