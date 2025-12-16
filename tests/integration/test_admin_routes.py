"""
測試 app/blueprints/admin/routes.py 擴展測試
"""
import pytest
from unittest.mock import patch, MagicMock


class TestAdminVerify:
    """測試管理員驗證端點"""
    
    def test_verify_success(self, client):
        """測試驗證成功"""
        response = client.post('/api/admin/verify', json={
            'password': 'admin123'
        })
        
        assert response.status_code == 200
        data = response.get_json()
        assert data['success'] is True
    
    def test_verify_wrong_password(self, client):
        """測試驗證失敗"""
        response = client.post('/api/admin/verify', json={
            'password': 'wrong'
        })
        
        assert response.status_code == 200
        data = response.get_json()
        assert data['success'] is False
    
    def test_verify_empty_password(self, client):
        """測試空密碼驗證"""
        response = client.post('/api/admin/verify', json={
            'password': ''
        })
        
        assert response.status_code == 200
        data = response.get_json()
        assert data['success'] is False

