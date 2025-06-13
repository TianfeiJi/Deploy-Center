"""Deploy Center

@Author: Tianfei Ji
"""
import uvicorn
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from middleware.verify_token_middleware import VerifyTokenMiddleware
from fastapi.responses import JSONResponse
from routes.auth_routes import auth_router
from routes.agent_routes import agent_router
from routes.user_routes import user_router
from routes.system_config_routes import system_config_router
from routes.two_factor_routes import two_factor_router


app = FastAPI(
    title="Deploy Center",
    description=(""),
    version="1.0.0", 
    contact={ 
        "name": "纪田飞",
        "url": "http://jitianfei.com",
        "email": "ieacoder@foxmail.com",
    },
    openapi_url=None    # 禁用API文档
)

# 添加 Token校验 middleware
app.add_middleware(VerifyTokenMiddleware)

# 添加 CORS 中间件
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 允许任何源
    allow_credentials=True,  # 允许发送 cookies
    allow_methods=["*"],  # 允许所有 HTTP 方法
    allow_headers=["*"],  # 允许所有头部信息
)


@app.get("/api/deploy-center/index")
async def index():
    return {"code": 200, "status": "success", "msg": "Welcome to Deploy Center!", "data": None}


# 全局HTTPException异常捕获处理
@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    return JSONResponse(status_code=exc.status_code, content=exc.detail, headers=exc.headers)


app.include_router(auth_router)
app.include_router(agent_router)
app.include_router(user_router)
app.include_router(system_config_router)
app.include_router(two_factor_router)


if __name__ == "__main__":
   uvicorn.run(app, host="0.0.0.0", port=1333)