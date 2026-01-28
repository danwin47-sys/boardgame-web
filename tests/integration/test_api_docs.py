"""
測試 app/blueprints/api/docs.py 模組
"""
import pytest


class TestApiDocs:
    """測試 API 文件端點"""

    def test_openapi_json(self, client):
        """測試 OpenAPI JSON 規格"""
        response = client.get("/api/openapi.json")
        assert response.status_code == 200

        data = response.get_json()
        assert "openapi" in data
        assert data["openapi"] == "3.0.0"
        assert "info" in data
        assert "paths" in data

    def test_openapi_info(self, client):
        """測試 OpenAPI info 區塊"""
        response = client.get("/api/openapi.json")
        data = response.get_json()

        info = data["info"]
        assert info["title"] == "Boardgame-Web API"
        assert "version" in info

    def test_openapi_paths_exist(self, client):
        """測試 OpenAPI paths 存在"""
        response = client.get("/api/openapi.json")
        data = response.get_json()

        paths = data["paths"]
        assert "/api/games" in paths
        assert "/api/members" in paths
        assert "/health" in paths

    def test_swagger_ui_page(self, client):
        """測試 Swagger UI 頁面"""
        response = client.get("/api/docs")
        assert response.status_code == 200
        assert b"swagger-ui" in response.data

    def test_openapi_tags(self, client):
        """測試 OpenAPI tags"""
        response = client.get("/api/openapi.json")
        data = response.get_json()

        assert "tags" in data
        tag_names = [t["name"] for t in data["tags"]]
        assert "Games" in tag_names
        assert "Members" in tag_names
        assert "BGG" in tag_names
