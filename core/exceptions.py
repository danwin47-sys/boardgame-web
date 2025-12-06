# coding: utf-8
"""
自定義異常模組
定義 boardgame-web 專案的異常類別
"""


class BoardGameException(Exception):
    """桌遊系統基礎異常"""
    pass


class GameNotFoundException(BoardGameException):
    """找不到指定的桌遊"""

    def __init__(self, game_name: str):
        self.game_name = game_name
        super().__init__(f"找不到桌遊：{game_name}")


class GameAlreadyBorrowedException(BoardGameException):
    """桌遊已被借出"""

    def __init__(self, game_name: str, borrower: str):
        self.game_name = game_name
        self.borrower = borrower
        super().__init__(f"《{game_name}》已經被 {borrower} 借走了")


class GameNotBorrowedException(BoardGameException):
    """桌遊未被借出（嘗試歸還未借出的遊戲）"""

    def __init__(self, game_name: str):
        self.game_name = game_name
        super().__init__(f"《{game_name}》目前未被借出")


class MemberNotFoundException(BoardGameException):
    """找不到指定的社員"""

    def __init__(self, member_identifier: str):
        self.member_identifier = member_identifier
        super().__init__(f"找不到社員：{member_identifier}")


class SheetConnectionError(BoardGameException):
    """Google Sheets 連線錯誤"""

    def __init__(self, message: str = "無法連線到 Google Sheets"):
        super().__init__(message)


class InvalidDataError(BoardGameException):
    """資料格式錯誤"""

    def __init__(self, message: str):
        super().__init__(f"資料格式錯誤：{message}")
