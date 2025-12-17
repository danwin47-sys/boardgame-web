"""
BGG Ranks Service
提供 BGG 排名數據的查詢功能
"""
import sqlite3
from typing import Optional, List, Dict, Any
from pathlib import Path
import logging

logger = logging.getLogger(__name__)


class BGGRanksService:
    """BGG 排名數據查詢服務"""

    def __init__(self, db_path: Optional[str] = None):
        """
        初始化 BGG Ranks Service

        Args:
            db_path: SQLite 資料庫路徑，預設為 data/bgg_ranks/bgg_ranks.db
        """
        if db_path is None:
            # 預設路徑
            base_dir = Path(__file__).parent.parent
            self.db_path: str = str(base_dir / 'data' / 'bgg_ranks' / 'bgg_ranks.db')
        else:
            self.db_path = db_path
        logger.info(
            f"BGGRanksService initialized with database: {
                self.db_path}")

    def _get_connection(self):
        """建立資料庫連接"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def get_by_id(self, bgg_id: int) -> Optional[Dict[str, Any]]:
        """
        根據 BGG ID 查詢遊戲資訊

        Args:
            bgg_id: BGG 遊戲 ID

        Returns:
            遊戲資訊字典，如果找不到則返回 None
        """
        try:
            conn = self._get_connection()
            cursor = conn.cursor()

            cursor.execute(
                'SELECT * FROM bgg_ranks WHERE bgg_id = ?', (bgg_id,))
            row = cursor.fetchone()
            conn.close()

            if row:
                return dict(row)
            return None
        except Exception as e:
            logger.error(f"Error getting game by ID {bgg_id}: {e}")
            return None

    def search_by_name(
            self, name: str, limit: int = 10) -> List[Dict[str, Any]]:
        """
        模糊搜尋遊戲名稱

        Args:
            name: 遊戲名稱（支援部分匹配）
            limit: 返回結果數量限制

        Returns:
            遊戲資訊列表
        """
        try:
            conn = self._get_connection()
            cursor = conn.cursor()

            cursor.execute('''
                SELECT * FROM bgg_ranks
                WHERE name LIKE ?
                ORDER BY rank
                LIMIT ?
            ''', (f'%{name}%', limit))

            rows = cursor.fetchall()
            conn.close()

            return [dict(row) for row in rows]
        except Exception as e:
            logger.error(f"Error searching games by name '{name}': {e}")
            return []

    def get_top_games(self, limit: int = 100,
                      exclude_expansions: bool = True) -> List[Dict[str, Any]]:
        """
        獲取 BGG Top N 遊戲

        Args:
            limit: 返回遊戲數量
            exclude_expansions: 是否排除擴充

        Returns:
            Top N 遊戲列表
        """
        try:
            conn = self._get_connection()
            cursor = conn.cursor()

            query = 'SELECT * FROM bgg_ranks WHERE rank IS NOT NULL'
            if exclude_expansions:
                query += ' AND is_expansion = 0'
            query += ' ORDER BY rank LIMIT ?'

            cursor.execute(query, (limit,))
            rows = cursor.fetchall()
            conn.close()

            return [dict(row) for row in rows]
        except Exception as e:
            logger.error(f"Error getting top {limit} games: {e}")
            return []

    def get_by_category_rank(
            self, category: str, limit: int = 50) -> List[Dict[str, Any]]:
        """
        根據分類排名獲取遊戲

        Args:
            category: 分類名稱 (strategy, thematic, family, party, abstract, wargame, cgs, children)
            limit: 返回結果數量

        Returns:
            該分類 Top N 遊戲列表
        """
        category_map = {
            'strategy': 'strategygames_rank',
            'thematic': 'thematic_rank',
            'family': 'familygames_rank',
            'party': 'partygames_rank',
            'abstract': 'abstracts_rank',
            'wargame': 'wargames_rank',
            'cgs': 'cgs_rank',
            'children': 'childrensgames_rank'
        }

        column = category_map.get(category.lower())
        if not column:
            logger.warning(f"Invalid category: {category}")
            return []

        try:
            conn = self._get_connection()
            cursor = conn.cursor()

            query = f'''
                SELECT * FROM bgg_ranks
                WHERE {column} IS NOT NULL
                ORDER BY {column}
                LIMIT ?
            '''

            cursor.execute(query, (limit,))
            rows = cursor.fetchall()
            conn.close()

            return [dict(row) for row in rows]
        except Exception as e:
            logger.error(f"Error getting {category} games: {e}")
            return []

    def get_stats(self) -> Dict[str, Any]:
        """
        獲取資料庫統計資訊

        Returns:
            統計資訊字典
        """
        try:
            conn = self._get_connection()
            cursor = conn.cursor()

            stats = {}

            # 總遊戲數
            cursor.execute('SELECT COUNT(*) as count FROM bgg_ranks')
            stats['total_games'] = cursor.fetchone()['count']

            # 有排名的遊戲數
            cursor.execute(
                'SELECT COUNT(*) as count FROM bgg_ranks WHERE rank IS NOT NULL')
            stats['ranked_games'] = cursor.fetchone()['count']

            # 擴充數量
            cursor.execute(
                'SELECT COUNT(*) as count FROM bgg_ranks WHERE is_expansion = 1')
            stats['expansions'] = cursor.fetchone()['count']

            # 最近更新時間
            cursor.execute('SELECT MAX(updated_date) as latest FROM bgg_ranks')
            stats['last_updated'] = cursor.fetchone()['latest']

            conn.close()

            return stats
        except Exception as e:
            logger.error(f"Error getting stats: {e}")
            return {}
