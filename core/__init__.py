# coding: utf-8
"""
Core 模組
提供桌遊管理系統的核心功能
"""

# 導出常用的類別和函數
from .constants import *
from .exceptions import *
from .utils import (
    get_current_timestamp,
    format_datetime,
    create_history_entry,
    append_history,
)
from .cache import SimpleCache

__all__ = [
    # 常量
    "GAMES_CACHE_TTL",
    "MEMBERS_CACHE_TTL",
    "GAME_STATUS_AVAILABLE",
    "GAME_STATUS_BORROWED",
    "WORKSHEET_GAMES",
    "WORKSHEET_MEMBERS",
    # 異常
    "BoardGameException",
    "GameNotFoundException",
    "GameAlreadyBorrowedException",
    "GameNotBorrowedException",
    "MemberNotFoundException",
    "SheetConnectionError",
    "InvalidDataError",
    # 工具函數
    "get_current_timestamp",
    "format_datetime",
    "create_history_entry",
    "append_history",
    # 快取
    "SimpleCache",
]
