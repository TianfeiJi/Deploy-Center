"""
This module provides centralized logging configuration using Loguru.

Features:
    - Daily log files with strict file name format: YYYY-MM-DD.log
    - Asynchronous file writing via Loguru queue
    - Console output with color formatting for development
    - Configurable logging level and file output switch
"""
import sys
from pathlib import Path
from loguru import logger
from config.app_config import app_config


CURRENT_FILE = Path(__file__).resolve()
BASE_DIR = CURRENT_FILE.parents[2]
LOG_DIR = BASE_DIR / "logs"
LOG_DIR.mkdir(parents=True, exist_ok=True)

LOG_FORMAT = (
    "<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | "
    "<level>{level: <8}</level> | "
    "<cyan>{module}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - "
    "<level>{message}</level>"
)

FILE_FORMAT = (
    "{time:YYYY-MM-DD HH:mm:ss.SSS} | "
    "{level: <8} | "
    "{module}:{function}:{line} - "
    "{message}"
)

log_level = (app_config.logging.level or "DEBUG").upper()

logger.remove()

def daily_file_sink(message):
    """
    Write logs to a file strictly named as YYYY-MM-DD.log.
    """
    record = message.record
    log_date = record["time"].strftime("%Y-%m-%d")
    log_file = LOG_DIR / f"{log_date}.log"
    with open(log_file, "a", encoding="utf-8") as f:
        f.write(str(message))
        f.flush()

logger.add(
    sys.stdout,
    format=LOG_FORMAT,
    colorize=True,
    backtrace=False,
    diagnose=False,
    level=log_level
)

if app_config.logging.file:
    sink_id = logger.add(
        daily_file_sink,
        format=FILE_FORMAT,
        colorize=False,
        enqueue=False,
        backtrace=False,
        diagnose=False,
        level=log_level
    )
    logger.debug(
        f"[Logger file sink configured] sink_id='{sink_id}' | dir='{LOG_DIR}' | naming='YYYY-MM-DD.log' | level='{log_level}'"
    )
else:
    logger.debug(
        f"[Logger file sink skipped] file=disabled | level='{log_level}'"
    )