# coding: utf-8
"""
API Schema 模組

使用 Pydantic 定義 API 請求/回應的資料結構，提供：
- 自動資料驗證
- 清晰的類型定義
- 自動文檔生成 (未來整合 OpenAPI)
"""
from typing import Optional, List
from pydantic import BaseModel, Field


# ============ 遊戲相關 Schema ============


class BorrowGameRequest(BaseModel):
    """借用遊戲請求"""

    name: str = Field(..., description="遊戲名稱")
    user_name: str = Field(..., description="借閱者姓名")
    user_id: str = Field(..., description="借閱者 ID")


class ReturnGameRequest(BaseModel):
    """歸還遊戲請求"""

    name: str = Field(..., description="遊戲名稱")


class BatchBorrowRequest(BaseModel):
    """批次借用請求"""

    game_names: List[str] = Field(..., description="遊戲名稱列表")
    member_id: str = Field(..., description="借閱者 ID")


class BatchReturnRequest(BaseModel):
    """批次歸還請求"""

    game_names: List[str] = Field(..., description="遊戲名稱列表")


# ============ BGG 相關 Schema ============


class AddToCollectionRequest(BaseModel):
    """加入館藏請求"""

    game_id: int = Field(..., description="BGG 遊戲 ID")
    custodian: Optional[str] = Field(default="", description="保管人")
    force: Optional[bool] = Field(default=False, description="強制加入（忽略重複檢查）")


class LinkGameRequest(BaseModel):
    """連結遊戲請求"""

    bgg_id: int = Field(..., description="BGG 遊戲 ID")


# ============ 管理員相關 Schema ============


class AdminLoginRequest(BaseModel):
    """管理員登入請求"""

    password: str = Field(..., description="管理員密碼")


# ============ 通用回應 Schema ============


class SuccessResponse(BaseModel):
    """成功回應"""

    success: bool = True
    message: str


class ErrorResponse(BaseModel):
    """錯誤回應"""

    success: bool = False
    error_code: str
    message: str


class GameResponse(BaseModel):
    """遊戲資料回應"""

    name: str
    status: Optional[str] = None
    borrower: Optional[str] = None
    borrower_id: Optional[str] = None
    custodian: Optional[str] = None
    bgg_id: Optional[int] = None
    image: Optional[str] = None
    players: Optional[str] = None
