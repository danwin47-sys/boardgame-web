"""
BoardGameGeek API Service
提供桌遊搜尋、詳細資訊查詢等功能
"""
from typing import List, Dict, Any, Optional
import logging

from .bgg_api_client import BGGApiClient
from .cache import cache_with_timeout
from .demo_data import DEMO_GAMES, DEMO_GAME_DETAILS
from config import Config

logger = logging.getLogger(__name__)


class BGGService:
    """BoardGameGeek API 服務"""
    
    def __init__(self):
        """初始化 BGG 客戶端"""
        if not Config.DEMO_MODE:
            # 使用新的 BGGApiClient，支援 Bearer Token
            self.client = BGGApiClient(
                api_token=Config.BGG_API_TOKEN,
                timeout=Config.BGG_TIMEOUT,
                retries=Config.BGG_RETRIES
            )
            logger.info("BGG Service initialized (Live mode with Bearer Token)")
        else:
            self.client = None
            logger.info("BGG Service initialized (Demo mode)")
    
    @cache_with_timeout(seconds=300)  # 快取 5 分鐘
    def search_games(self, query: str, exact: bool = False) -> List[Dict[str, Any]]:
        """
        搜尋桌遊
        
        Args:
            query: 搜尋關鍵字
            exact: 是否精確搜尋
            
        Returns:
            桌遊列表，每個項目包含 id, name, year
        """
        if not query or not query.strip():
            return []
        
        # 演示模式：使用範例數據
        if Config.DEMO_MODE:
            logger.info(f"[DEMO MODE] Searching for: {query}")
            query_lower = query.lower()
            
            # 尋找匹配的演示數據
            for key in DEMO_GAMES.keys():
                if key in query_lower:
                    logger.info(f"[DEMO MODE] Found {len(DEMO_GAMES[key])} games")
                    return DEMO_GAMES[key]
            
            # 如果沒有匹配，返回預設數據
            logger.info(f"[DEMO MODE] Returning default games")
            return DEMO_GAMES['default']
        
        # 真實 API 模式
        try:
            logger.info(f"Searching BGG for: {query}")
            results = self.client.search(query, exact=exact)
            
            games = []
            for game in results:
                games.append({
                    'id': game.id,
                    'name': game.name,
                    'year': getattr(game, 'year', None),
                    'type': getattr(game, 'type', 'boardgame')
                })
            
            logger.info(f"Found {len(games)} games for query: {query}")
            return games
            
        except Exception as e:
            error_msg = str(e)
            logger.error(f"Error during BGG search for '{query}': {error_msg}")
            
            # 提供更詳細的錯誤訊息
            if "non-XML reply" in error_msg:
                logger.warning("BGG API returned non-XML response - server may be overloaded or under maintenance")
            elif "timeout" in error_msg.lower():
                logger.warning("BGG API timeout - server is responding slowly")
            
            return []
    
    @cache_with_timeout(seconds=3600)  # 快取 1 小時
    def get_game_details(self, game_id: int) -> Optional[Dict[str, Any]]:
        """
        取得桌遊詳細資訊
        
        Args:
            game_id: BGG 遊戲 ID
            
        Returns:
            桌遊詳細資訊字典，包含名稱、評分、排名、圖片等
        """
        # 演示模式：返回範例詳細資料
        if Config.DEMO_MODE:
            logger.info(f"[DEMO MODE] Getting details for game {game_id}")
            return DEMO_GAME_DETAILS.get(game_id, DEMO_GAME_DETAILS[13])  # 預設返回 Catan
        
        # 真實 API 模式
        try:
            game = self.client.game(game_id=game_id)
            
            if not game:
                logger.warning(f"Game not found: {game_id}")
                return None
            
            # 處理玩家人數
            min_players = getattr(game, 'min_players', None)
            max_players = getattr(game, 'max_players', None)
            players = f"{min_players}-{max_players}" if min_players and max_players else "N/A"
            if min_players == max_players and min_players:
                players = str(min_players)
            
            # 處理遊戲時間
            playing_time = getattr(game, 'playing_time', None)
            min_time = getattr(game, 'min_playing_time', None)
            max_time = getattr(game, 'max_playing_time', None)
            
            time_str = f"{playing_time} 分鐘" if playing_time else "N/A"
            if min_time and max_time and min_time != max_time:
                time_str = f"{min_time}-{max_time} 分鐘"
            
            details = {
                'id': game.id,
                'name': game.name,
                'year': getattr(game, 'year', None),
                'description': getattr(game, 'description', ''),
                'image': getattr(game, 'image', ''),
                'thumbnail': getattr(game, 'thumbnail', ''),
                'min_players': min_players,
                'max_players': max_players,
                'players_display': players,
                'playing_time': playing_time,
                'playing_time_display': time_str,
                'min_age': getattr(game, 'min_age', None),
                'rating_average': round(getattr(game, 'rating_average', 0), 2),
                'rating_bayes_average': round(getattr(game, 'rating_bayes_average', 0), 2),
                'rating_users': getattr(game, 'users_rated', 0),
                'rank': self._get_overall_rank(game),
                'categories': [cat for cat in getattr(game, 'categories', [])],
                'mechanics': [mech for mech in getattr(game, 'mechanics', [])],
                'designers': [designer for designer in getattr(game, 'designers', [])],
                'artists': [artist for artist in getattr(game, 'artists', [])],
                'publishers': [pub for pub in getattr(game, 'publishers', [])]
            }
            
            logger.info(f"Retrieved details for game: {game.name} (ID: {game_id})")
            return details
            
        except Exception as e:
            logger.error(f"Error getting game {game_id}: {e}")
            return None
    
    def _get_overall_rank(self, game) -> Optional[int]:
        """取得桌遊的整體排名"""
        try:
            ranks = getattr(game, 'ranks', [])
            for rank in ranks:
                if rank.get('name') == 'boardgame' or rank.get('type') == 'subtype':
                    rank_value = rank.get('value')
                    if rank_value and rank_value != 'Not Ranked':
                        return int(rank_value)
            return None
        except:
            return None
    
    @cache_with_timeout(seconds=1800)  # 快取 30 分鐘
    def get_hot_games(self, limit: int = 10) -> List[Dict[str, Any]]:
        """
        取得熱門桌遊列表
        
        Args:
            limit: 限制數量
            
        Returns:
            熱門桌遊列表
        """
        try:
            hot_items = self.client.hot_items('boardgame')
            
            games = []
            for item in hot_items[:limit]:
                games.append({
                    'id': item.id,
                    'name': item.name,
                    'year': getattr(item, 'year', None),
                    'rank': getattr(item, 'rank', None),
                    'thumbnail': getattr(item, 'thumbnail', '')
                })
            
            logger.info(f"Retrieved {len(games)} hot games")
            return games
            
        except Exception as e:
            logger.error(f"Error getting hot games: {e}")
            return []
