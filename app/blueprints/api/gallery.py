"""
Gallery API Blueprint
處理桌遊展示牆相關的路由
"""
from typing import Tuple, Optional, List, Dict, Any
from flask import Blueprint, jsonify, request, Response
import logging

from app.utils import get_manager, error_response

logger = logging.getLogger(__name__)

# 建立 Blueprint
gallery_bp = Blueprint("gallery", __name__, url_prefix="/api/gallery")


def parse_players_range(players_str: Any) -> Tuple[Optional[int], Optional[int]]:
    """解析人數範圍字串

    支援多種格式：'2-4', '2~4', '5+', 或單一數字。

    Args:
        players_str: 人數範圍字串，例如 '2-4', '5+', 或空字串/None

    Returns:
        Tuple[Optional[int], Optional[int]]: (最小人數, 最大人數)
            - 成功解析時返回對應的數值
            - 無法解析時返回 (None, None)

    Examples:
        >>> parse_players_range('2-4')
        (2, 4)
        >>> parse_players_range('5+')
        (5, 99)
        >>> parse_players_range('3')
        (3, 3)
    """
    if not players_str or players_str == "":
        return None, None

    # 處理數字類型（直接轉為單一數字）
    if isinstance(players_str, int):
        return players_str, players_str

    # 確保是字串類型
    players_str = str(players_str)

    try:
        # 處理 '5+' 格式
        if "+" in players_str:
            min_val = int(players_str.replace("+", "").strip())
            return min_val, 99

        # 處理 '2-4' 或 '2~4' 格式
        if "-" in players_str or "~" in players_str:
            separator = "-" if "-" in players_str else "~"
            parts = players_str.split(separator)
            if len(parts) == 2:
                return int(parts[0].strip()), int(parts[1].strip())

        # 處理單一數字
        val = int(players_str.strip())
        return val, val
    except (ValueError, AttributeError):
        return None, None


def classify_game_type(game_data: Dict[str, Any]) -> List[str]:
    """根據遊戲資訊自動分類遊戲類型

    根據遊戲的人數、難度等資訊自動判斷遊戲類型。
    可能的類型包括：派對遊戲、策略遊戲、家庭遊戲、兒童遊戲、其他。

    Args:
        game_data: 遊戲數據字典，應包含以下欄位：
            - minPlayers: 最小玩家人數
            - maxPlayers: 最大玩家人數
            - difficulty: 難度（簡單/普通/中等/困難）

    Returns:
        List[str]: 遊戲類型列表，可能包含多個類型

    Examples:
        >>> classify_game_type({'minPlayers': 2, 'maxPlayers': 8, 'difficulty': '簡單'})
        ['派對遊戲', '家庭遊戲']
    """
    types = []

    min_players = game_data.get("minPlayers", 1)
    max_players = game_data.get("maxPlayers", 10)
    difficulty = game_data.get("difficulty", "").lower()

    # 派對遊戲：6+ 人，通常簡單
    if max_players >= 6:
        types.append("派對遊戲")

    # 策略遊戲：困難或中等難度
    if difficulty in ["困難", "中等", "普通"]:
        if min_players <= 4 and max_players <= 5:
            types.append("策略遊戲")

    # 家庭遊戲：3-6 人，簡單到普通
    if min_players <= 3 and max_players >= 4:
        if difficulty in ["簡單", "普通", ""]:
            types.append("家庭遊戲")

    # 兒童遊戲：簡單難度
    if difficulty == "簡單" and max_players <= 6:
        types.append("兒童遊戲")

    # 如果沒有分類到任何類型，使用預設
    if not types:
        types.append("其他")

    return types


