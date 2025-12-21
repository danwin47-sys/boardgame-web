"""
共用的 BoardGameManager 獲取函數
避免在每個 Blueprint 重複相同的程式碼
"""
from flask import current_app
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
