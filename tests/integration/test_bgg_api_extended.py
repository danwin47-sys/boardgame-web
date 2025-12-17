"""
測試 app/blueprints/api/bgg.py 的擴展測試
涵蓋更多端點和成功案例
"""
import pytest
from unittest.mock import patch, MagicMock
from flask import Flask

class TestBGGOurHotGames:
    """測試 /our-hot-games 端點"""
    
    @patch('app.blueprints.api.bgg.get_bgg_service')
    @patch('app.blueprints.api.bgg.get_manager')
    def test_get_our_hot_games_success(self, mock_get_manager, mock_get_bgg_service, client):
        """測試成功獲取館藏熱門遊戲"""
        # Mock Manager
        mock_manager = MagicMock()
        mock_get_manager.return_value = mock_manager
        
        # Mock BGG Service
        mock_bgg_service = MagicMock()
        mock_bgg_service.get_our_hot_games.return_value = [
            {'id': 1, 'name': 'Game 1', 'rank': 1},
            {'id': 2, 'name': 'Game 2', 'rank': 2}
        ]
        mock_get_bgg_service.return_value = mock_bgg_service
        
        response = client.get('/api/bgg/our-hot-games')
        
        assert response.status_code == 200
        data = response.get_json()
        assert data['success'] is True
        assert len(data['games']) == 2
        assert data['total'] == 2

    @patch('app.blueprints.api.bgg.get_bgg_service')
    @patch('app.blueprints.api.bgg.get_manager')
    def test_get_our_hot_games_error(self, mock_get_manager, mock_get_bgg_service, client):
        """測試獲取館藏熱門遊戲失敗"""
        mock_get_manager.side_effect = Exception("Database error")
        
        response = client.get('/api/bgg/our-hot-games')
        
        assert response.status_code == 500
        data = response.get_json()
        assert data['success'] is False


class TestBGGRecommendationsExtended:
    """測試 /recommendations 端點的擴展測試"""
    
    @patch('app.blueprints.api.bgg.get_bgg_service')
    @patch('app.blueprints.api.bgg.get_manager')
    def test_get_recommendations_success(self, mock_get_manager, mock_get_bgg_service, client):
        """測試成功獲取推薦"""
        # Mock Manager
        mock_manager = MagicMock()
        mock_manager.client.load_bgg_recommendations.return_value = [123, 456]
        mock_manager.load_data.return_value = [
            {'name': '中文遊戲', 'bgg_id': 123}
        ]
        mock_get_manager.return_value = mock_manager
        
        # Mock BGG Service
        mock_bgg_service = MagicMock()
        mock_bgg_service.get_game_details.side_effect = lambda x: {'id': x, 'name': f'Game {x}'}
        mock_get_bgg_service.return_value = mock_bgg_service
        
        response = client.get('/api/bgg/recommendations?category=party')
        
        assert response.status_code == 200
        data = response.get_json()
        assert data['success'] is True
        assert len(data['games']) == 2
        # 檢查中文名稱是否被加入
        assert data['games'][0]['chinese_name'] == '中文遊戲'

    @patch('app.blueprints.api.bgg.get_bgg_service')
    @patch('app.blueprints.api.bgg.get_manager')
    def test_get_recommendations_empty(self, mock_get_manager, mock_get_bgg_service, client):
        """測試沒有推薦資料"""
        mock_manager = MagicMock()
        mock_manager.client.load_bgg_recommendations.return_value = []
        mock_get_manager.return_value = mock_manager
        
        response = client.get('/api/bgg/recommendations?category=party')
        
        assert response.status_code == 200
        data = response.get_json()
        assert data['success'] is True
        assert data['games'] == []


