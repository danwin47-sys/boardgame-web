# coding: utf-8
"""
自定義異常模組
定義 boardgame-web 專案的異常類別

所有自定義異常都繼承自 BoardGameException，並提供：
- http_status_code: 對應的 HTTP 狀態碼
- error_code: 自定義錯誤代碼
- to_dict(): 轉換為 JSON 回應格式
"""
from typing import Dict, Any


class BoardGameException(Exception):
    """桌遊系統基礎異常

    所有專案自定義異常的基類。提供統一的錯誤回應格式。

    Attributes:
        http_status_code: HTTP 狀態碼，預設 500
        error_code: 錯誤代碼，用於前端識別錯誤類型
    """

    http_status_code: int = 500
    error_code: str = "INTERNAL_ERROR"

    def to_dict(self) -> Dict[str, Any]:
        """轉換為 JSON 回應格式

        Returns:
            統一格式的錯誤回應字典
        """
        return {"success": False, "error_code": self.error_code, "message": str(self)}


class GameNotFoundException(BoardGameException):
    """找不到指定的桌遊

    Attributes:
        game_name: 找不到的遊戲名稱
    """

    http_status_code = 404
    error_code = "GAME_NOT_FOUND"

    def __init__(self, game_name: str):
        self.game_name = game_name
        super().__init__(f"找不到桌遊：{game_name}")


class GameAlreadyBorrowedException(BoardGameException):
    """桌遊已被借出

    Attributes:
        game_name: 遊戲名稱
        borrower: 目前借閱者
    """

    http_status_code = 409
    error_code = "GAME_ALREADY_BORROWED"

    def __init__(self, game_name: str, borrower: str):
        self.game_name = game_name
        self.borrower = borrower
        super().__init__(f"《{game_name}》已經被 {borrower} 借走了")


class GameNotBorrowedException(BoardGameException):
    """桌遊未被借出（嘗試歸還未借出的遊戲）

    Attributes:
        game_name: 遊戲名稱
    """

    http_status_code = 400
    error_code = "GAME_NOT_BORROWED"

    def __init__(self, game_name: str):
        self.game_name = game_name
        super().__init__(f"《{game_name}》目前未被借出")


class MemberNotFoundException(BoardGameException):
    """找不到指定的社員

    Attributes:
        member_identifier: 社員識別碼（ID 或姓名）
    """

    http_status_code = 404
    error_code = "MEMBER_NOT_FOUND"

    def __init__(self, member_identifier: str):
        self.member_identifier = member_identifier
        super().__init__(f"找不到社員：{member_identifier}")


class SheetConnectionError(BoardGameException):
    """Google Sheets 連線錯誤"""

    http_status_code = 503
    error_code = "SHEET_CONNECTION_ERROR"

    def __init__(self, message: str = "無法連線到 Google Sheets"):
        super().__init__(message)


class InvalidDataError(BoardGameException):
    """資料格式錯誤"""

    http_status_code = 400
    error_code = "INVALID_DATA"

    def __init__(self, message: str):
        super().__init__(f"資料格式錯誤：{message}")


class ValidationError(BoardGameException):
    """請求驗證錯誤"""

    http_status_code = 400
    error_code = "VALIDATION_ERROR"

    def __init__(self, message: str):
        super().__init__(message)


class DuplicateGameError(BoardGameException):
    """遊戲重複錯誤"""

    http_status_code = 409
    error_code = "DUPLICATE_GAME"

    def __init__(self, game_name: str, bgg_id: int):
        self.game_name = game_name
        self.bgg_id = bgg_id
        super().__init__(f"遊戲「{game_name}」(BGG ID: {bgg_id}) 已存在於館藏中")
