"""
BGG (BoardGameGeek) API Routes
處理所有 BGG 相關的 API 端點
"""
import logging
import traceback
from typing import Optional, Tuple
from urllib.parse import unquote

from flask import Blueprint, Response, jsonify, request

from app.utils import error_response, get_manager
from core.types import ResponseTuple

logger = logging.getLogger(__name__)

# 建立 Blueprint
bgg_bp = Blueprint("bgg", __name__, url_prefix="/api/bgg")

# 延遲導入 BGG Service，避免循環依賴
_bgg_service = None


def get_bgg_service():
    """延遲載入 BGG Service

    使用單例模式，確保 BGG Service 只被初始化一次。

    Returns:
        BGGService: BGG 服務實例
    """
    global _bgg_service
    if _bgg_service is None:
        from core.bgg_service import BGGService

        logger.info("正在初始化 BGG API 連線...")
        _bgg_service = BGGService()
    return _bgg_service


# ============ BGG 通用 API ============


@bgg_bp.route("/search", methods=["GET"])
def search_bgg() -> ResponseTuple:
    """搜尋 BGG 桌遊

    根據關鍵字搜尋 BoardGameGeek 資料庫中的桌遊。

    Query Parameters:
        q (str): 搜尋關鍵字（必填）

    Returns:
        Tuple[Response, int]: JSON 響應和 HTTP 狀態碼
            - 成功時: ({'success': True, 'results': [...]}, 200)
            - 失敗時: ({'success': False, 'error': '錯誤訊息'}, 400/500)

    Raises:
        Exception: 當 BGG API 請求失敗時
    """
    try:
        query = request.args.get("q", "").strip()
        if not query:
            return error_response("缺少搜尋關鍵字 (q)", "MISSING_QUERY_PARAMETER", 400)

        logger.debug(f"BGG search query: {query}")
        bgg = get_bgg_service()
        results = bgg.search_games(query)

        return jsonify({"success": True, "results": results}), 200
    except Exception as e:
        logger.error(f"BGG search exception: {e}")
        traceback.print_exc()
        return error_response(str(e), "BGG_SEARCH_ERROR", 500)


@bgg_bp.route("/games/<int:game_id>", methods=["GET"])
def get_bgg_game(game_id: int) -> ResponseTuple:
    """取得 BGG 遊戲詳情

    根據 BGG ID 獲取遊戲的詳細資訊。

    Args:
        game_id: BGG 遊戲 ID

    Returns:
        Tuple[Response, int]: JSON 響應和 HTTP 狀態碼
            - 成功時: ({'success': True, 'game': {...}}, 200)
            - 失敗時: ({'success': False, 'error': '錯誤訊息'}, 404/500)

    Raises:
        Exception: 當 BGG API 請求失敗時
    """
    try:
        logger.debug(f"Fetching BGG game details: {game_id}")
        bgg = get_bgg_service()
        game = bgg.get_game_details(game_id)

        if game:
            return jsonify({"success": True, "game": game}), 200
        else:
            return error_response("找不到遊戲", "GAME_NOT_FOUND", 404)
    except Exception as e:
        logger.error(f"Get BGG game exception: {e}")
        traceback.print_exc()
        return error_response(str(e), "BGG_API_ERROR", 500)


@bgg_bp.route("/hot", methods=["GET"])
def get_hot_games() -> ResponseTuple:
    """取得 BGG 熱門桌遊

    從 BoardGameGeek 獲取當前熱門的桌遊列表。

    Query Parameters:
        limit (int, optional): 限制返回數量，預設為 10

    Returns:
        Tuple[Response, int]: JSON 響應和 HTTP 狀態碼
            - 成功時: ({'success': True, 'games': [...]}, 200)
            - 失敗時: ({'success': False, 'error': '錯誤訊息'}, 500)

    Raises:
        Exception: 當 BGG API 請求失敗時
    """
    try:
        limit = int(request.args.get("limit", 10))
        logger.debug(f"Fetching hot games, limit: {limit}")

        bgg = get_bgg_service()
        games = bgg.get_hot_games(limit)

        return jsonify({"success": True, "games": games}), 200
    except Exception as e:
        logger.error(f"Get hot games exception: {e}")
        traceback.print_exc()
        return error_response(str(e), "BGG_HOT_GAMES_ERROR", 500)


