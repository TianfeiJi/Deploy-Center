from datetime import datetime, timezone
import subprocess
import json
from fastapi import APIRouter, Query
from models.common.http_result import HttpResult
from utils.docker_util import run_docker_command
from loguru import logger

# 初始化Router和Logger
docker_router = APIRouter()

@docker_router.get("/api/deploy-agent/docker/container-status", summary="获取指定容器原始运行状态", description="根据容器名称返回 Docker 原生状态描述")
async def get_container_status(container_name: str = Query(..., description="容器名称")):
    check_time = datetime.now(timezone.utc).isoformat()

    try:
        result = run_docker_command(["ps", "-a", "--format", "{{json .}}"])

        for line in result.strip().split("\n"):
            info = json.loads(line)
            name = info.get("Names", "")
            status_str = info.get("Status", "")

            if container_name == name:
                return HttpResult(code=200, status="success", msg=None, data={
                    "container_name": name,
                    "container_status": status_str,
                    "check_time": check_time
                })

        return HttpResult(code=200, status="success", msg="容器未找到", data={
            "container_name": container_name,
            "container_status": "Awaiting Deployment",
            "check_time": check_time
        })
    except subprocess.CalledProcessError as e:
        logger.error(f"Docker命令执行失败: {e}")
        return HttpResult(code=500, status="failed", msg=str(e), data=None)
    except Exception as e:
        logger.error(f"异常: {e}")
        return HttpResult(code=500, status="failed", msg=str(e), data=None)

@docker_router.get("/api/deploy-agent/docker/container-summary", summary="获取Docker容器状态汇总")
async def get_docker_container_summary():
    """
    获取Docker容器状态概览（运行中、已停止、异常）
    """
    try:
        result = run_docker_command(["ps", "-a", "--format", "{{json .}}"])

        running = 0
        exited = 0
        restarting = 0
        containers = []

        for line in result.strip().split("\n"):
            info = json.loads(line)
            status = info.get("Status", "")

            if "Up" in status:
                running += 1
            elif "Exited" in status:
                exited += 1
            elif "Restarting" in status:
                restarting += 1

            containers.append(info)

        summary = {
            "running": running,
            "exited": exited,
            "restarting": restarting,
            "total": len(containers),
        }

        return HttpResult[dict](code=200, status="success", msg=None, data=summary)
    except Exception as e:
        logger.error(f"获取容器状态汇总失败: {e}")
        return HttpResult[dict](code=500, status="failed", msg=str(e), data=None)


@docker_router.get("/api/deploy-agent/docker/containers", summary="列出所有容器详细信息")
async def list_all_containers():
    """
    获取所有容器的详细信息列表（简化版）
    """
    try:
        result = run_docker_command(["ps", "-a", "--format", "{{json .}}"])

        containers = [json.loads(line) for line in result.strip().split("\n") if line]

        return HttpResult[list](code=200, status="success", msg=None, data=containers)
    except Exception as e:
        logger.error(f"列出容器失败: {e}")
        return HttpResult[list](code=500, status="failed", msg=str(e), data=None)


@docker_router.get("/api/deploy-agent/docker/images", summary="列出本地镜像")
async def list_docker_images():
    """
    获取本地所有Docker镜像信息
    """
    try:
        result = run_docker_command(["images", "--format", "{{json .}}"])
        images = [json.loads(line) for line in result.strip().split("\n") if line]

        return HttpResult[list](code=200, status="success", msg=None, data=images)
    except Exception as e:
        logger.error(f"列出镜像失败: {e}")
        return HttpResult[list](code=500, status="failed", msg=str(e), data=None)


@docker_router.get("/api/deploy-agent/docker/info", summary="获取Docker引擎信息")
async def get_docker_info():
    """
    获取Docker基本信息
    """
    try:
        result = run_docker_command(["info", "--format", "{{json .}}"])
        info = json.loads(result)

        return HttpResult[dict](code=200, status="success", msg=None, data=info)
    except Exception as e:
        logger.error(f"获取Docker信息失败: {e}")
        return HttpResult[dict](code=500, status="failed", msg=str(e), data=None)


@docker_router.post("/api/deploy-agent/docker/run", summary="运行Docker命令（受限）")
async def run_safe_docker_command(command: str):
    """
    受限地运行单条Docker命令（只允许固定白名单命令）
    """
    allowed_commands = {"ps", "images", "info", "version"}
    if command not in allowed_commands:
        return HttpResult[None](code=400, status="failed", msg="非法命令", data=None)

    try:
        output = run_docker_command([command])
        return HttpResult[str](code=200, status="success", msg=None, data=output)
    except Exception as e:
        logger.error(f"执行Docker命令失败: {e}")
        return HttpResult[str](code=500, status="failed", msg=str(e), data=None)
