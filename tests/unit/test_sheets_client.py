"""
測試 core/sheets_client.py 模組 (使用 mock)
"""
import pytest
from unittest.mock import MagicMock, patch, PropertyMock
import json
import os
import gspread
from core.sheets_client import SheetsClient
from core.exceptions import SheetConnectionError
from core.constants import GAMES_CACHE_TTL, MEMBERS_CACHE_TTL, GAME_STATUS_AVAILABLE


class TestSheetsClientInit:
    """測試初始化與連線邏輯"""

    @patch('core.sheets_client.gspread')
    @patch('core.sheets_client.os.environ.get')
    def test_connect_env_success(self, mock_env, mock_gspread):
        """測試從環境變數連線成功"""
        # 模擬環境變數
        def env_side_effect(key, default=None):
            if key == 'SHEET_URL':
                return 'https://docs.google.com/spreadsheets/d/test-sheet-id'
            if key == 'GOOGLE_CREDENTIALS':
                return '{"type": "service_account"}'
            return default
        
        mock_env.side_effect = env_side_effect
        
        # 模擬 gspread
        mock_gc = MagicMock()
        mock_sh = MagicMock()
        mock_gspread.service_account_from_dict.return_value = mock_gc
        mock_gc.open_by_url.return_value = mock_sh
        
        client = SheetsClient()
        
        assert client.valid is True
        assert client.gc == mock_gc
        assert client.sh == mock_sh
        mock_gspread.service_account_from_dict.assert_called_once()
        mock_gc.open_by_url.assert_called_with('https://docs.google.com/spreadsheets/d/test-sheet-id')

    @patch('core.sheets_client.gspread')
    @patch('core.sheets_client.os.environ.get')
    def test_connect_env_fail(self, mock_env, mock_gspread):
        """測試環境變數連線失敗"""
        mock_env.return_value = 'invalid_json'
        mock_gspread.service_account_from_dict.side_effect = Exception("Invalid JSON")
        
        # 確保本地檔案檢查也失敗
        with patch('os.path.exists', return_value=False):
            client = SheetsClient()
            
            assert client.valid is False
            assert client.gc is None

    @patch('core.sheets_client.gspread')
    @patch('core.sheets_client.os.environ.get')
    @patch('os.path.exists')
    def test_connect_local_success(self, mock_exists, mock_env, mock_gspread):
        """測試從本地檔案連線成功"""
        # 模擬環境變數無效 (第一次檢查)
        
        call_count = 0
        def env_side_effect(key, default=None):
            nonlocal call_count
            call_count += 1
            # 1. SHEET_URL (init -> _connect) -> None
            # 2. GOOGLE_CREDENTIALS (init -> _connect) -> None
            # 3. SHEET_URL (init -> _connect -> load_dotenv) -> 'test_url'
            if key == 'SHEET_URL' and call_count > 2:
                return 'test_url'
            return None

        mock_env.side_effect = env_side_effect
        
        # 模擬本地檔案存在
        mock_exists.return_value = True
        
        # 模擬 gspread
        mock_gc = MagicMock()
        mock_sh = MagicMock()
        mock_gspread.service_account.return_value = mock_gc
        mock_gc.open_by_url.return_value = mock_sh
        
        # Patch dotenv.load_dotenv
        with patch('dotenv.load_dotenv'):
            client = SheetsClient()
    
            assert client.valid is True
            assert client.gc == mock_gc
            mock_gspread.service_account.assert_called_once()


class TestSheetsClientWorksheets:
    """測試工作表存取"""

    def setup_method(self):
        self.client = SheetsClient()
        self.client.valid = True
        self.client.sh = MagicMock()

    def test_get_games_worksheet_success(self):
        """測試取得遊戲工作表"""
        mock_ws = MagicMock()
        self.client.sh.worksheet.return_value = mock_ws
        
        ws = self.client.get_games_worksheet()
        
        assert ws == mock_ws
        assert self.client.games_ws == mock_ws
        self.client.sh.worksheet.assert_called_with('games')

    def test_get_games_worksheet_fail(self):
        """測試取得遊戲工作表失敗"""
        self.client.sh.worksheet.side_effect = Exception("Not found")
        
        with pytest.raises(SheetConnectionError):
            self.client.get_games_worksheet()

    def test_get_members_worksheet_success(self):
        """測試取得會員工作表"""
        mock_ws = MagicMock()
        self.client.sh.worksheet.return_value = mock_ws
        
        ws = self.client.get_members_worksheet()
        
        assert ws == mock_ws
        assert self.client.members_ws == mock_ws
        self.client.sh.worksheet.assert_called_with('members')

    def test_get_members_worksheet_fail(self):
        """測試取得會員工作表失敗"""
        self.client.sh.worksheet.side_effect = Exception("Not found")
        
        with pytest.raises(SheetConnectionError):
            self.client.get_members_worksheet()

    def test_get_bgg_cache_worksheet_create(self):
        """測試建立新的 BGG 快取工作表"""
        # 模擬找不到工作表
        self.client.sh.worksheet.side_effect = gspread.exceptions.WorksheetNotFound
        mock_new_ws = MagicMock()
        self.client.sh.add_worksheet.return_value = mock_new_ws
        
        ws = self.client.get_bgg_cache_worksheet()
        
        assert ws == mock_new_ws
        self.client.sh.add_worksheet.assert_called_once()
        mock_new_ws.update.assert_called_once() # 驗證標題列寫入


