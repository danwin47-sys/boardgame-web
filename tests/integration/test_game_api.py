"""
整合測試：Game API 端點
"""
import pytest
import json


@pytest.mark.integration
@pytest.mark.api
class TestGameAPI:
    """測試遊戲相關的 API 端點"""
    
    def test_get_games(self, client):
        """測試獲取桌遊列表"""
        response = client.get('/api/games')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert isinstance(data, list)
    
    def test_borrow_game_missing_data(self, client):
        """測試借桌遊時缺少資料"""
        response = client.post('/api/borrow', 
                              data=json.dumps({}),
                              content_type='application/json')
        
        assert response.status_code == 400
        data = json.loads(response.data)
        assert data['success'] == False
    
    def test_borrow_game_missing_fields(self, client):
        """測試借桌遊時缺少必要欄位"""
        response = client.post('/api/borrow',
                              data=json.dumps({'name': '測試桌遊'}),
                              content_type='application/json')
        
        assert response.status_code == 400
        data = json.loads(response.data)
        assert data['success'] == False
        assert '缺少必要欄位' in data['error']
    
    def test_return_game_missing_name(self, client):
        """測試歸還桌遊時缺少名稱"""
        response = client.post('/api/return',
                              data=json.dumps({}),
                              content_type='application/json')
        
        assert response.status_code == 400
        data = json.loads(response.data)
        assert data['success'] == False


@pytest.mark.integration
@pytest.mark.api
class TestMemberAPI:
    """測試社員相關的 API 端點"""
    
    def test_get_members(self, client):
        """測試獲取社員列表"""
        response = client.get('/api/members')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert isinstance(data, list)
