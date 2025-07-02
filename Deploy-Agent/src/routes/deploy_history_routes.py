from typing import List
from fastapi import APIRouter
from models.entity.deploy_history import DeployHistory
from models.vo.deploy_history_vo import DeployHistoryVo
from models.common.http_result import HttpResult
from manager import DEPLOY_HISTORY_DATA_MANAGER, PROJECT_DATA_MANAGER

deploy_history_router = APIRouter()

# 获取部署历史列表
@deploy_history_router.get("/api/deploy-agent/deploy-history/list", summary="获取部署历史列表")
async def get_deploy_history_list():
    deploy_history_list: List[DeployHistory] = DEPLOY_HISTORY_DATA_MANAGER.list_deploy_historys()
    # 转换为 DeployHistoryVo 并设置 project_code
    vo_list = []
    for deploy_history in deploy_history_list:
        project = PROJECT_DATA_MANAGER.get_project(deploy_history.project_id)
        if project is None:
            continue
        # 创建 DeployHistoryVo 并复制属性
        vo = DeployHistoryVo(
            **deploy_history.model_dump(),
            project_code = project.get('project_code'),
            project_name = project.get('project_name'),
        )
        vo_list.append(vo)
        
    # 按 created_at 倒序排序
    vo_list.sort(key=lambda x: x.created_at, reverse=True)
    return HttpResult(code=200, status="success", msg=None, data=vo_list)