"""
測試 core/member_service.py 模組 (使用 mock)
"""
from unittest.mock import MagicMock, patch

import pytest

from core.member_service import MemberService


class TestMemberService:
    """測試 MemberService"""

    def test_init(self):
        """測試初始化"""
        mock_client = MagicMock()
        service = MemberService(mock_client)

        assert service.client == mock_client

    def test_find_member_by_id_found(self):
        """測試按 ID 查找會員 - 找到"""
        mock_client = MagicMock()
        mock_client.load_members.return_value = [
            {"id": "A001", "name": "張三", "department": "資工系"},
            {"id": "A002", "name": "李四", "department": "電機系"},
        ]

        service = MemberService(mock_client)
        member = service.find_member_by_id("A001")

        assert member is not None
        assert member["id"] == "A001"
        assert member["name"] == "張三"

    def test_find_member_by_id_not_found(self):
        """測試按 ID 查找會員 - 未找到"""
        mock_client = MagicMock()
        mock_client.load_members.return_value = [{"id": "A001", "name": "張三"}]

        service = MemberService(mock_client)
        member = service.find_member_by_id("X999")

        assert member is None

    def test_find_member_by_id_empty_list(self):
        """測試會員列表為空"""
        mock_client = MagicMock()
        mock_client.load_members.return_value = []

        service = MemberService(mock_client)
        member = service.find_member_by_id("A001")

        assert member is None

    def test_find_member_by_name_found(self):
        """測試按姓名查找會員 - 找到"""
        mock_client = MagicMock()
        mock_client.load_members.return_value = [
            {"id": "A001", "name": "張三"},
            {"id": "A002", "name": "李四"},
        ]

        service = MemberService(mock_client)
        member = service.find_member_by_name("李四")

        assert member is not None
        assert member["name"] == "李四"

    def test_find_member_by_name_not_found(self):
        """測試按姓名查找會員 - 未找到"""
        mock_client = MagicMock()
        mock_client.load_members.return_value = [{"id": "A001", "name": "張三"}]

        service = MemberService(mock_client)
        member = service.find_member_by_name("王五")

        assert member is None

    def test_find_member_by_name_partial_match(self):
        """測試姓名部分匹配（不應該匹配）"""
        mock_client = MagicMock()
        mock_client.load_members.return_value = [{"id": "A001", "name": "張三"}]

        service = MemberService(mock_client)
        member = service.find_member_by_name("張")

        # 部分匹配不應該成功
        assert member is None
