"""
BGG XML API v2 Client with Bearer Token Authentication
直接使用 requests 呼叫 BGG API，支援 Bearer Token 認證
"""
import requests
import xml.etree.ElementTree as ET
from typing import List, Dict, Any, Optional
import logging
import time

logger = logging.getLogger(__name__)


class BGGApiClient:
    """BGG XML API v2 客戶端（支援 Bearer Token）"""

    BASE_URL = "https://boardgamegeek.com/xmlapi2"

    def __init__(
            self,
            api_token: str = "",
            timeout: int = 15,
            retries: int = 2):
        """
        初始化 BGG API 客戶端

        Args:
            api_token: BGG Bearer Token
            timeout: 請求超時時間（秒）
            retries: 失敗重試次數
        """
        self.api_token = api_token
        self.timeout = timeout
        self.retries = retries
        self.session = requests.Session()

        # 設定 Bearer Token 和 User-Agent
        if self.api_token:
            self.session.headers.update({
                'Authorization': f'Bearer {self.api_token}',
                'User-Agent': 'boardgame-web/1.0 (BGG API integration; https://github.com/danwin47-sys/boardgame-web)'
            })
            logger.info(
                "BGG API Client initialized with Bearer Token and User-Agent")
        else:
            # 即使沒有 token 也設定 User-Agent
            self.session.headers.update({
                'User-Agent': 'boardgame-web/1.0 (BGG API integration; https://github.com/danwin47-sys/boardgame-web)'
            })
            logger.warning(
                "BGG API Client initialized WITHOUT Bearer Token - API calls may fail")

    def _make_request(self,
                      endpoint: str,
                      params: Optional[Dict[str,
                                            Any]] = None) -> Optional[ET.Element]:
        """
        發送 API 請求並解析 XML 回應

        Args:
            endpoint: API 端點（例如：'search', 'thing'）
            params: 查詢參數

        Returns:
            XML Element 或 None（失敗時）
        """
        url = f"{self.BASE_URL}/{endpoint}"
        params = params or {}

        for attempt in range(self.retries + 1):
            try:
                logger.debug(
                    f"BGG API Request: {url}, params: {params}, attempt: {
                        attempt + 1}")
                response = self.session.get(
                    url, params=params, timeout=self.timeout)

                # 檢查 HTTP 狀態碼
                if response.status_code == 401:
                    logger.error(
                        "BGG API returned 401 Unauthorized - check your Bearer Token")
                    return None
                elif response.status_code == 429:
                    logger.warning(
                        "BGG API rate limit exceeded - waiting before retry")
                    time.sleep(2 ** attempt)  # 指數退避
                    continue
                elif response.status_code != 200:
                    logger.error(
                        f"BGG API returned status {
                            response.status_code}")
                    return None

                # 解析 XML
                try:
                    root = ET.fromstring(response.content)
                    return root
                except ET.ParseError as e:
                    logger.error(f"Failed to parse XML response: {e}")
                    logger.debug(f"Response content: {response.text[:500]}")
                    return None

            except requests.exceptions.Timeout:
                logger.warning(
                    f"BGG API timeout (attempt {attempt + 1}/{self.retries + 1})")
                if attempt < self.retries:
                    time.sleep(1)
                    continue
            except requests.exceptions.RequestException as e:
                logger.error(f"BGG API request failed: {e}")
                if attempt < self.retries:
                    time.sleep(1)
                    continue

        return None

    def search(self, query: str, exact: bool = False) -> List[Dict[str, Any]]:
        """
        搜尋桌遊

        Args:
            query: 搜尋關鍵字
            exact: 是否精確搜尋

        Returns:
            桌遊列表，每個項目包含 id, name, year
        """
        params = {
            'query': query,
            'type': 'boardgame'
        }
        if exact:
            params['exact'] = '1'

        root = self._make_request('search', params)
        if root is None:
            return []

        games = []
        for item in root.findall('item'):
            try:
                game_id = item.get('id')
                name_elem = item.find('name')
                year_elem = item.find('yearpublished')

                if game_id and name_elem is not None:
                    year_value = year_elem.get(
                        'value') if year_elem is not None else None
                    year = int(year_value) if year_value else None

                    games.append({
                        'id': int(game_id),
                        'name': name_elem.get('value', ''),
                        'year': year,
                        'type': item.get('type', 'boardgame')
                    })
            except (ValueError, AttributeError) as e:
                logger.warning(f"Error parsing search result item: {e}")
                continue

        logger.info(f"BGG search for '{query}' returned {len(games)} results")
        return games

    def game(self, game_id: int) -> Optional[Dict[str, Any]]:
        """
        取得桌遊詳細資訊

        Args:
            game_id: BGG 遊戲 ID

        Returns:
            桌遊詳細資訊字典
        """
        params = {
            'id': game_id,
            'stats': '1'  # 包含統計資料（評分、排名等）
        }

        root = self._make_request('thing', params)
        if root is None:
            return None

        item = root.find('item')
        if item is None:
            logger.warning(f"Game {game_id} not found in BGG response")
            return None

        try:
            # 基本資訊
            game_id = int(item.get('id', 0))

            # 遊戲名稱（優先使用 primary name）
            name = ""
            for name_elem in item.findall('name'):
                if name_elem.get('type') == 'primary':
                    name = name_elem.get('value', '')
                    break
            if not name:
                fallback_name_elem = item.find('name')
                name = fallback_name_elem.get(
                    'value', '') if fallback_name_elem is not None else ''

            # 年份
            year_elem = item.find('yearpublished')
            year_value = year_elem.get(
                'value') if year_elem is not None else None
            year = int(year_value) if year_value else None

            # 描述
            desc_elem = item.find('description')
            description = desc_elem.text if desc_elem is not None else ''

            # 圖片
            image_elem = item.find('image')
            image = image_elem.text if image_elem is not None else ''

            thumbnail_elem = item.find('thumbnail')
            thumbnail = thumbnail_elem.text if thumbnail_elem is not None else ''

            # 玩家人數
            minplayers_elem = item.find('minplayers')
            minplayers_value = minplayers_elem.get(
                'value') if minplayers_elem is not None else None
            min_players = int(minplayers_value) if minplayers_value else None

            maxplayers_elem = item.find('maxplayers')
            maxplayers_value = maxplayers_elem.get(
                'value') if maxplayers_elem is not None else None
            max_players = int(maxplayers_value) if maxplayers_value else None

            # 遊戲時間
            playingtime_elem = item.find('playingtime')
            playingtime_value = playingtime_elem.get(
                'value') if playingtime_elem is not None else None
            playing_time = int(
                playingtime_value) if playingtime_value else None

            minplaytime_elem = item.find('minplaytime')
            minplaytime_value = minplaytime_elem.get(
                'value') if minplaytime_elem is not None else None
            min_time = int(minplaytime_value) if minplaytime_value else None

            maxplaytime_elem = item.find('maxplaytime')
            maxplaytime_value = maxplaytime_elem.get(
                'value') if maxplaytime_elem is not None else None
            max_time = int(maxplaytime_value) if maxplaytime_value else None

            # 年齡
            minage_elem = item.find('minage')
            minage_value = minage_elem.get(
                'value') if minage_elem is not None else None
            min_age = int(minage_value) if minage_value else None

            # 統計資料
            stats = item.find('statistics/ratings')
            rating_average = 0.0
            rating_bayes_average = 0.0
            rating_users = 0
            rank = None

            if stats is not None:
                avg_elem = stats.find('average')
                rating_average = float(
                    avg_elem.get(
                        'value',
                        0)) if avg_elem is not None else 0.0

                bayesavg_elem = stats.find('bayesaverage')
                rating_bayes_average = float(bayesavg_elem.get(
                    'value', 0)) if bayesavg_elem is not None else 0.0

                users_elem = stats.find('usersrated')
                rating_users = int(
                    users_elem.get(
                        'value',
                        0)) if users_elem is not None else 0

                # 排名
                for rank_elem in stats.findall('ranks/rank'):
                    if rank_elem.get('name') == 'boardgame':
                        rank_value = rank_elem.get('value')
                        if rank_value and rank_value != 'Not Ranked':
                            try:
                                rank = int(rank_value)
                            except ValueError:
                                pass
                        break

            # 類別、機制、設計師、美術、出版商
            categories = [link.get('value', '') for link in item.findall("link[@type='boardgamecategory']")]
            mechanics = [link.get('value', '') for link in item.findall("link[@type='boardgamemechanic']")]
            designers = [link.get('value', '') for link in item.findall("link[@type='boardgamedesigner']")]
            artists = [link.get('value', '') for link in item.findall("link[@type='boardgameartist']")]
            publishers = [link.get('value', '') for link in item.findall("link[@type='boardgamepublisher']")]
            
            # 判斷是否為擴充（更可靠的多重檢查）
            game_type = item.get('type', 'boardgame')
            
            # 方法1: 檢查 type 屬性
            is_expansion = (game_type == 'boardgameexpansion')
            
            # 方法2: 檢查是否有 inbound 的 boardgameexpansion link（更可靠）
            # 有些擴充的 type 是 'boardgame'，但會有指向主遊戲的 inbound link
            parent_game = None
            for link in item.findall("link[@type='boardgameexpansion']"):
                if link.get('inbound') == 'true':
                    is_expansion = True  # 有 inbound expansion link 就是擴充
                    parent_game = link.get('value')
                    break  # 取第一個主遊戲
            
            # 方法3: 檢查類別中是否有 "Expansion for Base-game"
            if not is_expansion and 'Expansion for Base-game' in categories:
                is_expansion = True

            # 顯示格式
            # 顯示格式
            players_display = f"{min_players}-{max_players}" if min_players and max_players else "N/A"
            if min_players == max_players and min_players:
                players_display = str(min_players)

            time_str = f"{playing_time} 分鐘" if playing_time else "N/A"
            if min_time and max_time and min_time != max_time:
                time_str = f"{min_time}-{max_time} 分鐘"

            details = {
                'id': game_id,
                'name': name,
                'type': game_type,
                'is_expansion': is_expansion,
                'parent_game': parent_game,
                'year': year,
                'description': description,
                'image': image,
                'thumbnail': thumbnail,
                'min_players': min_players,
                'max_players': max_players,
                'players_display': players_display,
                'playing_time': playing_time,
                'playing_time_display': time_str,
                'min_age': min_age,
                'rating_average': round(rating_average, 2),
                'rating_bayes_average': round(rating_bayes_average, 2),
                'rating_users': rating_users,
                'rank': rank,
                'categories': categories,
                'mechanics': mechanics,
                'designers': designers,
                'artists': artists,
                'publishers': publishers
            }

            logger.info(f"Retrieved details for game: {name} (ID: {game_id})")
            return details

        except Exception as e:
            logger.error(f"Error parsing game details for ID {game_id}: {e}")
            return None

    def hot_items(self, item_type: str = 'boardgame') -> List[Dict[str, Any]]:
        """
        取得熱門項目

        Args:
            item_type: 項目類型（預設：'boardgame'）

        Returns:
            熱門項目列表
        """
        root = self._make_request('hot', {'type': item_type})
        if root is None:
            return []

        items = []
        for item in root.findall('item'):
            try:
                item_id = int(item.get('id', 0))
                rank = int(item.get('rank', 0))

                name_elem = item.find('name')
                name = name_elem.get(
                    'value', '') if name_elem is not None else ''

                year_elem = item.find('yearpublished')
                year_value = year_elem.get(
                    'value') if year_elem is not None else None
                year = int(year_value) if year_value else None

                thumbnail_elem = item.find('thumbnail')
                thumbnail = thumbnail_elem.get(
                    'value', '') if thumbnail_elem is not None else ''

                items.append({
                    'id': item_id,
                    'name': name,
                    'year': year,
                    'rank': rank,
                    'thumbnail': thumbnail
                })
            except (ValueError, AttributeError) as e:
                logger.warning(f"Error parsing hot item: {e}")
                continue

        logger.info(f"Retrieved {len(items)} hot {item_type}s")
        return items
