"""
測試例外類別模組
"""
import pytest
from core.exceptions import (
    BoardGameException,
    GameNotFoundException,
    MemberNotFoundException,
    GameAlreadyBorrowedException,
    GameNotBorrowedException,
    SheetConnectionError,
    InvalidDataError
)


class TestExceptions:
    """測試 core/exceptions.py 中的例外類別"""
    
    def test_boardgame_exception_base(self):
        """測試基礎例外類別"""
        exc = BoardGameException("測試錯誤")
        assert str(exc) == "測試錯誤"
        assert isinstance(exc, Exception)
    
    def test_game_not_found_exception(self):
        """測試遊戲未找到例外"""
        exc = GameNotFoundException("測試遊戲")
        assert "測試遊戲" in str(exc)
        assert exc.game_name == "測試遊戲"
        assert isinstance(exc, BoardGameException)
    
    def test_member_not_found_exception(self):
        """測試社員未找到例外"""
        exc = MemberNotFoundException("TEST001")
        assert "TEST001" in str(exc)
        assert exc.member_identifier == "TEST001"
        assert isinstance(exc, BoardGameException)
    
    def test_game_already_borrowed_exception(self):
        """測試遊戲已被借出例外"""
        exc = GameAlreadyBorrowedException("卡坦島", "張三")
        assert "卡坦島" in str(exc)
        assert "張三" in str(exc)
        assert exc.game_name == "卡坦島"
        assert exc.borrower == "張三"
    
    def test_game_not_borrowed_exception(self):
        """測試遊戲未被借出例外"""
        exc = GameNotBorrowedException("璀璨寶石")
        assert "璀璨寶石" in str(exc)
        assert exc.game_name == "璀璨寶石"
    
    def test_sheet_connection_error(self):
        """測試 Google Sheets 連線錯誤"""
        exc = SheetConnectionError("連線超時")
        assert "連線超時" in str(exc)
        
        # 測試預設訊息
        exc2 = SheetConnectionError()
        assert "Google Sheets" in str(exc2)
    
    def test_invalid_data_error(self):
        """測試資料格式錯誤"""
        exc = InvalidDataError("缺少必要欄位")
        assert "缺少必要欄位" in str(exc)
    
    def test_exceptions_can_be_raised(self):
        """測試例外可以被拋出和捕獲"""
        with pytest.raises(GameNotFoundException):
            raise GameNotFoundException("測試")
        
        with pytest.raises(MemberNotFoundException):
            raise MemberNotFoundException("TEST")
        
        with pytest.raises(GameAlreadyBorrowedException):
            raise GameAlreadyBorrowedException("遊戲", "借閱者")
