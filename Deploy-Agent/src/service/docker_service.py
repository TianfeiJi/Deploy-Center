import json
from typing import Any, Dict, List, Optional

from utils.docker_util import run_docker_command


class DockerService:
    DOCKER_PS_JSON_ARGS = ["ps", "-a", "--format", "{{json .}}"]

    @staticmethod
    def list_containers() -> List[Dict[str, Any]]:
        result = run_docker_command(DockerService.DOCKER_PS_JSON_ARGS)

        containers: List[Dict[str, Any]] = []
        for line in result.strip().split("\n"):
            if not line:
                continue
            containers.append(json.loads(line))

        return containers

    @staticmethod
    def get_container(container_name: str) -> Optional[Dict[str, Any]]:
        for container in DockerService.list_containers():
            if container.get("Names") == container_name:
                return container
        return None

    @staticmethod
    def get_container_status(container_name: str) -> Optional[str]:
        container = DockerService.get_container(container_name)
        if container is None:
            return None
        return container.get("Status")

    @staticmethod
    def get_container_ps_info(container_name: str) -> Optional[Dict[str, Any]]:
        result = run_docker_command([
            "ps", "-a",
            "--filter", f"name={container_name}",
            "--format", "{{json .}}"
        ])

        result = result.strip()
        if not result:
            return None

        return json.loads(result)

    @staticmethod
    def get_container_inspect_info(container_name: str) -> Optional[Dict[str, Any]]:
        result = run_docker_command(["inspect", container_name])

        inspect_list = json.loads(result)
        if not inspect_list:
            return None

        return inspect_list[0]

    @staticmethod
    def get_container_summary() -> Dict[str, int]:
        containers = DockerService.list_containers()

        running = 0
        exited = 0
        restarting = 0

        for container in containers:
            status = container.get("Status", "")

            if "Up" in status:
                running += 1
            elif "Exited" in status:
                exited += 1
            elif "Restarting" in status:
                restarting += 1

        return {
            "running": running,
            "exited": exited,
            "restarting": restarting,
            "total": len(containers),
        }

    @staticmethod
    def list_images() -> List[Dict[str, Any]]:
        result = run_docker_command(["images", "--format", "{{json .}}"])

        images: List[Dict[str, Any]] = []
        for line in result.strip().split("\n"):
            if not line:
                continue
            images.append(json.loads(line))

        return images

    @staticmethod
    def get_docker_info() -> Dict[str, Any]:
        result = run_docker_command(["info", "--format", "{{json .}}"])
        return json.loads(result)

    @staticmethod
    def get_container_logs(
        container_name: str,
        tail: int = 50,
        timestamps: bool = False,
        since: Optional[str] = None,
        until: Optional[str] = None,
    ) -> Dict[str, Any]:
        docker_command = ["logs", f"--tail={tail}"]

        if timestamps:
            docker_command.append("--timestamps")

        if since:
            docker_command.extend(["--since", since])

        if until:
            docker_command.extend(["--until", until])

        docker_command.append(container_name)

        logs_text = run_docker_command(docker_command)

        return {
            "container_name": container_name,
            "tail": tail,
            "timestamps": timestamps,
            "since": since,
            "until": until,
            "logs": logs_text,
        }

    @staticmethod
    def start_container(container_name: str) -> str:
        return run_docker_command(["start", container_name])

    @staticmethod
    def stop_container(container_name: str) -> str:
        return run_docker_command(["stop", container_name])

    @staticmethod
    def restart_container(container_name: str) -> str:
        return run_docker_command(["restart", container_name])
    
    @staticmethod
    def get_container_stats(container_name: str) -> Optional[Dict[str, Any]]:
        """
        获取指定容器资源使用情况（单次快照）
        """
        result = run_docker_command(
            ["stats", "--no-stream", "--format", "{{json .}}", container_name],
            log_command=False
        )

        result = result.strip()
        if not result:
            return None

        return json.loads(result)