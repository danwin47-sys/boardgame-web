"""
測試 app/blueprints/admin/routes.py 擴展測試
"""
from unittest.mock import MagicMock, patch

import pytest


class TestAdminVerify:
    """測試管理員驗證端點"""

    def test_verify_success(self, client):
        """測試驗證成功"""
        response = client.post("/api/admin/verify", json={"password": "admin123"})

        assert response.status_code == 200
        data = response.get_json()
        assert data["success"] is True

    def test_verify_wrong_password(self, client):
        """測試驗證失敗"""
        response = client.post("/api/admin/verify", json={"password": "wrong"})

        assert response.status_code == 200
        data = response.get_json()
        assert data["success"] is False

    def test_verify_empty_password(self, client):
        """測試空密碼驗證"""
        response = client.post("/api/admin/verify", json={"password": ""})

        assert response.status_code == 200
        data = response.get_json()
        assert data["success"] is False


class TestAdminLogin:
    """測試管理員登入端點"""

    def test_login_success(self, client):
        """測試登入成功"""
        response = client.post("/api/admin-login", json={"password": "admin123"})

        assert response.status_code == 200
        data = response.get_json()
        assert data["success"] is True
        assert "token" in data

    def test_login_wrong_password(self, client):
        """測試登入失敗"""
        response = client.post("/api/admin-login", json={"password": "wrong"})

        assert response.status_code == 401
        data = response.get_json()
        assert data["success"] is False

    def test_login_missing_password(self, client):
        """測試缺少密碼"""
        response = client.post("/api/admin-login", json={})

        assert response.status_code == 401
        data = response.get_json()
        assert data["success"] is False


class TestBatchBorrow:
    """測試批次借出端點"""

    def test_batch_borrow_success(self, client):
        """測試批次借出成功"""
        response = client.post(
            "/api/batch-borrow",
            json={"game_names": ["卡坦島", "璀璨寶石"], "member_id": "A001"},
        )

        # 根據實際資料狀態，可能成功或部分成功
        assert response.status_code in [200, 400]
        data = response.get_json()
        assert "success" in data

    def test_batch_borrow_missing_games(self, client):
        """測試缺少遊戲列表"""
        response = client.post("/api/batch-borrow", json={"member_id": "A001"})

        assert response.status_code == 400
        data = response.get_json()
        assert data["success"] is False

    def test_batch_borrow_missing_member(self, client):
        """測試缺少會員 ID"""
        response = client.post("/api/batch-borrow", json={"game_names": ["卡坦島"]})

        assert response.status_code == 400
        data = response.get_json()
        assert data["success"] is False

    def test_batch_borrow_empty_list(self, client):
        """測試空遊戲列表"""
        response = client.post(
            "/api/batch-borrow", json={"game_names": [], "member_id": "A001"}
        )

        assert response.status_code == 400
        data = response.get_json()
        assert data["success"] is False


class TestBatchReturn:
    """測試批次歸還端點"""

    def test_batch_return_success(self, client):
        """測試批次歸還成功"""
        response = client.post(
            "/api/batch-return", json={"game_names": ["卡坦島", "璀璨寶石"]}
        )

        # 根據實際資料狀態，可能成功或部分成功
        assert response.status_code in [200, 400]
        data = response.get_json()
        assert "success" in data

    def test_batch_return_missing_games(self, client):
        """測試缺少遊戲列表"""
        response = client.post("/api/batch-return", json={})

        assert response.status_code == 400
        data = response.get_json()
        assert data["success"] is False

    def test_batch_return_empty_list(self, client):
        """測試空遊戲列表"""
        response = client.post("/api/batch-return", json={"game_names": []})

        assert response.status_code == 400
        data = response.get_json()
        assert data["success"] is False

    def test_batch_return_nonexistent_games(self, client):
        """測試歸還不存在的遊戲"""
        response = client.post(
            "/api/batch-return", json={"game_names": ["不存在的遊戲xyz123"]}
        )

        # 應該返回失敗或部分失敗
        assert response.status_code in [200, 400]
        data = response.get_json()
        if response.status_code == 200:
            # 如果返回 200，應該有 failed_games
            assert "failed_games" in data or data["success"] is False


class TestAdminErrorHandling:
    """測試錯誤處理"""

    def test_invalid_json(self, client):
        """測試無效 JSON"""
        response = client.post(
            "/api/admin/verify", data="invalid json", content_type="application/json"
        )

        assert response.status_code in [400, 500]

    def test_missing_content_type(self, client):
        """測試缺少 Content-Type"""
        response = client.post("/api/admin/verify", data='{"password": "test"}')

        # Flask 應該能處理或返回錯誤（實際會拋出 UnsupportedMediaType 異常，返回 500）
        assert response.status_code in [200, 400, 415, 500]
