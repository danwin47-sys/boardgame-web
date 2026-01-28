"""
測試 app/blueprints/api/bgg.py 模組
"""
from unittest.mock import MagicMock, patch

import pytest


class TestBGGSearch:
    """測試 BGG 搜尋端點"""

    def test_search_no_query(self, client):
        """測試沒有查詢參數"""
        response = client.get("/api/bgg/search")

        assert response.status_code == 400
        data = response.get_json()
        assert data["success"] is False

    def test_search_empty_query(self, client):
        """測試空查詢"""
        response = client.get("/api/bgg/search?q=")

        assert response.status_code == 400

    @patch("app.blueprints.api.bgg.get_bgg_service")
    def test_search_success(self, mock_service_fn, client):
        """測試搜尋成功"""
        mock_service = MagicMock()
        mock_service.search_games.return_value = [
            {"id": 13, "name": "Catan", "year": 1995}
        ]
        mock_service_fn.return_value = mock_service

        response = client.get("/api/bgg/search?q=Catan")

        assert response.status_code == 200
        data = response.get_json()
        assert data["success"] is True


class TestBGGHotGames:
    """測試 BGG 熱門遊戲端點"""

    @patch("app.blueprints.api.bgg.get_bgg_service")
    def test_get_hot_games(self, mock_service_fn, client):
        """測試取得熱門遊戲"""
        mock_service = MagicMock()
        mock_service.get_hot_games.return_value = [
            {"id": 13, "name": "Catan", "rank": 1}
        ]
        mock_service_fn.return_value = mock_service

        response = client.get("/api/bgg/hot")

        assert response.status_code == 200
        data = response.get_json()
        assert data["success"] is True

    @patch("app.blueprints.api.bgg.get_bgg_service")
    def test_get_hot_games_with_limit(self, mock_service_fn, client):
        """測試取得熱門遊戲帶 limit"""
        mock_service = MagicMock()
        mock_service.get_hot_games.return_value = []
        mock_service_fn.return_value = mock_service

        response = client.get("/api/bgg/hot?limit=5")

        assert response.status_code == 200


class TestBGGRecommendations:
    """測試 BGG 推薦端點"""

    @patch("app.blueprints.api.bgg.get_bgg_service")
    @patch("app.blueprints.api.bgg.get_manager")
    def test_get_recommendations_no_category(
        self, mock_manager, mock_service_fn, client
    ):
        """測試沒有分類參數"""
        response = client.get("/api/bgg/recommendations")

        assert response.status_code == 400
