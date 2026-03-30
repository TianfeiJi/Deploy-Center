import re


class DeployValidationError(Exception):
    pass


class DeployValidator:

    @staticmethod
    def validate_dockerfile(content: str):
        """
        校验 Dockerfile 内容
        """
        if not content or not content.strip():
            raise DeployValidationError("Dockerfile 不能为空")

        # 必须包含 FROM
        if not re.search(r"^\s*FROM\s+", content, re.IGNORECASE | re.MULTILINE):
            raise DeployValidationError("Dockerfile 必须包含 FROM 指令")

        # 禁止危险模式
        dangerous_patterns = [
            r"--privileged",
            r"/var/run/docker.sock",
            r"docker\s+run"
        ]

        for pattern in dangerous_patterns:
            if re.search(pattern, content, re.IGNORECASE):
                raise DeployValidationError(f"Dockerfile 包含危险操作: {pattern}")

        return True

    @staticmethod
    def validate_docker_command(command: str):
        """
        校验 docker run 命令
        """
        if not command or not command.strip():
            raise DeployValidationError("Docker 启动命令不能为空")

        cmd = command.strip()

        # 必须以 docker run 开头
        if not cmd.startswith("docker run"):
            raise DeployValidationError("仅允许 docker run 命令")

        # 禁止多命令执行
        forbidden_symbols = [";", "&&", "||", "|", "`", "$(", ">", "<"]
        for symbol in forbidden_symbols:
            if symbol in cmd:
                raise DeployValidationError(f"检测到非法符号: {symbol}")

        # 禁止危险命令关键词
        forbidden_keywords = [
            "rm ",
            "shutdown",
            "reboot",
            "mkfs",
            "dd ",
            "chmod 777 /",
            "chown root",
        ]

        for keyword in forbidden_keywords:
            if keyword in cmd.lower():
                raise DeployValidationError(f"检测到危险命令: {keyword}")

        # 禁止挂 docker.sock
        if "/var/run/docker.sock" in cmd:
            raise DeployValidationError("禁止挂载 docker.sock")

        # 禁止挂载根目录
        if re.search(r"-v\s*/\s*:", cmd):
            raise DeployValidationError("禁止挂载宿主机根目录")

        return True