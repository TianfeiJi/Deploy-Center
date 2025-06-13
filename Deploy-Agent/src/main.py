"""Deploy Agent

@Author: Tianfei Ji

TODO:
1. 其他项目部署接口
"""
import uvicorn
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from middleware.verify_user_middleware import VerifyUserMiddleware
from routes.project_routes import project_router
from routes.deploy_history_routes import deploy_history_router
from routes.deploy_log_routes import deploy_log_router
from routes.docker_routes import docker_router
from routes.server_routes import server_router
from routes.system_config_routes import system_config_router
from routes.template_routes import template_router
from routes.inspect_routes import inspect_router
from fastapi.openapi.docs import get_swagger_ui_html


app = FastAPI(
    title="Deploy Agent",
    description=(""),
    version="1.0.0", 
    contact={ 
        "name": "纪田飞",
        "url": "http://jitianfei.com",
        "email": "ieacoder@foxmail.com",
    },
    docs_url=None
    # openapi_url=None    # 禁用API文档
)

# 更换国内 CDN
@app.get("/docs", include_in_schema=False)
async def custom_swagger_ui_html():
    return get_swagger_ui_html(
        openapi_url=app.openapi_url,
        title="Deploy Agent API Docs",
        swagger_js_url="https://cdn.bootcdn.net/ajax/libs/swagger-ui/5.3.2/swagger-ui-bundle.min.js",
        swagger_css_url="https://cdn.bootcdn.net/ajax/libs/swagger-ui/5.3.2/swagger-ui.min.css"
    )


# 验证请求头是否携带X-User 用户信息的中间件
# app.add_middleware(VerifyUserMiddleware)

# 添加 CORS 中间件
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 允许任何源
    allow_credentials=True,  # 允许发送 cookies
    allow_methods=["*"],  # 允许所有 HTTP 方法
    allow_headers=["*"],  # 允许所有头部信息
)

@app.get("/api/deploy-agent/index")
async def index():
    return {"code": 200, "status": "success", "msg": "Deploy Agent Ready!", "data": None}


# 全局HTTPException异常捕获处理
@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    return JSONResponse(status_code=exc.status_code, content=exc.detail, headers=exc.headers)


app.include_router(project_router)
app.include_router(deploy_history_router)
app.include_router(deploy_log_router)
app.include_router(docker_router)
app.include_router(server_router)
app.include_router(system_config_router)
app.include_router(template_router)
app.include_router(inspect_router)


if __name__ == "__main__":
   uvicorn.run(app, host="0.0.0.0", port=2333)