"""
通用型別定義

集中管理 boardgame-web 專案中常用的型別定義。
這些型別用於提供更好的 IDE 支援和型別檢查。
"""
from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple, TypedDict, Union

# ============ 桌遊相關型別 ============


class GameDict(TypedDict, total=False):
    """
    桌遊資料結構

    Attributes:
        name: 遊戲名稱
        bgg_id: BoardGameGeek ID (可選)
        players: 玩家人數範圍 (例如: "2-4")
        status: 遊戲狀態 ("可用", "已借出", "維護中" 等)
        custodian: 保管人
        image: 遊戲圖片 URL (可選)
        bgg_thumbnail: BGG 縮圖 URL (可選)
        is_expansion: 是否為擴充
        main_game: 主遊戲名稱 (如果是擴充)
        borrower: 借用人 (可選)
        borrow_date: 借用日期 (可選)
    """

    name: str
    bgg_id: Optional[int]
    players: str
    status: str
    custodian: str
    image: Optional[str]
    bgg_thumbnail: Optional[str]
    is_expansion: bool
    main_game: Optional[str]
    borrower: Optional[str]
    borrow_date: Optional[str]


class MemberDict(TypedDict, total=False):
    """
    社員資料結構

    Attributes:
        name: 社員姓名
        email: 電子郵件 (可選)
        join_date: 加入日期 (可選)
        status: 狀態 (可選)
    """

    name: str
    email: Optional[str]
    join_date: Optional[str]
    status: Optional[str]


# ============ API 回應型別 ============


class ErrorResponse(TypedDict, total=False):
    """
    標準錯誤回應結構

    Attributes:
        success: 固定為 False
        error_code: 錯誤代碼 (例如: "GAME_NOT_FOUND")
        message: 錯誤訊息 (使用者可讀)
        request_id: 請求追蹤 ID (開發環境)
    """

    success: bool  # 固定為 False
    error_code: str
    message: str
    request_id: Optional[str]


class SuccessResponse(TypedDict, total=False):
    """
    標準成功回應結構

    Attributes:
        success: 固定為 True
        data: 回應資料
        message: 成功訊息 (可選)
    """

    success: bool  # 固定為 True
    data: Any
    message: Optional[str]


# ============ BGG API 型別 ============


class BGGGameDict(TypedDict, total=False):
    """
    BoardGameGeek 遊戲資料結構

    Attributes:
        id: BGG 遊戲 ID
        name: 遊戲名稱
        year_published: 出版年份
        min_players: 最小玩家數
        max_players: 最大玩家數
        players_display: 玩家數顯示字串 (例如: "2-4")
        image: 遊戲圖片 URL
        thumbnail: 縮圖 URL
        description: 遊戲描述
        rating: BGG 評分
        chinese_name: 中文名稱 (如果有)
    """

    id: int
    name: str
    year_published: int
    min_players: int
    max_players: int
    players_display: str
    image: str
    thumbnail: str
    description: str
    rating: float
    chinese_name: Optional[str]


# ============ 常用型別別名 ============

# 列表型別
GameList = List[GameDict]
"""桌遊列表"""

MemberList = List[MemberDict]
"""社員列表"""

BGGGameList = List[BGGGameDict]
"""BGG 遊戲列表"""

# API 回應型別
ResponseTuple = Tuple[Dict[str, Any], int]
"""API 回應元組: (JSON 字典, HTTP 狀態碼)"""

# JSON 型別
JSONDict = Dict[str, Any]
"""泛用 JSON 字典"""

JSONList = List[Dict[str, Any]]
"""JSON 字典列表"""
