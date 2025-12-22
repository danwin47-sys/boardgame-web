"""
整合測試：Main 路由
"""
import pytest
import json


@pytest.mark.integration
class TestMainRoutes:
    """測試主要路由端點"""
    
    def test_home_page(self, client):
        """測試首頁"""
        response = client.get('/')
        assert response.status_code == 200
    
    def test_favicon(self, client):
        """測試 favicon"""
        response = client.get('/favicon.ico')
        # 可能返回 200 或 404，取決於檔案是否存在
        assert response.status_code in [200, 404]
    
    def test_health_check(self, client):
        """測試健康檢查端點"""
        response = client.get('/api/health')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['status'] == 'ok'
        assert 'timestamp' in data
    
    def test_sys_info(self, client):
        """測試系統資訊端點"""
        response = client.get('/api/sys_info')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert isinstance(data, dict)
        assert 'cwd' in data or 'error' in data
    
    def test_404_not_found(self, client):
        """測試 404 錯誤處理"""
        response = client.get('/nonexistent-path')
        assert response.status_code == 404
