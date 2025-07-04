from fastapi import Request, status
from starlette.middleware.base import BaseHTTPMiddleware
from typing import Callable, List
import ipaddress
from models.common.http_result import HttpResult
from loguru import logger

from manager import SYSTEM_CONFIG_DATA_MANAGER


def ip_in_allow_list(client_ip: str, allow_list: List[str]) -> bool:
    """
    判断客户端 IP 是否在允许的访问列表中。
    支持三种匹配方式：
      - 精确匹配，如 127.0.0.1
      - 通配符匹配，如 192.168.1.*
      - CIDR 网段匹配，如 10.0.0.0/8
    """
    for rule in allow_list:
        rule = rule.strip()
        if not rule:
            continue

        if "*" in rule:
            # 通配符匹配前缀
            prefix = rule.split("*")[0]
            if client_ip.startswith(prefix):
                return True

        elif "/" in rule:
            # CIDR 匹配
            try:
                if ipaddress.ip_address(client_ip) in ipaddress.ip_network(rule, strict=False):
                    return True
            except ValueError:
                logger.warning(f"非法 CIDR 格式：{rule}")
                continue

        elif client_ip == rule:
            return True

    return False


def get_client_ip(request: Request) -> str:
    """
    获取客户端真实 IP。
    优先读取 X-Forwarded-For 头部（用于支持反向代理场景），否则回退为 request.client.host。
    """
    x_forwarded_for = request.headers.get("x-forwarded-for")
    if x_forwarded_for:
        return x_forwarded_for.split(",")[0].strip()
    return request.client.host


class IPAccessControlMiddleware(BaseHTTPMiddleware):
    """
    IP 访问控制中间件：
    若开启配置项 enable_ip_allow_list，则校验请求来源 IP 是否在允许列表 ip_allow_list 中。
    否则直接拒绝请求。
    """

    async def dispatch(self, request: Request, call_next: Callable):
        # 读取是否启用 IP 访问控制
        enable_config = SYSTEM_CONFIG_DATA_MANAGER.get_config("enable_ip_allow_list")
        is_enabled = enable_config and str(enable_config.config_value).lower() == "true"

        if not is_enabled:
            return await call_next(request)

        # 读取允许访问的 IP 列表
        allow_list_config = SYSTEM_CONFIG_DATA_MANAGER.get_config("ip_allow_list")
        allow_list_str = str(allow_list_config.config_value or "")
        allow_list = [ip.strip() for ip in allow_list_str.split(",") if ip.strip()]

        client_ip = get_client_ip(request)

        if not ip_in_allow_list(client_ip, allow_list):
            logger.warning(f"非法访问尝试：IP {client_ip} 不在允许列表")
            return HttpResult.failed(msg="非法访问", code=403).json_response()

        return await call_next(request)