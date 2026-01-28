"""
Search API Integration Tests
測試搜尋 API 端點的整合測試
"""
import pytest
from flask import json


class TestGlobalSearchAPI:
    """測試全站搜尋 API"""

    def test_global_search_success(self, client):
        """測試全站搜尋成功"""
        response = client.get("/api/search/global?q=卡")
        assert response.status_code == 200

        data = json.loads(response.data)
        assert data["success"] is True
        assert "results" in data
        assert "games" in data["results"]
        assert "members" in data["results"]
        assert "total" in data["results"]
        assert isinstance(data["results"]["games"], list)
        assert isinstance(data["results"]["members"], list)
        assert isinstance(data["results"]["total"], int)

    def test_global_search_missing_query(self, client):
        """測試缺少搜尋關鍵字"""
        response = client.get("/api/search/global")
        assert response.status_code == 400

        data = json.loads(response.data)
        assert data["success"] is False
        assert "error_code" in data
        assert "message" in data
        assert "缺少搜尋關鍵字" in data["message"]

    def test_global_search_empty_query(self, client):
        """測試空搜尋關鍵字"""
        response = client.get("/api/search/global?q=")
        assert response.status_code == 400

        data = json.loads(response.data)
        assert data["success"] is False
        assert "error_code" in data

    def test_global_search_with_fuzzy_true(self, client):
        """測試啟用模糊搜尋"""
        response = client.get("/api/search/global?q=卡&fuzzy=true")
        assert response.status_code == 200

        data = json.loads(response.data)
        assert data["success"] is True
        assert "results" in data

    def test_global_search_with_fuzzy_false(self, client):
        """測試停用模糊搜尋"""
        response = client.get("/api/search/global?q=卡坦島&fuzzy=false")
        assert response.status_code == 200

        data = json.loads(response.data)
        assert data["success"] is True
        assert "results" in data

    def test_global_search_special_characters(self, client):
        """測試特殊字元搜尋"""
        response = client.get("/api/search/global?q=A001")
        assert response.status_code == 200

        data = json.loads(response.data)
        assert data["success"] is True

    def test_global_search_unicode(self, client):
        """測試 Unicode 字元搜尋"""
        response = client.get("/api/search/global?q=璀璨寶石")
        assert response.status_code == 200

        data = json.loads(response.data)
        assert data["success"] is True


class TestSearchGamesAPI:
    """測試遊戲搜尋 API"""

    def test_search_games_success(self, client):
        """測試搜尋遊戲成功"""
        response = client.get("/api/search/games?q=卡")
        assert response.status_code == 200

        data = json.loads(response.data)
        assert data["success"] is True
        assert "results" in data
        assert "total" in data
        assert isinstance(data["results"], list)
        assert isinstance(data["total"], int)
        assert data["total"] == len(data["results"])

    def test_search_games_missing_query(self, client):
        """測試缺少搜尋關鍵字"""
        response = client.get("/api/search/games")
        assert response.status_code == 400

        data = json.loads(response.data)
        assert data["success"] is False
        assert "error_code" in data
        assert "缺少搜尋關鍵字" in data["message"]

    def test_search_games_empty_query(self, client):
        """測試空搜尋關鍵字"""
        response = client.get("/api/search/games?q=")
        assert response.status_code == 400

        data = json.loads(response.data)
        assert data["success"] is False

    def test_search_games_with_fuzzy_true(self, client):
        """測試啟用模糊搜尋"""
        response = client.get("/api/search/games?q=卡&fuzzy=true")
        assert response.status_code == 200

        data = json.loads(response.data)
        assert data["success"] is True

    def test_search_games_with_fuzzy_false(self, client):
        """測試停用模糊搜尋"""
        response = client.get("/api/search/games?q=卡坦島&fuzzy=false")
        assert response.status_code == 200

        data = json.loads(response.data)
        assert data["success"] is True

    def test_search_games_result_structure(self, client):
        """測試遊戲搜尋結果結構"""
        response = client.get("/api/search/games?q=卡")
        data = json.loads(response.data)

        if len(data["results"]) > 0:
            game = data["results"][0]
            # 驗證遊戲資料結構
            assert "name" in game
            assert "status" in game

    def test_search_games_no_results(self, client):
        """測試搜尋無結果"""
        response = client.get("/api/search/games?q=不可能存在的遊戲名稱xyz123")
        assert response.status_code == 200

        data = json.loads(response.data)
        assert data["success"] is True
        assert data["total"] == 0
        assert len(data["results"]) == 0


