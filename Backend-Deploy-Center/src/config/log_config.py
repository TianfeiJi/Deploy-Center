import os
import sys
from loguru import logger
from datetime import datetime


# 获取当前文件的绝对路径
current_file_path = os.path.abspath(__file__)
# 获取当前文件所在文件夹
current_folder = os.path.dirname(current_file_path)
# 获取父级文件夹
parent_directory = os.path.dirname(current_folder)
# 获取父级的父级文件夹
parent_parent_directory = os.path.dirname(parent_directory)
# 日志文件所在文件夹
log_directory = os.path.join(parent_parent_directory, "logs")


os.makedirs(log_directory, exist_ok=True)

logger.remove()  # 移除默认处理器

log_filename = os.path.join(log_directory, f"{datetime.now().strftime('%Y-%m-%d')}.log")

custom_format = (
            "<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | "
            "<level>{level: <8}</level> | "
            "<fg #53c0c0>{name}</fg #53c0c0>:<fg #f0e68c>{function}</fg #f0e68c>:<cyan>{line}</cyan> - <level>{message}</level>"
        )

# 添加标准输出输出：实时输出到控制台
logger.add(
    sys.stdout,
    format=custom_format,
    colorize=True,  # 控制台输出需要颜色
    backtrace=True,  # 包含调用堆栈
    diagnose=True  # 包含诊断信息
)

# 添加文件输出：按日期自动切换日志文件
logger.add(
    log_filename,
    format=custom_format,
    colorize=False,  # 文件输出不需要颜色
    rotation="00:00",  # 每天自动切换日志文件
    enqueue=True,  # 异步写入
    backtrace=True,  # 包含调用堆栈
    diagnose=True  # 包含诊断信息
)


# 返回 logger 实例
def get_logger():
    return logger