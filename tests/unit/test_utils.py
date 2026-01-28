"""
測試核心工具函數
"""
from datetime import datetime

import pytest

from core.utils import (
    append_history,
    create_history_entry,
    format_datetime,
    get_current_timestamp,
)


class TestUtils:
    """測試 core/utils.py 中的工具函數"""

    def test_get_current_timestamp(self):
        """測試取得當前時間戳（毫秒）"""
        timestamp = get_current_timestamp()
        assert isinstance(timestamp, int)
        assert timestamp > 0
        # 驗證是毫秒時間戳（應該是13位數字）
        assert len(str(timestamp)) >= 13

    def test_format_datetime(self):
        """測試時間戳格式化"""
        # 使用已知的時間戳（2024-01-01 10:30:00）
        timestamp_ms = 1704081000000  # 2024-01-01 10:30:00 UTC
        formatted = format_datetime(timestamp_ms)
        assert isinstance(formatted, str)
        # 驗證格式為 YYYY-MM-DD HH:MM
        assert len(formatted.split(" ")) == 2
        assert len(formatted.split(":")) == 2

    def test_create_history_entry(self):
        """測試建立歷史記錄項目"""
        # 使用指定的時間戳
        timestamp_ms = 1704081000000
        entry = create_history_entry("測試使用者", "借閱", timestamp_ms)

        assert "測試使用者" in entry
        assert "借閱" in entry
        assert "[" in entry and "]" in entry  # 應包含日期括號

    def test_create_history_entry_without_timestamp(self):
        """測試建立歷史記錄項目（使用當前時間）"""
        entry = create_history_entry("測試使用者", "歸還")

        assert "測試使用者" in entry
        assert "歸還" in entry
        assert "[" in entry and "]" in entry

    def test_append_history(self):
        """測試附加歷史記錄"""
        existing = "[2024-01-01 10:00] 張三 借閱"
        new_entry = "[2024-01-02 11:00] 李四 歸還"

        result = append_history(existing, new_entry)
        assert existing in result
        assert new_entry in result
        assert "|" in result  # 應使用 | 分隔

    def test_append_history_empty_existing(self):
        """測試附加歷史記錄到空字串"""
        new_entry = "[2024-01-01 10:00] 張三 借閱"
        result = append_history("", new_entry)
        assert result == new_entry
