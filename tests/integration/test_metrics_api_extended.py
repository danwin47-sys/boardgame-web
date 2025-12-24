"""
測試 metrics API - 提升覆蓋率從 48% 到 70%+
"""
import pytest
import json
from unittest.mock import MagicMock, patch


class TestMetricsAPIGameStats:
    """測試遊戲統計 API"""
    
    @patch('app.blueprints.api.metrics.game_facade')
    def test_get_game_stats_success(self, mock_facade, client):
        """測試取得遊戲統計 - 成功"""
        mock_facade.get_all_games.return_value = [
            {'status': '可借', 'is_expansion': '0'},
            {'status': '可借', 'is_expansion': '1'},
            {'status': '借出', 'is_expansion': '0'},
        ]
        
        response = client.get('/api/metrics/game-stats')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['success'] is True
        assert 'total' in data
        assert 'available' in data
        assert 'borrowed' in data
    
    @patch('app.blueprints.api.metrics.game_facade')
    def test_get_game_stats_error(self, mock_facade, client):
        """測試取得遊戲統計 - 錯誤"""
        mock_facade.get_all_games.side_effect = Exception("Error")
        
        response = client.get('/api/metrics/game-stats')
        
        assert response.status_code == 500


class TestMetricsAPIBorrowStats:
    """測試借閱統計 API"""
    
    @patch('app.blueprints.api.metrics.game_facade')
    def test_get_borrow_stats_success(self, mock_facade, client):
        """測試取得借閱統計 - 成功"""
        mock_facade.get_all_games.return_value = [
            {'status': '借出', 'borrower': 'Alice', 'borrower_id': '001'},
            {'status': '借出', 'borrower': 'Bob', 'borrower_id': '002'},
            {'status': '可借'},
        ]
        
        response = client.get('/api/metrics/borrow-stats')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['success'] is True
        assert 'total_borrowed' in data
    
    @patch('app.blueprints.api.metrics.game_facade')
    def test_get_borrow_stats_error(self, mock_facade, client):
        """測試取得借閱統計 - 錯誤"""
        mock_facade.get_all_games.side_effect = Exception("Error")
        
        response = client.get('/api/metrics/borrow-stats')
        
        assert response.status_code == 500


class TestMetricsAPIExpansionStats:
    """測試擴充統計 API"""
    
    @patch('app.blueprints.api.metrics.expansion_service')
    @patch('app.blueprints.api.metrics.game_facade')
    def test_get_expansion_stats_success(self, mock_facade, mock_exp_service, client):
        """測試取得擴充統計 - 成功"""
        mock_facade.get_all_games.return_value = [
            {'name': 'Catan', 'is_expansion': '0'},
            {'name': 'Catan Exp', 'is_expansion': '1', 'parent_game': 'Catan'},
        ]
        
        response = client.get('/api/metrics/expansion-stats')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['success'] is True
        assert 'total_expansions' in data
    
    @patch('app.blueprints.api.metrics.game_facade')
    def test_get_expansion_stats_error(self, mock_facade, client):
        """測試取得擴充統計 - 錯誤"""
        mock_facade.get_all_games.side_effect = Exception("Error")
        
        response = client.get('/api/metrics/expansion-stats')
        
        assert response.status_code == 500


class TestMetricsAPITopBorrowers:
    """測試熱門借閱者 API"""
    
    @patch('app.blueprints.api.metrics.game_facade')
    def test_get_top_borrowers_success(self, mock_facade, client):
        """測試取得熱門借閱者 - 成功"""
        mock_facade.get_all_games.return_value = [
            {'status': '借出', 'borrower': 'Alice', 'borrower_id': '001'},
            {'status': '借出', 'borrower': 'Alice', 'borrower_id': '001'},
            {'status': '借出', 'borrower': 'Bob', 'borrower_id': '002'},
        ]
        
        response = client.get('/api/metrics/top-borrowers')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['success'] is True
        assert 'top_borrowers' in data
    
    @patch('app.blueprints.api.metrics.game_facade')
    def test_get_top_borrowers_with_limit(self, mock_facade, client):
        """測試取得熱門借閱者 - 有限制"""
        mock_facade.get_all_games.return_value = []
        
        response = client.get('/api/metrics/top-borrowers?limit=5')
        
        assert response.status_code == 200
    
    @patch('app.blueprints.api.metrics.game_facade')
    def test_get_top_borrowers_error(self, mock_facade, client):
        """測試取得熱門借閱者 - 錯誤"""
        mock_facade.get_all_games.side_effect = Exception("Error")
        
        response = client.get('/api/metrics/top-borrowers')
        
        assert response.status_code == 500
