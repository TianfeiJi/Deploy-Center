from typing import List, Optional

from fastapi import APIRouter, Query

from models.entity.deploy_task import DeployTask
from models.common.http_result import HttpResult
from manager import DEPLOY_TASK_DATA_MANAGER, PROJECT_DATA_MANAGER
from utils.user_context import get_current_user
from loguru import logger


deploy_task_router = APIRouter()


@deploy_task_router.get("/api/deploy-agent/deploy-task/list", summary="获取部署任务列表")
async def get_deploy_task_list(
    project_id: Optional[str] = Query(None, title="项目ID"),
):
    """
    获取部署任务列表（按创建时间倒序）。

    支持参数：
        - project_id: 按项目过滤

    返回字段：
        - DeployTask 原始字段
        - project_code
        - project_name
    """
    task_list: List[DeployTask] = DEPLOY_TASK_DATA_MANAGER.list_deploy_tasks()

    result = []

    for task in task_list:
        if project_id and task.project_id != project_id:
            continue

        project = PROJECT_DATA_MANAGER.get_project(task.project_id)
        if project is None:
            continue

        item = {
            **task.model_dump(),
            "project_code": project.get("project_code"),
            "project_name": project.get("project_name"),
        }
        result.append(item)

    result.sort(
        key=lambda x: x.get("created_at") or "",
        reverse=True
    )

    return HttpResult.ok()

# TODO：要做权限校验
@deploy_task_router.delete("/api/deploy-agent/deploy-task/delete/{id}", summary="删除部署任务")
async def delete_deploy_task(id: str):
    """
    删除指定部署任务。
    """
    task = DEPLOY_TASK_DATA_MANAGER.get_deploy_task(id)
    if task is None:
        return HttpResult.fail(code=404, msg=f"没有找到 id 为 {id} 的部署任务")
        
    current_user = get_current_user()
    
    allowed_status = {"SUCCESS", "FAILED", "CANCELLED"}
    if task.status not in allowed_status:
        return HttpResult.fail(code=400, msg=f"当前任务状态为 {task.status}，不允许删除")

    DEPLOY_TASK_DATA_MANAGER.delete_deploy_task(id)
    
    logger.info(
        f"删除部署任务: task_id={id}, project_id={task.project_id}, "
        f"operator={current_user.get('nickname') if current_user else None}"
    )
    
    return HttpResult.ok(msg="删除部署任务成功")