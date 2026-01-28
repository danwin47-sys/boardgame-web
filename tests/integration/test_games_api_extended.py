"""
測試 games API - 使用正確 mock 提升覆蓋率
"""
import json
from unittest.mock import MagicMock, patch

import pytest


class TestGamesAPIGetGames:
    """測試 GET /api/games 端點"""

    @patch("app.blueprints.api.games.get_manager")
    def test_get_games_success(self, mock_get_mgr, client):
        """測試取得所有遊戲 - 成功"""
        mock_mgr = MagicMock()
        mock_mgr.load_data.return_value = [
            {"name": "Catan", "status": "可借"},
            {"name": "Gloomhaven", "status": "借出"},
        ]
        mock_mgr.games = mock_mgr.load_data.return_value
        mock_get_mgr.return_value = mock_mgr

        response = client.get("/api/games")

        assert response.status_code == 200
        data = json.loads(response.data)
        assert len(data) == 2
        assert data[0]["name"] == "Catan"

    @patch("app.blueprints.api.games.get_manager")
    def test_get_games_error(self, mock_get_mgr, client):
        """測試取得所有遊戲 - 錯誤"""
        mock_get_mgr.side_effect = Exception("Database error")

        response = client.get("/api/games")

        assert response.status_code == 500
        data = json.loads(response.data)
        assert data["success"] is False


class TestGamesAPIBorrowGame:
    """測試 POST /api/borrow 端點"""

    @patch("app.blueprints.api.games.get_manager")
    def test_borrow_game_success(self, mock_get_mgr, client):
        """測試借出遊戲 - 成功"""
        mock_mgr = MagicMock()
        mock_mgr.find_member_by_id.return_value = {"id": "001", "name": "Alice"}
        mock_mgr.borrow_game.return_value = (True, "借出成功")
        mock_get_mgr.return_value = mock_mgr

        borrow_data = {"name": "Catan", "member_id": "001"}
        response = client.post(
            "/api/borrow", data=json.dumps(borrow_data), content_type="application/json"
        )

        assert response.status_code == 200
        data = json.loads(response.data)
        assert data["success"] is True
        assert "成功" in data["message"]

    @patch("app.blueprints.api.games.get_manager")
    def test_borrow_game_missing_data(self, mock_get_mgr, client):
        """測試借出遊戲 - 缺少資料"""
        response = client.post(
            "/api/borrow", data=json.dumps({}), content_type="application/json"
        )

        assert response.status_code == 400
        data = json.loads(response.data)
        assert data["success"] is False

    @patch("app.blueprints.api.games.get_manager")
    def test_borrow_game_member_not_found(self, mock_get_mgr, client):
        """測試借出遊戲 - 找不到社員"""
        mock_mgr = MagicMock()
        mock_mgr.find_member_by_id.return_value = None
        mock_get_mgr.return_value = mock_mgr

        borrow_data = {"name": "Catan", "member_id": "999"}
        response = client.post(
            "/api/borrow", data=json.dumps(borrow_data), content_type="application/json"
        )

        assert response.status_code == 404
        data = json.loads(response.data)
        assert data["success"] is False

    @patch("app.blueprints.api.games.get_manager")
    def test_borrow_game_fail(self, mock_get_mgr, client):
        """測試借出遊戲 - 借出失敗"""
        mock_mgr = MagicMock()
        mock_mgr.find_member_by_id.return_value = {"id": "001", "name": "Alice"}
        mock_mgr.borrow_game.return_value = (False, "遊戲已被借出")
        mock_get_mgr.return_value = mock_mgr

        borrow_data = {"name": "Catan", "member_id": "001"}
        response = client.post(
            "/api/borrow", data=json.dumps(borrow_data), content_type="application/json"
        )

        assert response.status_code == 400
        data = json.loads(response.data)
        assert data["success"] is False


