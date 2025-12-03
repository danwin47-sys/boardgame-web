"""
整合測試：Member API 端點
"""
import pytest
import json


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
