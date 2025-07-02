"""
This module provides centralized logging configuration using Loguru.

Features:
- Daily log rotation with fixed file name format (YYYY-MM-DD.log)
- Asynchronous file writing to prevent I/O blocking
- Console output with color formatting for development
"""
# ==============================================================================
# @File         : log_config.py
# @Author       : Tianfei Ji
# @Description  : 项目日志配置模块，基于 Loguru 实现按天记录、自动轮转、异步写入。
# ==============================================================================
import os
import sys
from datetime import datetime
from loguru import logger

# Define log output directory relative to this file
LOG_DIR = os.path.join(os.path.dirname(__file__), "logs")
os.makedirs(LOG_DIR, exist_ok=True)

# Define log filename format: "YYYY-MM-DD.log"
def get_daily_log_path(record):
    date_str = datetime.now().strftime("%Y-%m-%d")
    return os.path.join(LOG_DIR, f"{date_str}.log")

# Define rotation policy: rotate if current date != file date
def should_rotate_on_new_day(message, file):
    current_date = datetime.now().date()
    try:
        filename_date = datetime.strptime(os.path.basename(file.name).split(".")[0], "%Y-%m-%d").date()
    except ValueError:
        # fallback: always rotate if filename doesn't match expected format
        return True
    return current_date != filename_date

# Define log message format
LOG_FORMAT = (
    "<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | "
    "<level>{level: <8}</level> | "
    "<cyan>{module}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - "
    "<level>{message}</level>"
)

# Remove the default logger to apply custom handlers only
logger.remove()

# Console output (colored, for development/debugging)
logger.add(
    sys.stdout,
    format=LOG_FORMAT,
    colorize=True,
    backtrace=True,
    diagnose=True
)

# File output (daily rolling, filename = YYYY-MM-DD.log)
logger.add(
    get_daily_log_path,
    rotation=should_rotate_on_new_day,
    format=LOG_FORMAT,
    colorize=False,
    enqueue=True,
    backtrace=True,
    diagnose=True
)