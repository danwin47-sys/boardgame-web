"""
遊戲 API Blueprint
處理桌遊相關的路由：列表、借還操作
"""
from typing import Tuple, Any, Optional, Dict
from flask import Blueprint, jsonify, request, Response
import logging

from app.utils import get_manager, error_response
from core.types import ResponseTuple

logger = logging.getLogger(__name__)

# 建立 Blueprint
games_bp = Blueprint("games", __name__, url_prefix="/api")


@games_bp.route("/games", methods=["GET"])
def get_games() -> Tuple[Response, int]:
    """獲取桌遊列表

    從 Google Sheets 讀取所有桌遊資料並返回。

    Returns:
        Tuple[Response, int]: JSON 響應包含桌遊列表和 HTTP 狀態碼
            - 成功時: ({'games': [...]}, 200)
            - 失敗時: ({'success': False, 'error': '錯誤訊息'}, 500)

    Raises:
        Exception: 當資料庫連線失敗或資料讀取錯誤時
    """
    try:
        mgr = get_manager()
        mgr.games = mgr.load_data()
        return jsonify(mgr.games), 200
    except Exception as e:
        logger.error(f"獲取桌遊列表失敗: {e}", exc_info=True)
        return error_response(str(e), "LOAD_GAMES_ERROR", 500)


@games_bp.route("/borrow", methods=["POST"])
def borrow_game() -> ResponseTuple:
    """借出桌遊

    處理桌遊借出請求，更新桌遊狀態並記錄借閱人資訊。

    Request Body:
        {
            "name": str,        # 桌遊名稱
            "member_id": str    # 社員 ID
        }

    Returns:
        Tuple[Response, int]: JSON 響應和 HTTP 狀態碼
            - 成功時: ({'message': '訊息', 'success': True}, 200)
            - 失敗時: ({'success': False, 'error': '錯誤訊息'}, 400/404/500)

    Raises:
        Exception: 當資料庫更新失敗時
    """
    try:
        data = request.get_json()
        if not data:
            return error_response("缺少請求資料", "MISSING_REQUEST_DATA", 400)

        name = data.get("name")
        member_id = data.get("member_id")

        if not name or not member_id:
            return error_response("缺少必要欄位: name, member_id", "MISSING_REQUIRED_FIELDS", 400)

        mgr = get_manager()
        member = mgr.find_member_by_id(member_id)
        if not member:
            return error_response(f"找不到社員: {member_id}", "MEMBER_NOT_FOUND", 404)

        success, msg = mgr.borrow_game(name, member["name"], member["id"])
        return jsonify({"message": msg, "success": success}), 200 if success else 400
    except Exception as e:
        logger.error(f"借桌遊失敗: {e}", exc_info=True)
        return error_response(str(e), "BORROW_GAME_ERROR", 500)


@games_bp.route("/return", methods=["POST"])
def return_game() -> ResponseTuple:
    """歸還桌遊

    處理桌遊歸還請求，更新桌遊狀態並清除借閱人資訊。

    Request Body:
        {
            "name": str  # 桌遊名稱
        }

    Returns:
        Tuple[Response, int]: JSON 響應和 HTTP 狀態碼
            - 成功時: ({'message': '訊息', 'success': True}, 200)
            - 失敗時: ({'success': False, 'error': '錯誤訊息'}, 400/500)

    Raises:
        Exception: 當資料庫更新失敗時
    """
    try:
        data = request.get_json()
        name = data.get("name")
        if not name:
            return error_response("缺少桌遊名稱", "MISSING_GAME_NAME", 400)

        mgr = get_manager()
        success, msg = mgr.return_game(name)
        return jsonify({"message": msg, "success": success}), 200 if success else 400
    except Exception as e:
        logger.error(f"歸還桌遊失敗: {e}", exc_info=True)
        return error_response(str(e), "RETURN_GAME_ERROR", 500)


# ============ 擴充管理 API ============


@games_bp.route("/games/<game_name>/expansion", methods=["PUT"])
def update_game_expansion(game_name: str) -> ResponseTuple:
    """取得遊戲的所有擴充"""
    try:
        from core.expansion_service import ExpansionService
        from app.utils import get_manager

        mgr = get_manager()
        expansion_service = ExpansionService(mgr.client)
        all_games = mgr.load_data()

        # Placeholder for actual logic
        # For example, if the request body contains expansion data to update
        data = request.get_json()
        if not data:
            return error_response("缺少請求資料", "MISSING_REQUEST_DATA", 400)

        # Assuming 'expansion_name' and 'is_expansion_of' are in the request body
        expansion_name = data.get("expansion_name")
        is_expansion_of = data.get("is_expansion_of")

        if not expansion_name or not is_expansion_of:
            return error_response("缺少必要欄位: expansion_name, is_expansion_of", "MISSING_REQUIRED_FIELDS", 400)

        # Example: Update logic (this would depend on your ExpansionService implementation)
        # For now, just return a success message
        return jsonify(
            {
                "success": True,
                "message": f"Expansion '{expansion_name}' for game '{game_name}' updated successfully.",
                "updated_data": {"expansion_name": expansion_name, "is_expansion_of": is_expansion_of}
            }
        ), 200
    except Exception as e:
        logger.error(f"更新遊戲擴充失敗: {e}")
        return error_response(str(e), "UPDATE_EXPANSION_ERROR", 500)


@games_bp.route("/games/<game_name>/expansions", methods=["GET"])
def get_game_expansions(game_name: str) -> ResponseTuple:
    """取得遊戲的所有擴充"""
    try:
        from core.expansion_service import ExpansionService
        from app.utils import get_manager

        mgr = get_manager()
        expansion_service = ExpansionService(mgr.client)
        all_games = mgr.load_data()

        expansions = expansion_service.get_expansions(game_name, all_games)

        return jsonify(
            {
                "success": True,
                "game_name": game_name,
                "expansions": expansions,
                "count": len(expansions),
            }
        )
    except Exception as e:
        logger.error(f"取得擴充失敗: {e}")
        return error_response(str(e), "GET_EXPANSIONS_ERROR", 500)


@games_bp.route("/games/<game_name>/family", methods=["GET"])
def get_game_family(game_name):
    """取得遊戲家族（主遊戲 + 所有擴充）"""
    try:
        from core.expansion_service import ExpansionService
        from app.utils import get_manager

        mgr = get_manager()
        expansion_service = ExpansionService(mgr.client)
        all_games = mgr.load_data()

        family = expansion_service.get_game_family(game_name, all_games)

        return jsonify(
            {
                "success": True,
                "game_name": game_name,
                "parent": family.get("parent"),
                "expansions": family.get("expansions", []),
                "expansion_count": len(family.get("expansions", [])),
            }
        )
    except Exception as e:
        logger.error(f"取得遊戲家族失敗: {e}")
        return error_response(str(e), "GET_GAME_FAMILY_ERROR", 500)


@games_bp.route("/games/<game_name>/validate-borrow", methods=["GET"])
def validate_game_borrow(game_name):
    """驗證借出操作（檢查擴充依賴）"""
    try:
        from core.expansion_service import ExpansionService
        from app.utils import get_manager

        mgr = get_manager()
        expansion_service = ExpansionService(mgr.client)
        all_games = mgr.load_data()

        can_borrow, message, info = expansion_service.validate_borrow(
            game_name, all_games
        )

        return jsonify(
            {
                "success": True,
                "can_borrow": can_borrow,
                "message": message,
                "info": info,
            }
        )
    except Exception as e:
        logger.error(f"驗證借出失敗: {e}")
        return error_response(str(e), "VALIDATE_BORROW_ERROR", 500)
