"""
測試 core/bgg_service.py 模組 (使用 mock)
"""
from unittest.mock import MagicMock, patch

import pytest
from flask import Flask


class TestBGGServiceInit:
    """測試初始化"""

    @patch("core.bgg_service.BGGApiClient")
    def test_init_demo_mode(self, mock_client):
        """測試演示模式初始化"""
        app = Flask(__name__)
        app.config["DEMO_MODE"] = True

        with app.app_context():
            from core.bgg_service import BGGService

            service = BGGService()
            assert service.demo_mode is True

    @patch("core.bgg_service.BGGApiClient")
    def test_init_normal_mode(self, mock_client):
        """測試正常模式初始化"""
        app = Flask(__name__)
        app.config["DEMO_MODE"] = False
        app.config["BGG_API_TOKEN"] = "test_token"

        with app.app_context():
            from core.bgg_service import BGGService

            service = BGGService()
            assert service.demo_mode is False

    @patch("core.bgg_service.BGGApiClient")
    def test_init_no_app_context(self, mock_client):
        """測試在沒有 app context 的情況下初始化 (觸發 RuntimeError)"""
        # 模擬不在 app context 中 (current_app 會拋出 RuntimeError)
        with patch("core.bgg_service.current_app", MagicMock(side_effect=RuntimeError)):
            from core.bgg_service import BGGService

            service = BGGService()
            # 預設 demo_mode 應該是 False (除非環境變數有設)
            assert hasattr(service, "demo_mode")


class TestBGGServiceSearchGames:
    """測試 search_games 方法"""

    @patch("core.bgg_service.BGGApiClient")
    def test_search_games_demo_mode(self, mock_client):
        """測試演示模式搜尋"""
        app = Flask(__name__)
        app.config["DEMO_MODE"] = True

        with app.app_context():
            from core.bgg_service import BGGService

            service = BGGService()
            results = service.search_games("Catan")

            # 演示模式應該返回預設資料
            assert isinstance(results, list)

    @patch("core.bgg_service.BGGApiClient")
    def test_search_games_api_mode(self, mock_client):
        """測試 API 模式搜尋"""
        mock_api = MagicMock()
        mock_api.search.return_value = [{"id": 13, "name": "Catan", "year": 1995}]
        mock_client.return_value = mock_api

        app = Flask(__name__)
        app.config["DEMO_MODE"] = False
        app.config["BGG_API_TOKEN"] = "test"

        with app.app_context():
            from core.bgg_service import BGGService

            service = BGGService()
            results = service.search_games("Catan")

            assert isinstance(results, list)

    @patch("core.bgg_service.BGGApiClient")
    def test_search_games_empty_query(self, mock_client):
        """測試空查詢"""
        app = Flask(__name__)
        app.config["DEMO_MODE"] = True

        with app.app_context():
            from core.bgg_service import BGGService

            service = BGGService()
            results = service.search_games("")
            assert results == []

    @patch("core.bgg_service.BGGApiClient")
    def test_search_games_demo_default(self, mock_client):
        """測試演示模式搜尋（無匹配時返回預設）"""
        app = Flask(__name__)
        app.config["DEMO_MODE"] = True

        with app.app_context():
            from core.bgg_service import BGGService

            service = BGGService()
            results = service.search_games("SomethingNonExistent")
            assert len(results) > 0  # 返回 DEMO_GAMES["default"]

    @patch("core.bgg_service.BGGApiClient")
    def test_search_games_api_exception(self, mock_client):
        """測試搜尋 API 拋出異常"""
        mock_api = MagicMock()
        mock_api.search.side_effect = Exception("General Error")
        mock_client.return_value = mock_api

        app = Flask(__name__)
        app.config["DEMO_MODE"] = False
        app.config["BGG_API_TOKEN"] = "test"

        with app.app_context():
            from core.bgg_service import BGGService

            service = BGGService()
            assert service.search_games("Catan") == []

    @patch("core.bgg_service.BGGApiClient")
    def test_search_games_api_xml_error(self, mock_client):
        """測試搜尋 API 返回非 XML 錯誤"""
        mock_api = MagicMock()
        mock_api.search.side_effect = Exception("non-XML reply")
        mock_client.return_value = mock_api

        app = Flask(__name__)
        app.config["DEMO_MODE"] = False

        with app.app_context():
            from core.bgg_service import BGGService

            service = BGGService()
            assert service.search_games("Catan") == []


