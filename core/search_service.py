"""
搜尋服務模組
提供全站搜尋功能，包含遊戲搜尋、會員搜尋和模糊匹配
"""
import logging
from difflib import SequenceMatcher
from typing import Any, Dict, List, Optional

from .constants import FIELD_BORROWER, FIELD_BORROWER_ID, FIELD_NAME, FIELD_STATUS
from .member_service import MemberService
from .sheets_client import SheetsClient

logger = logging.getLogger(__name__)


class SearchService:
    """
    搜尋服務類別
    負責處理全站搜尋邏輯，包含遊戲和會員搜尋
    """

    def __init__(self, sheets_client: SheetsClient, member_service: MemberService):
        """
        初始化搜尋服務

        Args:
            sheets_client: Google Sheets 客戶端
            member_service: 會員服務
        """
        self.client = sheets_client
        self.member_service = member_service
        self.similarity_threshold = 0.6  # 模糊匹配的相似度閾值

    def _calculate_similarity(self, str1: str, str2: str) -> float:
        """
        計算兩個字串的相似度

        Args:
            str1: 第一個字串
            str2: 第二個字串

        Returns:
            float: 相似度分數 (0.0 - 1.0)
        """
        return SequenceMatcher(None, str1.lower(), str2.lower()).ratio()

    def _fuzzy_match(self, query: str, text: str) -> bool:
        """
        模糊匹配檢查

        Args:
            query: 搜尋關鍵字
            text: 要匹配的文字

        Returns:
            bool: 是否匹配
        """
        if not query or not text:
            return False

        query_lower = query.lower()
        text_lower = text.lower()

        # 1. 完全匹配
        if query_lower == text_lower:
            return True

        # 2. 部分匹配（substring）
        if query_lower in text_lower:
            return True

        # 3. 相似度匹配
        similarity = self._calculate_similarity(query, text)
        return similarity >= self.similarity_threshold

    def search_games(self, query: str, fuzzy: bool = True) -> List[Dict[str, Any]]:
        """
        搜尋遊戲

        Args:
            query: 搜尋關鍵字
            fuzzy: 是否啟用模糊搜尋

        Returns:
            List[Dict[str, Any]]: 符合條件的遊戲列表
        """
        if not query or not query.strip():
            return []

        try:
            games = self.client.load_games()
            results = []

            for game in games:
                game_name = game.get(FIELD_NAME, "")

                if fuzzy:
                    # 模糊搜尋
                    if self._fuzzy_match(query, game_name):
                        # 計算相似度分數用於排序
                        similarity = self._calculate_similarity(query, game_name)
                        game_copy = game.copy()
                        game_copy["_similarity"] = similarity
                        results.append(game_copy)
                else:
                    # 精確搜尋（部分匹配）
                    if query.lower() in game_name.lower():
                        results.append(game)

            # 按相似度排序（如果有的話）
            if fuzzy and results:
                results.sort(key=lambda x: x.get("_similarity", 0), reverse=True)
                # 移除內部使用的相似度分數
                for game in results:
                    game.pop("_similarity", None)

            logger.info(f"搜尋遊戲 '{query}': 找到 {len(results)} 個結果")
            return results

        except Exception as e:
            logger.error(f"搜尋遊戲失敗: {e}")
            return []

    def search_members(self, query: str, fuzzy: bool = True) -> List[Dict[str, Any]]:
        """
        搜尋會員

        Args:
            query: 搜尋關鍵字（姓名或 ID）
            fuzzy: 是否啟用模糊搜尋

        Returns:
            List[Dict[str, Any]]: 符合條件的會員列表
        """
        if not query or not query.strip():
            return []

        try:
            members = self.client.load_members()
            results = []

            for member in members:
                member_name = member.get("name", "")
                member_id = member.get("id", "")

                # 檢查姓名或 ID
                if fuzzy:
                    if self._fuzzy_match(query, member_name) or self._fuzzy_match(
                        query, member_id
                    ):
                        # 計算相似度（取姓名和 ID 中較高的）
                        name_similarity = self._calculate_similarity(query, member_name)
                        id_similarity = self._calculate_similarity(query, member_id)
                        similarity = max(name_similarity, id_similarity)

                        member_copy = member.copy()
                        member_copy["_similarity"] = similarity
                        results.append(member_copy)
                else:
                    query_lower = query.lower()
                    if (
                        query_lower in member_name.lower()
                        or query_lower in member_id.lower()
                    ):
                        results.append(member)

            # 按相似度排序
            if fuzzy and results:
                results.sort(key=lambda x: x.get("_similarity", 0), reverse=True)
                for member in results:
                    member.pop("_similarity", None)

            logger.info(f"搜尋會員 '{query}': 找到 {len(results)} 個結果")
            return results

        except Exception as e:
            logger.error(f"搜尋會員失敗: {e}")
            return []

    def global_search(self, query: str, fuzzy: bool = True) -> Dict[str, Any]:
        """
        全站搜尋（遊戲 + 會員）

        Args:
            query: 搜尋關鍵字
            fuzzy: 是否啟用模糊搜尋

        Returns:
            Dict[str, Any]: 包含遊戲和會員搜尋結果的字典
                {
                    'games': [...],
                    'members': [...],
                    'total': int
                }
        """
        if not query or not query.strip():
            return {"games": [], "members": [], "total": 0}

        games = self.search_games(query, fuzzy)
        members = self.search_members(query, fuzzy)

        return {"games": games, "members": members, "total": len(games) + len(members)}
