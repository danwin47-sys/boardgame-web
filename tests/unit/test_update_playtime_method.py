"""
測試 update_playtime_method 模組
"""
from unittest.mock import MagicMock, Mock

import pytest

from core.update_playtime_method import update_game_playtime


class TestUpdateGamePlaytime:
    """測試更新遊戲遊玩時間功能"""

    @pytest.fixture
    def mock_sheets_client(self):
        """建立 mock SheetsClient"""
        client = Mock()
        client.valid = True

        # Mock worksheet
        ws = Mock()
        client.get_games_worksheet.return_value = ws

        return client, ws

    def test_update_game_playtime_success(self, mock_sheets_client):
        """測試成功更新遊戲時間"""
        client, ws = mock_sheets_client

        # 模擬工作表資料
        ws.get_all_values.return_value = [
            ["name", "status", "minplaytime", "maxplaytime"],
            ["卡坦島", "在庫", "60", "120"],
            ["璀璨寶石", "在庫", "30", "30"],
        ]

        # 執行更新（將函數作為方法調用）
        result = update_game_playtime(client, "卡坦島", 45, 90)

        # 驗證
        assert result is True
        # 應該更新 minplaytime 和 maxplaytime
        assert ws.update_cell.call_count == 2

    def test_update_game_playtime_game_not_found(self, mock_sheets_client):
        """測試遊戲不存在的情況"""
        client, ws = mock_sheets_client

        # 模擬工作表資料
        ws.get_all_values.return_value = [["name", "status"], ["卡坦島", "在庫"]]

        # 執行更新（遊戲不存在）
        result = update_game_playtime(client, "不存在的遊戲", 45, 90)

        # 驗證
        assert result is False

    def test_update_game_playtime_no_worksheet(self, mock_sheets_client):
        """測試無法取得工作表"""
        client, ws = mock_sheets_client
        client.get_games_worksheet.return_value = None

        # 執行更新
        result = update_game_playtime(client, "卡坦島", 45, 90)

        # 驗證
        assert result is False

    def test_update_game_playtime_empty_data(self, mock_sheets_client):
        """測試工作表資料為空"""
        client, ws = mock_sheets_client
        ws.get_all_values.return_value = []

        # 執行更新
        result = update_game_playtime(client, "卡坦島", 45, 90)

        # 驗證
        assert result is False

    def test_update_game_playtime_exception_handling(self, mock_sheets_client):
        """測試異常處理"""
        client, ws = mock_sheets_client
        ws.get_all_values.side_effect = Exception("API Error")

        # 執行更新
        result = update_game_playtime(client, "卡坦島", 45, 90)

        # 驗證
        assert result is False

    def test_update_game_playtime_create_new_columns(self, mock_sheets_client):
        """測試建立新欄位"""
        client, ws = mock_sheets_client

        # 模擬工作表資料（沒有 playtime 欄位）
        headers = ["name", "status"]
        ws.get_all_values.return_value = [headers.copy(), ["卡坦島", "在庫"]]

        # 執行更新
        result = update_game_playtime(client, "卡坦島", 45, 90)

        # 驗證會建立新欄位並更新資料
        assert result is True
        # 應該呼叫 update_cell 來建立欄位和更新資料
        assert ws.update_cell.call_count >= 2
