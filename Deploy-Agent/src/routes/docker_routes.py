from typing import Any, Dict, List
import subprocess
import json

from fastapi import APIRouter, Query
from loguru import logger

from models.common.http_result import HttpResult
from utils.docker_util import run_docker_command
from models.dto.docker_container_logs_request import DockerContainerLogsRequest

docker_router = APIRouter()


@docker_router.get(
    "/api/deploy-agent/docker/containers/status",
    summary="获取指定容器运行状态",
    description="根据容器名称返回 Docker 原生状态描述"
)
async def get_docker_container_status(
    container_name: str = Query(..., description="容器名称")
):
    try:
        docker_ps_output = run_docker_command([
            "ps", "-a", "--format", "{{json .}}"
        ])

        for line in docker_ps_output.strip().split("\n"):
            if not line:
                continue

            container_record = json.loads(line)

            current_container_name = container_record.get("Names", "")
            current_container_status = container_record.get("Status", "")

            if current_container_name == container_name:
                return HttpResult[dict](
                    code=200,
                    msg=None,
                    data={
                        "container_name": current_container_name,
                        "container_status": current_container_status,
                    }
                )

        return HttpResult[dict](
            code=200,
            msg="容器未找到",
            data={
                "container_name": container_name,
                "container_status": "Awaiting Deployment",
            }
        )

    except subprocess.CalledProcessError as e:
        logger.error(f"查询容器状态失败: {e}")
        return HttpResult.fail(msg=str(e))

    except Exception as e:
        logger.error(f"查询容器状态异常: {e}")
        return HttpResult.fail(msg=str(e))

@docker_router.get(
    "/api/deploy-agent/docker/containers/info",
    summary="获取单个容器 ps -a 信息"
)
async def get_docker_container_info(
    container_name: str = Query(..., description="容器名称")
):
    """
    查询单个容器的 docker ps 视图信息。
    """
    try:
        result = run_docker_command([
            "ps", "-a",
            "--filter", f"name={container_name}",
            "--format", "{{json .}}"
        ])

        result = result.strip()
        if not result:
            return HttpResult.fail(code=404, msg="容器不存在")
        
        container_info = json.loads(result)

        return HttpResult.ok(data=container_info)

    except subprocess.CalledProcessError as e:
        logger.error(f"查询容器信息失败: {e}")
        return HttpResult.fail(msg=str(e))
    except Exception as e:
        logger.error(f"查询容器信息异常: {e}")
        return HttpResult.fail(msg=str(e))

@docker_router.get(
    "/api/deploy-agent/docker/containers/inspect",
    summary="获取单个容器 inspect 详细信息"
)
async def get_docker_container_inspect(
    container_name: str = Query(..., description="容器名称")
):
    """
    查询单个容器的 docker inspect 原始信息。
    适合高级调试、挂载、网络、环境变量等详细信息分析。
    """
    try:
        result = run_docker_command(["inspect", container_name])

        inspect_list = json.loads(result)
        if not inspect_list:
            return HttpResult.fail(code=404, msg="容器不存在")

        return HttpResult.ok(data=inspect_list[0])

    except subprocess.CalledProcessError as e:
        logger.error(f"查询容器 inspect 失败: {e}")
        return HttpResult.fail(msg=str(e))
    except Exception as e:
        logger.error(f"查询容器 inspect 异常: {e}")
        return HttpResult.fail(msg=str(e))


@docker_router.get(
    "/api/deploy-agent/docker/containers/summary",
    summary="获取 Docker 容器状态汇总"
)
async def get_docker_container_summary():
    """
    获取 Docker 容器状态概览。
    """
    try:
        result = run_docker_command(["ps", "-a", "--format", "{{json .}}"])

        running = 0
        exited = 0
        restarting = 0
        containers: List[Dict[str, Any]] = []

        for line in result.strip().split("\n"):
            if not line:
                continue

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

        return HttpResult.ok(data=summary)
    except Exception as e:
        logger.error(f"获取容器状态汇总失败: {e}")
        return HttpResult.fail(msg=str(e))


@docker_router.get(
    "/api/deploy-agent/docker/containers",
    summary="列出所有容器信息"
)
async def list_docker_containers():
    """
    获取所有容器的 docker ps 视图信息列表。
    """
    try:
        result = run_docker_command(["ps", "-a", "--format", "{{json .}}"])

        containers = [
            json.loads(line)
            for line in result.strip().split("\n")
            if line
        ]

        return HttpResult[list](data=containers)
    except Exception as e:
        logger.error(f"列出容器失败: {e}")
        return HttpResult.fail(msg=str(e))


@docker_router.get(
    "/api/deploy-agent/docker/images",
    summary="列出本地镜像"
)
async def list_docker_images():
    """
    获取本地所有 Docker 镜像信息。
    """
    try:
        result = run_docker_command(["images", "--format", "{{json .}}"])

        images = [
            json.loads(line)
            for line in result.strip().split("\n")
            if line
        ]

        return HttpResult.ok(data=images)
    except Exception as e:
        logger.error(f"列出镜像失败: {e}")
        return HttpResult.fail(msg=str(e))


@docker_router.get(
    "/api/deploy-agent/docker/info",
    summary="获取 Docker 引擎信息"
)
async def get_docker_info():
    """
    获取 Docker 基本信息。
    """
    try:
        result = run_docker_command(["info", "--format", "{{json .}}"])
        info = json.loads(result)

        return HttpResult.ok(data=info)
    except Exception as e:
        logger.error(f"获取 Docker 信息失败: {e}")
        return HttpResult.fail(msg=str(e))

@docker_router.post(
    "/api/deploy-agent/docker/containers/logs",
    summary="查询指定容器日志"
)
async def get_docker_container_logs(request: DockerContainerLogsRequest):
    try:
        docker_command = ["logs", f"--tail={request.tail}"]

        if request.timestamps:
            docker_command.append("--timestamps")

        if request.since:
            docker_command.extend(["--since", request.since])

        if request.until:
            docker_command.extend(["--until", request.until])

        docker_command.append(request.container_name)

        logs_text = run_docker_command(docker_command)

        return HttpResult.ok(data={
                "container_name": request.container_name,
                "tail": request.tail,
                "timestamps": request.timestamps,
                "since": request.since,
                "until": request.until,
                "logs": logs_text,
            })

    except subprocess.CalledProcessError as e:
        logger.error(f"查询容器日志失败: {e}")
        return HttpResult.fail(msg=str(e))

    except Exception as e:
        logger.error(f"查询容器日志异常: {e}")
        return HttpResult.fail(msg=str(e))