@gallery_bp.route("/games", methods=["GET"])
def get_gallery_games() -> Tuple[Response, int]:
    """獲取展示牆的桌遊列表

    從 Google Sheets 讀取桌遊資料，處理圖片、人數、類型等資訊，
    並根據查詢參數進行篩選。

    Query Parameters:
        status (str, optional): 依狀態篩選（例如：'歸還'、'借出'）

    Returns:
        Tuple[Response, int]: JSON 響應和 HTTP 狀態碼
            - 成功時: ({
                'success': True,
                'games': [...],
                'total': int
              }, 200)
            - 失敗時: ({'success': False, 'error': '錯誤訊息'}, 500)

    Response Format:
        每個遊戲物件包含以下欄位：
        - id: 遊戲 ID（使用名稱）
        - name: 遊戲名稱
        - status: 狀態
        - borrower: 借閱人
        - location: 位置
        - difficulty: 難度
        - custodian: 保管人
        - bggId: BGG ID（如果有）
        - thumbnail/image: 圖片 URL
        - minPlayers/maxPlayers: 人數範圍
        - minMinutes/maxMinutes: 遊戲時間
        - types: 類型列表
        - tags: 標籤列表

    Raises:
        Exception: 當資料庫連線失敗或資料讀取錯誤時
    """
    try:
        mgr = get_manager()
        mgr.games = mgr.load_data()

        # 處理篩選參數（未來擴展使用）
        status_filter = request.args.get("status", None)

        games_list = []
        for game in mgr.games:
            # 基本資訊
            game_data = {
                "id": game.get("name", ""),  # 使用名稱作為 ID
                "name": game.get("name", ""),
                "status": game.get("status", ""),
                "borrower": game.get("borrower", ""),
                "location": game.get("location", ""),
                "difficulty": game.get("diff", ""),
                "custodian": game.get("custodian", ""),
            }

            # BGG 相關資訊（所有資料從 Google Sheets 讀取，不調用 BGG API）
            bgg_id = game.get("bgg_id", "")
            if bgg_id:
                game_data["bggId"] = str(bgg_id)

            # 圖片資訊（與主頁面機制一致：優先使用 Google Sheets 的 bgg_thumbnail）
            bgg_thumbnail = game.get("bgg_thumbnail", "")
            image = game.get("image", "")
            thumbnail = game.get("thumbnail", "")

            # 優先順序：bgg_thumbnail → image → thumbnail
            if bgg_thumbnail:
                game_data["thumbnail"] = bgg_thumbnail
                game_data["image"] = bgg_thumbnail
            elif image:
                game_data["image"] = image
            elif thumbnail:
                game_data["thumbnail"] = thumbnail

            # 解析遊玩人數範圍
            players_str = game.get("players", "")
            if players_str:
                # 確保是字串類型
                players_str = str(players_str)

                # 移除中文字符和空格
                players_clean = players_str.replace("人", "").replace(" ", "").strip()

                if "-" in players_clean:
                    # 範圍格式：2-4
                    try:
                        parts = players_clean.split("-")
                        min_players = int(parts[0])
                        max_players = int(parts[1])
                        game_data["minPlayers"] = min_players
                        game_data["maxPlayers"] = max_players
                    except (ValueError, IndexError):
                        pass
                elif "+" in players_clean:
                    # 10+ 格式
                    try:
                        min_players = int(players_clean.replace("+", ""))
                        game_data["minPlayers"] = min_players
                        game_data["maxPlayers"] = 99
                    except ValueError:
                        pass
                else:
                    # 單一數字
                    try:
                        player_count = int(players_clean)
                        game_data["minPlayers"] = player_count
                        game_data["maxPlayers"] = player_count
                    except ValueError:
                        pass

            # 遊戲時間解析（從 Google Sheets 讀取，如果沒有則從 BGG Ranks 讀取並寫回）
            min_time_from_sheet = game.get("minplaytime")
            max_time_from_sheet = game.get("maxplaytime")

            # 嘗試轉換為整數
            try:
                if min_time_from_sheet:
                    game_data["minMinutes"] = int(min_time_from_sheet)
                if max_time_from_sheet:
                    game_data["maxMinutes"] = int(max_time_from_sheet)
            except (ValueError, TypeError):
                min_time_from_sheet = None
                max_time_from_sheet = None

            # 如果 Google Sheets 沒有遊戲時間資料，且有 BGG ID，則從 BGG Ranks 讀取並寫回
            if (not min_time_from_sheet or not max_time_from_sheet) and bgg_id:
                try:
                    from core.bgg_ranks_service import BGGRanksService

                    bgg_ranks = BGGRanksService()
                    bgg_data = bgg_ranks.get_by_id(int(bgg_id))

                    if bgg_data:
                        bgg_min_time = bgg_data.get("minplaytime")
                        bgg_max_time = bgg_data.get("maxplaytime")

                        if bgg_min_time and bgg_max_time:
                            game_data["minMinutes"] = int(bgg_min_time)
                            game_data["maxMinutes"] = int(bgg_max_time)

                            # 寫回 Google Sheets
                            try:
                                game_name = game.get("name", "")
                                if game_name:
                                    mgr.update_game_playtime(
                                        game_name, int(bgg_min_time), int(bgg_max_time)
                                    )
                                    logger.info(
                                        f"已將 BGG 遊戲時間寫回 Sheets: {game_name} ({bgg_min_time}-{bgg_max_time}分鐘)"
                                    )
                            except Exception as write_error:
                                logger.warning(f"無法將遊戲時間寫回 Sheets: {write_error}")
                except Exception as e:
                    logger.debug(f"無法從 BGG Ranks 讀取遊戲時間: {e}")

            # 如果還是沒有時間資料，使用預設值
            if "minMinutes" not in game_data:
                game_data["minMinutes"] = 30
            if "maxMinutes" not in game_data:
                game_data["maxMinutes"] = 60

            # 類型和標籤分類邏輯
            types = classify_game_type(game_data)
            tags = []

            # 根據難度加入標籤
            difficulty = game.get("diff", "")
            if difficulty:
                tags.append(difficulty)

            # 根據位置加入標籤
            location = game.get("location", "")
            if location and location not in ["", "-"]:
                tags.append(f"位置:{location}")

            game_data["types"] = types
            game_data["tags"] = tags

            # 狀態篩選
            if status_filter and game.get("status") != status_filter:
                continue

            games_list.append(game_data)

        return (
            jsonify({"success": True, "games": games_list, "total": len(games_list)}),
            200,
        )

    except Exception as e:
        logger.error(f"獲取展示牆遊戲列表失敗: {e}", exc_info=True)
        return error_response(str(e), "API_ERROR", 500)
