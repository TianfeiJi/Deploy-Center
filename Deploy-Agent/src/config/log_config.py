"""
This module provides centralized logging configuration using Loguru.

Features:
- Daily log rotation with fixed file name format (YYYY-MM-DD.log)
- Asynchronous file writing to prevent I/O blocking
- Console output with color formatting for development
- Configurable logging level and file output switch
"""

# ==============================================================================
# @File         : log_config.py
# @Author       : Tianfei Ji
# @Description  : Centralized logging configuration based on Loguru.
# ==============================================================================

import sys
from datetime import datetime
from pathlib import Path
from loguru import logger
from config.app_config import app_config

# Resolve base directory: /app/src/config/log_config.py → /app
CURRENT_FILE = Path(__file__).resolve()
BASE_DIR = CURRENT_FILE.parents[2]
LOG_DIR = BASE_DIR / "logs"
LOG_DIR.mkdir(parents=True, exist_ok=True)

# Define log file path: /app/logs/YYYY-MM-DD.log
LOG_PATH = LOG_DIR / f"{datetime.now():%Y-%m-%d}.log"

# Define log format
LOG_FORMAT = (
    "<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | "
    "<level>{level: <8}</level> | "
    "<cyan>{module}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - "
    "<level>{message}</level>"
)

# Extract log level from config
log_level = app_config.logging.get("level", "DEBUG").upper()

# Remove the default handler before applying custom sinks
logger.remove()

# Add console sink (colored output)
logger.add(
    sys.stdout,
    format=LOG_FORMAT,
    colorize=True,
    backtrace=True,
    diagnose=True,
    level=log_level
)

# Add file sink if enabled in config
if app_config.logging.get("file", False):
    rotation = "00:00"  # Daily rotation at midnight
    sink_id = logger.add(
        LOG_PATH,
        format=LOG_FORMAT,
        colorize=False,
        rotation=rotation,
        enqueue=True,
        backtrace=True,
        diagnose=True,
        level=log_level
    )
    logger.debug(
       f"[Logger file sink configured] sink_id='{sink_id}' | path='{LOG_PATH}' | rotation='{rotation}' | level='{log_level}'"
    )
else:
    logger.debug(
       f"[Logger file sink skipped] file=disabled | level='{log_level}'"
    )