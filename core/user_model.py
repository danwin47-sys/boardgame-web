from typing import Any, Dict, Optional

from flask_login import UserMixin

from core.sheets_client import SheetsClient


class User(UserMixin):
    """
    Flask-Login User Model
    Adapts Google Sheets member data to Flask-Login's UserMixin interface.
    """

    def __init__(self, user_data: Dict[str, Any]):
        """
        Args:
            user_data: Dictionary containing user data from Google Sheets
                       Expected keys: 'id' (or 'student_id'), 'name', 'line_user_id', etc.
        """
        self.user_data = user_data
        # 優先使用 'id' 作為 User ID，這通常是工號
        self.id = str(user_data.get("id", user_data.get("student_id", "")))
        self.name = user_data.get("name", "Unknown")
        self.line_user_id = user_data.get("line_user_id")
        self.email = user_data.get("email")
        # 讀取 status 作為頭銜
        self.title = user_data.get("status", "")

    @property
    def is_active(self) -> bool:
        """Override UserMixin.is_active if you want to support banning users."""
        # 例如：檢查 status 是否為 "已退社"
        status = self.title.lower() if self.title else ""
        return status != "已退社"

    @property
    def is_admin(self) -> bool:
        """
        檢查是否具有管理員權限
        如果頭銜包含 '社長', '副社長', '執行幹部' 則自動視為管理員
        """
        if not self.title:
            return False

        admin_titles = ["社長", "副社長", "執行幹部"]
        return any(title in self.title for title in admin_titles)

    @staticmethod
    def get(user_id: str) -> Optional["User"]:
        """
        Static method to load a user by ID.
        Used by Flask-Login's user_loader.
        """
        client = SheetsClient()
        user_data = client.get_user_by_student_id(user_id)
        if user_data:
            return User(user_data)
        return None
