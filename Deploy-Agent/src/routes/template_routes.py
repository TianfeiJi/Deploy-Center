from fastapi import APIRouter, Query
from typing import Dict, Optional
from models.common.http_result import HttpResult
from loguru import logger
from manager import TEMPLATE_MANAGER

template_router = APIRouter()

@template_router.get("/api/deploy-agent/template/list", summary="获取所有模板列表")
async def get_template_list(template_type: Optional[str] = Query(None, description="模板类型（可选）")):
    try:
        template_list = TEMPLATE_MANAGER.list_templates()
        if template_type:
            template_list = [
                tpl for tpl in template_list
                if tpl.get("template_type") == template_type
            ]

        return HttpResult.ok(data=template_list)
    except Exception as e:
        logger.error(f"获取模板列表失败: {e}")
        return HttpResult.fail(msg=str(e))

@template_router.get("/api/deploy-agent/template/{template_id}", summary="获取模板元数据")
async def get_template(template_id: str):
    try:
        template = TEMPLATE_MANAGER.get_template(template_id)
        if template is None:
            return HttpResult.fail(code=404, msg="Template not found")
        return HttpResult.ok(data=template)
    except Exception as e:
        logger.error(f"获取模板失败: {e}")
        return HttpResult.fail(msg=str(e))

@template_router.get("/api/deploy-agent/template/content/{template_id}", summary="获取模板文件内容")
async def get_template_content(template_id: str):
    try:
        content = TEMPLATE_MANAGER.get_template_content(template_id)
        return HttpResult.ok(data={"content": content})
    except Exception as e:
        logger.error(f"获取模板内容失败: {e}")
        return HttpResult.fail(msg=str(e))

@template_router.post("/api/deploy-agent/template", summary="创建新模板")
async def create_template(template_data: Dict):
    try:
        new_template = TEMPLATE_MANAGER.create_template(template_data)
        return HttpResult.ok(data=new_template)
    except Exception as e:
        logger.error(f"创建模板失败: {e}")
        return HttpResult.fail(msg=str(e))

@template_router.put("/api/deploy-agent/template/{template_id}", summary="更新模板")
async def update_template(template_id: str, updated_data: Dict):
    try:
        TEMPLATE_MANAGER.update_template(template_id, updated_data)
        return HttpResult.ok()
    except Exception as e:
        logger.error(f"更新模板失败: {e}")
        return HttpResult.fail(msg=str(e))

@template_router.delete("/api/deploy-agent/template/{template_id}", summary="删除模板")
async def delete_template(template_id: str):
    try:
        TEMPLATE_MANAGER.delete_template(template_id)
        return HttpResult.ok()
    except Exception as e:
        logger.error(f"删除模板失败: {e}")
        return HttpResult.fail(msg=str(e))