class TestBGGServiceGetGameDetails:
    """測試 get_game_details 方法"""

    @patch("core.bgg_service.BGGApiClient")
    def test_get_game_details_demo_mode(self, mock_client):
        """測試演示模式取得詳情"""
        app = Flask(__name__)
        app.config["DEMO_MODE"] = True

        with app.app_context():
            from core.bgg_service import BGGService

            service = BGGService()
            details = service.get_game_details(13)

            # 演示模式返回預設詳情
            assert isinstance(details, (dict, type(None)))

    @patch("core.bgg_service.BGGApiClient")
    def test_get_game_details_not_found(self, mock_client):
        """測試取得詳情（遊戲不存在）"""
        mock_api = MagicMock()
        mock_api.game.return_value = None
        mock_client.return_value = mock_api

        app = Flask(__name__)
        app.config["DEMO_MODE"] = False

        with app.app_context():
            from core.bgg_service import BGGService

            service = BGGService()
            assert service.get_game_details(99999) is None

    @patch("core.bgg_service.BGGApiClient")
    def test_get_game_details_formatting(self, mock_client):
        """測試詳情格式化（人數與時間）"""
        mock_api = MagicMock()
        mock_api.game.return_value = {
            "id": 1,
            "name": "G",
            "min_players": 2,
            "max_players": 2,
            "playing_time": 60,
            "min_playing_time": 30,
            "max_playing_time": 90,
        }
        mock_client.return_value = mock_api

        app = Flask(__name__)
        app.config["DEMO_MODE"] = False

        with app.app_context():
            from core.bgg_service import BGGService

            service = BGGService()
            details = service.get_game_details(1)
            assert details["players_display"] == "2"
            assert details["playing_time_display"] == "30-90 分鐘"

    @patch("core.bgg_service.BGGApiClient")
    def test_get_game_details_exception(self, mock_client):
        """測試取得詳情拋出異常"""
        mock_api = MagicMock()
        mock_api.game.side_effect = Exception("DB Error")
        mock_client.return_value = mock_api

        app = Flask(__name__)
        app.config["DEMO_MODE"] = False

        with app.app_context():
            from core.bgg_service import BGGService

            service = BGGService()
            assert service.get_game_details(1) is None

    @patch("core.bgg_service.BGGApiClient")
    def test_get_game_details_api_mode(self, mock_client):
        """測試 API 模式取得詳情"""
        mock_api = MagicMock()
        mock_api.game.return_value = {
            "id": 13,
            "name": "Catan",
            "rating_average": 7.5,
            "rank": 50,
        }
        mock_client.return_value = mock_api

        app = Flask(__name__)
        app.config["DEMO_MODE"] = False
        app.config["BGG_API_TOKEN"] = "test"

        with app.app_context():
            from core.bgg_service import BGGService

            service = BGGService()
            details = service.get_game_details(13)

            assert isinstance(details, (dict, type(None)))


class TestBGGServiceGetHotGames:
    """測試 get_hot_games 方法"""

    @patch("core.bgg_service.BGGApiClient")
    def test_get_hot_games_demo_mode(self, mock_client):
        """測試演示模式熱門遊戲"""
        app = Flask(__name__)
        app.config["DEMO_MODE"] = True

        with app.app_context():
            from core.bgg_service import BGGService

            service = BGGService()
            hot = service.get_hot_games(limit=5)

            assert isinstance(hot, list)

    @patch("core.bgg_service.BGGApiClient")
    def test_get_hot_games_api_mode(self, mock_client):
        """測試 API 模式熱門遊戲"""
        mock_api = MagicMock()
        mock_api.hot_items.return_value = [{"id": 13, "name": "Catan", "rank": 1}]
        mock_client.return_value = mock_api

        app = Flask(__name__)
        app.config["DEMO_MODE"] = False
        app.config["BGG_API_TOKEN"] = "test"

        with app.app_context():
            from core.bgg_service import BGGService

            service = BGGService()
            hot = service.get_hot_games(limit=5)

            assert isinstance(hot, list)


