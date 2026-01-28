# coding: utf-8
"""
統一日誌配置模組

提供專案統一的日誌配置，支援：
- 控制台輸出（彩色格式）
- 檔案輸出（JSON 格式，可選）
- 環境變數控制日誌等級
"""
import logging
import os
import sys
from typing import Optional

# 日誌格式常數
CONSOLE_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
CONSOLE_FORMAT_SIMPLE = "%(levelname)s - %(message)s"
FILE_FORMAT = (
    "%(asctime)s - %(name)s - %(levelname)s - %(filename)s:%(lineno)d - %(message)s"
)


def setup_logging(
    level: Optional[str] = None,
    log_file: Optional[str] = None,
    simple_format: bool = False,
) -> None:
    """設定統一的日誌配置

    Args:
        level: 日誌等級 (DEBUG, INFO, WARNING, ERROR)，預設從環境變數 LOG_LEVEL 讀取
        log_file: 日誌檔案路徑，若指定則同時輸出到檔案
        simple_format: 是否使用簡化格式
    """
    # 從環境變數讀取日誌等級
    if level is None:
        level = os.environ.get("LOG_LEVEL", "INFO").upper()

    log_level = getattr(logging, level, logging.INFO)

    # 選擇格式
    console_format = CONSOLE_FORMAT_SIMPLE if simple_format else CONSOLE_FORMAT

    # 設定根 logger
    root_logger = logging.getLogger()
    root_logger.setLevel(log_level)

    # 清除既有的 handlers（避免重複）
    root_logger.handlers.clear()

    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(log_level)
    console_handler.setFormatter(logging.Formatter(console_format))
    root_logger.addHandler(console_handler)

    # File handler (optional)
    if log_file:
        file_handler = logging.FileHandler(log_file, encoding="utf-8")
        file_handler.setLevel(log_level)
        file_handler.setFormatter(logging.Formatter(FILE_FORMAT))
        root_logger.addHandler(file_handler)

    # 減少第三方套件的日誌輸出
    logging.getLogger("urllib3").setLevel(logging.WARNING)
    logging.getLogger("werkzeug").setLevel(logging.WARNING)
    logging.getLogger("httpx").setLevel(logging.WARNING)

    logging.info(f"Logging initialized: level={level}")


def get_logger(name: str) -> logging.Logger:
    """取得指定名稱的 logger

    這是一個便利函數，等同於 logging.getLogger(name)

    Args:
        name: logger 名稱，通常使用 __name__

    Returns:
        Logger 實例
    """
    return logging.getLogger(name)
