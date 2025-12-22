"""
社員 API Blueprint
處理社員相關的路由
"""
from typing import Tuple
from flask import Blueprint, jsonify, Response
import logging

from app.utils import get_manager

logger = logging.getLogger(__name__)

# 建立 Blueprint
members_bp = Blueprint("members", __name__, url_prefix="/api")


@members_bp.route("/members", methods=["GET"])
def get_members() -> Tuple[Response, int]:
    """獲取社員列表

    從 Google Sheets 讀取所有社員資料並返回。

    Returns:
        Tuple[Response, int]: JSON 響應包含社員列表和 HTTP 狀態碼
            - 成功時: ([{...}, {...}, ...], 200)
            - 失敗時: ({'success': False, 'error': '錯誤訊息'}, 500)

    Raises:
        Exception: 當資料庫連線失敗或資料讀取錯誤時
    """
    try:
        mgr = get_manager()
        members = mgr.load_members()
        return jsonify(members), 200
    except Exception as e:
        logger.error(f"獲取社員列表失敗: {e}", exc_info=True)
        return jsonify({"success": False, "error": str(e)}), 500
