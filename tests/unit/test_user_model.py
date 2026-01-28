"""
測試 User Model
"""
from unittest.mock import Mock, patch

import pytest

from core.user_model import User


class TestUserModel:
    """測試 User 模型"""

    def test_user_creation_with_id(self):
        """測試使用 id 建立 User"""
        user_data = {
            "id": "A001",
            "name": "測試用戶",
            "line_user_id": "U123456",
            "email": "test@example.com",
            "status": "社長",
        }

        user = User(user_data)

        assert user.id == "A001"
        assert user.name == "測試用戶"
        assert user.line_user_id == "U123456"
        assert user.email == "test@example.com"
        assert user.title == "社長"

    def test_user_creation_with_student_id(self):
        """測試使用 student_id 建立 User（向後兼容）"""
        user_data = {"student_id": "B002", "name": "學生用戶"}

        user = User(user_data)

        assert user.id == "B002"
        assert user.name == "學生用戶"

    def test_user_creation_with_defaults(self):
        """測試使用預設值建立 User"""
        user_data = {}

        user = User(user_data)

        assert user.id == ""
        assert user.name == "Unknown"
        assert user.line_user_id is None
        assert user.email is None
        assert user.title == ""  # status 預設為空字串，不是 None

    def test_is_active_normal_user(self):
        """測試一般用戶的 is_active"""
        user_data = {"id": "A001", "status": "社員"}
        user = User(user_data)

        assert user.is_active is True

    def test_is_active_inactive_user(self):
        """測試已退社用戶的 is_active"""
        user_data = {"id": "A001", "status": "已退社"}
        user = User(user_data)

        assert user.is_active is False

    def test_is_active_no_status(self):
        """測試沒有 status 的用戶"""
        user_data = {"id": "A001"}
        user = User(user_data)

        assert user.is_active is True

    def test_is_admin_president(self):
        """測試社長是管理員"""
        user_data = {"id": "A001", "status": "社長"}
        user = User(user_data)

        assert user.is_admin is True

    def test_is_admin_vice_president(self):
        """測試副社長是管理員"""
        user_data = {"id": "A002", "status": "副社長"}
        user = User(user_data)

        assert user.is_admin is True

    def test_is_admin_executive(self):
        """測試執行幹部是管理員"""
        user_data = {"id": "A003", "status": "執行幹部"}
        user = User(user_data)

        assert user.is_admin is True

    def test_is_admin_normal_member(self):
        """測試一般社員不是管理員"""
        user_data = {"id": "A004", "status": "社員"}
        user = User(user_data)

        assert user.is_admin is False

    def test_is_admin_no_title(self):
        """測試沒有頭銜的用戶不是管理員"""
        user_data = {"id": "A005"}
        user = User(user_data)

        assert user.is_admin is False

    @patch("core.user_model.SheetsClient")
    def test_get_user_found(self, mock_sheets_client_class):
        """測試 User.get() 找到用戶"""
        # Mock SheetsClient 實例
        mock_client = Mock()
        mock_sheets_client_class.return_value = mock_client

        # Mock 返回用戶資料
        mock_client.get_user_by_student_id.return_value = {
            "id": "A001",
            "name": "測試用戶",
            "status": "社長",
        }

        # 執行
        user = User.get("A001")

        # 驗證
        assert user is not None
        assert user.id == "A001"
        assert user.name == "測試用戶"
        assert user.is_admin is True
        mock_client.get_user_by_student_id.assert_called_once_with("A001")

    @patch("core.user_model.SheetsClient")
    def test_get_user_not_found(self, mock_sheets_client_class):
        """測試 User.get() 找不到用戶"""
        # Mock SheetsClient 實例
        mock_client = Mock()
        mock_sheets_client_class.return_value = mock_client

        # Mock 返回 None
        mock_client.get_user_by_student_id.return_value = None

        # 執行
        user = User.get("NOTFOUND")

        # 驗證
        assert user is None
        mock_client.get_user_by_student_id.assert_called_once_with("NOTFOUND")

    def test_user_is_authenticated(self):
        """測試 UserMixin 的 is_authenticated 屬性"""
        user_data = {"id": "A001", "name": "測試用戶"}
        user = User(user_data)

        # UserMixin 預設 is_authenticated 為 True
        assert user.is_authenticated is True

    def test_user_is_anonymous(self):
        """測試 UserMixin 的 is_anonymous 屬性"""
        user_data = {"id": "A001", "name": "測試用戶"}
        user = User(user_data)

        # UserMixin 預設 is_anonymous 為 False
        assert user.is_anonymous is False

    def test_user_get_id(self):
        """測試 UserMixin 的 get_id() 方法"""
        user_data = {"id": "A001", "name": "測試用戶"}
        user = User(user_data)

        # get_id() 應該返回 user.id
        assert user.get_id() == "A001"
