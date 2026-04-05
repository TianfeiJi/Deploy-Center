import subprocess
from typing import List
from loguru import logger


# Docker命令执行路径，需根据宿主机挂载配置一致
DOCKER_PATH = "/usr/bin/docker"

# 安全执行Docker命令的辅助函数
def run_docker_command(args: List[str], log_command: bool = True) -> str:
    command = [DOCKER_PATH] + args

    if log_command:
        logger.debug(f"[docker] exec: {' '.join(command)}")

    try:
        result = subprocess.run(
            command,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            check=True
        )

        if log_command:
            logger.debug(f"[docker] success: {result.stdout.strip()}")

        return result.stdout

    except subprocess.CalledProcessError as e:
        if log_command:
            logger.error(f"[docker] failed: {' '.join(command)} -> {e.stdout}")
        raise