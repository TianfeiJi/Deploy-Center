import json
import uuid
import httpx
from pathlib import Path
from httpx import RequestError
from urllib.parse import urlparse
from datetime import datetime, timezone

from fastapi import File, Query, Request, UploadFile, Form, APIRouter

from models.common.http_result import HttpResult
from models.entity.deploy_task import DeployTask
from models.dto.add_web_project_request_dto import AddWebProjectRequestDto
from models.dto.add_java_project_request_dto import AddJavaProjectRequestDto
from models.dto.add_python_project_request_dto import AddPythonProjectRequestDto
from models.dto.update_web_project_request_dto import UpdateWebProjectRequestDto
from models.dto.update_java_project_request_dto import UpdateJavaProjectRequestDto
from models.dto.update_python_project_request_dto import UpdatePythonProjectRequestDto
from manager import PROJECT_DATA_MANAGER
from container.app_container import DEPLOY_TASK_SERVICE
from utils.user_context import get_current_user
from utils.file_util import save_uploaded_file


project_router = APIRouter()


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

# 获取项目详情
@project_router.get("/api/deploy-agent/project", summary="获取项目详情", description="根据项目 ID 获取对应的项目详细信息")
async def get_project(id: str = Query(..., description="项目 ID")):
    project = PROJECT_DATA_MANAGER.get_project(id)
    if project is not None:
        return HttpResult[dict](code=200, status="success", msg=None, data=project)
    else:
        return HttpResult[None](code=500, status="failed", msg=f"未找到 ID 为 {id} 的项目", data=None)

# ==================== 项目部署通用接口 ====================
@project_router.get("/api/deploy-agent/project/support/render-template-content", summary="渲染模板内容, 渲染dockerfile和dockercommand")
async def render_template_content(
    project_id: str = Query(..., description="项目 ID"),
    template_id: str = Query(..., description="模板 ID")
):
    from utils.template_content_renderer import render_template_for_project
    content = render_template_for_project(project_id, template_id)
    return {"code": 200, "status": "success", "msg": None, "data": content}

# ==================== 前端项目接口 ====================
@project_router.get(
    "/api/deploy-agent/project/web/check-deployment-status",
    summary="检测项目是否已部署",
    description="根据项目 ID 判断是否已部署，逻辑为检查 container_project_path 是否存在有效文件"
)
async def check_web_project_deployment_status(id: str = Query(..., description="项目ID")):
    check_time = datetime.now(timezone.utc).isoformat()

    # 1. 获取项目信息
    project = PROJECT_DATA_MANAGER.get_project(id)
    if project is None:
        return HttpResult(code=404, status="failed", msg="项目不存在", data=None)

    # 2. 获取部署路径
    container_path = project.get("container_project_path")
    if not container_path:
        return HttpResult(code=400, status="failed", msg="项目未配置container_project_path（容器项目路径）", data=None)

    path_obj = Path(container_path)

    # 3. 判断目录是否存在，且是否包含任何文件（忽略空目录）
    if path_obj.exists() and any(path_obj.iterdir()):
        deployment_status = "Deployed"
    else:
        deployment_status = "未部署"

    print(f"[部署状态检测] 项目ID: {id} 路径: {container_path} 状态: {deployment_status}")

    return HttpResult(code=200, status="success", msg=None, data={
        "project_id": id,
        "container_project_path": container_path,
        "deployment_status": deployment_status,
        "check_time": check_time
    })

