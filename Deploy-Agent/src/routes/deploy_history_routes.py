from typing import List
from fastapi import APIRouter
from manager.project_data_manager import ProjectDataManager
from manager.deploy_history_data_manager import DeployHistoryDataManager
from models.entity.deploy_history import DeployHistory
from models.vo.deploy_history_vo import DeployHistoryVo
from models.common.http_result import HttpResult


deploy_history_router = APIRouter()
deploy_history_data_manager = DeployHistoryDataManager.get_instance()
project_data_manager = ProjectDataManager.get_instance()


# 获取部署历史列表
@deploy_history_router.get("/api/deploy-agent/deploy-history/list", summary="获取部署历史列表")
async def get_deploy_history_list():
    deploy_history_list: List[DeployHistory] = deploy_history_data_manager.list_deploy_historys()
    # 转换为 DeployHistoryVo 并设置 project_code
    vo_list = []
    for deploy_history in deploy_history_list:
        project = project_data_manager.get_project(deploy_history.project_id)
        if project is None:
            continue
        # 创建 DeployHistoryVo 并复制属性
        vo = DeployHistoryVo(
            id=deploy_history.id,
            project_id = deploy_history.project_id,
            project_code = project.get('project_code'),
            project_name = project.get('project_name'),
            status = deploy_history.status,
            created_at = deploy_history.created_at,
            created_by = deploy_history.created_by,
            updated_at = deploy_history.updated_at,
            updated_by = deploy_history.updated_by
        )
        vo_list.append(vo)
        
    # 按 created_at 倒序排序
    vo_list.sort(key=lambda x: x.created_at, reverse=True)
    return HttpResult(code=200, status="success", msg=None, data=vo_list)