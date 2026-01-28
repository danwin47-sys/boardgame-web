"""
測試 Auth Service
"""
from unittest.mock import MagicMock, Mock, patch

import jwt
import pytest

from core.auth_service import AuthService


class TestAuthService:
    """測試 Auth Service"""

    @pytest.fixture
    def mock_sheets_client(self):
        """建立 mock SheetsClient"""
        return Mock()

    @pytest.fixture
    def auth_service(self, mock_sheets_client):
        """建立 AuthService 實例"""
        with patch.dict(
            "os.environ",
            {
                "LINE_CHANNEL_ID": "test_channel_id",
                "LINE_CHANNEL_SECRET": "test_secret",
                "LINE_CALLBACK_URL": "http://localhost:5000/auth/line/callback",
            },
        ):
            service = AuthService(mock_sheets_client)
            return service

    @pytest.fixture
    def app_context(self):
        """建立 Flask app context"""
        from app import create_app

        app = create_app("testing")
        with app.app_context():
            with app.test_request_context():
                yield app

    def test_init(self, mock_sheets_client):
        """測試 AuthService 初始化"""
        with patch.dict(
            "os.environ",
            {
                "LINE_CHANNEL_ID": "test_id",
                "LINE_CHANNEL_SECRET": "test_secret",
                "LINE_CALLBACK_URL": "http://test.com/callback",
            },
        ):
            service = AuthService(mock_sheets_client)

            assert service.sheets_client == mock_sheets_client
            assert service.channel_id == "test_id"
            assert service.channel_secret == "test_secret"
            assert service.callback_url == "http://test.com/callback"

    def test_generate_login_url(self, auth_service, app_context):
        """測試生成 LINE Login URL"""
        from flask import session

        url = auth_service.generate_login_url()

        # 驗證 URL 格式
        assert "https://access.line.me/oauth2/v2.1/authorize" in url
        assert "response_type=code" in url
        assert "client_id=test_channel_id" in url
        assert "redirect_uri=http://localhost:5000/auth/line/callback" in url
        assert "scope=openid profile" in url
        assert "state=" in url
        assert "nonce=" in url

        # 驗證 session 中存儲了 state 和 nonce
        assert "oauth_state" in session
        assert "oauth_nonce" in session
        assert len(session["oauth_state"]) > 0
        assert len(session["oauth_nonce"]) > 0

    def test_handle_callback_invalid_state(self, auth_service, app_context):
        """測試 callback 處理 - state 不匹配"""
        from flask import session

        session["oauth_state"] = "correct_state"
        session["oauth_nonce"] = "test_nonce"

        success, profile, error = auth_service.handle_callback(
            "test_code", "wrong_state"
        )

        assert success is False
        assert profile is None
        assert error == "Invalid state parameter"

    @patch("core.auth_service.requests.post")
    def test_handle_callback_no_id_token(self, mock_post, auth_service, app_context):
        """測試 callback 處理 - 沒有 id_token"""
        from flask import session

        session["oauth_state"] = "test_state"
        session["oauth_nonce"] = "test_nonce"

        # Mock API 返回沒有 id_token
        mock_response = Mock()
        mock_response.json.return_value = {"access_token": "test_token"}
        mock_post.return_value = mock_response

        success, profile, error = auth_service.handle_callback(
            "test_code", "test_state"
        )

        assert success is False
        assert profile is None
        assert error == "No id_token found"

    @patch("core.auth_service.requests.post")
    @patch("core.auth_service.jwt.decode")
    def test_handle_callback_success(
        self, mock_jwt_decode, mock_post, auth_service, app_context
    ):
        """測試 callback 處理 - 成功"""
        from flask import session

        session["oauth_state"] = "test_state"
        session["oauth_nonce"] = "test_nonce"

        # Mock API 返回
        mock_response = Mock()
        mock_response.json.return_value = {"id_token": "test_id_token"}
        mock_post.return_value = mock_response

        # Mock JWT 解碼
        mock_jwt_decode.return_value = {
            "sub": "U123456",
            "name": "測試用戶",
            "picture": "http://example.com/pic.jpg",
            "nonce": "test_nonce",
        }

        success, profile, error = auth_service.handle_callback(
            "test_code", "test_state"
        )

        assert success is True
        assert profile is not None
        assert profile["line_user_id"] == "U123456"
        assert profile["name"] == "測試用戶"
        assert profile["picture"] == "http://example.com/pic.jpg"
        assert error is None

    @patch("core.auth_service.requests.post")
    @patch("core.auth_service.jwt.decode")
    def test_handle_callback_invalid_nonce(
        self, mock_jwt_decode, mock_post, auth_service, app_context
    ):
        """測試 callback 處理 - nonce 不匹配"""
        from flask import session

        session["oauth_state"] = "test_state"
        session["oauth_nonce"] = "correct_nonce"

        # Mock API 返回
        mock_response = Mock()
        mock_response.json.return_value = {"id_token": "test_id_token"}
        mock_post.return_value = mock_response

        # Mock JWT 解碼 - nonce 不匹配
        mock_jwt_decode.return_value = {
            "sub": "U123456",
            "name": "測試用戶",
            "nonce": "wrong_nonce",
        }

        success, profile, error = auth_service.handle_callback(
            "test_code", "test_state"
        )

        assert success is False
        assert profile is None
        assert error == "Invalid nonce"

    @patch("core.auth_service.requests.post")
    def test_handle_callback_api_error(self, mock_post, auth_service, app_context):
        """測試 callback 處理 - API 錯誤"""
        from flask import session

        session["oauth_state"] = "test_state"
        session["oauth_nonce"] = "test_nonce"

        # Mock API 拋出異常
        mock_post.side_effect = Exception("API Error")

        success, profile, error = auth_service.handle_callback(
            "test_code", "test_state"
        )

        assert success is False
        assert profile is None
        assert "API Error" in error

    def test_check_user_exists(self, auth_service, mock_sheets_client):
        """測試檢查用戶是否存在"""
        # Mock 返回用戶資料
        mock_sheets_client.get_user_by_line_id.return_value = {
            "id": "A001",
            "name": "測試用戶",
            "line_user_id": "U123456",
        }

        result = auth_service.check_user_exists("U123456")

        assert result is not None
        assert result["id"] == "A001"
        mock_sheets_client.get_user_by_line_id.assert_called_once_with("U123456")

    def test_check_user_not_exists(self, auth_service, mock_sheets_client):
        """測試檢查用戶不存在"""
        mock_sheets_client.get_user_by_line_id.return_value = None

        result = auth_service.check_user_exists("U999999")

        assert result is None
        mock_sheets_client.get_user_by_line_id.assert_called_once_with("U999999")

    def test_bind_student_id_success(self, auth_service, mock_sheets_client):
        """測試綁定工號 - 成功"""
        # Mock 工號存在且未綁定
        mock_sheets_client.get_user_by_student_id.return_value = {
            "id": "A001",
            "name": "測試用戶",
            "line_user_id": "",
        }
        mock_sheets_client.bind_user_to_line_id.return_value = True

        success, message = auth_service.bind_student_id("U123456", "A001")

        assert success is True
        assert message == "綁定成功！"
        mock_sheets_client.bind_user_to_line_id.assert_called_once_with(
            "A001", "U123456"
        )

    def test_bind_student_id_not_found(self, auth_service, mock_sheets_client):
        """測試綁定工號 - 工號不存在"""
        mock_sheets_client.get_user_by_student_id.return_value = None

        success, message = auth_service.bind_student_id("U123456", "NOTFOUND")

        assert success is False
        assert "找不到此工號" in message
        mock_sheets_client.bind_user_to_line_id.assert_not_called()

    def test_bind_student_id_already_bound(self, auth_service, mock_sheets_client):
        """測試綁定工號 - 已被其他帳號綁定"""
        # Mock 工號已被其他 LINE 帳號綁定
        mock_sheets_client.get_user_by_student_id.return_value = {
            "id": "A001",
            "name": "測試用戶",
            "line_user_id": "U999999",  # 不同的 LINE ID
        }

        success, message = auth_service.bind_student_id("U123456", "A001")

        assert success is False
        assert "已被其他 LINE 帳號綁定" in message
        mock_sheets_client.bind_user_to_line_id.assert_not_called()

    def test_bind_student_id_rebind_same_user(self, auth_service, mock_sheets_client):
        """測試綁定工號 - 重新綁定相同用戶（允許）"""
        # Mock 工號已被相同 LINE 帳號綁定
        mock_sheets_client.get_user_by_student_id.return_value = {
            "id": "A001",
            "name": "測試用戶",
            "line_user_id": "U123456",  # 相同的 LINE ID
        }
        mock_sheets_client.bind_user_to_line_id.return_value = True

        success, message = auth_service.bind_student_id("U123456", "A001")

        assert success is True
        assert message == "綁定成功！"

    def test_bind_student_id_bind_failed(self, auth_service, mock_sheets_client):
        """測試綁定工號 - 綁定操作失敗"""
        mock_sheets_client.get_user_by_student_id.return_value = {
            "id": "A001",
            "name": "測試用戶",
            "line_user_id": "",
        }
        mock_sheets_client.bind_user_to_line_id.return_value = False

        success, message = auth_service.bind_student_id("U123456", "A001")

        assert success is False
        assert "綁定失敗" in message