@project_router.get("/api/deploy-agent/project/web/check-accessibility", summary="检测前端项目是否可访问", description="根据项目 access_url 判断是否可达")
async def check_web_project_accessibility(url: str = Query(..., description="前端项目的访问地址")):
    # 判空 & 去除空格
    if not url or not url.strip():
        return HttpResult(code=400, status="failed", msg="url不能为空", data=None)

    url = url.strip()

    # 补全前缀（如果没有）
    if not url.startswith(("http://", "https://")):
        url = "http://" + url

    check_time = datetime.now(timezone.utc).isoformat()
    parsed = urlparse(url)
    target = parsed.geturl()
    print(f"[Web项目可及性检测] 开始检测 URL：{target}")
    try:
        # 限制请求超时3s，防止阻塞
        async with httpx.AsyncClient(timeout=3.0, follow_redirects=True) as client:
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36",
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
                "Accept-Language": "zh-CN,zh;q=0.9",
                "Cache-Control": "no-cache",
                "Pragma": "no-cache",
                "Connection": "keep-alive"
            }
            response = await client.get(target, headers=headers)
            
            runtime_status = "Accessible" if 200 <= response.status_code < 400 else "Inaccessible"
            
            print(f"[Web项目可及性检测] URL: {target} 状态码: {response.status_code}, 判定为: {runtime_status}")
            
            return HttpResult(code=200, status="success", msg=None, data={
                "runtime_status": runtime_status,
                "check_time": check_time,
                "status_code": response.status_code,
                "reason_phrase": response.reason_phrase
            })
    except RequestError as e:
        print(f"[Web项目可及性检测] 网络异常：{target}，错误类型：{e.__class__.__name__}，详情：{repr(e)}")
        # 请求失败，网络或连接问题
        return HttpResult(code=200, status="success", msg=None, data={
            "runtime_status": "Inaccessible",
            "check_time": check_time,
            "error": str(e)
        })
    except Exception as e:
        print(f"[Web项目可及性检测] 未知异常：{target}，错误：{e}")
        return HttpResult(code=200, status="success", msg=None, data={
            "runtime_status": "Unknown",
            "check_time": check_time,
            "error": str(e)
        })

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
        "created_at": datetime.now(),
        "updated_at": None,
        "last_deployed_at": None
    }
    PROJECT_DATA_MANAGER.create_project(new_web_project)
    return {"code": 200, "status": "success", "msg": new_project_id, "data": None}

@project_router.put("/api/deploy-agent/project/web/update", summary="更新 Web 项目")
async def update_web_project(update_dto: UpdateWebProjectRequestDto):
    PROJECT_DATA_MANAGER.update_project(update_dto.id, update_dto.model_dump(exclude={"id"}))
    return {"code": 200, "status": "success", "msg": None, "data": None}

@project_router.post(
    "/api/deploy-agent/project/web/deploy",
    summary="部署前端项目",
    description="上传前端项目压缩包并创建部署任务。注意：当前仅负责上传并解压静态资源，不处理 nginx 配置。"
)
async def deploy_web_project(
    file: UploadFile = File(..., title="前端项目压缩包"),
    project_id: str = Form(..., title="前端项目ID"),
    task_name: str = Form("Web 项目部署", title="任务名称"),
    trigger_type: str = Form("MANUAL", title="触发方式"),
    deploy_mechanism: str = Form("UPLOAD", title="部署方式"),
):
    try:
        # 1. 校验项目是否存在
        project = PROJECT_DATA_MANAGER.get_project(project_id)
        if project is None:
            return HttpResult[None](
                code=400,
                status="failed",
                msg=f"没有 id 为 {project_id} 的 Java 项目",
                data=None
            )
            
        # 2. 获取当前用户
        current_user = get_current_user()
        
        # 3. 保存上传文件到临时目录
        upload_file_path = save_uploaded_file(file)

        task: DeployTask = DEPLOY_TASK_SERVICE.submit_task(
            project_id=project_id,
            task_name=task_name,
            trigger_type=trigger_type,
            deploy_mechanism=deploy_mechanism,
            upload_file_name=file.filename,
            upload_file_path=upload_file_path,
            build_image_name=project.get("docker_image_name"),
            build_image_tag=project.get("docker_image_tag"),
            container_name=project.get("container_name"),
            operator_id=current_user.get("id") if current_user else None,
            operator_name=current_user.get("nickname") if current_user else None,
        )

        return HttpResult[dict](
            code=200,
            status="success",
            msg="部署任务已提交",
            data={
                "task_id": task.id,
                "project_id": task.project_id
            }
        )

    except Exception as e:
        import traceback
        traceback.print_exc()
        return HttpResult[None](
            code=500,
            status="failed",
            msg=f"提交部署任务失败: {str(e)}",
            data=None
        )