@bgg_bp.route("/our-hot-games", methods=["GET"])
def get_our_hot_games() -> ResponseTuple:
    """取得館藏中的熱門遊戲

    從 BGG 熱門遊戲列表中篩選出本館藏已有的遊戲。

    Query Parameters:
        limit (int, optional): 檢查前 N 個熱門遊戲，預設為 50

    Returns:
        Tuple[Response, int]: JSON 響應和 HTTP 狀態碼
            - 成功時: ({
                'success': True,
                'games': [...],
                'total': int
              }, 200)
            - 失敗時: ({'success': False, 'error': '錯誤訊息'}, 500)

    Raises:
        Exception: 當資料讀取失敗時
    """
    try:
        limit = int(request.args.get("limit", 50))
        logger.debug(f"Fetching our hot games, checking top {limit}")

        # 取得 Manager
        mgr = get_manager()

        # 使用 BGG Service 的新方法
        bgg = get_bgg_service()
        our_hot_games = bgg.get_our_hot_games(mgr.client, limit=limit)

        return (
            jsonify(
                {"success": True, "games": our_hot_games, "total": len(our_hot_games)}
            ),
            200,
        )
    except Exception as e:
        logger.error(f"Get our hot games exception: {e}")
        traceback.print_exc()
        return error_response(str(e), "OUR_HOT_GAMES_ERROR", 500)


@bgg_bp.route("/recommendations", methods=["GET"])
def get_recommendations() -> ResponseTuple:
    """取得推薦桌遊

    從 Google Sheets 讀取指定分類的推薦遊戲列表，並獲取遊戲詳細資訊。
    支援 BGG 推薦和社團推薦兩種來源。

    Query Parameters:
        category (str): 分類名稱（party/strategy/family/children）
        source (str, optional): 來源（bgg 或 club），預設為 'bgg'

    Returns:
        Tuple[Response, int]: JSON 響應和 HTTP 狀態碼
            - 成功時: ({'success': True, 'games': [...]}, 200)
            - 失敗時: ({'success': False, 'error': '錯誤訊息'}, 400/500)

    Raises:
        Exception: 當資料讀取或 API 請求失敗時
    """
    try:
        category = request.args.get("category")
        source = request.args.get("source", "bgg")  # bgg or club

        if not category:
            return error_response("缺少 category 參數", "MISSING_CATEGORY_PARAMETER", 400)

        logger.debug(f"Fetching recommendations: source={source}, category={category}")

        # 組合 Sheet 中的分類鍵值
        sheet_category = f"{source}-{category}"

        # 取得 Manager
        mgr = get_manager()

        # 從 Google Sheet 讀取 ID
        game_ids = mgr.client.load_bgg_recommendations(sheet_category)

        if not game_ids:
            logger.warning(f"找不到推薦資料: {sheet_category}")
            return jsonify({"success": True, "games": []}), 200

        logger.info(f"從 Sheet 讀取 {sheet_category}，共 {len(game_ids)} 個遊戲")

        # 獲取遊戲詳情
        bgg = get_bgg_service()
        games = []

        # 載入公司內部桌遊數據 (用於中文名稱對照)
        internal_games = mgr.load_data()
        bgg_id_to_chinese = {}
        for internal_game in internal_games:
            bgg_id = internal_game.get("bgg_id")
            chinese_name = internal_game.get("name")
            if bgg_id and chinese_name:
                try:
                    bgg_id_to_chinese[int(bgg_id)] = chinese_name
                except (ValueError, TypeError):
                    continue

        for game_id in game_ids:
            try:
                game = bgg.get_game_details(game_id)
                if game:
                    # 加入中文名稱
                    if game["id"] in bgg_id_to_chinese:
                        game["chinese_name"] = bgg_id_to_chinese[game["id"]]

                    games.append(game)
            except Exception as e:
                logger.error(f"Error fetching game details for {game_id}: {e}")
                continue

        return jsonify({"success": True, "games": games}), 200

    except Exception as e:
        logger.error(f"Get recommendations exception: {e}")
        traceback.print_exc()
        return error_response(str(e), "BGG_RECOMMENDATIONS_ERROR", 500)


