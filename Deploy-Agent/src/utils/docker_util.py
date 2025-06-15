import subprocess
from config.log_config import get_logger

logger = get_logger()



# Docker命令执行路径，需根据宿主机挂载配置一致
DOCKER_PATH = "/usr/bin/docker"

# 安全执行Docker命令的辅助函数
def run_docker_command(args: list) -> str:
    command = [DOCKER_PATH] + args
    logger.info(f"执行Docker命令：{' '.join(command)}")
    output = subprocess.check_output(command, encoding="utf-8")
    return output