@project_router.delete("/api/deploy-agent/project/web/delete/{id}", summary="删除 Web 项目")
async def delete_web_project(id: str):
    PROJECT_DATA_MANAGER.delete_project(id)
    return {"code": 200, "status": "success", "msg": None, "data": None}

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
        "created_at": datetime.now(),
        "updated_at": None,
        "last_deployed_at": None
    }
    PROJECT_DATA_MANAGER.create_project(new_java_project)
    return HttpResult[None](code=200, status="success", msg=None, data=None)

@project_router.put("/api/deploy-agent/project/java/update", summary="更新 Java 项目")
async def update_java_project(update_dto: UpdateJavaProjectRequestDto):
    PROJECT_DATA_MANAGER.update_project(update_dto.id, update_dto.model_dump(exclude={"id"}))
    return {"code": 200, "status": "success", "msg": None, "data": None}

@project_router.post(
    "/api/deploy-agent/project/java/deploy",
    summary="部署 Java 项目",
    description="上传 Java 项目的 JAR 包并创建部署任务。"
)
async def deploy_java_project(
    file: UploadFile = File(..., title="JAR 文件", description="上传要部署的 JAR 文件"),
    project_id: str = Form(..., title="项目ID"),
    task_name: str = Form("Java 项目部署", title="任务名称"),
    trigger_type: str = Form("MANUAL", title="触发方式"),
    deploy_mechanism: str = Form("UPLOAD", title="部署方式"),
    dockerfile_content: str = Form(..., title="Dockerfile内容"),
    dockercommand_content: str = Form(..., title="Docker命令"),
):
    try:
        # 1. 校验项目是否存在
        project = PROJECT_DATA_MANAGER.get_project(project_id)
        if project is None:
            return HttpResult[None](
                code=400,
                status="failed",
                msg=f"没有 id 为 {project_id} 的 Java 项目",
                data=None
            )
            
        # 2. 获取当前用户
        current_user = get_current_user()
        
        # 3. 保存上传文件到临时目录
        upload_file_path = save_uploaded_file(file)

        task: DeployTask = DEPLOY_TASK_SERVICE.submit_task(
            project_id=project_id,
            task_name=task_name,
            trigger_type=trigger_type,
            deploy_mechanism=deploy_mechanism,
            upload_file_name=file.filename,
            upload_file_path=upload_file_path,
            build_image_name=project.get("docker_image_name"),
            build_image_tag=project.get("docker_image_tag"),
            container_name=project.get("container_name"),
            dockerfile_content=dockerfile_content,
            dockercommand_content=dockercommand_content,
            operator_id=current_user.get("id") if current_user else None,
            operator_name=current_user.get("nickname") if current_user else None,
        )

        return HttpResult[dict](
            code=200,
            status="success",
            msg="部署任务已提交",
            data={
                "task_id": task.id,
                "project_id": task.project_id
            }
        )

    except Exception as e:
        import traceback
        traceback.print_exc()
        return HttpResult[None](
            code=500,
            status="failed",
            msg=f"提交部署任务失败: {str(e)}",
            data=None
        )

# TODO: 设置一个参数判断是否删除服务器上的项目文件？
@project_router.delete("/api/deploy-agent/project/java/delete/{id}", summary="删除 Web 项目")
async def delete_java_project(id: str):
    PROJECT_DATA_MANAGER.delete_project(id)
    return {"code": 200, "status": "success", "msg": None, "data": None}

# ==================== Python 项目接口 ====================
@project_router.get("/api/deploy-agent/project/python/get/{id}", summary="获取 Python 项目详情")
async def get_python_project(id: str):
    project = PROJECT_DATA_MANAGER.get_project(id)
    if project is not None:
        return HttpResult[dict](code=200, status="success", msg=None, data=project)
    else:
        return HttpResult[None](code=500, status="failed", msg=f"没有id为{id}的项目", data=None)

