import json
from utils.jwt_util import JWTUtil
from fastapi import APIRouter, File, Form, HTTPException, Query, Request, UploadFile
import httpx
from models.entity.agent import Agent
from manager.user_data_manager import UserDataManager
from manager.agent_data_manager import AgentDataManager
from typing import Any, Dict, List, Optional
from models.common.http_result import HttpResult
from config.log_config import get_logger

agent_router = APIRouter()
logger = get_logger()


@agent_router.get("/api/deploy-center/agent/list", summary="获取Agent列表")
async def get_agent_list():
    try:
        agent_data_manager = AgentDataManager.get_instance()
        agent_list: List[Agent] = agent_data_manager.list_agents()
        return HttpResult[List[Agent]](code=200, status="success", msg=None, data=[agent for agent in agent_list])
    except Exception as e:
        return HttpResult[None](code=500, status="failed", msg=str(e), data=None)


@agent_router.get("/api/deploy-center/agent/{agent_id}", summary="获取Agent详情")
async def get_agent(agent_id: int):
    try:
        agent_data_manager = AgentDataManager.get_instance()
        agent = agent_data_manager.get_agent(agent_id)
        if not agent:
            raise HTTPException(status_code=404, detail="Agent not found")
        return HttpResult(code=200, status="success", msg=None, data=agent)
    except Exception as e:
        return HttpResult(code=500, status="failed", msg=str(e), data=None)


@agent_router.post("/api/deploy-center/agent/register", summary="注册Agent")
async def agent_register(agent_data: dict):
    try:
        # To enhance security, call an Agent-side API
        # TODO：为提升注册安全性，应在注册前调用 Agent 自身的验证接口，确认其允许被当前 Center 注册
        # 若验证通过 -> 执行注册逻辑
        # 若验证失败 -> 中止注册并返回失败信息
        agent_data_manager = AgentDataManager.get_instance()
        agent = agent_data_manager.create_agent(agent_data)
        return HttpResult[dict](code=200, status="success", msg=None, data=agent)
    except Exception as e:
        return HttpResult[dict](code=500, status="failed", msg=str(e), data=None)


@agent_router.put("/api/deploy-center/agent/{agent_id}", summary="更新Agent信息")
async def update_agent(agent_id: int, updated_info: dict):
    try:
        agent_data_manager = AgentDataManager.get_instance()
        agent_data_manager.update_agent(agent_id, updated_info)
        return HttpResult[dict](code=200, status="success", msg=None, data=None)
    except ValueError as ve:
        return HttpResult[dict](code=404, status="failed", msg=str(ve), data=None)
    except Exception as e:
        return HttpResult[dict](code=500, status="failed", msg=str(e), data=None)


@agent_router.delete("/api/deploy-center/agent/{agent_id}", summary="删除Agent")
async def delete_agent(agent_id: int):
    try:
        agent_data_manager = AgentDataManager.get_instance()
        agent_data_manager.delete_agent(agent_id)
        return HttpResult[dict](code=200, status="success", msg=None, data=None)
    except Exception as e:
        return HttpResult[dict](code=500, status="failed", msg=str(e), data=None)


"""
TODO: 
1. 发请求的时候，携带userId和userName过去。拿到结果的时候，设置userName再返回出去
"""
@agent_router.post("/api/deploy-center/agent/{agent_id}/call-api", summary="远程调用Agent API (支持文件上传)")
async def call_agent_api(agent_id: int, api_path: str, method: str, request: Request):
    """
    转发请求到指定 Agent 服务

    本函数实现请求的透明转发，将接收到的请求（包括 headers、body、HTTP 方法等）完整转发到指定的 Agent，属于反向代理 / 请求转发的一种实现。

    另注：由于直接对headers等直接进行完整转发，所以Token也会转发到Agent，以此实现认证信息的传递。

    Args:
        agent_id (int): 目标 Agent 的唯一标识 ID。
        api_path (str): 需要调用的 Agent API 路径，例如 `/api/deploy-agent/project/java/deploy`。
        method (str): 调用目标 Agent API 时所使用的 HTTP 请求方法，如 GET、POST、PUT、DELETE 等，具体取决于 api_path 所需的请求方式。
        request (Request): FastAPI 提供的原始请求对象，包含 body、headers 等。

    Returns:
        dict: 标准返回结构，包括 code、status、msg、data 字段，转发成功返回 Agent API 响应数据，失败时返回错误信息。

    Raises:
        HTTPException: 如果根据 agent_id 找不到对应 Agent，抛出 404 异常。
        Exception: 其他请求过程中遇到的异常均捕获并返回 500 错误信息。

    流程说明:
        1. 根据 agent_id 获取 Agent 信息（IP、端口），如果不存在则返回 404。
        2. 拼接目标 Agent API 的完整 URL。
        3. 获取当前请求的 headers 和 body，保持 multipart 文件、JSON 等完整性。
        4. 移除 headers 中的 'host' 字段，避免代理请求时产生冲突。
        5. 使用 httpx.AsyncClient 发送原始请求到 Agent，设置 30 秒超时。
        6. 捕获 Agent 的响应并返回，若响应失败或异常，记录日志并返回 500。

    典型用途:
        - 多 Agent 服务部署，Center 作为统一入口。
        - 支持文件上传、JSON 请求等复杂场景。
        - 简单实现 API 网关/反向代理模式。
    """
    try:
        agent_data_manager = AgentDataManager.get_instance()
        agent = agent_data_manager.get_agent(agent_id)
        if not agent:
            raise HTTPException(status_code=404, detail="Agent not found")

        url = f"{agent.service_url}{api_path}"
        logger.info(f"调用Agent API: {url}, 方法: {method}")

        # 获取原始 body 和 headers
        body = await request.body()
        headers = dict(request.headers)

        # 需要清除 host，避免影响
        headers.pop('host', None)

        # 获取token
        token = request.headers.get("Authorization").replace("Bearer ", "")
        user_info = JWTUtil.get_user_from_token(token)
        user_id = user_info.get("user_id")
        user_data_manager = UserDataManager.get_instance()
        user = user_data_manager.get_user(user_id)
        # 将用户对象序列化为 JSON 字符串
        user_json = json.dumps(user.model_dump(), default=str)

        # 将user_json添加到 headers 中
        headers["X-User"] = user_json

        async with httpx.AsyncClient(timeout=30) as client:
            response = await client.request(
                method=method.upper(),
                url=url,
                content=body,
                headers=headers
            )

            logger.info(f"Agent API返回: {response.status_code}, {response.text}")
            response.raise_for_status()
            return {"code": 200, "status": "success", "msg": "Agent API调用成功", "data": response.json()}
    except httpx.RequestError as e:
        logger.error(f"请求Agent失败: {e}")
        return {"code": 500, "status": "failed", "msg": f"Request error: {e}", "data": None}
    except Exception as e:
        logger.error(f"调用Agent API: {url} 出错: {e}")
        return {"code": 500, "status": "failed", "msg": str(e), "data": None}