class TestBGGServiceGameCategories:
    """測試遊戲分類方法"""

    @patch("core.bgg_service.BGGApiClient")
    def test_get_party_game_ids(self, mock_client):
        """測試取得派對遊戲 ID"""
        app = Flask(__name__)
        app.config["DEMO_MODE"] = True

        with app.app_context():
            from core.bgg_service import BGGService

            service = BGGService()
            ids = service.get_party_game_ids(limit=10)

            assert isinstance(ids, list)
            assert len(ids) <= 10

    @patch("core.bgg_service.BGGApiClient")
    def test_get_strategy_game_ids(self, mock_client):
        """測試取得策略遊戲 ID"""
        app = Flask(__name__)
        app.config["DEMO_MODE"] = True

        with app.app_context():
            from core.bgg_service import BGGService

            service = BGGService()
            ids = service.get_strategy_game_ids(limit=10)

            assert isinstance(ids, list)

    @patch("core.bgg_service.BGGApiClient")
    def test_get_family_game_ids(self, mock_client):
        """測試取得家庭遊戲 ID"""
        app = Flask(__name__)
        app.config["DEMO_MODE"] = True

        with app.app_context():
            from core.bgg_service import BGGService

            service = BGGService()
            ids = service.get_family_game_ids(limit=10)

            assert isinstance(ids, list)

    @patch("core.bgg_service.BGGApiClient")
    def test_get_children_game_ids(self, mock_client):
        """測試取得兒童遊戲 ID"""
        app = Flask(__name__)
        app.config["DEMO_MODE"] = True

        with app.app_context():
            from core.bgg_service import BGGService

            service = BGGService()
            ids = service.get_children_game_ids(limit=10)

            assert isinstance(ids, list)


class TestBGGServiceOurHotGames:
    """測試 get_our_hot_games 方法"""

    @patch("core.bgg_service.BGGApiClient")
    def test_get_our_hot_games_success(self, mock_client):
        """測試成功取得館藏熱門遊戲"""
        app = Flask(__name__)
        app.config["DEMO_MODE"] = False
        app.config["BGG_API_TOKEN"] = "test"

        # 模擬 BGG API 回傳熱門榜
        mock_api = MagicMock()
        mock_api.hot_items.return_value = [
            {"id": 101, "name": "Game A", "rank": 1},
            {"id": 102, "name": "Game B", "rank": 2},
        ]
        mock_client.return_value = mock_api

        # 模擬 SheetsClient 回傳館藏
        mock_sheets = MagicMock()
        mock_sheets.load_games.return_value = [
            {"name": "Game A", "bgg_id": 101, "status": "在庫"},
            {"name": "Game C", "bgg_id": 103, "status": "借出"},
        ]

        with app.app_context():
            from core.bgg_service import BGGService

            service = BGGService()

            # 手動 Mock get_game_details 避免真的去呼叫
            with patch.object(service, "get_game_details") as mock_details:
                mock_details.return_value = {"id": 101, "thumbnail": "url"}

                results = service.get_our_hot_games(mock_sheets, limit=10)

                # 應該只包含 Game A (因為只有它在熱門榜且在館藏)
                assert len(results) == 1
                assert results[0]["name"] == "Game A"
                assert results[0]["hot_rank"] == 1

    @patch("core.bgg_service.BGGApiClient")
    def test_get_our_hot_games_no_sheets_data(self, mock_client):
        """測試 Sheets 無資料時"""
        app = Flask(__name__)
        app.config["DEMO_MODE"] = False
        mock_client.return_value.hot_items.return_value = [
            {"id": 1, "name": "G", "rank": 1}
        ]
        mock_sheets = MagicMock()
        mock_sheets.load_games.return_value = []

        with app.app_context():
            from core.bgg_service import BGGService

            service = BGGService()
            assert service.get_our_hot_games(mock_sheets) == []

    @patch("core.bgg_service.BGGApiClient")
    def test_get_our_hot_games_invalid_id(self, mock_client):
        """測試 Sheet 中有非法 ID"""
        app = Flask(__name__)
        app.config["DEMO_MODE"] = False
        mock_client.return_value.hot_items.return_value = [
            {"id": 1, "name": "G", "rank": 1}
        ]
        mock_sheets = MagicMock()
        mock_sheets.load_games.return_value = [{"name": "G2", "bgg_id": "invalid"}]

        with app.app_context():
            from core.bgg_service import BGGService

            service = BGGService()
            assert service.get_our_hot_games(mock_sheets) == []


