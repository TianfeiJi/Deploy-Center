"""
@File           : inspect_routes.py
@Author         : Tianfei Ji
@Description    : 提供当前 Deploy-Agent 的元信息接口。
"""
import platform
import socket
import subprocess
from datetime import datetime
from fastapi import APIRouter
from models.common.http_result import HttpResult
from config.log_config import get_logger
from config.version import AGENT_VERSION

inspect_router = APIRouter()
logger = get_logger()

@inspect_router.get("/api/deploy-agent/inspect/info", summary="获取 Agent 汇总信息")
async def get_info():
    """
    获取 Deploy-Agent 自身的基本信息汇总：
        - Agent 版本
        - 主机名、操作系统、CPU 架构
        - Python 版本、Docker 版本
        - 当前时间（代表活跃状态）
    """
    try:
        try:
            docker_version = subprocess.check_output(["docker", "--version"], encoding="utf-8").strip()
        except Exception as e:
            docker_version = f"无法获取: {e}"

        data = {
            "status": "healthy",
            "agent_version": AGENT_VERSION,
            "hostname": socket.gethostname(),
            "os": platform.system(),
            "arch": platform.machine(),
            "python_version": platform.python_version(),
            "docker_version": docker_version,
            "fetched_at": datetime.now().isoformat()
        }
        return HttpResult[dict](code=200, status="success", msg=None, data=data)
    except Exception as e:
        logger.error(f"获取 Agent 信息失败: {e}")
        return HttpResult[dict](code=500, status="failed", msg=str(e), data=None)

@inspect_router.get("/api/deploy-agent/health", summary="健康检查接口")
async def health_check():
    """
    返回当前 Agent 健康状态。
    """
    return HttpResult[str](code=200, status="success", msg=None, data="healthy")

@inspect_router.get("/api/deploy-agent/inspect/agent-version", summary="获取 Agent 版本")
async def get_version():
    """
    返回当前 Agent 的版本信息。
    """
    return HttpResult[str](code=200, status="success", msg=None, data=AGENT_VERSION)