from typing import Optional, Dict, Any
from .sheets_client import SheetsClient
from .exceptions import MemberNotFoundException


class MemberService:
    """
    負責社員資料的查詢與驗證邏輯。
    """

    def __init__(self, sheets_client: SheetsClient):
        self.client = sheets_client

    def find_member_by_id(self, member_id: str) -> Optional[Dict[str, Any]]:
        """
        根據 ID 查詢社員

        Args:
            member_id: 社員 ID

        Returns:
            社員資料字典，若找不到則返回 None
        """
        members = self.client.load_members()
        target_id = str(member_id).strip()

        for m in members:
            if str(m.get("id", "")).strip() == target_id:
                return m
        return None

    def find_member_by_name(self, name: str) -> Optional[Dict[str, Any]]:
        """
        根據姓名查詢社員

        Args:
            name: 社員姓名

        Returns:
            社員資料字典，若找不到則返回 None
        """
        members = self.client.load_members()
        target_name = str(name).strip()

        for m in members:
            if str(m.get("name", "")).strip() == target_name:
                return m
        return None
