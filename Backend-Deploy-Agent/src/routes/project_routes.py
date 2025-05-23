from datetime import datetime
import json
import os
import time
import uuid
from manager.project_data_manager import ProjectDataManager
from fastapi import File, Query, Request, UploadFile, Form, APIRouter
from models.common.http_result import HttpResult
from deployers.java_project_deployer import JavaProjectDeployer
from deployers.web_project_deploy import WebProjectDeployer
from models.dto.add_web_project_request_dto import AddWebProjectRequestDto
from models.dto.add_java_project_request_dto import AddJavaProjectRequestDto
from models.dto.update_java_project_request_dto import UpdateJavaProjectRequestDto
from models.dto.update_web_project_request_dto import UpdateWebProjectRequestDto


project_router = APIRouter()
PROJECT_DATA_MANAGER = ProjectDataManager().get_instance()


# 获取所有项目数据
@project_router.get("/api/deploy-agent/project/list", summary="获取项目数据", description="返回所有项目数据。")
async def get_project_list(request: Request):
    try:
        user_json: str = request.headers.get("X-User")
        user = json.loads(user_json)
        permissions: list = user.get("permissions")
        projects = PROJECT_DATA_MANAGER.list_projects()
        if (permissions is not None):
            projects = [project for project in projects if project.get("project_code") in permissions]

        return HttpResult[object](code=200, status="success", msg=None, data=[project for project in projects])
    except FileNotFoundError:
        return HttpResult[None](code=404, status="success", msg="project_data.json not found.", data=None)

# ==================== 项目部署通用接口 ====================
@project_router.get("/api/deploy-agent/project/support/render-template-content", summary="渲染模板内容, 渲染dockerfile和dockercommand")
async def render_template_content(
    project_id: str = Query(..., description="项目 ID"),
    template_id: str = Query(..., description="模板 ID")
):
    from utils.template_content_renderer import render_template_for_project
    content = render_template_for_project(project_id, template_id)
    return {"code": 200, "status": "success", "msg": None, "data": content}

# ==================== Java项目接口 ====================
@project_router.get("/api/deploy-agent/project/java/get/{id}", summary="获取 Java 项目详情")
async def delete_java_project(id: str):
    project = PROJECT_DATA_MANAGER.get_project(id)
    if (project != None):
        return HttpResult[dict](code=200, status="success", msg=None, data=project)
    else:
        return HttpResult[None](code=500, status="failed", msg=f"没有id为{id}的项目", data=None)

@project_router.post("/api/deploy-agent/project/java/add", summary="创建 待部署的 Java 项目")
async def add_java_project(dto: AddJavaProjectRequestDto):
    new_project_id = str(uuid.uuid4()).replace("-", "")[:8]
    new_java_project = {
        "id": new_project_id,
        "project_type": "Java",
        "project_code": dto.project_code,
        "project_name": dto.project_name,
        "project_group": dto.project_group,
        "docker_image_name": dto.docker_image_name,
        "docker_image_tag": dto.docker_image_tag,
        "external_port": dto.external_port,
        "internal_port": dto.internal_port,
        "network": dto.network,
        "jdk_version": dto.jdk_version,
        "host_project_path": dto.host_project_path,
        "container_project_path":  dto.container_project_path,
        "git_repository": dto.git_repository,
        "status": "created",
        "created_at": datetime.now().isoformat(),
        "updated_at": None,
        "last_deployed_at": None
    }
    PROJECT_DATA_MANAGER.create_project(new_java_project)
    return HttpResult[None](code=200, status="success", msg=None, data=None)

@project_router.put("/api/deploy-agent/project/java/update", summary="更新 Java 项目")
async def update_java_project(update_dto: UpdateJavaProjectRequestDto):
    PROJECT_DATA_MANAGER.update_project(update_dto.id, update_dto.model_dump(exclude={"id"}))
    return {"code": 200, "status": "success", "msg": None, "data": None}