@project_router.post("/api/deploy-agent/project/python/add", summary="创建待部署的 Python 项目")
async def add_python_project(dto: AddPythonProjectRequestDto):
    new_project_id = str(uuid.uuid4()).replace("-", "")[:8]
    new_python_project = {
        "id": new_project_id,
        "project_type": "Python",
        "project_code": dto.project_code,
        "project_name": dto.project_name,
        "project_group": dto.project_group,
        "docker_image_name": dto.docker_image_name,
        "docker_image_tag": dto.docker_image_tag,
        "external_port": dto.external_port,
        "internal_port": dto.internal_port,
        "network": dto.network,
        "python_version": dto.python_version,
        "host_project_path": dto.host_project_path,
        "container_project_path": dto.container_project_path,
        "git_repository": dto.git_repository,
        "created_at": datetime.now(),
        "updated_at": None,
        "last_deployed_at": None
    }
    PROJECT_DATA_MANAGER.create_project(new_python_project)
    return HttpResult[None](code=200, status="success", msg=None, data=None)

@project_router.put("/api/deploy-agent/project/python/update", summary="更新 Python 项目")
async def update_python_project(update_dto: UpdatePythonProjectRequestDto):
    PROJECT_DATA_MANAGER.update_project(update_dto.id, update_dto.model_dump(exclude={"id"}))
    return HttpResult[None](code=200, status="success", msg=None, data=None)

@project_router.post(
    "/api/deploy-agent/project/python/deploy",
    summary="部署 Python 项目",
    description="上传 Python 项目的 ZIP 包并部署 Docker 容器。"
)
async def deploy_python_project(
    file: UploadFile = File(..., title="ZIP 文件", description="上传要部署的 Python 项目压缩包"),
    project_id: str = Form(..., title="项目ID"),
    task_name: str = Form("Python 项目部署", title="任务名称"),
    trigger_type: str = Form("MANUAL", title="触发方式"),
    deploy_mechanism: str = Form("UPLOAD", title="部署方式"),
    dockercommand_content: str = Form(..., title="Docker命令"),
):
    try:
        # 1. 校验项目是否存在
        project = PROJECT_DATA_MANAGER.get_project(project_id)
        if project is None:
            return HttpResult[None](
                code=400,
                status="failed",
                msg=f"没有 id 为 {project_id} 的 Java 项目",
                data=None
            )
            
        # 2. 获取当前用户
        current_user = get_current_user()
        
        # 3. 保存上传文件到临时目录
        upload_file_path = save_uploaded_file(file)
        
        # 4. 提交部署任务
        task: DeployTask = DEPLOY_TASK_SERVICE.submit_task(
            project_id=project_id,
            task_name=task_name,
            trigger_type=trigger_type,
            deploy_mechanism=deploy_mechanism,
            upload_file_name=file.filename,
            upload_file_path=upload_file_path,
            build_image_name=project.get("docker_image_name"),
            build_image_tag=project.get("docker_image_tag"),
            container_name=project.get("container_name"),
            dockercommand_content=dockercommand_content,
            operator_id=current_user.get("id") if current_user else None,
            operator_name=current_user.get("nickname") if current_user else None,
        )
      
        return HttpResult[dict](
            code=200,
            status="success",
            msg="部署任务已提交",
            data={
                "task_id": task.id,
                "project_id": task.project_id
            }
        )

    except Exception as e:
        import traceback
        traceback.print_exc()
        return HttpResult[None](
            code=500,
            status="failed",
            msg=f"提交部署任务失败: {str(e)}",
            data=None
        )

@project_router.delete("/api/deploy-agent/project/python/delete/{id}", summary="删除 Python 项目")
async def delete_python_project(id: str):
    PROJECT_DATA_MANAGER.delete_project(id)
    return HttpResult[None](code=200, status="success", msg=None, data=None)