class TestSheetsClientLoadData:
    """測試資料讀取與快取"""

    def setup_method(self):
        self.client = SheetsClient()
        self.client.valid = True
        self.client.sh = MagicMock()
        self.client.games_ws = MagicMock()
        self.client.members_ws = MagicMock()

    def test_load_games_success(self):
        """測試成功讀取遊戲並寫入快取"""
        expected_data = [{'name': 'Catan', 'status': 'Available'}]
        self.client.games_ws.get_all_records.return_value = expected_data
        
        # 第一次讀取
        data = self.client.load_games()
        
        assert data == expected_data
        assert self.client._games_cache == expected_data
        assert self.client._games_cache_time > 0
        self.client.games_ws.get_all_records.assert_called_once()

    def test_load_games_cache_hit(self):
        """測試快取命中"""
        cached_data = [{'name': 'Catan'}]
        self.client._games_cache = cached_data
        import time
        self.client._games_cache_time = time.time()
        
        data = self.client.load_games()
        
        assert data == cached_data
        # 確保沒有呼叫 API
        self.client.games_ws.get_all_records.assert_not_called()

    def test_load_games_retry(self):
        """測試讀取失敗後重試"""
        # 第一次呼叫失敗，第二次成功 (模擬重連後)
        self.client.games_ws.get_all_records.side_effect = [Exception("API Error"), [{'name': 'Catan'}]]
        
        with patch.object(self.client, '_connect') as mock_connect:
            # 模擬重連成功
            def reconnect_side_effect():
                self.client.valid = True
            mock_connect.side_effect = reconnect_side_effect
            
            data = self.client.load_games()
            
            assert len(data) == 1
            assert data[0]['name'] == 'Catan'
            mock_connect.assert_called_once()

    def test_load_members_success(self):
        """測試成功讀取會員"""
        expected_data = [{'id': '001', 'name': 'Alice'}]
        self.client.members_ws.get_all_records.return_value = expected_data
        
        data = self.client.load_members()
        
        assert data == expected_data
        assert self.client._members_cache == expected_data

    def test_load_members_retry(self):
        """測試讀取會員失敗後重試"""
        # 第一次呼叫失敗，第二次成功 (模擬重連後)
        self.client.members_ws.get_all_records.side_effect = [Exception("API Error"), [{'id': '001'}]]
        
        with patch.object(self.client, '_connect') as mock_connect:
            # 模擬重連成功
            def reconnect_side_effect():
                self.client.valid = True
            mock_connect.side_effect = reconnect_side_effect
            
            data = self.client.load_members()
            
            assert len(data) == 1
            assert data[0]['id'] == '001'
            mock_connect.assert_called_once()

    def test_invalidate_games_cache(self):
        """測試快取失效"""
        self.client._games_cache = [{'name': 'Catan'}]
        self.client._games_cache_time = 12345
        
        self.client.invalidate_games_cache()
        
        assert self.client._games_cache is None
        assert self.client._games_cache_time == 0


