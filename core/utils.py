# coding: utf-8
"""
工具函數模組
提供時間處理、格式化等工具函數
"""
import time
from datetime import datetime
from typing import Optional
from .constants import DATETIME_FORMAT, MILLISECONDS_PER_SECOND


def get_current_timestamp() -> int:
    """
    取得當前時間戳（毫秒）

    Returns:
        int: 當前時間的毫秒時間戳
    """
    return int(time.time() * MILLISECONDS_PER_SECOND)


def format_datetime(timestamp_ms: int) -> str:
    """
    格式化時間戳為可讀字串

    Args:
        timestamp_ms: 毫秒時間戳

    Returns:
        str: 格式化的日期時間字串，格式為 'YYYY-MM-DD HH:MM'
    """
    return datetime.fromtimestamp(timestamp_ms / MILLISECONDS_PER_SECOND).strftime(
        DATETIME_FORMAT
    )


def create_history_entry(
    user_name: str, action: str, timestamp_ms: Optional[int] = None
) -> str:
    """
    創建歷史記錄條目

    Args:
        user_name: 使用者名稱
        action: 動作（借閱或歸還）
        timestamp_ms: 時間戳（毫秒），若為 None 則使用當前時間

    Returns:
        str: 格式化的歷史記錄條目，例如 "[2024-01-01 12:00] 張三 借閱"
    """
    if timestamp_ms is None:
        timestamp_ms = get_current_timestamp()

    date_str = format_datetime(timestamp_ms)
    return f"[{date_str}] {user_name} {action}"


def append_history(existing_history: str, new_entry: str) -> str:
    """
    附加新的歷史記錄到現有歷史

    Args:
        existing_history: 現有的歷史記錄字串
        new_entry: 新的歷史記錄條目

    Returns:
        str: 合併後的歷史記錄
    """
    if existing_history:
        return f"{existing_history} | {new_entry}"
    return new_entry
