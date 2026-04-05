from typing import Any
import subprocess

from fastapi import APIRouter, Query
from loguru import logger

from models.common.http_result import HttpResult
from models.dto.docker_container_logs_request import DockerContainerLogsRequest
from service.docker_service import DockerService

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
        container_status = DockerService.get_container_status(container_name)

        if container_status is None:
            return HttpResult.ok(data={
                "container_name": container_name,
                "container_status": "Awaiting Deployment",
            }, msg="容器未找到")

        return HttpResult.ok(data={
            "container_name": container_name,
            "container_status": container_status,
        })

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
        container_info = DockerService.get_container_ps_info(container_name)

        if container_info is None:
            return HttpResult.fail(code=404, msg="容器不存在")

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
        inspect_info = DockerService.get_container_inspect_info(container_name)

        if inspect_info is None:
            return HttpResult.fail(code=404, msg="容器不存在")

        return HttpResult.ok(data=inspect_info)

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
        summary = DockerService.get_container_summary()
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
        containers = DockerService.list_containers()
        return HttpResult.ok(data=containers)

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
        images = DockerService.list_images()
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
        info = DockerService.get_docker_info()
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
        logs_data = DockerService.get_container_logs(
            container_name=request.container_name,
            tail=request.tail,
            timestamps=request.timestamps,
            since=request.since,
            until=request.until,
        )

        return HttpResult.ok(data=logs_data)

    except subprocess.CalledProcessError as e:
        logger.error(f"查询容器日志失败: {e}")
        return HttpResult.fail(msg=str(e))
    except Exception as e:
        logger.error(f"查询容器日志异常: {e}")
        return HttpResult.fail(msg=str(e))


@docker_router.post(
    "/api/deploy-agent/docker/containers/start",
    summary="启动容器"
)
async def start_container(container_name: str = Query(..., description="容器名称")):
    try:
        status = DockerService.get_container_status(container_name)

        if status is None:
            return HttpResult.fail(code=404, msg="容器不存在")

        if status.startswith("Up"):
            return HttpResult.fail(msg="容器已在运行")

        output = DockerService.start_container(container_name)
        return HttpResult.ok(data=output)

    except subprocess.CalledProcessError as e:
        logger.error(f"启动容器失败: {e}")
        return HttpResult.fail(msg=str(e))
    except Exception as e:
        logger.error(f"启动容器异常: {e}")
        return HttpResult.fail(msg=str(e))


@docker_router.post(
    "/api/deploy-agent/docker/containers/stop",
    summary="停止容器"
)
async def stop_container(container_name: str = Query(..., description="容器名称")):
    try:
        status = DockerService.get_container_status(container_name)

        if status is None:
            return HttpResult.fail(code=404, msg="容器不存在")

        if not status.startswith("Up"):
            return HttpResult.fail(msg="容器未在运行")

        output = DockerService.stop_container(container_name)
        return HttpResult.ok(data=output)

    except subprocess.CalledProcessError as e:
        logger.error(f"停止容器失败: {e}")
        return HttpResult.fail(msg=str(e))
    except Exception as e:
        logger.error(f"停止容器异常: {e}")
        return HttpResult.fail(msg=str(e))


@docker_router.post(
    "/api/deploy-agent/docker/containers/restart",
    summary="重启容器"
)
async def restart_container(container_name: str = Query(..., description="容器名称")):
    try:
        status = DockerService.get_container_status(container_name)

        if status is None:
            return HttpResult.fail(code=404, msg="容器不存在")

        if not status.startswith("Up"):
            return HttpResult.fail(msg="容器未在运行，无法重启")

        output = DockerService.restart_container(container_name)
        return HttpResult.ok(data=output)

    except subprocess.CalledProcessError as e:
        logger.error(f"重启容器失败: {e}")
        return HttpResult.fail(msg=str(e))
    except Exception as e:
        logger.error(f"重启容器异常: {e}")
        return HttpResult.fail(msg=str(e))

@docker_router.get(
    "/api/deploy-agent/docker/containers/stats",
    summary="获取指定容器资源监控信息"
)
async def get_docker_container_stats(
    container_name: str = Query(..., description="容器名称")
):
    try:
        stats = DockerService.get_container_stats(container_name)

        if stats is None:
            return HttpResult.fail(code=404, msg="容器不存在或未运行")

        return HttpResult.ok(data=stats)

    except subprocess.CalledProcessError as e:
        logger.error(f"获取容器 stats 失败: {e}")
        return HttpResult.fail(msg=str(e))

    except Exception as e:
        logger.error(f"获取容器 stats 异常: {e}")
        return HttpResult.fail(msg=str(e))