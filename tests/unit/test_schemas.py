"""
測試 app/schemas.py Pydantic 模組
"""
import pytest
from pydantic import ValidationError

from app.schemas import (
    AddToCollectionRequest,
    AdminLoginRequest,
    BatchBorrowRequest,
    BatchReturnRequest,
    BorrowGameRequest,
    ErrorResponse,
    GameResponse,
    LinkGameRequest,
    ReturnGameRequest,
    SuccessResponse,
)


class TestGameSchemas:
    """測試遊戲相關 Schema"""

    def test_borrow_game_request_valid(self):
        """測試有效的借用請求"""
        req = BorrowGameRequest(name="卡坦島", user_name="張三", user_id="A001")
        assert req.name == "卡坦島"
        assert req.user_name == "張三"
        assert req.user_id == "A001"

    def test_borrow_game_request_missing_field(self):
        """測試缺少必填欄位"""
        with pytest.raises(ValidationError):
            BorrowGameRequest(name="卡坦島", user_name="張三")

    def test_return_game_request_valid(self):
        """測試有效的歸還請求"""
        req = ReturnGameRequest(name="璀璨寶石")
        assert req.name == "璀璨寶石"

    def test_batch_borrow_request_valid(self):
        """測試有效的批次借用請求"""
        req = BatchBorrowRequest(game_names=["卡坦島", "璀璨寶石"], member_id="A001")
        assert len(req.game_names) == 2
        assert req.member_id == "A001"

    def test_batch_return_request_valid(self):
        """測試有效的批次歸還請求"""
        req = BatchReturnRequest(game_names=["卡坦島", "璀璨寶石"])
        assert len(req.game_names) == 2


class TestBGGSchemas:
    """測試 BGG 相關 Schema"""

    def test_add_to_collection_request_valid(self):
        """測試有效的加入館藏請求"""
        req = AddToCollectionRequest(game_id=13)
        assert req.game_id == 13
        assert req.custodian == ""
        assert req.force is False

    def test_add_to_collection_request_with_options(self):
        """測試帶選項的加入館藏請求"""
        req = AddToCollectionRequest(game_id=13, custodian="保管人", force=True)
        assert req.custodian == "保管人"
        assert req.force is True

    def test_link_game_request_valid(self):
        """測試有效的連結遊戲請求"""
        req = LinkGameRequest(bgg_id=13)
        assert req.bgg_id == 13


class TestAdminSchemas:
    """測試管理員相關 Schema"""

    def test_admin_login_request_valid(self):
        """測試有效的登入請求"""
        req = AdminLoginRequest(password="admin123")
        assert req.password == "admin123"

    def test_admin_login_request_missing_password(self):
        """測試缺少密碼"""
        with pytest.raises(ValidationError):
            AdminLoginRequest()


class TestResponseSchemas:
    """測試回應 Schema"""

    def test_success_response(self):
        """測試成功回應"""
        resp = SuccessResponse(message="操作成功")
        assert resp.success is True
        assert resp.message == "操作成功"

    def test_error_response(self):
        """測試錯誤回應"""
        resp = ErrorResponse(error_code="GAME_NOT_FOUND", message="找不到遊戲")
        assert resp.success is False
        assert resp.error_code == "GAME_NOT_FOUND"

    def test_game_response(self):
        """測試遊戲資料回應"""
        resp = GameResponse(name="卡坦島", status="可借", bgg_id=13)
        assert resp.name == "卡坦島"
        assert resp.bgg_id == 13
        assert resp.borrower is None
