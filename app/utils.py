"""
共用的 BoardGameManager 獲取函數
避免在每個 Blueprint 重複相同的程式碼
"""
from flask import current_app, g
from typing import Dict, Any, Tuple, Optional
import logging
import traceback

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
    details: Optional[Dict[str, Any]] = None,
    error_obj: Exception = None
) -> Tuple[Dict[str, Any], int]:
    """
    創建標準化的錯誤回應（帶詳細日誌）
    
    Args:
        message: 錯誤訊息（使用者可讀）
        error_code: 錯誤代碼（用於程式化處理）
        status_code: HTTP 狀態碼
        details: 額外的錯誤詳情（可選）
        error_obj: 原始異常對象（用於記錄堆疊追蹤）
    
    Returns:
        Tuple[Dict, int]: (JSON 回應字典, HTTP 狀態碼)
    
    Example:
        try:
            # some code
        except Exception as e:
            return error_response(
                "載入資料失敗",
                "LOAD_DATA_ERROR",
                500,
                error_obj=e
            )
    """
    request_id = getattr(g, 'request_id', 'unknown')
    
    # 構建詳細的日誌資訊
    log_data = {
        'request_id': request_id,
        'error_code': error_code,
        'error_message': message,  # 改名避免與 logging 衝突
        'status_code': status_code
    }
    
    if details:
        log_data['context'] = details
    
    # 如果有異常對象，記錄完整堆疊
    if error_obj:
        log_data['exception_type'] = type(error_obj).__name__
        log_data['exception_message'] = str(error_obj)
    
    # 記錄錯誤（使用適當的日誌層級）
    if status_code >= 500:
        logger.error(
            f"[{request_id}] {error_code}: {message}",
            extra=log_data,
            exc_info=error_obj is not None
        )
    elif status_code >= 400:
        logger.warning(
            f"[{request_id}] {error_code}: {message}",
            extra=log_data
        )
    
    # 返回標準錯誤回應
    response = {
        "success": False,
        "error_code": error_code,
        "message": message
    }
    
    # 在開發環境加入 request_id（方便除錯）
    if current_app.debug and request_id != 'unknown':
        response["request_id"] = request_id
    
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
