"""
測試 core/facade.py 模組
"""
from unittest.mock import MagicMock, patch

import pytest


class TestBoardGameManager:
    """測試 BoardGameManager Facade"""

    @patch("core.facade.SheetsClient")
    @patch("core.facade.MemberService")
    @patch("core.facade.GameService")
    def test_initialization(self, mock_game_service, mock_member_service, mock_sheets_client):
        """測試初始化"""
        from core.facade import BoardGameManager

        mgr = BoardGameManager()

        assert mock_sheets_client.called
        assert mock_member_service.called
        assert mock_game_service.called
        assert mgr.games == []

    @patch("core.facade.SheetsClient")
    @patch("core.facade.MemberService")
    @patch("core.facade.GameService")
    def test_valid_property(self, mock_game_service, mock_member_service, mock_sheets_client):
        """測試 valid 屬性"""
        from core.facade import BoardGameManager

        mock_client = MagicMock()
        mock_client.valid = True
        mock_sheets_client.return_value = mock_client

        mgr = BoardGameManager()

        assert mgr.valid is True

    @patch("core.facade.SheetsClient")
    @patch("core.facade.MemberService")
    @patch("core.facade.GameService")
    def test_get_current_timestamp(self, mock_game_service, mock_member_service, mock_sheets_client):
        """測試 get_current_timestamp"""
        from core.facade import BoardGameManager

        mgr = BoardGameManager()
        timestamp = mgr.get_current_timestamp()

        assert timestamp is not None
        assert isinstance(timestamp, (str, int))

    @patch("core.facade.SheetsClient")
    @patch("core.facade.MemberService")
    @patch("core.facade.GameService")
    def test_load_data_delegation(self, mock_game_service, mock_member_service, mock_sheets_client):
        """測試 load_data 委派到 client (非 DEMO_MODE)"""
        import os

        from core.facade import BoardGameManager

        mock_client = MagicMock()
        mock_client.load_games.return_value = [{"name": "Test Game"}]
        mock_sheets_client.return_value = mock_client

        with patch.dict(os.environ, {"DEMO_MODE": "false"}):
            mgr = BoardGameManager()
            result = mgr.load_data()

            assert mock_client.load_games.called
            assert result == [{"name": "Test Game"}]

    @patch("core.facade.SheetsClient")
    @patch("core.facade.MemberService")
    @patch("core.facade.GameService")
    def test_load_data_demo_mode(self, mock_game_service, mock_member_service, mock_sheets_client):
        """測試 DEMO_MODE 下載入預設資料"""
        import os

        from core.facade import BoardGameManager

        with patch.dict(os.environ, {"DEMO_MODE": "true"}):
            mgr = BoardGameManager()
            result = mgr.load_data()

            # 不應該呼叫 client
            assert not mock_sheets_client.return_value.load_games.called
            # 應該回傳列表 (demo data)
            assert isinstance(result, list)
            assert len(result) > 0

    @patch("core.facade.SheetsClient")
    @patch("core.facade.MemberService")
    @patch("core.facade.GameService")
    def test_load_members_delegation(self, mock_game_service, mock_member_service, mock_sheets_client):
        """測試 load_members 委派到 client"""
        import os

        from core.facade import BoardGameManager

        mock_client = MagicMock()
        mock_client.load_members.return_value = [{"id": "A001"}]
        mock_sheets_client.return_value = mock_client

        with patch.dict(os.environ, {"DEMO_MODE": "false"}):
            mgr = BoardGameManager()
            result = mgr.load_members()

            assert mock_client.load_members.called
            assert result == [{"id": "A001"}]

    @patch("core.facade.SheetsClient")
    @patch("core.facade.MemberService")
    @patch("core.facade.GameService")
    def test_find_member_by_id_delegation(self, mock_game_service, mock_member_service, mock_sheets_client):
        """測試 find_member_by_id 委派到 member_service"""
        from core.facade import BoardGameManager

        mock_ms = MagicMock()
        mock_ms.find_member_by_id.return_value = {"id": "A001", "name": "Test"}
        mock_member_service.return_value = mock_ms

        mgr = BoardGameManager()
        result = mgr.find_member_by_id("A001")

        assert mock_ms.find_member_by_id.called

    @patch("core.facade.SheetsClient")
    @patch("core.facade.MemberService")
    @patch("core.facade.GameService")
    def test_borrow_game_delegation(self, mock_game_service, mock_member_service, mock_sheets_client):
        """測試 borrow_game 委派到 game_service"""
        from core.facade import BoardGameManager

        mock_gs = MagicMock()
        mock_gs.borrow_game.return_value = True
        mock_game_service.return_value = mock_gs

        mgr = BoardGameManager()
        result = mgr.borrow_game("Test", "User", "A001")

        assert mock_gs.borrow_game.called

    @patch("core.facade.SheetsClient")
    @patch("core.facade.MemberService")
    @patch("core.facade.GameService")
    def test_return_game_delegation(self, mock_game_service, mock_member_service, mock_sheets_client):
        """測試 return_game 委派到 game_service"""
        from core.facade import BoardGameManager

        mock_gs = MagicMock()
        mock_gs.return_game.return_value = True
        mock_game_service.return_value = mock_gs

        mgr = BoardGameManager()
        result = mgr.return_game("Test")

        assert mock_gs.return_game.called