class TestSearchMembersAPI:
    """測試會員搜尋 API"""

    def test_search_members_success(self, client):
        """測試搜尋會員成功"""
        response = client.get("/api/search/members?q=A")
        assert response.status_code == 200

        data = json.loads(response.data)
        assert data["success"] is True
        assert "results" in data
        assert "total" in data
        assert isinstance(data["results"], list)
        assert isinstance(data["total"], int)
        assert data["total"] == len(data["results"])

    def test_search_members_missing_query(self, client):
        """測試缺少搜尋關鍵字"""
        response = client.get("/api/search/members")
        assert response.status_code == 400

        data = json.loads(response.data)
        assert data["success"] is False
        assert "error_code" in data
        assert "message" in data
        assert "缺少搜尋關鍵字" in data["message"]

    def test_search_members_empty_query(self, client):
        """測試空搜尋關鍵字"""
        response = client.get("/api/search/members?q=")
        assert response.status_code == 400

        data = json.loads(response.data)
        assert data["success"] is False

    def test_search_members_with_fuzzy_true(self, client):
        """測試啟用模糊搜尋"""
        response = client.get("/api/search/members?q=張&fuzzy=true")
        assert response.status_code == 200

        data = json.loads(response.data)
        assert data["success"] is True

    def test_search_members_with_fuzzy_false(self, client):
        """測試停用模糊搜尋"""
        response = client.get("/api/search/members?q=A001&fuzzy=false")
        assert response.status_code == 200

        data = json.loads(response.data)
        assert data["success"] is True

    def test_search_members_by_id(self, client):
        """測試按 ID 搜尋會員"""
        response = client.get("/api/search/members?q=A001")
        assert response.status_code == 200

        data = json.loads(response.data)
        assert data["success"] is True

    def test_search_members_result_structure(self, client):
        """測試會員搜尋結果結構"""
        response = client.get("/api/search/members?q=A")
        data = json.loads(response.data)

        if len(data["results"]) > 0:
            member = data["results"][0]
            # 驗證會員資料結構
            assert "id" in member or "name" in member

    def test_search_members_no_results(self, client):
        """測試搜尋無結果"""
        response = client.get("/api/search/members?q=不可能存在的會員名稱xyz123")
        assert response.status_code == 200

        data = json.loads(response.data)
        assert data["success"] is True
        assert data["total"] == 0
        assert len(data["results"]) == 0


class TestSearchAPIEdgeCases:
    """測試搜尋 API 邊界情況"""

    def test_search_with_whitespace_query(self, client):
        """測試僅包含空白的搜尋"""
        response = client.get("/api/search/global?q=   ")
        assert response.status_code == 400

        data = json.loads(response.data)
        assert data["success"] is False

    def test_search_with_very_long_query(self, client):
        """測試超長搜尋關鍵字"""
        long_query = "卡" * 100
        response = client.get(f"/api/search/global?q={long_query}")
        assert response.status_code == 200

        data = json.loads(response.data)
        assert data["success"] is True

    def test_search_case_insensitive(self, client):
        """測試大小寫不敏感搜尋"""
        response1 = client.get("/api/search/games?q=catan")
        response2 = client.get("/api/search/games?q=CATAN")
        response3 = client.get("/api/search/games?q=Catan")

        assert response1.status_code == 200
        assert response2.status_code == 200
        assert response3.status_code == 200

        # 所有回應都應該成功
        data1 = json.loads(response1.data)
        data2 = json.loads(response2.data)
        data3 = json.loads(response3.data)

        assert data1["success"] is True
        assert data2["success"] is True
        assert data3["success"] is True

    def test_search_with_numbers(self, client):
        """測試數字搜尋"""
        response = client.get("/api/search/games?q=7")
        assert response.status_code == 200

        data = json.loads(response.data)
        assert data["success"] is True

    def test_search_with_mixed_content(self, client):
        """測試混合內容搜尋（中英文數字）"""
        response = client.get("/api/search/games?q=卡坦島Catan2023")
        assert response.status_code == 200

        data = json.loads(response.data)
        assert data["success"] is True
