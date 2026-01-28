"""
測試常數模組
"""
import pytest

from core.constants import (
    ACTION_BORROW,
    ACTION_RETURN,
    DATETIME_FORMAT,
    FIELD_BORROWER,
    FIELD_BORROWER_ID,
    FIELD_CUSTODIAN,
    FIELD_HISTORY,
    FIELD_MDATE,
    FIELD_NAME,
    FIELD_STATUS,
    GAME_STATUS_AVAILABLE,
    GAME_STATUS_BORROWED,
    MILLISECONDS_PER_SECOND,
)


class TestConstants:
    """測試 core/constants.py 中的常數定義"""

    def test_game_status_constants(self):
        """測試遊戲狀態常數"""
        assert GAME_STATUS_BORROWED == "借出"
        assert GAME_STATUS_AVAILABLE == "在庫"

    def test_field_name_constants(self):
        """測試欄位名稱常數"""
        assert FIELD_NAME == "name"
        assert FIELD_STATUS == "status"
        assert FIELD_BORROWER == "borrower"
        assert FIELD_BORROWER_ID == "borrower_id"
        assert FIELD_MDATE == "mdate"
        assert FIELD_HISTORY == "history"
        assert FIELD_CUSTODIAN == "custodian"

    def test_action_constants(self):
        """測試動作常數"""
        assert ACTION_BORROW == "借閱"
        assert ACTION_RETURN == "歸還"

    def test_time_constants(self):
        """測試時間相關常數"""
        assert MILLISECONDS_PER_SECOND == 1000
        assert DATETIME_FORMAT == "%Y-%m-%d %H:%M"

    def test_constants_are_strings(self):
        """測試所有主要常數都是字串"""
        constants = [
            GAME_STATUS_BORROWED,
            GAME_STATUS_AVAILABLE,
            FIELD_NAME,
            FIELD_STATUS,
            FIELD_BORROWER,
            ACTION_BORROW,
            ACTION_RETURN,
        ]
        for const in constants:
            assert isinstance(const, str)

    def test_constants_are_integers(self):
        """測試數字常數"""
        assert isinstance(MILLISECONDS_PER_SECOND, int)