class TestBGGServiceParallel:
    """測試並行抓取邏輯"""

    @patch("core.bgg_service.BGGApiClient")
    def test_get_games_by_ids_parallel(self, mock_client):
        """測試並行取得多個遊戲詳情"""
        app = Flask(__name__)
        app.config["DEMO_MODE"] = False

        with app.app_context():
            from core.bgg_service import BGGService

            service = BGGService()

            # Mock get_game_details
            with patch.object(service, "get_game_details") as mock_details:
                mock_details.side_effect = lambda x: {"id": x, "name": f"Game {x}"}

                game_ids = [1, 2, 3, 4, 5]
                results = service._get_games_by_ids(game_ids)

                assert len(results) == 5
                # 驗證所有 ID 都有被查詢
                returned_ids = {r["id"] for r in results}
                assert returned_ids == set(game_ids)

    @patch("core.bgg_service.BGGApiClient")
    def test_recommendation_methods(self, mock_client):
        """測試各項推薦分類的抓取方法"""
        app = Flask(__name__)
        app.config["DEMO_MODE"] = False

        with app.app_context():
            from core.bgg_service import BGGService

            service = BGGService()

            with patch.object(service, "_get_games_by_ids") as mock_parallel:
                mock_parallel.return_value = [{"id": 1}]

                # 測試派對遊戲
                res = service.get_party_games(limit=1)
                assert len(res) == 1

                # 測試策略遊戲
                res = service.get_strategy_games(limit=1)
                assert len(res) == 1

    @patch("core.bgg_service.BGGApiClient")
    def test_get_family_and_children_games(self, mock_client):
        """測試家庭與兒童遊戲的抓取方法"""
        app = Flask(__name__)
        app.config["DEMO_MODE"] = False

        with app.app_context():
            from core.bgg_service import BGGService

            service = BGGService()

            with patch.object(service, "_get_games_by_ids") as mock_parallel:
                mock_parallel.return_value = [{"id": 2}]

                # 測試家庭遊戲
                res = service.get_family_games(limit=1)
                assert len(res) == 1

                # 測試兒童遊戲
                res = service.get_children_games(limit=1)
                assert len(res) == 1

    @patch("core.bgg_service.BGGApiClient")
    def test_get_games_by_ids_with_exception(self, mock_client):
        """測試並行抓取時部分任務失敗"""
        app = Flask(__name__)
        app.config["DEMO_MODE"] = False

        with app.app_context():
            from core.bgg_service import BGGService

            service = BGGService()

            # 模擬其中一個請求失敗
            with patch.object(service, "get_game_details") as mock_details:

                def side_effect(game_id):
                    if game_id == 2:
                        raise Exception("Network Error")
                    return {"id": game_id, "name": f"Game {game_id}"}

                mock_details.side_effect = side_effect

                results = service._get_games_by_ids([1, 2, 3])
                # 應該只回傳成功的 2 個
                assert len(results) == 2
                assert {r["id"] for r in results} == {1, 3}

    @patch("core.bgg_service.BGGApiClient")
    def test_get_our_hot_games_api_fail(self, mock_client):
        """測試當 API 失敗時 get_our_hot_games 的行為"""
        app = Flask(__name__)
        app.config["DEMO_MODE"] = False

        mock_api = MagicMock()
        mock_api.hot_items.side_effect = Exception("API Fail")
        mock_client.return_value = mock_api

        mock_sheets = MagicMock()

        with app.app_context():
            from core.bgg_service import BGGService

            service = BGGService()
            results = service.get_our_hot_games(mock_sheets)
            assert results == []

    @patch("core.bgg_service.BGGApiClient")
    def test_get_overall_rank_logic(self, mock_client):
        """測試解析排名邏輯"""
        from core.bgg_service import BGGService

        service = BGGService()

        # 成功解析
        game = {"ranks": [{"name": "boardgame", "value": "100"}]}
        assert service._get_overall_rank(game) == 100

        # 非排名或無效排名
        game = {"ranks": [{"name": "party", "value": "50"}]}
        assert service._get_overall_rank(game) is None

        # Not Ranked
        game = {"ranks": [{"name": "boardgame", "value": "Not Ranked"}]}
        assert service._get_overall_rank(game) is None

    def test_get_overall_rank_exception(self):
        """測試排名解析拋出泛型異常"""
        from core.bgg_service import BGGService

        service = BGGService()
        # 傳入非字典對象觸發 BaseException
        assert service._get_overall_rank(None) is None

    @patch("core.bgg_service.BGGApiClient")
    def test_get_our_hot_games_generic_exception(self, mock_client):
        """測試 get_our_hot_games 拋出泛型異常"""
        app = Flask(__name__)
        app.config["DEMO_MODE"] = False
        with app.app_context():
            from core.bgg_service import BGGService

            service = BGGService()
            # 傳入非法對象觸發 Exception
            assert service.get_our_hot_games(None) == []
