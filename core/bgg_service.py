"""
BoardGameGeek API Service
提供桌遊搜尋、詳細資訊查詢等功能
"""
from typing import List, Dict, Any, Optional
import logging
from flask import current_app

from .bgg_api_client import BGGApiClient
from .cache import cache_with_timeout
from .demo_data import DEMO_GAMES, DEMO_GAME_DETAILS

logger = logging.getLogger(__name__)


class BGGService:
    """BoardGameGeek API 服務"""
    
    def __init__(self):
        """初始化 BGG 客戶端"""
        # 嘗試從 Flask app context 獲取配置
        try:
            demo_mode = current_app.config.get('DEMO_MODE', False)
            bgg_token = current_app.config.get('BGG_API_TOKEN', '')
            bgg_timeout = current_app.config.get('BGG_TIMEOUT', 15)
            bgg_retries = current_app.config.get('BGG_RETRIES', 2)
        except RuntimeError:
            # 如果不在 app context 中，使用環境變數
            import os
            demo_mode = os.environ.get("DEMO_MODE", "False").lower() in ('true', '1', 'yes')
            bgg_token = os.environ.get("BGG_API_TOKEN", "cfebcba0-a1a7-4792-a6a6-d8514ecdc8c7")
            bgg_timeout = int(os.environ.get("BGG_TIMEOUT", 15))
            bgg_retries = int(os.environ.get("BGG_RETRIES", 2))
        
        
        if not demo_mode:
            # 使用新的 BGGApiClient，支援 Bearer Token
            self.client = BGGApiClient(
                api_token=bgg_token,
                timeout=bgg_timeout,
                retries=bgg_retries
            )
            logger.info("BGG Service initialized (Live mode with Bearer Token)")
        else:
            self.client = None
            logger.info("BGG Service initialized (Demo mode)")
        
        self.demo_mode = demo_mode
    
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
        if self.demo_mode:
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
                    'id': game['id'],
                    'name': game['name'],
                    'year': game.get('year'),
                    'type': game.get('type', 'boardgame')
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
        if self.demo_mode:
            logger.info(f"[DEMO MODE] Getting details for game {game_id}")
            return DEMO_GAME_DETAILS.get(game_id, DEMO_GAME_DETAILS[13])  # 預設返回 Catan
        
        # 真實 API 模式
        try:
            game = self.client.game(game_id=game_id)
            
            if not game:
                logger.warning(f"Game not found: {game_id}")
                return None
            
            # 處理玩家人數
            min_players = game.get('min_players')
            max_players = game.get('max_players')
            players = f"{min_players}-{max_players}" if min_players and max_players else "N/A"
            if min_players == max_players and min_players:
                players = str(min_players)
            
            # 處理遊戲時間
            playing_time = game.get('playing_time')
            min_time = game.get('min_playing_time')
            max_time = game.get('max_playing_time')
            
            time_str = f"{playing_time} 分鐘" if playing_time else "N/A"
            if min_time and max_time and min_time != max_time:
                time_str = f"{min_time}-{max_time} 分鐘"
            
            details = {
                'id': game['id'],
                'name': game['name'],
                'year': game.get('year'),
                'description': game.get('description', ''),
                'image': game.get('image', ''),
                'thumbnail': game.get('thumbnail', ''),
                'min_players': min_players,
                'max_players': max_players,
                'players_display': players,
                'playing_time': playing_time,
                'playing_time_display': time_str,
                'min_age': game.get('min_age'),
                'rating_average': round(game.get('rating_average', 0), 2),
                'rating_bayes_average': round(game.get('rating_bayes_average', 0), 2),
                'rating_users': game.get('rating_users', 0),
                'rank': self._get_overall_rank(game),
                'categories': game.get('categories', []),
                'mechanics': game.get('mechanics', []),
                'designers': game.get('designers', []),
                'artists': game.get('artists', []),
                'publishers': game.get('publishers', [])
            }
            
            logger.info(f"Retrieved details for game: {game['name']} (ID: {game_id})")
            return details
            
        except Exception as e:
            logger.error(f"Error getting game {game_id}: {e}")
            return None
    
    def _get_overall_rank(self, game) -> Optional[int]:
        """取得桌遊的整體排名"""
        try:
            ranks = game.get('ranks', [])
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
                    'id': item['id'],
                    'name': item['name'],
                    'year': item.get('year'),
                    'rank': item.get('rank'),
                    'thumbnail': item.get('thumbnail', '')
                })
            
            logger.info(f"Retrieved {len(games)} hot games")
            return games
            
        except Exception as e:
            logger.error(f"Error getting hot games: {e}")
            return []
    
    def get_party_games(self, limit: int = 10) -> List[Dict[str, Any]]:
        """取得派对桌游（使用精选游戏 ID）"""
        # 派对游戏: Codenames, Dixit, Spyfall, Wavelength, Just One等
        party_game_ids = [178900, 39856, 166384, 262543, 254640, 181304, 124742, 139030, 131835]
        return self._get_games_by_ids(party_game_ids[:limit])
    
    def get_strategy_games(self, limit: int = 10) -> List[Dict[str, Any]]:
        """取得策略桌游（使用精选游戏 ID）"""
        # 策略游戏: Gloomhaven, Brass Birmingham, Terraforming Mars, Wingspan等
        strategy_game_ids = [174430, 224517, 167791, 266192, 233078, 161936, 220308, 182028, 173346]
        return self._get_games_by_ids(strategy_game_ids[:limit])
    
    def get_family_games(self, limit: int = 10) -> List[Dict[str, Any]]:
        """取得家庭桌游（使用精选游戏 ID）"""
        # 家庭游戏: Catan, Ticket to Ride, Splendor, Azul, Carcassonne等
        family_game_ids = [13, 9209, 148228, 230802, 822, 30549, 31260, 68448, 84876]
        return self._get_games_by_ids(family_game_ids[:limit])
    
    def get_children_games(self, limit: int = 10) -> List[Dict[str, Any]]:
        """取得儿童桌游（使用精选游戏 ID）"""
        # 儿童游戏: King of Tokyo, Zombie Kidz Evolution, My First Carcassonne等
        children_game_ids = [70323, 256952, 41010, 163412, 42215, 244521, 244522, 123540, 193621]
        return self._get_games_by_ids(children_game_ids[:limit])
    
    def _get_games_by_ids(self, game_ids: List[int]) -> List[Dict[str, Any]]:
        """根据 ID 列表获取游戏资讯"""
        games = []
        for game_id in game_ids:
            try:
                game = self.get_game_details(game_id)
                if game:
                    games.append({
                        'id': game['id'],
                        'name': game['name'],
                        'year': game.get('year'),
                        'thumbnail': game.get('thumbnail'),
                        'rating_average': game.get('rating_average')
                    })
            except Exception as e:
                logger.warning(f"Failed to get game {game_id}: {e}")
                continue
        return games
