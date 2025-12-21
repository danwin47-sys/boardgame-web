"""
測試 core/bgg_ranks_service.py 模組 (使用 mock)
"""
import pytest
from unittest.mock import MagicMock, patch
import sqlite3

from core.bgg_ranks_service import BGGRanksService


class TestBGGRanksServiceInit:
    """測試初始化"""
    
    def test_init_default_path(self):
        """測試預設路徑初始化"""
        service = BGGRanksService()
        assert service.db_path is not None
    
    def test_init_custom_path(self):
        """測試自定義路徑初始化"""
        service = BGGRanksService(db_path="/custom/path.db")
        assert service.db_path == "/custom/path.db"


class TestBGGRanksServiceGetById:
    """測試 get_by_id 方法"""
    
    @patch.object(BGGRanksService, '_get_connection')
    def test_get_by_id_found(self, mock_conn):
        """測試按 ID 查找 - 找到"""
        mock_cursor = MagicMock()
        mock_cursor.fetchone.return_value = {
            'bgg_id': 13,
            'name': 'Catan',
            'rank': 50
        }
        mock_connection = MagicMock()
        mock_connection.cursor.return_value = mock_cursor
        mock_conn.return_value = mock_connection
        
        service = BGGRanksService()
        result = service.get_by_id(13)
        
        assert result is not None
        assert result['bgg_id'] == 13
    
    @patch.object(BGGRanksService, '_get_connection')
    def test_get_by_id_not_found(self, mock_conn):
        """測試按 ID 查找 - 未找到"""
        mock_cursor = MagicMock()
        mock_cursor.fetchone.return_value = None
        mock_connection = MagicMock()
        mock_connection.cursor.return_value = mock_cursor
        mock_conn.return_value = mock_connection
        
        service = BGGRanksService()
        result = service.get_by_id(99999999)
        
        assert result is None
    
    @patch.object(BGGRanksService, '_get_connection')
    def test_get_by_id_error(self, mock_conn):
        """測試查詢錯誤"""
        mock_conn.side_effect = Exception("Database error")
        
        service = BGGRanksService()
        result = service.get_by_id(13)
        
        assert result is None


class TestBGGRanksServiceSearchByName:
    """測試 search_by_name 方法"""
    
    @patch.object(BGGRanksService, '_get_connection')
    def test_search_by_name_found(self, mock_conn):
        """測試按名稱搜尋 - 找到"""
        mock_cursor = MagicMock()
        mock_cursor.fetchall.return_value = [
            {'bgg_id': 13, 'name': 'Catan', 'rank': 50},
            {'bgg_id': 14, 'name': 'Catan Expansion', 'rank': 100}
        ]
        mock_connection = MagicMock()
        mock_connection.cursor.return_value = mock_cursor
        mock_conn.return_value = mock_connection
        
        service = BGGRanksService()
        results = service.search_by_name("Catan")
        
        assert len(results) == 2
    
    @patch.object(BGGRanksService, '_get_connection')
    def test_search_by_name_not_found(self, mock_conn):
        """測試按名稱搜尋 - 未找到"""
        mock_cursor = MagicMock()
        mock_cursor.fetchall.return_value = []
        mock_connection = MagicMock()
        mock_connection.cursor.return_value = mock_cursor
        mock_conn.return_value = mock_connection
        
        service = BGGRanksService()
        results = service.search_by_name("NonexistentGame")
        
        assert results == []


class TestBGGRanksServiceGetTopGames:
    """測試 get_top_games 方法"""
    
    @patch.object(BGGRanksService, '_get_connection')
    def test_get_top_games(self, mock_conn):
        """測試取得 Top N 遊戲"""
        mock_cursor = MagicMock()
        mock_cursor.fetchall.return_value = [
            {'bgg_id': 1, 'name': 'Game 1', 'rank': 1},
            {'bgg_id': 2, 'name': 'Game 2', 'rank': 2}
        ]
        mock_connection = MagicMock()
        mock_connection.cursor.return_value = mock_cursor
        mock_conn.return_value = mock_connection
        
        service = BGGRanksService()
        results = service.get_top_games(limit=10)
        
        assert len(results) == 2


class TestBGGRanksServiceGetStats:
    """測試 get_stats 方法"""
    
    @patch.object(BGGRanksService, '_get_connection')
    def test_get_stats(self, mock_conn):
        """測試取得統計資訊"""
        mock_cursor = MagicMock()
        mock_cursor.fetchone.side_effect = [
            {'count': 100000},
            {'count': 90000},
            {'count': 10000},
            {'latest': '2024-01-01'}
        ]
        mock_connection = MagicMock()
        mock_connection.cursor.return_value = mock_cursor
        mock_conn.return_value = mock_connection
        
        service = BGGRanksService()
        stats = service.get_stats()
        
        assert 'total_games' in stats
    
    @patch.object(BGGRanksService, '_get_connection')
    def test_get_stats_error(self, mock_conn):
        """測試統計資訊錯誤"""
        mock_conn.side_effect = Exception("Database error")
        
        service = BGGRanksService()
        stats = service.get_stats()
        
        assert stats == {}
