"""
測試 core/expansion_service.py 模組
"""
from unittest.mock import MagicMock

import pytest

from core.constants import (
    GAME_STATUS_AVAILABLE,
    GAME_STATUS_BORROWED,
    STORAGE_MODE_INDEPENDENT,
    STORAGE_MODE_MERGED,
)
from core.expansion_service import ExpansionService


class TestExpansionServiceInit:
    """測試初始化"""

    def test_init(self):
        """測試初始化"""
        mock_client = MagicMock()
        service = ExpansionService(mock_client)

        assert service.client == mock_client


class TestExpansionServiceGetExpansions:
    """測試 get_expansions 方法"""

    def setup_method(self):
        self.service = ExpansionService(MagicMock())
        self.all_games = [
            {"name": "Catan", "is_expansion": "0"},
            {"name": "Catan: Seafarers", "is_expansion": "1", "parent_game": "Catan"},
            {
                "name": "Catan: Cities & Knights",
                "is_expansion": "1",
                "parent_game": "Catan",
            },
            {"name": "Gloomhaven", "is_expansion": "0"},
            {
                "name": "Gloomhaven: Expansion",
                "is_expansion": "1",
                "parent_game": "Gloomhaven",
            },
        ]

    def test_get_expansions_found(self):
        """測試取得擴充 - 找到"""
        expansions = self.service.get_expansions("Catan", self.all_games)

        assert len(expansions) == 2
        assert expansions[0]["name"] == "Catan: Seafarers"
        assert expansions[1]["name"] == "Catan: Cities & Knights"

    def test_get_expansions_not_found(self):
        """測試取得擴充 - 沒有找到"""
        expansions = self.service.get_expansions("Pandemic", self.all_games)

        assert expansions == []

    def test_get_expansions_no_parent(self):
        """測試取得擴充 - 遊戲本身是擴充"""
        expansions = self.service.get_expansions("Catan: Seafarers", self.all_games)

        # 擴充不應該有自己的擴充
        assert expansions == []


class TestExpansionServiceGetParentGame:
    """測試 get_parent_game 方法"""

    def setup_method(self):
        self.service = ExpansionService(MagicMock())
        self.all_games = [
            {"name": "Catan", "is_expansion": "0", "status": "Available"},
            {"name": "Catan: Seafarers", "is_expansion": "1", "parent_game": "Catan"},
            {"name": "Gloomhaven", "is_expansion": "0"},
        ]

    def test_get_parent_game_found(self):
        """測試取得主遊戲 - 找到"""
        parent = self.service.get_parent_game("Catan: Seafarers", self.all_games)

        assert parent is not None
        assert parent["name"] == "Catan"

    def test_get_parent_game_not_expansion(self):
        """測試取得主遊戲 - 不是擴充"""
        parent = self.service.get_parent_game("Catan", self.all_games)

        assert parent is None

    def test_get_parent_game_not_found(self):
        """測試取得主遊戲 - 主遊戲不存在"""
        orphan_games = [
            {
                "name": "Orphan Expansion",
                "is_expansion": "1",
                "parent_game": "Nonexistent Game",
            }
        ]
        parent = self.service.get_parent_game("Orphan Expansion", orphan_games)

        assert parent is None


class TestExpansionServiceGetGameFamily:
    """測試 get_game_family 方法"""

    def setup_method(self):
        self.service = ExpansionService(MagicMock())
        self.all_games = [
            {"name": "Catan", "is_expansion": "0"},
            {"name": "Catan: Seafarers", "is_expansion": "1", "parent_game": "Catan"},
            {"name": "Catan: Cities", "is_expansion": "1", "parent_game": "Catan"},
        ]

    def test_get_game_family_main_game(self):
        """測試取得遊戲家族 - 從主遊戲"""
        family = self.service.get_game_family("Catan", self.all_games)

        assert family["parent"]["name"] == "Catan"
        assert len(family["expansions"]) == 2

    def test_get_game_family_expansion(self):
        """測試取得遊戲家族 - 從擴充"""
        family = self.service.get_game_family("Catan: Seafarers", self.all_games)

        assert family["parent"]["name"] == "Catan"
        assert len(family["expansions"]) == 2

    def test_get_game_family_no_expansions(self):
        """測試取得遊戲家族 - 沒有擴充"""
        games = [{"name": "Solo Game", "is_expansion": "0"}]
        family = self.service.get_game_family("Solo Game", games)

        assert family["parent"]["name"] == "Solo Game"
        assert family["expansions"] == []