@bgg_bp.route("/collection", methods=["POST"])
def add_to_collection() -> ResponseTuple:
    """從 BGG 加入桌遊到館藏

    根據 BGG ID 獲取遊戲詳情並將遊戲加入到 Google Sheets 館藏中。
    支援重複檢查，避免加入已存在的遊戲。

    Request Body:
        {
            "game_id": int,           # BGG 遊戲 ID（必填）
            "custodian": str,         # 保管人（選填）
            "force": bool             # 強制加入（選填，預設 False）
        }

    Returns:
        Tuple[Response, int]: JSON 響應和 HTTP 狀態碼
            - 成功時: ({
                'success': True,
                'message': '訊息',
                'game': {遊戲資料}
              }, 200)
            - 重複時: ({
                'success': False,
                'duplicate': True,
                'existing_game': {...},
                'message': '遊戲已存在'
              }, 409)
            - 失敗時: ({'success': False, 'error': '錯誤訊息'}, 400/404/500)

    Note:
        - 自動從 BGG 獲取遊戲詳情（名稱、玩家數、圖片等）
        - 新加入的遊戲狀態預設為「可用」
        - 加入前檢查 BGG ID 是否已存在
        - 可使用 force=true 強制加入重複遊戲
        - 加入後會自動清除遊戲列表快取

    Raises:
        Exception: 當 BGG API 請求失敗或 Google Sheets 更新失敗時
    """
    try:
        data = request.get_json()
        game_id = data.get("game_id")
        custodian = data.get("custodian", "")
        force = data.get("force", False)

        if not game_id:
            return error_response("缺少 game_id", "MISSING_GAME_ID", 400)

        logger.debug(
            f"Adding BGG game to collection: {game_id}, custodian: {custodian}, force: {force}"
        )

        # 取得 Manager
        mgr = get_manager()

        # 檢查遊戲是否已存在（除非強制加入）
        if not force:
            existing_games = mgr.load_data()
            for existing_game in existing_games:
                existing_bgg_id = existing_game.get("bgg_id")
                # 檢查 BGG ID 是否相符
                if existing_bgg_id and str(existing_bgg_id) == str(game_id):
                    logger.warning(
                        f"遊戲已存在：{existing_game.get('name')} (BGG ID: {game_id})"
                    )
                    return (
                        jsonify(
                            {
                                "success": False,
                                "duplicate": True,
                                "existing_game": {
                                    "name": existing_game.get("name"),
                                    "bgg_id": existing_game.get("bgg_id"),
                                    "custodian": existing_game.get("custodian", ""),
                                    "status": existing_game.get("status", ""),
                                    "players": existing_game.get("players", ""),
                                },
                                "message": f'遊戲「{existing_game.get("name")}」(BGG ID: {game_id}) 已存在於館藏中',
                            }
                        ),
                        409,
                    )

        # 取得遊戲詳情
        bgg = get_bgg_service()
        game = bgg.get_game_details(game_id)

        if not game:
            return error_response(f"找不到 BGG 遊戲: {game_id}", "GAME_NOT_FOUND", 404)

        # 準備要加入到 Google Sheets 的遊戲資料
        game_data = {
            "name": game["name"],
            "bgg_id": game_id,
            "players": game.get("players_display", ""),
            "image": game.get("image", ""),
            "bgg_thumbnail": game.get("thumbnail", ""),
            "custodian": custodian,
            "status": "可用",  # 新加入的遊戲預設為可用
        }

        # 將遊戲加入到 Google Sheets
        success = mgr.client.add_new_game(game_data)

        if success:
            msg = f'已成功將「{game["name"]}」加入館藏'
            if force:
                msg += "（強制加入）"
            logger.info(
                f"成功將 BGG 遊戲加入館藏：{game['name']} (ID: {game_id}){' [FORCED]' if force else ''}"
            )
            return jsonify({"success": True, "message": msg, "game": game_data}), 200
        else:
            return jsonify({"success": False, "error": "加入遊戲到 Google Sheets 失敗"}), 500

    except Exception as e:
        logger.error(f"Add to collection exception: {e}")
        traceback.print_exc()
        return error_response(str(e), "ADD_TO_COLLECTION_ERROR", 500)


# ============ BGG 遊戲連結 API ============


@bgg_bp.route("/games/link/search/<game_name>", methods=["GET"])
def search_for_linking(game_name: str) -> ResponseTuple:
    """搜尋 BGG 遊戲（用於連結功能）

    根據遊戲名稱搜尋 BGG，用於將本地遊戲連結到 BGG 資料庫。

    Args:
        game_name: URL 編碼的遊戲名稱

    Returns:
        Tuple[Response, int]: JSON 響應和 HTTP 狀態碼
            - 成功時: ({
                'success': True,
                'game_name': str,
                'results': [...]
              }, 200)
            - 失敗時: ({'success': False, 'error': '錯誤訊息'}, 500)

    Raises:
        Exception: 當 BGG API 請求失敗時
    """
    try:
        decoded_game_name = unquote(game_name)
        logger.debug(
            f"search_for_linking - Original: {game_name}, Decoded: {decoded_game_name}"
        )

        bgg = get_bgg_service()
        results = bgg.search_games(decoded_game_name)

        return (
            jsonify(
                {"success": True, "game_name": decoded_game_name, "results": results}
            ),
            200,
        )
    except Exception as e:
        logger.error(f"search_for_linking exception: {e}")
        traceback.print_exc()
        return error_response(str(e), "BGG_SEARCH_LINKING_ERROR", 500)


