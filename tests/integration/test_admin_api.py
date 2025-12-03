"""
整合測試：Admin API 端點
"""
import pytest
import json


@pytest.mark.integration
@pytest.mark.api
class TestAdminAPI:
    """測試管理員相關的 API 端點"""
    
    def test_admin_login_success(self, client):
        """測試管理員登入成功"""
        response = client.post('/api/admin-login',
                              data=json.dumps({'password': 'admin123'}),
                              content_type='application/json')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['success'] == True
        assert 'token' in data
    
    def test_admin_login_failure(self, client):
        """測試管理員登入失敗"""
        response = client.post('/api/admin-login',
                              data=json.dumps({'password': 'wrong_password'}),
                              content_type='application/json')
        
        assert response.status_code == 401
        data = json.loads(response.data)
        assert data['success'] == False
    
    def test_batch_borrow_missing_data(self, client):
        """測試批次借出缺少資料"""
        response = client.post('/api/batch-borrow',
                              data=json.dumps({}),
                              content_type='application/json')
        
        assert response.status_code == 400
        data = json.loads(response.data)
        assert data['success'] == False
    
    def test_batch_return_missing_data(self, client):
        """測試批次歸還缺少資料"""
        response = client.post('/api/batch-return',
                              data=json.dumps({}),
                              content_type='application/json')
        
        assert response.status_code == 400
        data = json.loads(response.data)
        assert data['success'] == False