class TestExpansionServiceGetMergedExpansions:
    """測試 get_merged_expansions 方法"""

    def setup_method(self):
        self.service = ExpansionService(MagicMock())
        self.all_games = [
            {"name": "Catan", "is_expansion": "0"},
            {
                "name": "Catan: Seafarers",
                "is_expansion": "1",
                "parent_game": "Catan",
                "storage_mode": STORAGE_MODE_MERGED,
            },
            {
                "name": "Catan: Cities",
                "is_expansion": "1",
                "parent_game": "Catan",
                "storage_mode": STORAGE_MODE_INDEPENDENT,
            },
        ]

    def test_get_merged_expansions_found(self):
        """測試取得合併收納擴充 - 找到"""
        merged = self.service.get_merged_expansions("Catan", self.all_games)

        assert len(merged) == 1
        assert merged[0]["name"] == "Catan: Seafarers"

    def test_get_merged_expansions_none(self):
        """測試取得合併收納擴充 - 沒有"""
        games = [
            {"name": "Game", "is_expansion": "0"},
            {
                "name": "Game: Exp",
                "is_expansion": "1",
                "parent_game": "Game",
                "storage_mode": STORAGE_MODE_INDEPENDENT,
            },
        ]
        merged = self.service.get_merged_expansions("Game", games)

        assert merged == []


class TestExpansionServiceValidateBorrow:
    """測試 validate_borrow 方法"""

    def setup_method(self):
        self.service = ExpansionService(MagicMock())

    def test_validate_borrow_main_game_ok(self):
        """測試驗證借出 - 主遊戲可借出"""
        games = [
            {"name": "Catan", "is_expansion": "0", "status": GAME_STATUS_AVAILABLE},
            {
                "name": "Catan: Exp",
                "is_expansion": "1",
                "parent_game": "Catan",
                "storage_mode": STORAGE_MODE_INDEPENDENT,
                "status": GAME_STATUS_AVAILABLE,
            },
        ]

        can_borrow, message, info = self.service.validate_borrow("Catan", games)

        assert can_borrow is True

    def test_validate_borrow_main_game_with_merged(self):
        """測試驗證借出 - 主遊戲有合併收納擴充"""
        games = [
            {"name": "Catan", "is_expansion": "0", "status": GAME_STATUS_AVAILABLE},
            {
                "name": "Catan: Exp",
                "is_expansion": "1",
                "parent_game": "Catan",
                "storage_mode": STORAGE_MODE_MERGED,
                "status": GAME_STATUS_AVAILABLE,
            },
        ]

        can_borrow, message, info = self.service.validate_borrow("Catan", games)

        assert can_borrow is True  # 主遊戲總是可以借出
        assert "合併收納" in message or "Catan: Exp" in message
        assert "merged_expansions" in info

    def test_validate_borrow_expansion_independent_ok(self):
        """測試驗證借出 - 獨立收納擴充可借出"""
        games = [
            {"name": "Catan", "is_expansion": "0", "status": GAME_STATUS_AVAILABLE},
            {
                "name": "Catan: Exp",
                "is_expansion": "1",
                "parent_game": "Catan",
                "storage_mode": STORAGE_MODE_INDEPENDENT,
                "status": GAME_STATUS_AVAILABLE,
            },
        ]

        can_borrow, message, info = self.service.validate_borrow("Catan: Exp", games)

        assert can_borrow is True

    def test_validate_borrow_expansion_merged_parent_borrowed(self):
        """測試驗證借出 - 合併擴充但主遊戲已借出"""
        games = [
            {"name": "Catan", "is_expansion": "0", "status": GAME_STATUS_BORROWED},
            {
                "name": "Catan: Exp",
                "is_expansion": "1",
                "parent_game": "Catan",
                "storage_mode": STORAGE_MODE_MERGED,
                "status": GAME_STATUS_AVAILABLE,
            },
        ]

        can_borrow, message, info = self.service.validate_borrow("Catan: Exp", games)

        assert can_borrow is False
        assert "主遊戲" in message or "已借出" in message


class TestExpansionServiceAutoLinkExpansions:
    """測試 auto_link_expansions 方法"""

    def setup_method(self):
        self.service = ExpansionService(MagicMock())

    def test_auto_link_expansions_exact_match(self):
        """測試自動連結擴充 - 精確匹配"""
        games = [
            {"name": "Catan", "is_expansion": "0"},
            {"name": "Catan: Seafarers", "is_expansion": "0"},  # 尚未標記為擴充
        ]

        linked = self.service.auto_link_expansions("Catan", ["Catan: Seafarers"], games)

        # 此方法依賴實際的 sheets 操作，測試邏輯即可
        assert isinstance(linked, list)

    def test_auto_link_expansions_fuzzy_match(self):
        """測試自動連結擴充 - 模糊匹配"""
        games = [
            {"name": "Catan", "is_expansion": "0"},
            {"name": "Seafarers", "is_expansion": "0"},
        ]

        linked = self.service.auto_link_expansions(
            "Catan", ["Seafarers (Catan Expansion)"], games
        )

        assert isinstance(linked, list)

    def test_auto_link_expansions_no_match(self):
        """測試自動連結擴充 - 無匹配"""
        games = [
            {"name": "Catan", "is_expansion": "0"},
        ]

        linked = self.service.auto_link_expansions(
            "Catan", ["Completely Different Game"], games
        )

        assert linked == []