@bgg_bp.route("/games/link/<game_name>", methods=["POST"])
def link_game(game_name: str) -> ResponseTuple:
    """連結桌遊到 BGG

    將 Google Sheets 中的桌遊連結到 BGG 資料庫，並更新 BGG ID、縮圖等資訊。

    Args:
        game_name: URL 編碼的遊戲名稱

    Request Body:
        {
            "bgg_id": int  # BGG 遊戲 ID（必填）
        }

    Returns:
        Tuple[Response, int]: JSON 響應和 HTTP 狀態碼
            - 成功時: ({'success': True, 'message': '訊息'}, 200)
            - 失敗時: ({'success': False, 'error': '錯誤訊息'}, 400/404/500)

    Raises:
        Exception: 當資料庫更新失敗時
    """
    try:
        decoded_game_name = unquote(game_name)
        logger.debug(f"link_game - Original: {game_name}")
        logger.debug(f"link_game - Decoded: {decoded_game_name}")

        data = request.get_json()
        bgg_id = data.get("bgg_id")

        if not bgg_id:
            return error_response("缺少 bgg_id", "MISSING_BGG_ID", 400)

        # 使用共用 manager
        mgr = get_manager()

        all_games = mgr.load_data()
        all_game_names = [g.get("name", "") for g in all_games]
        logger.debug(f"Available games: {all_game_names}")
        logger.debug(f"Looking for: '{decoded_game_name}'")

        # 取得 BGG 遊戲詳情以獲取縮圖和玩家數
        bgg = get_bgg_service()
        game_details = bgg.get_game_details(bgg_id)
        thumbnail_url = game_details.get("thumbnail") if game_details else None
        image_url = game_details.get("image") if game_details else None
        players_display = game_details.get("players_display") if game_details else None

        success = mgr.client.update_game_bgg_id(
            decoded_game_name, bgg_id, thumbnail_url, image_url, players_display
        )

        if success:
            return (
                jsonify(
                    {
                        "success": True,
                        "message": f"已成功連結「{decoded_game_name}」到 BGG (ID: {bgg_id})",
                    }
                ),
                200,
            )
        else:
            game_list = "、".join(all_game_names[:5])
            return (
                jsonify(
                    {
                        "success": False,
                        "error": f"找不到桌遊「{decoded_game_name}」，請確認名稱是否正確。可用的桌遊: {game_list}...",
                    }
                ),
                404,
            )
    except Exception as e:
        logger.error(f"link_game exception: {e}")
        traceback.print_exc()
        return error_response(str(e), "LINK_GAME_ERROR", 500)


@bgg_bp.route("/games/link/<game_name>", methods=["DELETE"])
def unlink_game(game_name: str) -> ResponseTuple:
    """取消桌遊與 BGG 的連結

    移除 Google Sheets 中桌遊的 BGG ID 連結。

    Args:
        game_name: URL 編碼的遊戲名稱

    Returns:
        Tuple[Response, int]: JSON 響應和 HTTP 狀態碼
            - 成功時: ({'success': True, 'message': '訊息'}, 200)
            - 失敗時: ({'success': False, 'error': '錯誤訊息'}, 404/500)

    Raises:
        Exception: 當資料庫更新失敗時
    """
    try:
        decoded_game_name = unquote(game_name)
        logger.debug(
            f"unlink_game - Original: {game_name}, Decoded: {decoded_game_name}"
        )

        # 使用共用 manager
        mgr = get_manager()

        success = mgr.client.update_game_bgg_id(decoded_game_name, None)

        if success:
            return (
                jsonify(
                    {"success": True, "message": f"已取消「{decoded_game_name}」與 BGG 的連結"}
                ),
                200,
            )
        else:
            return (
                jsonify(
                    {"success": False, "error": f"找不到桌遊「{decoded_game_name}」，請確認名稱是否正確"}
                ),
                404,
            )
    except Exception as e:
        logger.error(f"unlink_game exception: {e}")
        traceback.print_exc()
        return error_response(str(e), "UNLINK_GAME_ERROR", 500)
