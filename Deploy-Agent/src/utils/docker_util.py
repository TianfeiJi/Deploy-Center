import subprocess
from typing import List


# Docker命令执行路径，需根据宿主机挂载配置一致
DOCKER_PATH = "/usr/bin/docker"

# 安全执行Docker命令的辅助函数
def run_docker_command(args: List[str]) -> str:
    command = [DOCKER_PATH] + args
    result = subprocess.run(
        command,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        check=True
    )
    return result.stdout