class TestBGGCollection:
    """測試 /collection 端點"""
    
    @patch('app.blueprints.api.bgg.get_bgg_service')
    @patch('app.blueprints.api.bgg.get_manager')
    def test_add_to_collection_success(self, mock_get_manager, mock_get_bgg_service, client):
        """測試成功加入館藏"""
        # Mock Manager
        mock_manager = MagicMock()
        mock_manager.load_data.return_value = [] # 沒有重複
        mock_manager.client.add_new_game.return_value = True
        mock_get_manager.return_value = mock_manager
        
        # Mock BGG Service
        mock_bgg_service = MagicMock()
        mock_bgg_service.get_game_details.return_value = {
            'name': 'New Game', 'players_display': '2-4', 'image': 'url', 'thumbnail': 'url'
        }
        mock_get_bgg_service.return_value = mock_bgg_service
        
        response = client.post('/api/bgg/collection', json={'game_id': 123})
        
        assert response.status_code == 200
        data = response.get_json()
        assert data['success'] is True
        assert '已成功將' in data['message']

    @patch('app.blueprints.api.bgg.get_bgg_service')
    @patch('app.blueprints.api.bgg.get_manager')
    def test_add_to_collection_duplicate(self, mock_get_manager, mock_get_bgg_service, client):
        """測試重複加入"""
        # Mock Manager
        mock_manager = MagicMock()
        mock_manager.load_data.return_value = [{'name': 'Existing Game', 'bgg_id': 123}]
        mock_get_manager.return_value = mock_manager
        
        response = client.post('/api/bgg/collection', json={'game_id': 123})
        
        assert response.status_code == 409
        data = response.get_json()
        assert data['success'] is False
        assert data['duplicate'] is True

    @patch('app.blueprints.api.bgg.get_bgg_service')
    @patch('app.blueprints.api.bgg.get_manager')
    def test_add_to_collection_force(self, mock_get_manager, mock_get_bgg_service, client):
        """測試強制加入重複遊戲"""
        # Mock Manager
        mock_manager = MagicMock()
        mock_manager.load_data.return_value = [{'name': 'Existing Game', 'bgg_id': 123}]
        mock_manager.client.add_new_game.return_value = True
        mock_get_manager.return_value = mock_manager
        
        # Mock BGG Service
        mock_bgg_service = MagicMock()
        mock_bgg_service.get_game_details.return_value = {'name': 'Existing Game'}
        mock_get_bgg_service.return_value = mock_bgg_service
        
        response = client.post('/api/bgg/collection', json={'game_id': 123, 'force': True})
        
        assert response.status_code == 200
        data = response.get_json()
        assert data['success'] is True


class TestBGGLinkingExtended:
    """測試連結功能的擴展測試"""
    
    @patch('app.blueprints.api.bgg.get_bgg_service')
    @patch('app.blueprints.api.bgg.get_manager')
    def test_link_game_success(self, mock_get_manager, mock_get_bgg_service, client):
        """測試成功連結遊戲"""
        # Mock Manager
        mock_manager = MagicMock()
        mock_manager.load_data.return_value = [{'name': 'My Game'}]
        mock_manager.client.update_game_bgg_id.return_value = True
        mock_get_manager.return_value = mock_manager
        
        # Mock BGG Service
        mock_bgg_service = MagicMock()
        mock_bgg_service.get_game_details.return_value = {'thumbnail': 'url'}
        mock_get_bgg_service.return_value = mock_bgg_service
        
        response = client.post('/api/bgg/games/link/My%20Game', json={'bgg_id': 123})
        
        assert response.status_code == 200
        data = response.get_json()
        assert data['success'] is True

    @patch('app.blueprints.api.bgg.get_manager')
    def test_unlink_game_success(self, mock_get_manager, client):
        """測試成功取消連結"""
        mock_manager = MagicMock()
        mock_manager.client.update_game_bgg_id.return_value = True
        mock_get_manager.return_value = mock_manager
        
        response = client.delete('/api/bgg/games/link/My%20Game')
        
        assert response.status_code == 200
        data = response.get_json()
        assert data['success'] is True