class TestSheetsClientWriteData:
    """測試資料寫入"""

    def setup_method(self):
        self.client = SheetsClient()
        self.client.valid = True
        self.client.sh = MagicMock()
        self.client.games_ws = MagicMock()

    def test_add_new_game_success(self):
        """測試成功新增遊戲"""
        game_data = {'name': 'New Game', 'players': '2-4'}
        self.client.games_ws.row_values.return_value = ['name', 'status', 'players']
        
        result = self.client.add_new_game(game_data)
        
        assert result is True
        self.client.games_ws.append_row.assert_called_with(['New Game', GAME_STATUS_AVAILABLE, '2-4'])
        # 確保快取失效
        assert self.client._games_cache is None

    def test_add_new_game_fail(self):
        """測試新增遊戲失敗"""
        self.client.games_ws.row_values.side_effect = Exception("API Error")
        
        result = self.client.add_new_game({'name': 'Fail Game'})
        
        assert result is False

    def test_create_batch_update(self):
        """測試建立批次更新"""
        update = self.client.create_batch_update(1, 0, 'test')
        assert update['range'] == 'A1' # row 1, col 0 -> A1
        assert update['values'] == [['test']]

    def test_update_game_bgg_id_success(self):
        """測試成功更新 BGG ID"""
        # 模擬現有資料
        self.client.games_ws.get_all_records.return_value = [
            {'name': 'Other Game'},
            {'name': 'Target Game'}
        ]
        self.client.games_ws.row_values.return_value = ['name', 'bgg_id', 'bgg_thumbnail', 'image']
        
        result = self.client.update_game_bgg_id(
            game_name='Target Game',
            bgg_id=12345,
            thumbnail_url='http://thumb.jpg',
            image_url='http://image.jpg',
            players_display='2-4'
        )
        
        assert result is True
        # 驗證 update_cell 呼叫 (row=3, 因為是第二筆資料 + 標題列1)
        assert self.client.games_ws.update_cell.call_count >= 3
        assert self.client._games_cache is None

    def test_update_game_bgg_id_not_found(self):
        """測試更新不存在的遊戲"""
        self.client.games_ws.get_all_records.return_value = []
        
        result = self.client.update_game_bgg_id('Ghost Game', 123)
        
        assert result is False

    def test_update_game_bgg_id_fail(self):
        """測試更新 BGG ID 失敗"""
        self.client.games_ws.get_all_records.side_effect = Exception("API Error")
        
        result = self.client.update_game_bgg_id('Target Game', 123)
        
        assert result is False


class TestSheetsClientBGGRecommendations:
    """測試 BGG 推薦快取功能"""

    def setup_method(self):
        self.client = SheetsClient()
        self.client.valid = True
        self.client.sh = MagicMock()

    def test_save_bgg_recommendations_new(self):
        """測試儲存新的推薦快取"""
        mock_ws = MagicMock()
        self.client.sh.worksheet.return_value = mock_ws
        mock_ws.get_all_records.return_value = []
        
        game_ids = [1, 2, 3]
        result = self.client.save_bgg_recommendations('party', game_ids)
        
        assert result is True
        mock_ws.append_row.assert_called_once()
        args = mock_ws.append_row.call_args[0][0]
        assert args[0] == 'party'
        assert args[1] == 1
        assert args[2] == 2
        assert args[3] == 3
        assert args[4] == 0  # padding

    def test_save_bgg_recommendations_update(self):
        """測試更新現有推薦快取"""
        mock_ws = MagicMock()
        self.client.sh.worksheet.return_value = mock_ws
        mock_ws.get_all_records.return_value = [{'分類': 'party'}]
        
        game_ids = [1, 2, 3]
        result = self.client.save_bgg_recommendations('party', game_ids)
        
        assert result is True
        mock_ws.update.assert_called_once()

    def test_save_bgg_recommendations_fail(self):
        """測試儲存推薦快取失敗"""
        self.client.sh.worksheet.side_effect = Exception("API Error")
        
        result = self.client.save_bgg_recommendations('party', [])
        
        assert result is False

    def test_load_bgg_recommendations_hit(self):
        """測試讀取推薦快取命中"""
        mock_ws = MagicMock()
        self.client.sh.worksheet.return_value = mock_ws
        
        # 模擬快取資料
        record = {'分類': 'party'}
        for i in range(1, 51):
            record[f'BGG_ID_{i}'] = i if i <= 3 else 0
        record['更新時間'] = '2025-01-01'
        
        mock_ws.get_all_records.return_value = [record]
        
        ids = self.client.load_bgg_recommendations('party')
        
        assert ids == [1, 2, 3]

    def test_get_bgg_recommendations_update_time(self):
        """測試取得更新時間"""
        mock_ws = MagicMock()
        self.client.sh.worksheet.return_value = mock_ws
        mock_ws.get_all_records.return_value = [{'分類': 'party', '更新時間': '2025-01-01'}]
        
        time_str = self.client.get_bgg_recommendations_update_time('party')
        
        assert time_str == '2025-01-01'
