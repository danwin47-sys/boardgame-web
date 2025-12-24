"""
共用的 BoardGameManager 獲取函數
避免在每個 Blueprint 重複相同的程式碼
"""
from flask import current_app
from typing import Dict, Any, Tuple, Optional
import logging

logger = logging.getLogger(__name__)


def get_manager():
    """從 app.config 獲取 BoardGameManager 單例

    使用單例模式確保整個應用程式使用同一個 BoardGameManager 實例。

    Returns:
        BoardGameManager: 全域的 BoardGameManager 實例

    Note:
        - 第一次調用時會自動初始化 BoardGameManager
        - 後續調用會返回已存在的實例
    """
    if "boardgame_manager" not in current_app.config:
        from core.facade import BoardGameManager

        logger.info("正在初始化 BoardGameManager...")
        current_app.config["boardgame_manager"] = BoardGameManager()
    return current_app.config["boardgame_manager"]


def error_response(
    message: str,
    error_code: str = "ERROR",
    status_code: int = 400,
    details: Optional[Dict[str, Any]] = None
) -> Tuple[Dict[str, Any], int]:
    """
    創建標準化的錯誤回應
    
    Args:
        message: 錯誤訊息（使用者可讀）
        error_code: 錯誤代碼（用於程式化處理）
        status_code: HTTP 狀態碼
        details: 額外的錯誤詳情（可選）
    
    Returns:
        Tuple[Dict, int]: (JSON 回應字典, HTTP 狀態碼)
    
    Example:
        from app.utils import error_response
        return error_response("找不到遊戲", "GAME_NOT_FOUND", 404)
    """
    response = {
        "success": False,
        "error_code": error_code,
        "message": message
    }
    if details:
        response["details"] = details
    return response, status_code


def success_response(
    data: Any = None,
    message: Optional[str] = None,
    status_code: int = 200
) -> Tuple[Dict[str, Any], int]:
    """
    創建標準化的成功回應
    
    Args:
        data: 回應資料
        message: 成功訊息（可選）
        status_code: HTTP 狀態碼
    
    Returns:
        Tuple[Dict, int]: (JSON 回應字典, HTTP 狀態碼)
    
    Example:
        from app.utils import success_response
        return success_response(games, "查詢成功")
    """
    response = {"success": True}
    if message:
        response["message"] = message
    if data is not None:
        # 如果 data 已經是字典且包含資料，直接合併
        if isinstance(data, dict):
            response.update(data)
        else:
            response["data"] = data
    return response, status_code
