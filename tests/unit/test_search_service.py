"""
測試 core/search_service.py 模組
"""
from unittest.mock import MagicMock

import pytest

from core.constants import FIELD_NAME, FIELD_STATUS
from core.search_service import SearchService


class TestSearchServiceInit:
    """測試初始化"""

    def test_init(self):
        """測試初始化"""
        mock_client = MagicMock()
        mock_member_service = MagicMock()

        service = SearchService(mock_client, mock_member_service)

        assert service.client == mock_client
        assert service.member_service == mock_member_service
        assert service.similarity_threshold == 0.6


class TestSearchServiceFuzzyMatch:
    """測試模糊匹配邏輯"""

    def setup_method(self):
        self.service = SearchService(MagicMock(), MagicMock())

    def test_exact_match(self):
        """測試完全匹配"""
        assert self.service._fuzzy_match("卡坦島", "卡坦島") is True

    def test_substring_match(self):
        """測試部分匹配"""
        assert self.service._fuzzy_match("卡坦", "卡坦島") is True
        assert self.service._fuzzy_match("島", "卡坦島") is True

    def test_case_insensitive(self):
        """測試大小寫不敏感"""
        assert self.service._fuzzy_match("catan", "Catan") is True
        assert self.service._fuzzy_match("CATAN", "catan") is True

    def test_no_match(self):
        """測試不匹配"""
        assert self.service._fuzzy_match("卡坦島", "璀璨寶石") is False


class TestSearchServiceSearchGames:
    """測試遊戲搜尋"""

    def setup_method(self):
        self.mock_client = MagicMock()
        self.mock_member_service = MagicMock()
        self.service = SearchService(self.mock_client, self.mock_member_service)

    def test_search_games_exact_match(self):
        """測試精確匹配遊戲"""
        self.mock_client.load_games.return_value = [
            {FIELD_NAME: "卡坦島", FIELD_STATUS: "可用"},
            {FIELD_NAME: "璀璨寶石", FIELD_STATUS: "可用"},
        ]

        results = self.service.search_games("卡坦島")

        assert len(results) == 1
        assert results[0][FIELD_NAME] == "卡坦島"

    def test_search_games_partial_match(self):
        """測試部分匹配"""
        self.mock_client.load_games.return_value = [
            {FIELD_NAME: "卡坦島", FIELD_STATUS: "可用"},
            {FIELD_NAME: "卡坦島擴充", FIELD_STATUS: "可用"},
        ]

        results = self.service.search_games("卡坦")

        assert len(results) == 2

    def test_search_games_empty_query(self):
        """測試空查詢"""
        results = self.service.search_games("")

        assert len(results) == 0
        self.mock_client.load_games.assert_not_called()

    def test_search_games_no_results(self):
        """測試無結果"""
        self.mock_client.load_games.return_value = [
            {FIELD_NAME: "卡坦島", FIELD_STATUS: "可用"}
        ]

        results = self.service.search_games("不存在的遊戲")

        assert len(results) == 0


class TestSearchServiceSearchMembers:
    """測試會員搜尋"""

    def setup_method(self):
        self.mock_client = MagicMock()
        self.mock_member_service = MagicMock()
        self.service = SearchService(self.mock_client, self.mock_member_service)

    def test_search_members_by_name(self):
        """測試按姓名搜尋"""
        self.mock_client.load_members.return_value = [
            {"id": "A001", "name": "張三"},
            {"id": "A002", "name": "李四"},
        ]

        results = self.service.search_members("張三")

        assert len(results) == 1
        assert results[0]["name"] == "張三"

    def test_search_members_by_id(self):
        """測試按 ID 搜尋"""
        self.mock_client.load_members.return_value = [
            {"id": "A001", "name": "張三"},
            {"id": "B002", "name": "李四"},  # 使用不同前綴避免模糊匹配
        ]

        results = self.service.search_members("A001")

        assert len(results) == 1
        assert results[0]["id"] == "A001"

    def test_search_members_partial_match(self):
        """測試部分匹配"""
        self.mock_client.load_members.return_value = [
            {"id": "A001", "name": "張三"},
            {"id": "A002", "name": "張四"},
        ]

        results = self.service.search_members("張")

        assert len(results) == 2


class TestSearchServiceGlobalSearch:
    """測試全站搜尋"""

    def setup_method(self):
        self.mock_client = MagicMock()
        self.mock_member_service = MagicMock()
        self.service = SearchService(self.mock_client, self.mock_member_service)

    def test_global_search_success(self):
        """測試全站搜尋成功"""
        self.mock_client.load_games.return_value = [
            {FIELD_NAME: "卡坦島", FIELD_STATUS: "可用"}
        ]
        self.mock_client.load_members.return_value = [
            {"id": "A001", "name": "卡卡"}  # 使用包含"卡"的名字
        ]

        results = self.service.global_search("卡")

        assert "games" in results
        assert "members" in results
        assert "total" in results
        assert results["total"] == 2

    def test_global_search_empty_query(self):
        """測試空查詢"""
        results = self.service.global_search("")

        assert results["total"] == 0
        assert len(results["games"]) == 0
        assert len(results["members"]) == 0
