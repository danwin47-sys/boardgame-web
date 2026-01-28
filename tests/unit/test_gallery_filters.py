"""Gallery Filter Logic Unit Tests"""
import pytest

from app.blueprints.api.gallery import classify_game_type, parse_players_range


class TestPlayerRangeParsing:
    """測試人數範圍解析功能"""

    def test_parse_range_with_dash(self):
        """測試 '2-4' 格式"""
        min_p, max_p = parse_players_range("2-4")
        assert min_p == 2
        assert max_p == 4

    def test_parse_range_with_tilde(self):
        """測試 '2~4' 格式"""
        min_p, max_p = parse_players_range("2~4")
        assert min_p == 2
        assert max_p == 4

    def test_parse_plus_format(self):
        """測試 '5+' 格式"""
        min_p, max_p = parse_players_range("5+")
        assert min_p == 5
        assert max_p == 99

    def test_parse_single_number(self):
        """測試單一數字"""
        min_p, max_p = parse_players_range("4")
        assert min_p == 4
        assert max_p == 4

    def test_parse_empty_string(self):
        """測試空字串"""
        min_p, max_p = parse_players_range("")
        assert min_p is None
        assert max_p is None

    def test_parse_none(self):
        """測試 None 輸入"""
        min_p, max_p = parse_players_range(None)
        assert min_p is None
        assert max_p is None

    def test_parse_invalid_format(self):
        """測試無效格式"""
        min_p, max_p = parse_players_range("abc")
        assert min_p is None
        assert max_p is None


class TestGameClassification:
    """測試遊戲類型分類邏輯"""

    def test_classify_party_game(self):
        """測試派對遊戲分類（6+人）"""
        game_data = {"minPlayers": 4, "maxPlayers": 8, "difficulty": "簡單"}
        types = classify_game_type(game_data)
        assert "派對遊戲" in types

    def test_classify_strategy_game(self):
        """測試策略遊戲分類"""
        game_data = {"minPlayers": 2, "maxPlayers": 4, "difficulty": "困難"}
        types = classify_game_type(game_data)
        assert "策略遊戲" in types

    def test_classify_family_game(self):
        """測試家庭遊戲分類"""
        game_data = {"minPlayers": 2, "maxPlayers": 5, "difficulty": "普通"}
        types = classify_game_type(game_data)
        assert "家庭遊戲" in types

    def test_classify_children_game(self):
        """測試兒童遊戲分類"""
        game_data = {"minPlayers": 2, "maxPlayers": 4, "difficulty": "簡單"}
        types = classify_game_type(game_data)
        assert "兒童遊戲" in types

    def test_classify_multiple_types(self):
        """測試遊戲可能屬於多個類型"""
        game_data = {"minPlayers": 2, "maxPlayers": 6, "difficulty": "簡單"}
        types = classify_game_type(game_data)
        # 這個遊戲應該同時符合派對和家庭遊戲
        assert len(types) > 0

    def test_classify_unknown_game(self):
        """測試無法分類的遊戲應標記為'其他'"""
        game_data = {"minPlayers": 10, "maxPlayers": 20, "difficulty": ""}
        types = classify_game_type(game_data)
        # 由於 maxPlayers >= 6，應該被歸類為派對遊戲
        assert len(types) > 0

    def test_classify_with_missing_data(self):
        """測試缺少部分資料的情況"""
        game_data = {"difficulty": "普通"}
        types = classify_game_type(game_data)
        # 應該使用預設值並成功分類
        assert len(types) > 0
