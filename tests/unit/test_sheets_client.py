"""
測試 core/sheets_client.py 模組 (使用 mock)
"""
import pytest
from unittest.mock import MagicMock, patch


class TestSheetsClientInit:
    """測試初始化"""
    
    @patch('core.sheets_client.gspread')
    def test_init_no_credentials(self, mock_gspread):
        """測試沒有憑證時初始化"""
        mock_gspread.service_account.side_effect = Exception("No credentials")
        
        from core.sheets_client import SheetsClient
        client = SheetsClient()
        
        # 應該設置 valid 為 False
        assert client.valid is False
    
    @patch('core.sheets_client.gspread')
    @patch('core.sheets_client.os.environ.get')
    def test_init_with_credentials(self, mock_env, mock_gspread):
        """測試有憑證時初始化"""
        mock_env.return_value = 'test_sheet_id'
        mock_gc = MagicMock()
        mock_gspread.service_account.return_value = mock_gc
        
        from core.sheets_client import SheetsClient
        client = SheetsClient()
        
        # 嘗試連接


class TestSheetsClientLoadGames:
    """測試 load_games 方法"""
    
    @patch('core.sheets_client.gspread')
    def test_load_games_not_connected(self, mock_gspread):
        """測試未連接時載入遊戲"""
        mock_gspread.service_account.side_effect = Exception("No credentials")
        
        from core.sheets_client import SheetsClient
        client = SheetsClient()
        games = client.load_games()
        
        # 未連接應該返回空列表
        assert games == []
    
    @patch('core.sheets_client.gspread')
    def test_load_games_from_cache(self, mock_gspread):
        """測試從快取載入遊戲"""
        mock_gspread.service_account.side_effect = Exception("No credentials")
        
        from core.sheets_client import SheetsClient
        client = SheetsClient()
        
        # 設置快取
        client._games_cache = [{'name': 'Catan'}]
        client._games_cache_time = 9999999999  # 未來時間
        
        # 但由於 valid 是 False，還是會返回空
        games = client.load_games()


class TestSheetsClientLoadMembers:
    """測試 load_members 方法"""
    
    @patch('core.sheets_client.gspread')
    def test_load_members_not_connected(self, mock_gspread):
        """測試未連接時載入會員"""
        mock_gspread.service_account.side_effect = Exception("No credentials")
        
        from core.sheets_client import SheetsClient
        client = SheetsClient()
        members = client.load_members()
        
        # 未連接應該返回空列表
        assert members == []


class TestSheetsClientCacheInvalidation:
    """測試快取失效"""
    
    @patch('core.sheets_client.gspread')
    def test_invalidate_games_cache(self, mock_gspread):
        """測試使遊戲快取失效"""
        mock_gspread.service_account.side_effect = Exception("No credentials")
        
        from core.sheets_client import SheetsClient
        client = SheetsClient()
        
        # 設置快取
        client._games_cache = [{'name': 'Catan'}]
        client._games_cache_time = 123456
        
        # 使快取失效
        client.invalidate_games_cache()
        
        assert client._games_cache is None
        assert client._games_cache_time == 0


class TestSheetsClientBatchUpdate:
    """測試批次更新"""
    
    @patch('core.sheets_client.gspread')
    def test_create_batch_update(self, mock_gspread):
        """測試建立批次更新"""
        mock_gspread.service_account.side_effect = Exception("No credentials")
        
        from core.sheets_client import SheetsClient
        client = SheetsClient()
        
        update = client.create_batch_update(1, 0, 'test_value')
        
        assert update is not None
        assert 'range' in update
        assert 'values' in update
