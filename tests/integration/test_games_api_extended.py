"""
測試 games API - 提升覆蓋率從 41% 到 70%+
"""
import pytest
import json
from unittest.mock import MagicMock, patch


class TestGamesAPIGet:
    """測試 GET /api/games 端點"""
    
    @patch('app.blueprints.api.games.game_facade')
    def test_get_all_games_success(self, mock_facade, client):
        """測試取得所有遊戲 - 成功"""
        mock_facade.get_all_games.return_value = [
            {'name': 'Catan', 'status': '可借'},
            {'name': 'Gloomhaven', 'status': '借出'}
        ]
        
        response = client.get('/api/games')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['success'] is True
        assert len(data['games']) == 2
    
    @patch('app.blueprints.api.games.game_facade')
    def test_get_all_games_error(self, mock_facade, client):
        """測試取得所有遊戲 - 錯誤"""
        mock_facade.get_all_games.side_effect = Exception("Database error")
        
        response = client.get('/api/games')
        
        assert response.status_code == 500


class TestGamesAPIPost:
    """測試 POST /api/games 端點"""
    
    @patch('app.blueprints.api.games.game_facade')
    def test_add_game_success(self, mock_facade, client):
        """測試新增遊戲 - 成功"""
        mock_facade.add_game.return_value = True
        
        game_data = {'name': '新遊戲', 'status': '可借'}
        response = client.post(
            '/api/games',
            data=json.dumps(game_data),
            content_type='application/json'
        )
        
        assert response.status_code == 201
    
    @patch('app.blueprints.api.games.game_facade')
    def test_add_game_missing_name(self, mock_facade, client):
        """測試新增遊戲 - 缺少名稱"""
        response = client.post(
            '/api/games',
            data=json.dumps({'status': '可借'}),
            content_type='application/json'
        )
        
        assert response.status_code == 400
    
    @patch('app.blueprints.api.games.game_facade')
    def test_add_game_error(self, mock_facade, client):
        """測試新增遊戲 - 錯誤"""
        mock_facade.add_game.return_value = False
        
        game_data = {'name': '新遊戲'}
        response = client.post(
            '/api/games',
            data=json.dumps(game_data),
            content_type='application/json'
        )
        
        assert response.status_code == 500


class TestGamesAPIPut:
    """測試 PUT /api/games/<name> 端點"""
    
    @patch('app.blueprints.api.games.game_facade')
    def test_update_game_success(self, mock_facade, client):
        """測試更新遊戲 - 成功"""
        mock_facade.update_game.return_value = True
        
        update_data = {'status': '借出', 'borrower': 'John'}
        response = client.put(
            '/api/games/Catan',
            data=json.dumps(update_data),
            content_type='application/json'
        )
        
        assert response.status_code == 200
    
    @patch('app.blueprints.api.games.game_facade')
    def test_update_game_not_found(self, mock_facade, client):
        """測試更新遊戲 - 找不到"""
        mock_facade.update_game.return_value = False
        
        response = client.put(
            '/api/games/NonExistent',
            data=json.dumps({'status': '借出'}),
            content_type='application/json'
        )
        
        assert response.status_code == 404


class TestGamesAPIDelete:
    """測試 DELETE /api/games/<name> 端點"""
    
    @patch('app.blueprints.api.games.game_facade')
    def test_delete_game_success(self, mock_facade, client):
        """測試刪除遊戲 - 成功"""
        mock_facade.delete_game.return_value = True
        
        response = client.delete('/api/games/OldGame')
        
        assert response.status_code == 200
    
    @patch('app.blueprints.api.games.game_facade')
    def test_delete_game_not_found(self, mock_facade, client):
        """測試刪除遊戲 - 找不到"""
        mock_facade.delete_game.return_value = False
        
        response = client.delete('/api/games/NonExistent')
        
        assert response.status_code == 404
