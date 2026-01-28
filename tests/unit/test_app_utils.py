"""
測試 app/utils.py 模組
"""
from unittest.mock import MagicMock

import pytest
from flask import Flask, g

from app.utils import error_response, get_manager, success_response


class TestAppUtils:
    """測試 app/utils.py"""

    def test_get_manager_singleton(self):
        """測試 get_manager 單例模式"""
        app = Flask(__name__)
        app.config["boardgame_manager"] = "existing_manager"

        with app.app_context():
            manager = get_manager()
            assert manager == "existing_manager"

    def test_error_response_500_with_obj(self):
        """測試 500 錯誤回應並帶有異常對象"""
        app = Flask(__name__)
        with app.test_request_context("/"):
            g.request_id = "test-id"
            err = Exception("Test exception")

            response, status = error_response(
                message="Error message",
                error_code="TEST_ERROR",
                status_code=500,
                details={"key": "value"},
                error_obj=err,
            )

            assert status == 500
            assert response["success"] is False
            assert response["error_code"] == "TEST_ERROR"
            assert response["key"] == "value"

    def test_error_response_400_debug_mode(self):
        """測試 400 錯誤回應並在 Debug 模式下"""
        app = Flask(__name__)
        app.debug = True
        with app.test_request_context("/"):
            g.request_id = "debug-id"

            response, status = error_response(
                message="Bad request", error_code="BAD_REQ", status_code=400
            )

            assert status == 400
            assert response["request_id"] == "debug-id"

    def test_success_response_with_dict(self):
        """測試成功回應帶有字典資料"""
        response, status = success_response(data={"item": "info"}, message="Success")

        assert status == 200
        assert response["success"] is True
        assert response["message"] == "Success"
        assert response["item"] == "info"

    def test_success_response_with_list(self):
        """測試成功回應帶有列表資料"""
        response, status = success_response(data=[1, 2, 3])

        assert status == 200
        assert response["data"] == [1, 2, 3]