"""TODO 额外的参数
1. 是否更新docker-compose
2. 
"""
@project_router.post("/api/deploy-agent/project/java/deploy", summary="部署 Java 项目", description="上传 Java 项目的 JAR 包并创建 Docker 容器来部署该项目。")
async def deploy_java_project(
    id: str = Form(..., title="项目ID"),
    file: UploadFile = File(..., title="JAR 文件", description="上传要部署的 JAR 文件"),
    dockerfile_content: str = Form(..., title="Dockerfile内容"),
    dockercommand_content: str = Form(..., title="Docker命令"),
):
    # """ 临时测试 保存文件到本地"""
    # # 确保保存文件的目录存在
    # save_dir = "temp"
    # os.makedirs(save_dir, exist_ok=True)  # 如果目录不存在，自动创建

    # # 构造文件保存路径
    # file_path = os.path.join(save_dir, file.filename)

    # # 保存文件到本地
    # with open(file_path, "wb") as f:
    #     f.write(file.file.read())

    # # 模拟文件上传完毕后的后续部署操作耗时
    # time.sleep(5)

    # return {"code": 200, "status": "success", "msg": f"接口测试：项目{id}部署成功", "data": None}
    msg = JavaProjectDeployer().deploy(id, file, dockerfile_content, dockercommand_content)
    return {"code": 200, "status": "success", "msg": msg, "data": None}

# TODO: 设置一个参数判断是否删除服务器上的项目文件？
@project_router.delete("/api/deploy-agent/project/java/delete/{id}", summary="删除 Web 项目")
async def delete_java_project(id: str):
    PROJECT_DATA_MANAGER.delete_project(id)
    return {"code": 200, "status": "success", "msg": None, "data": None}

# ==================== 前端项目接口 ====================
@project_router.get("/api/deploy-agent/project/web/get/{id}", summary="获取Web项目详情")
async def get_web_project(id: str):
    project = PROJECT_DATA_MANAGER.get_project(id)
    if (project != None):
        return HttpResult[dict](code=200, status="success", msg=None, data=project)
    else:
        return HttpResult[None](code=500, status="failed", msg=f"没有id为{id}的项目", data=None)

@project_router.post("/api/deploy-agent/project/web/add", summary="创建 待部署的 Web 项目")
async def add_web_project(dto: AddWebProjectRequestDto):
    new_project_id = str(uuid.uuid4()).replace("-", "")[:8]
    new_web_project = {
        "id": new_project_id,
        "project_type": "Web",
        "project_code": dto.project_code,
        "project_name": dto.project_name,
        "project_group": dto.project_group,
        "host_project_path": dto.host_project_path,
        "container_project_path": dto.container_project_path,
        "access_url": dto.access_url,
        "git_repository": dto.git_repository,
        "status": "created",
        "created_at": datetime.now().isoformat(),
        "updated_at": None,
        "last_deployed_at": None
    }
    PROJECT_DATA_MANAGER.create_project(new_web_project)
    return {"code": 200, "status": "success", "msg": new_project_id, "data": None}

@project_router.put("/api/deploy-agent/project/web/update", summary="更新 Web 项目")
async def update_web_project(update_dto: UpdateWebProjectRequestDto):
    PROJECT_DATA_MANAGER.update_project(update_dto.id, update_dto.model_dump(exclude={"id"}))
    return {"code": 200, "status": "success", "msg": None, "data": None}

@project_router.post("/api/deploy-agent/project/web/deploy", summary="部署前端项目", description="上传前端项目的压缩包到指定路径，并完成解压。注意：只负责上传打包后到文件，需要额外手动处理nginx的配置")
async def deploy_web_project(
    id: str = Form(..., title="前端项目ID"),
    file: UploadFile = File(..., title="前端项目压缩包")
):
    return WebProjectDeployer().deploy(id, file)

@project_router.delete("/api/deploy-agent/project/web/delete/{id}", summary="删除 Web 项目")
async def delete_web_project(id: str):
    PROJECT_DATA_MANAGER.delete_project(id)
    return {"code": 200, "status": "success", "msg": None, "data": None}
