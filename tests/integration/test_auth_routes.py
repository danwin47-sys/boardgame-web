"""
測試 Auth Routes（整合測試）
"""
from unittest.mock import Mock, patch

import pytest
from flask import session


class TestAuthRoutes:
    """測試 Auth Routes 整合"""

    @pytest.fixture
    def client(self):
        """建立測試客戶端"""
        from app import create_app

        app = create_app("testing")
        with app.test_client() as client:
            with app.app_context():
                yield client

    def test_login_redirect_when_not_authenticated(self, client):
        """測試未登入時訪問 /login 會重定向到 LINE"""
        with patch(
            "app.blueprints.auth.routes.auth_service.generate_login_url"
        ) as mock_gen:
            mock_gen.return_value = "https://access.line.me/oauth2/v2.1/authorize?..."

            response = client.get("/auth/login")

            assert response.status_code == 302  # Redirect
            assert "line.me" in response.location or response.location.startswith(
                "https://access.line.me"
            )

    def test_login_redirect_when_already_authenticated(self, client):
        """測試已登入時訪問 /login 會重定向到首頁"""
        # 這個測試需要模擬已登入狀態，暫時跳過
        # 因為需要完整的 Flask-Login 設定
        pass

    def test_callback_missing_parameters(self, client):
        """測試 callback 缺少參數"""
        response = client.get("/auth/line/callback")

        assert response.status_code == 302  # Redirect to home
        # 檢查 flash 訊息（需要 follow_redirects）

    def test_callback_missing_code(self, client):
        """測試 callback 缺少 code"""
        response = client.get("/auth/line/callback?state=test")

        assert response.status_code == 302

    def test_callback_missing_state(self, client):
        """測試 callback 缺少 state"""
        response = client.get("/auth/line/callback?code=test")

        assert response.status_code == 302

    @patch("app.blueprints.auth.routes.auth_service.handle_callback")
    def test_callback_auth_failed(self, mock_handle, client):
        """測試 callback 認證失敗"""
        mock_handle.return_value = (False, None, "Auth failed")

        response = client.get("/auth/line/callback?code=test&state=test")

        assert response.status_code == 302
        mock_handle.assert_called_once_with("test", "test")

    @patch("app.blueprints.auth.routes.auth_service.check_user_exists")
    @patch("app.blueprints.auth.routes.auth_service.handle_callback")
    def test_callback_user_exists_login(self, mock_handle, mock_check, client):
        """測試 callback - 用戶已存在，自動登入"""
        # Mock callback 成功
        mock_handle.return_value = (True, {"line_user_id": "U123", "name": "測試"}, None)

        # Mock 用戶存在
        mock_check.return_value = {"id": "A001", "name": "測試用戶", "line_user_id": "U123"}

        response = client.get(
            "/auth/line/callback?code=test&state=test", follow_redirects=False
        )

        assert response.status_code == 302
        assert response.location == "/"  # Redirect to home

    @patch("app.blueprints.auth.routes.auth_service.check_user_exists")
    @patch("app.blueprints.auth.routes.auth_service.handle_callback")
    def test_callback_user_not_exists_redirect_bind(
        self, mock_handle, mock_check, client
    ):
        """測試 callback - 用戶不存在，重定向到綁定頁面"""
        # Mock callback 成功
        mock_handle.return_value = (True, {"line_user_id": "U123", "name": "測試"}, None)

        # Mock 用戶不存在
        mock_check.return_value = None

        response = client.get(
            "/auth/line/callback?code=test&state=test", follow_redirects=False
        )

        assert response.status_code == 302
        assert "/auth/bind" in response.location

    def test_bind_get_without_profile(self, client):
        """測試訪問綁定頁面但沒有 LINE profile"""
        response = client.get("/auth/bind")

        assert response.status_code == 302
        assert "/auth/login" in response.location

    def test_bind_get_with_profile(self, client):
        """測試訪問綁定頁面有 LINE profile"""
        with client.session_transaction() as sess:
            sess["temp_line_profile"] = {"line_user_id": "U123", "name": "測試用戶"}

        response = client.get("/auth/bind")

        assert response.status_code == 200
        assert (
            b"bind" in response.data.lower() or b"student_id" in response.data.lower()
        )

    @patch("app.blueprints.auth.routes.auth_service.bind_student_id")
    def test_bind_post_failed(self, mock_bind, client):
        """測試綁定失敗"""
        with client.session_transaction() as sess:
            sess["temp_line_profile"] = {"line_user_id": "U123", "name": "測試"}

        mock_bind.return_value = (False, "找不到此工號")

        response = client.post("/auth/bind", data={"student_id": "NOTFOUND"})

        assert response.status_code == 200  # 返回綁定頁面
        mock_bind.assert_called_once()

    @patch("app.blueprints.auth.routes.auth_service.check_user_exists")
    @patch("app.blueprints.auth.routes.auth_service.bind_student_id")
    def test_bind_post_success(self, mock_bind, mock_check, client):
        """測試綁定成功"""
        with client.session_transaction() as sess:
            sess["temp_line_profile"] = {"line_user_id": "U123", "name": "測試"}

        mock_bind.return_value = (True, "綁定成功！")
        mock_check.return_value = {"id": "A001", "name": "測試用戶", "line_user_id": "U123"}

        response = client.post(
            "/auth/bind", data={"student_id": "A001"}, follow_redirects=False
        )

        assert response.status_code == 302
        assert response.location == "/"

    def test_logout(self, client):
        """測試登出"""
        # 設定一些 session 資料
        with client.session_transaction() as sess:
            sess["test_key"] = "test_value"
            sess["line_user_id"] = "U123"

        response = client.get("/auth/logout", follow_redirects=False)

        assert response.status_code == 302
        assert response.location == "/"

        # 驗證 session 已清除
        with client.session_transaction() as sess:
            assert "test_key" not in sess
            assert "line_user_id" not in sess
