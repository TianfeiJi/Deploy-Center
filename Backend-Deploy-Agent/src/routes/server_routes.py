import time
from fastapi import APIRouter
import psutil
import cpuinfo
import platform
import socket
from models.common.http_result import HttpResult
from config.log_config import get_logger


logger = get_logger()
server_router = APIRouter()


@server_router.get("/api/deploy-agent/server/system_info", summary="获取服务器系统信息")
async def get_server_system_info():
    """
    获取服务器的系统信息
    """
    try:
        boot_time_timestamp = psutil.boot_time()
        boot_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(boot_time_timestamp))

        ip_address = None
        try:
            ip_address = socket.gethostbyname(socket.gethostname())
        except:
            pass
    
        memory = psutil.virtual_memory()
        cpu_info = cpuinfo.get_cpu_info()
        freq_info = psutil.cpu_freq()
        cpu_freq_mhz = freq_info.max if freq_info else None

        # 获取系统信息
        system_info = {
            "platform": platform.system(),
            "platform_version": platform.version(),
            "architecture": platform.machine(),
            "hostname": platform.node(),
            "cpu_brand": cpu_info.get('brand_raw', '未知'),  # CPU完整型号
            "cpu_arch": cpu_info.get('arch', '未知'),         # CPU架构，比如X86_64
            "cpu_cores_logical": psutil.cpu_count(logical=True),
            "cpu_cores_physical": psutil.cpu_count(logical=False),
            "cpu_freq_ghz": round(cpu_freq_mhz / 1000, 2) if cpu_freq_mhz else None,  # 转成GHz，保留2位小数
            "total_memory": memory.total // (1024 ** 2),
            "boot_time": boot_time,
            "ip_address": ip_address or "无法获取",
        }

        return HttpResult[dict](code=200, status="success", msg=None, data=system_info)
    except Exception as e:
        return HttpResult[dict](code=500, status="failed", msg=str(e), data=None)
    
@server_router.get("/api/deploy-agent/server/memory_info", summary="获取服务器内存信息")
async def get_server_memory_info():
    """
    获取服务器的内存信息
    """
    try:
        # 获取内存使用情况
        memory = psutil.virtual_memory()
        memory_info = {
            "total": memory.total // (1024 ** 2),  # 转换为 MB
            "available": memory.available // (1024 ** 2),
            "used": memory.used // (1024 ** 2),
            "percent": memory.percent,
        }
        
        return HttpResult[dict](code=200, status="success", msg=None, data=memory_info)
    except Exception as e:
        return HttpResult[dict](code=500, status="failed", msg=str(e), data=None)

@server_router.get("/api/deploy-agent/server/cpu_usage", summary="获取服务器CPU 使用率")
async def get_server_cpu_usage():
    """
    获取服务器的CPU使用率。
    """
    try:
        # 获取 CPU 使用率
        cpu_usage = psutil.cpu_percent(interval=1)
        return HttpResult(code=200, status="success", msg=None, data=cpu_usage)
    except Exception as e:
        return HttpResult(code=500, status="failed", msg=str(e), data=None)

@server_router.get("/api/deploy-agent/server/disk_info", summary="获取服务器磁盘信息")
async def get_server_disk_info():
    """
    获取服务器的磁盘信息。
    """
    try:
        # 获取磁盘使用情况
        disk = psutil.disk_usage('/')
        disk_info = {
            "total": disk.total // (1024 ** 3),  # 转换为 GB
            "used": disk.used // (1024 ** 3),
            "free": disk.free // (1024 ** 3),
            "percent": disk.percent,
        }

        return HttpResult[dict](code=200, status="success", msg=None, data=disk_info)
    except Exception as e:
        return HttpResult[dict](code=500, status="failed", msg=str(e), data=None)

@server_router.get("/api/deploy-agent/server/network_speed", summary="获取服务器实时网络速度")
async def get_server_network_speed():
    """
    获取服务器当前上传和下载速度（KB/s）
    """
    try:
        # 第一次采样
        net1 = psutil.net_io_counters()
        bytes_sent1 = net1.bytes_sent
        bytes_recv1 = net1.bytes_recv

        time.sleep(1)  # 采样间隔1秒

        # 第二次采样
        net2 = psutil.net_io_counters()
        bytes_sent2 = net2.bytes_sent
        bytes_recv2 = net2.bytes_recv

        upload_speed = (bytes_sent2 - bytes_sent1) / 1024  # KB/s
        download_speed = (bytes_recv2 - bytes_recv1) / 1024  # KB/s

        network_speed = {
            "upload_speed": round(upload_speed, 2),      # 上传速度，保留2位小数
            "download_speed": round(download_speed, 2)   # 下载速度，保留2位小数
        }

        return HttpResult[dict](code=200, status="success", msg=None, data=network_speed)
    except Exception as e:
        logger.error(f"获取服务器网络速度失败: {e}")
        return HttpResult[dict](code=500, status="failed", msg=str(e), data=None)

@server_router.get("/api/deploy-agent/server/network_info", summary="获取服务器网络信息")
async def get_server_network_info():
    """
    获取服务器网络信息
    """
    try:
        # 获取服务器网络信息
        network_info = {}
        # 获取网络接口信息
        net_if_addrs = psutil.net_if_addrs()
        for interface, addrs in net_if_addrs.items():
            network_info[interface] = []
            for addr in addrs:
                if addr.family == socket.AF_INET:  # IPv4 地址
                    network_info[interface].append({
                        "family": "IPv4",
                        "address": addr.address,
                        "netmask": addr.netmask,
                        "broadcast": addr.broadcast
                    })
                elif addr.family == socket.AF_INET6:  # IPv6 地址
                    network_info[interface].append({
                        "family": "IPv6",
                        "address": addr.address,
                        "netmask": addr.netmask,
                        "broadcast": addr.broadcast
                    })
                elif addr.family == psutil.AF_LINK:  # MAC 地址
                    network_info[interface].append({
                        "family": "MAC",
                        "address": addr.address
                    })

        # 获取网络带宽使用情况
        net_io_counters = psutil.net_io_counters(pernic=True)
        for interface, counters in net_io_counters.items():
            if interface not in network_info:
                network_info[interface] = []
            network_info[interface].append({
                "bytes_sent": counters.bytes_sent,
                "bytes_recv": counters.bytes_recv,
                "packets_sent": counters.packets_sent,
                "packets_recv": counters.packets_recv
            })

        return HttpResult[dict](code=200, status="success", msg=None, data=network_info)
    except Exception as e:
        return HttpResult[dict](code=500, status="failed", msg=str(e), data=None)