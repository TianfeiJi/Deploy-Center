import subprocess
from loguru import logger


# Docker命令执行路径，需根据宿主机挂载配置一致
DOCKER_PATH = "/usr/bin/docker"

# 安全执行Docker命令的辅助函数
def run_docker_command(args: list) -> str:
    command = [DOCKER_PATH] + args
    
    logger.debug(f"[docker] exec: {' '.join(command)}")

    try:
        result = subprocess.run(
            command,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            check=True
        )

        logger.debug(f"[docker] success: {result.stdout.strip()}")
        return result.stdout

    except subprocess.CalledProcessError as e:
        logger.error(f"[docker] failed: {' '.join(command)} -> {e.stdout}")
        raise