class TestGamesAPIReturnGame:
    """測試 POST /api/return 端點"""

    @patch("app.blueprints.api.games.get_manager")
    def test_return_game_success(self, mock_get_mgr, client):
        """測試歸還遊戲 - 成功"""
        mock_mgr = MagicMock()
        mock_mgr.return_game.return_value = (True, "歸還成功")
        mock_get_mgr.return_value = mock_mgr

        return_data = {"name": "Catan"}
        response = client.post(
            "/api/return", data=json.dumps(return_data), content_type="application/json"
        )

        assert response.status_code == 200
        data = json.loads(response.data)
        assert data["success"] is True

    @patch("app.blueprints.api.games.get_manager")
    def test_return_game_missing_name(self, mock_get_mgr, client):
        """測試歸還遊戲 - 缺少名稱"""
        response = client.post(
            "/api/return", data=json.dumps({}), content_type="application/json"
        )

        assert response.status_code == 400
        data = json.loads(response.data)
        assert data["success"] is False

    @patch("app.blueprints.api.games.get_manager")
    def test_return_game_fail(self, mock_get_mgr, client):
        """測試歸還遊戲 - 歸還失敗"""
        mock_mgr = MagicMock()
        mock_mgr.return_game.return_value = (False, "遊戲未被借出")
        mock_get_mgr.return_value = mock_mgr

        return_data = {"name": "Catan"}
        response = client.post(
            "/api/return", data=json.dumps(return_data), content_type="application/json"
        )

        assert response.status_code == 400
        data = json.loads(response.data)
        assert data["success"] is False


class TestGamesAPIExpansions:
    """測試擴充相關 API"""

    @patch("core.expansion_service.ExpansionService")
    @patch("app.blueprints.api.games.get_manager")
    def test_get_expansions_success(self, mock_get_mgr, mock_exp_service_class, client):
        """測試取得擴充 - 成功"""
        mock_mgr = MagicMock()
        mock_mgr.load_data.return_value = []
        mock_mgr.client = MagicMock()
        mock_get_mgr.return_value = mock_mgr

        mock_exp_service = MagicMock()
        mock_exp_service.get_expansions.return_value = [
            {"name": "Catan: Seafarers"},
            {"name": "Catan: Cities"},
        ]
        mock_exp_service_class.return_value = mock_exp_service

        response = client.get("/api/games/Catan/expansions")

        assert response.status_code == 200
        data = json.loads(response.data)
        assert data["success"] is True
        assert data["count"] == 2

    @patch("core.expansion_service.ExpansionService")
    @patch("app.blueprints.api.games.get_manager")
    def test_get_family_success(self, mock_get_mgr, mock_exp_service_class, client):
        """測試取得遊戲家族 - 成功"""
        mock_mgr = MagicMock()
        mock_mgr.load_data.return_value = []
        mock_mgr.client = MagicMock()
        mock_get_mgr.return_value = mock_mgr

        mock_exp_service = MagicMock()
        mock_exp_service.get_game_family.return_value = {
            "parent": {"name": "Catan"},
            "expansions": [{"name": "Catan: Seafarers"}],
        }
        mock_exp_service_class.return_value = mock_exp_service

        response = client.get("/api/games/Catan/family")

        assert response.status_code == 200
        data = json.loads(response.data)
        assert data["success"] is True
        assert data["expansion_count"] == 1

    @patch("core.expansion_service.ExpansionService")
    @patch("app.blueprints.api.games.get_manager")
    def test_validate_borrow_success(
        self, mock_get_mgr, mock_exp_service_class, client
    ):
        """測試驗證借出 - 成功"""
        mock_mgr = MagicMock()
        mock_mgr.load_data.return_value = []
        mock_mgr.client = MagicMock()
        mock_get_mgr.return_value = mock_mgr

        mock_exp_service = MagicMock()
        mock_exp_service.validate_borrow.return_value = (True, "可以借出", None)
        mock_exp_service_class.return_value = mock_exp_service

        response = client.get("/api/games/Catan/validate-borrow")

        assert response.status_code == 200
        data = json.loads(response.data)
        assert data["success"] is True
        assert data["can_borrow"] is True
