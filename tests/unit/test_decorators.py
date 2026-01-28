"""
測試 core/decorators.py 模組
"""
from unittest.mock import MagicMock

import pytest
from flask import Flask

from core.decorators import handle_exceptions, validate_fields, validate_json
from core.exceptions import BoardGameException, GameAlreadyBorrowedException, GameNotFoundException, MemberNotFoundException


@pytest.fixture
def app():
    """建立測試 Flask 應用"""
    app = Flask(__name__)
    app.config["TESTING"] = True
    return app


class TestValidateJson:
    """測試 validate_json 裝飾器"""

    def test_valid_json(self, app):
        """測試有效的 JSON 請求"""

        @app.route("/test", methods=["POST"])
        @validate_json
        def test_endpoint():
            return {"success": True}

        with app.test_client() as client:
            response = client.post("/test", json={"key": "value"})
            assert response.status_code == 200

    def test_empty_json(self, app):
        """測試空的 JSON 請求"""

        @app.route("/test", methods=["POST"])
        @validate_json
        def test_endpoint():
            return {"success": True}

        with app.test_client() as client:
            response = client.post("/test", json={})
            assert response.status_code == 400

    def test_no_json(self, app):
        """測試沒有 JSON 的請求"""

        @app.route("/test", methods=["POST"])
        @validate_json
        def test_endpoint():
            return {"success": True}

        with app.test_client() as client:
            response = client.post("/test")
            # Flask 對沒有 Content-Type 的請求返回 415
            assert response.status_code in [400, 415]


class TestValidateFields:
    """測試 validate_fields 裝飾器"""

    def test_all_fields_present(self, app):
        """測試所有必要欄位都存在"""

        @app.route("/test", methods=["POST"])
        @validate_fields("name", "email")
        def test_endpoint():
            return {"success": True}

        with app.test_client() as client:
            response = client.post("/test", json={"name": "test", "email": "test@test.com"})
            assert response.status_code == 200

    def test_missing_field(self, app):
        """測試缺少必要欄位"""

        @app.route("/test", methods=["POST"])
        @validate_fields("name", "email")
        def test_endpoint():
            return {"success": True}

        with app.test_client() as client:
            response = client.post("/test", json={"name": "test"})
            assert response.status_code == 400
            data = response.get_json()
            assert "email" in data["error"]

    def test_empty_field(self, app):
        """測試欄位為空值"""

        @app.route("/test", methods=["POST"])
        @validate_fields("name")
        def test_endpoint():
            return {"success": True}

        with app.test_client() as client:
            response = client.post("/test", json={"name": ""})
            assert response.status_code == 400


class TestHandleExceptions:
    """測試 handle_exceptions 裝飾器"""

    def test_game_not_found(self, app):
        """測試 GameNotFoundException"""

        @app.route("/test")
        @handle_exceptions
        def test_endpoint():
            raise GameNotFoundException("卡坦島")

        with app.test_client() as client:
            response = client.get("/test")
            assert response.status_code == 404
            data = response.get_json()
            assert data["success"] is False

    def test_member_not_found(self, app):
        """測試 MemberNotFoundException"""

        @app.route("/test")
        @handle_exceptions
        def test_endpoint():
            raise MemberNotFoundException("A001")

        with app.test_client() as client:
            response = client.get("/test")
            assert response.status_code == 404

    def test_game_already_borrowed(self, app):
        """測試 GameAlreadyBorrowedException"""

        @app.route("/test")
        @handle_exceptions
        def test_endpoint():
            raise GameAlreadyBorrowedException("卡坦島", "張三")

        with app.test_client() as client:
            response = client.get("/test")
            assert response.status_code == 409

    def test_generic_boardgame_exception(self, app):
        """測試一般的 BoardGameException"""

        @app.route("/test")
        @handle_exceptions
        def test_endpoint():
            raise BoardGameException("測試錯誤")

        with app.test_client() as client:
            response = client.get("/test")
            assert response.status_code == 400

    def test_unexpected_exception(self, app):
        """測試未預期的例外"""

        @app.route("/test")
        @handle_exceptions
        def test_endpoint():
            raise ValueError("未預期錯誤")

        with app.test_client() as client:
            response = client.get("/test")
            assert response.status_code == 500

    def test_no_exception(self, app):
        """測試正常執行（無例外）"""

        @app.route("/test")
        @handle_exceptions
        def test_endpoint():
            return {"success": True}

        with app.test_client() as client:
            response = client.get("/test")
            assert response.status_code == 200
