"""
BoardGameGeek API Service
提供桌遊搜尋、詳細資訊查詢等功能
"""
import logging
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Any, Dict, List, Optional

from flask import current_app

from .bgg_api_client import BGGApiClient
from .cache import cache_with_timeout
from .demo_data import DEMO_GAME_DETAILS, DEMO_GAMES

logger = logging.getLogger(__name__)


class BGGService:
    """BoardGameGeek API 服務"""

    def __init__(self):
        """初始化 BGG 客戶端"""
        # 嘗試從 Flask app context 獲取配置
        try:
            demo_mode = current_app.config.get("DEMO_MODE", False)
            bgg_token = current_app.config.get("BGG_API_TOKEN", "")
            bgg_timeout = current_app.config.get("BGG_TIMEOUT", 15)
            bgg_retries = current_app.config.get("BGG_RETRIES", 2)
        except RuntimeError:
            # 如果不在 app context 中，使用環境變數
            import os

            demo_mode = os.environ.get("DEMO_MODE", "False").lower() in (
                "true",
                "1",
                "yes",
            )
            bgg_token = os.environ.get("BGG_API_TOKEN", "")
            bgg_timeout = int(os.environ.get("BGG_TIMEOUT", 15))
            bgg_retries = int(os.environ.get("BGG_RETRIES", 2))

        if not demo_mode:
            # 使用新的 BGGApiClient，支援 Bearer Token
            self.client = BGGApiClient(
                api_token=bgg_token, timeout=bgg_timeout, retries=bgg_retries
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

        # 演示模式：使用範例資料
        if self.demo_mode:
            logger.info(f"[DEMO MODE] Searching for: {query}")
            query_lower = query.lower()

            # 尋找匹配的演示資料
            for key in DEMO_GAMES.keys():
                if key in query_lower:
                    logger.info(f"[DEMO MODE] Found {len(DEMO_GAMES[key])} games")
                    return DEMO_GAMES[key]

            # 如果沒有匹配，返回預設資料
            logger.info(f"[DEMO MODE] Returning default games")
            return DEMO_GAMES["default"]

        # 真實 API 模式
        try:
            logger.info(f"Searching BGG for: {query}")
            results = self.client.search(query, exact=exact)

            games = []
            for game in results:
                games.append(
                    {
                        "id": game["id"],
                        "name": game["name"],
                        "year": game.get("year"),
                        "type": game.get("type", "boardgame"),
                    }
                )

            logger.info(f"Found {len(games)} games for query: {query}")
            return games

        except Exception as e:
            error_msg = str(e)
            logger.error(f"Error during BGG search for '{query}': {error_msg}")

            # 提供更詳細的錯誤訊息
            if "non-XML reply" in error_msg:
                logger.warning(
                    "BGG API returned non-XML response - server may be overloaded or under maintenance"
                )
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
            min_players = game.get("min_players")
            max_players = game.get("max_players")
            players = (
                f"{min_players}-{max_players}" if min_players and max_players else "N/A"
            )
            if min_players == max_players and min_players:
                players = str(min_players)

            # 處理遊戲時間
            playing_time = game.get("playing_time")
            min_time = game.get("min_playing_time")
            max_time = game.get("max_playing_time")

            time_str = f"{playing_time} 分鐘" if playing_time else "N/A"
            if min_time and max_time and min_time != max_time:
                time_str = f"{min_time}-{max_time} 分鐘"

            details = {
                "id": game["id"],
                "name": game["name"],
                "year": game.get("year"),
                "description": game.get("description", ""),
                "image": game.get("image", ""),
                "thumbnail": game.get("thumbnail", ""),
                "min_players": min_players,
                "max_players": max_players,
                "players_display": players,
                "playing_time": playing_time,
                "playing_time_display": time_str,
                "min_age": game.get("min_age"),
                "rating_average": round(game.get("rating_average", 0), 2),
                "rating_bayes_average": round(game.get("rating_bayes_average", 0), 2),
                "rating_users": game.get("rating_users", 0),
                "rank": self._get_overall_rank(game),
                "categories": game.get("categories", []),
                "mechanics": game.get("mechanics", []),
                "designers": game.get("designers", []),
                "artists": game.get("artists", []),
                "publishers": game.get("publishers", []),
                "is_expansion": game.get("is_expansion", False),
                "parent_game": game.get("parent_game"),
                "parent_game_id": game.get("parent_game_id"),  # 新增：主遊戲的 BGG ID
            }

            logger.info(f"Retrieved details for game: {game['name']} (ID: {game_id})")
            return details

        except Exception as e:
            logger.error(f"Error getting game {game_id}: {e}")
            return None

    def _get_overall_rank(self, game) -> Optional[int]:
        """取得桌遊的整體排名"""
        try:
            ranks = game.get("ranks", [])
            for rank in ranks:
                if rank.get("name") == "boardgame" or rank.get("type") == "subtype":
                    rank_value = rank.get("value")
                    if rank_value and rank_value != "Not Ranked":
                        return int(rank_value)
            return None
        except BaseException:
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
            hot_items = self.client.hot_items("boardgame")

            games = []
            for item in hot_items[:limit]:
                games.append(
                    {
                        "id": item["id"],
                        "name": item["name"],
                        "year": item.get("year"),
                        "rank": item.get("rank"),
                        "thumbnail": item.get("thumbnail", ""),
                    }
                )

            logger.info(f"Retrieved {len(games)} hot games")
            return games

        except Exception as e:
            logger.error(f"Error getting hot games: {e}")
            return []

    def get_party_game_ids(self, limit: int = 100) -> List[int]:
        """取得派對桌遊 ID 列表（不呼叫 API，直接返回 ID）"""
        # 派對遊戲：經典遊戲 + 2024熱門
        party_game_ids = [
            # 經典派對遊戲
            178900,  # Codenames
            39856,  # Dixit
            166384,  # Spyfall
            262543,  # Wavelength
            254640,  # Just One
            181304,  # Welcome To...
            124742,  # Camel Up
            139030,  # Skull
            131835,  # Coup
            41114,  # The Resistance
            225694,  # Decrypto
            188834,  # Secret Hitler
            129622,  # Love Letter
            # 2024 熱門派對遊戲
            347805,  # Green Team Wins
            20100,  # Wits and Wagers
            329839,  # So Clover
            219215,  # Werewords
            375651,  # That's Not a Hat
            46213,  # Telestrations
            256788,  # Detective Club
            253664,  # Taco, Cat, Goat, Cheese, Pizza
            114438,  # But Wait, There's More
            # 更多派對遊戲
            131260,  # One Night Ultimate Werewolf
            244521,  # Time's Up!
            40692,  # Sushi Go!
            163412,  # Splendor (party-friendly)
            136063,  # Monikers
            177478,  # Insider
            171131,  # Pitchcar
            42215,  # Tsuro
            2726,  # Bohnanza
            37380,  # Dixit Odyssey
            98778,  # Hanabi
            13,  # Catan (family/party)
            194834,  # Costa Rica
            181449,  # Spyfall 2
            171273,  # The Mind
            256951,  # Wavelength Party Edition
            229853,  # A Fake Artist Goes to New York
            184267,  # One Night Ultimate Alien
            161533,  # Joking Hazard
            177383,  # Stealth Panda
            193738,  # Say Anything
            110327,  # Jungle Speed
            122515,  # 6 nimmt!
            8203,  # The Resistance: Avalon
            154203,  # Mascarade
            40398,  # Incan Gold
            18602,  # Cash 'n Guns
            126042,  # Geistes Blitz
            99732,  # Times Up! Party
        ]
        return party_game_ids[:limit]

    def get_party_games(self, limit: int = 10) -> List[Dict[str, Any]]:
        """取得派對桌遊（使用精選遊戲 ID）"""
        # 派對遊戲：經典遊戲 + 2024熱門
        party_game_ids = [
            # 經典派對遊戲
            178900,  # Codenames
            39856,  # Dixit
            166384,  # Spyfall
            262543,  # Wavelength
            254640,  # Just One
            181304,  # Welcome To...
            124742,  # Camel Up
            139030,  # Skull
            131835,  # Coup
            41114,  # The Resistance
            225694,  # Decrypto
            188834,  # Secret Hitler
            129622,  # Love Letter
            # 2024 熱門派對遊戲
            347805,  # Green Team Wins
            20100,  # Wits and Wagers
            329839,  # So Clover
            219215,  # Werewords
            375651,  # That's Not a Hat
            46213,  # Telestrations
            256788,  # Detective Club
            253664,  # Taco, Cat, Goat, Cheese, Pizza
            114438,  # But Wait, There's More
            # 更多派對遊戲
            131260,  # One Night Ultimate Werewolf
            244521,  # Time's Up!
            40692,  # Sushi Go!
            163412,  # Splendor (party-friendly)
            136063,  # Monikers
            177478,  # Insider
            171131,  # Pitchcar
            42215,  # Tsuro
            2726,  # Bohnanza
            37380,  # Dixit Odyssey
            98778,  # Hanabi
            13,  # Catan (family/party)
            194834,  # Costa Rica
            181449,  # Spyfall 2
            171273,  # The Mind
            256951,  # Wavelength Party Edition
            229853,  # A Fake Artist Goes to New York
            184267,  # One Night Ultimate Alien
            161533,  # Joking Hazard
            177383,  # Stealth Panda
            193738,  # Say Anything
            110327,  # Jungle Speed
            122515,  # 6 nimmt!
            8203,  # The Resistance: Avalon
            154203,  # Mascarade
            40398,  # Incan Gold
            18602,  # Cash 'n Guns
            126042,  # Geistes Blitz
            99732,  # Times Up! Party
        ]
        return self._get_games_by_ids(self.get_party_game_ids(limit))

    def get_strategy_game_ids(self, limit: int = 100) -> List[int]:
        """取得策略桌遊 ID 列表（不呼叫 API，直接返回 ID）"""
        # 策略遊戲：經典 + 2024熱門
        strategy_game_ids = [
            # 經典策略遊戲
            174430,  # Gloomhaven
            224517,  # Brass: Birmingham
            167791,  # Terraforming Mars
            266192,  # Wingspan
            233078,  # Twilight Imperium (Fourth Edition)
            161936,  # Pandemic Legacy: Season 1
            220308,  # Gaia Project
            182028,  # Through the Ages: A New Story of Civilization
            173346,  # 7 Wonders Duel
            169786,  # Scythe
            162886,  # Spirit Island
            342942,  # Ark Nova
            316554,  # Dune: Imperium
            # 2024 熱門策略遊戲
            329500,  # Unconscious Mind
            415848,  # Lands of Evershade
            359871,  # Arcs
            421006,  # The Lord of the Rings: Duel for Middle-Earth
            400602,  # Civolution
            418059,  # SETI: Search for Extraterrestrial Intelligence
            371183,  # Joyride: Survival of the Fastest
            403150,  # World Order
            428099,  # Revenant
            237182,  # Root
            420805,  # Black Forest
            413246,  # Bomb Busters
            414317,  # Harmonies
            321608,  # Hegemony: Lead Your Class to Victory
            417197,  # Rebirth
            338376,  # A Gest of Robin Hood
            392492,  # Stupor Mundi
            298231,  # Skyrise
            407343,  # Ironwood
            338960,  # Slay the Spire: The Board Game
            402669,  # Sand
            # 更多經典策略
            186834,  # Great Western Trail
            187645,  # Concordia
            175914,  # Viticulture Essential Edition
            230802,  # Azul (strategy-light)
            205637,  # Arkham Horror: The Card Game
            12333,  # Twilight Struggle
            68448,  # 7 Wonders
            148228,  # Splendor
            311193,  # Everdell
            284083,  # The Castles of Tuscany
            307377,  # Paladins of the West Kingdom
            266810,  # Barrage
            276025,  # Res Arcana
            177736,  # A Feast for Odin
            115746,  # War of the Ring: Second Edition
            246900,  # Eclipse: Second Dawn for the Galaxy
        ]
        return strategy_game_ids[:limit]

    def get_strategy_games(self, limit: int = 10) -> List[Dict[str, Any]]:
        """取得策略桌遊（使用精選遊戲 ID）"""
        # 策略遊戲：經典 + 2024熱門
        strategy_game_ids = [
            # 經典策略遊戲
            174430,  # Gloomhaven
            224517,  # Brass: Birmingham
            167791,  # Terraforming Mars
            266192,  # Wingspan
            233078,  # Twilight Imperium (Fourth Edition)
            161936,  # Pandemic Legacy: Season 1
            220308,  # Gaia Project
            182028,  # Through the Ages: A New Story of Civilization
            173346,  # 7 Wonders Duel
            169786,  # Scythe
            162886,  # Spirit Island
            342942,  # Ark Nova
            316554,  # Dune: Imperium
            # 2024 熱門策略遊戲
            329500,  # Unconscious Mind
            415848,  # Lands of Evershade
            359871,  # Arcs
            421006,  # The Lord of the Rings: Duel for Middle-Earth
            400602,  # Civolution
            418059,  # SETI: Search for Extraterrestrial Intelligence
            371183,  # Joyride: Survival of the Fastest
            403150,  # World Order
            428099,  # Revenant
            237182,  # Root
            420805,  # Black Forest
            413246,  # Bomb Busters
            414317,  # Harmonies
            321608,  # Hegemony: Lead Your Class to Victory
            417197,  # Rebirth
            338376,  # A Gest of Robin Hood
            392492,  # Stupor Mundi
            298231,  # Skyrise
            407343,  # Ironwood
            338960,  # Slay the Spire: The Board Game
            402669,  # Sand
            # 更多經典策略
            186834,  # Great Western Trail
            187645,  # Concordia
            175914,  # Viticulture Essential Edition
            230802,  # Azul (strategy-light)
            205637,  # Arkham Horror: The Card Game
            12333,  # Twilight Struggle
            68448,  # 7 Wonders
            148228,  # Splendor
            311193,  # Everdell
            284083,  # The Castles of Tuscany
            307377,  # Paladins of the West Kingdom
            266810,  # Barrage
            276025,  # Res Arcana
            177736,  # A Feast for Odin
        ]
        return self._get_games_by_ids(self.get_strategy_game_ids(limit))

    def get_family_game_ids(self, limit: int = 100) -> List[int]:
        """取得家庭桌遊 ID 列表（不呼叫 API，直接返回 ID）"""
        # 家庭遊戲：經典 + 2024熱門
        family_game_ids = [
            # 經典家庭遊戲
            13,  # CATAN
            9209,  # Ticket to Ride
            148228,  # Splendor
            230802,  # Azul
            822,  # Carcassonne
            30549,  # Pandemic
            31260,  # Agricola
            68448,  # 7 Wonders
            84876,  # The Castles of Burgundy
            204583,  # Kingdomino
            324856,  # The Crew: Mission Deep Sea
            295947,  # Cascadia
            281259,  # The Isle of Cats
            # 2024 熱門家庭遊戲
            367204,  # Trio (aka Nana)
            317351,  # The Crew: Mission Deep Sea (alt ID)
            396825,  # MLEM: Space Agency
            395982,  # River Valley Glass Works
            418464,  # Nune Attack
            396918,  # Captain Flip
            388147,  # Entaria
            393962,  # Aqua Biodiversity in the Oceans
            399127,  # Zooies
            385573,  # Festival
            396116,  # Happy Home
            360061,  # Decorum
            346610,  # Verdant
            377030,  # Shelfie
            375747,  # Kids Chronicles - The Old Oak Prophecy
            37780,  # Incan Gold
            386566,  # Skyrise
            409945,  # Santa's Workshop
            399623,  # Umbrella
            # 更多家庭遊戲
            178900,  # Codenames (family-friendly)
            266192,  # Wingspan
            171131,  # Pitchcar
            8217,  # Rummikub
            822,  # Carcassonne
            40692,  # Sushi Go!
            98778,  # Hanabi
            42215,  # Tsuro
            40398,  # Incan Gold (duplicate check)
            2651,  # Power Grid
            128882,  # Escape: The Curse of the Temple
            172308,  # Stone Age
            169786,  # Scythe (family-weight for experienced)
            110308,  # Forbidden Island
            254640,  # Just One
            201808,  # Clank! A Deck-Building Adventure
            192458,  # Century: Spice Road
            263918,  # Cartographers
        ]
        return family_game_ids[:limit]

    def get_family_games(self, limit: int = 10) -> List[Dict[str, Any]]:
        """取得家庭桌遊（使用精選遊戲 ID）"""
        # 家庭遊戲：經典 + 2024熱門
        family_game_ids = [
            # 經典家庭遊戲
            13,  # CATAN
            9209,  # Ticket to Ride
            148228,  # Splendor
            230802,  # Azul
            822,  # Carcassonne
            30549,  # Pandemic
            31260,  # Agricola
            68448,  # 7 Wonders
            84876,  # The Castles of Burgundy
            204583,  # Kingdomino
            324856,  # The Crew: Mission Deep Sea
            295947,  # Cascadia
            281259,  # The Isle of Cats
            # 2024 熱門家庭遊戲
            367204,  # Trio (aka Nana)
            317351,  # The Crew: Mission Deep Sea (alt ID)
            396825,  # MLEM: Space Agency
            395982,  # River Valley Glass Works
            418464,  # Nune Attack
            396918,  # Captain Flip
            388147,  # Entaria
            393962,  # Aqua Biodiversity in the Oceans
            399127,  # Zooies
            385573,  # Festival
            396116,  # Happy Home
            360061,  # Decorum
            346610,  # Verdant
            377030,  # Shelfie
            375747,  # Kids Chronicles - The Old Oak Prophecy
            37780,  # Incan Gold
            386566,  # Skyrise
            409945,  # Santa's Workshop
            399623,  # Umbrella
            # 更多家庭遊戲
            178900,  # Codenames (family-friendly)
            266192,  # Wingspan
            171131,  # Pitchcar
            8217,  # Rummikub
            822,  # Carcassonne
            40692,  # Sushi Go!
            98778,  # Hanabi
            42215,  # Tsuro
            40398,  # Incan Gold (duplicate check)
            2651,  # Power Grid
            128882,  # Escape: The Curse of the Temple
            172308,  # Stone Age
            169786,  # Scythe (family-weight for experienced)
            110308,  # Forbidden Island
            254640,  # Just One
        ]
        return self._get_games_by_ids(self.get_family_game_ids(limit))

    def get_children_game_ids(self, limit: int = 100) -> List[int]:
        """取得兒童桌遊 ID 列表（不呼叫 API，直接返回 ID）"""
        # 兒童遊戲：經典 + 2024熱門
        children_game_ids = [
            # 經典兒童遊戲
            70323,  # King of Tokyo
            256952,  # Zombie Kidz Evolution
            41010,  # My First Carcassonne
            163412,  # Patchwork
            42215,  # Tsuro
            244521,  # Time's Up! Kids
            244522,  # Time's Up! Family
            123540,  # Spot It! (Dobble)
            193621,  # My Little Scythe
            91514,  # Rhino Hero
            177524,  # Ice Cool
            150484,  # Outfoxed!
            125921,  # Catan Junior
            # 2024 熱門兒童遊戲
            218333,  # Rhino Hero: Super Battle
            270844,  # Coconuts
            344254,  # Yummy Yummy Monster Tummy
            343833,  # Turtle Splash!
            17329,  # Animal Upon Animal
            295490,  # Dodo
            233020,  # Fireball Island: The Curse of Vul-Kar
            247160,  # Dinosaur Tea Party
            191925,  # Bandido
            361861,  # Scribbly Gum
            226320,  # My Little Scythe (duplicate check)
            338460,  # The Isle of Cats: Explore & Draw
            # 更多兒童遊戲
            204583,  # Kingdomino (kid-friendly)
            40692,  # Sushi Go!
            40398,  # Incan Gold (kids version)
            110308,  # Forbidden Island
            128882,  # Escape: The Curse of the Temple
            954,  # Labyrinth
            822,  # My First Carcassonne (base)
            188834,  # Secret Hitler (older kids)
            2655,  # Hive
            13,  # Catan (family with kids)
            9209,  # Ticket to Ride (family)
            230802,  # Azul (abstract for kids)
            98778,  # Hanabi (cooperative)
            13,  # CATAN (duplicate - family game)
            181304,  # Welcome To... (older kids)
            131260,  # One Night Ultimate Werewolf (older kids)
            127398,  # Qwirkle
            822,  # Carcassonne (gateway)
            40692,  # Sushi Go! Party
            36218,  # Dominion
            68448,  # 7 Wonders (family)
            314491,  # Dragomino
            150484,  # Outfoxed! (duplicate for emphasis)
            312883,  # Sleeping Queens
            94483,  # Hoot Owl Hoot!
        ]
        return children_game_ids[:limit]

    def get_children_games(self, limit: int = 10) -> List[Dict[str, Any]]:
        """取得兒童桌遊（使用精選遊戲 ID）"""
        # 兒童遊戲：經典 + 2024熱門
        children_game_ids = [
            # 經典兒童遊戲
            70323,  # King of Tokyo
            256952,  # Zombie Kidz Evolution
            41010,  # My First Carcassonne
            163412,  # Patchwork
            42215,  # Tsuro
            244521,  # Time's Up! Kids
            244522,  # Time's Up! Family
            123540,  # Spot It! (Dobble)
            193621,  # My Little Scythe
            91514,  # Rhino Hero
            177524,  # Ice Cool
            150484,  # Outfoxed!
            125921,  # Catan Junior
            # 2024 熱門兒童遊戲
            218333,  # Rhino Hero: Super Battle
            270844,  # Coconuts
            344254,  # Yummy Yummy Monster Tummy
            343833,  # Turtle Splash!
            17329,  # Animal Upon Animal
            295490,  # Dodo
            233020,  # Fireball Island: The Curse of Vul-Kar
            247160,  # Dinosaur Tea Party
            191925,  # Bandido
            361861,  # Scribbly Gum
            226320,  # My Little Scythe (duplicate check)
            338460,  # The Isle of Cats: Explore & Draw
            # 更多兒童遊戲
            204583,  # Kingdomino (kid-friendly)
            40692,  # Sushi Go!
            40398,  # Incan Gold (kids version)
            110308,  # Forbidden Island
            128882,  # Escape: The Curse of the Temple
            954,  # Labyrinth
            822,  # My First Carcassonne (base)
            188834,  # Secret Hitler (older kids)
            2655,  # Hive
            13,  # Catan (family with kids)
            9209,  # Ticket to Ride (family)
            230802,  # Azul (abstract for kids)
            98778,  # Hanabi (cooperative)
            13,  # CATAN (duplicate - family game)
            181304,  # Welcome To... (older kids)
            131260,  # One Night Ultimate Werewolf (older kids)
            127398,  # Qwirkle
            822,  # Carcassonne (gateway)
            40692,  # Sushi Go! Party
            36218,  # Dominion
            68448,  # 7 Wonders (family)
        ]
        return self._get_games_by_ids(self.get_children_game_ids(limit))

    def _get_games_by_ids(self, game_ids: List[int]) -> List[Dict[str, Any]]:
        """
        根據 ID 列表獲取遊戲資訊（並發版本）

        使用 ThreadPoolExecutor 並發獲取多個遊戲詳情，
        大幅提升推薦頁面載入速度。

        Args:
            game_ids: 遊戲 ID 列表

        Returns:
            遊戲資訊列表
        """
        games = []

        # 使用並發執行，最多 5 個並發請求
        with ThreadPoolExecutor(max_workers=5) as executor:
            # 提交所有任務
            future_to_id = {
                executor.submit(self.get_game_details, game_id): game_id
                for game_id in game_ids
            }

            # 收集結果
            for future in as_completed(future_to_id):
                game_id = future_to_id[future]
                try:
                    game = future.result(timeout=10)
                    if game:
                        games.append(
                            {
                                "id": game["id"],
                                "name": game["name"],
                                "year": game.get("year"),
                                "thumbnail": game.get("thumbnail"),
                                "rating_average": game.get("rating_average"),
                            }
                        )
                except Exception as e:
                    logger.warning(f"Failed to get game {game_id}: {e}")
                    continue

        return games

    def get_our_hot_games(self, sheets_client, limit: int = 50) -> List[Dict[str, Any]]:
        """
        取得我們館藏中的熱門遊戲

        Args:
            sheets_client: SheetsClient 實例，用於讀取館藏資料
            limit: 檢查熱門榜前幾名（預設 50 名）

        Returns:
            館藏中的熱門遊戲列表，每個項目包含：
            - id: BGG ID
            - name: 遊戲名稱
            - hot_rank: 熱門排名
            - status: 借閱狀態
            - borrower: 借閱人（如果被借出）
            - local_name: 本地名稱
        """
        try:
            # 取得 BGG 熱門榜
            hot_list = self.get_hot_games(limit=limit)
            if not hot_list:
                logger.warning("無法取得 BGG 熱門榜")
                return []

            # 取得本地館藏
            our_games = sheets_client.load_games()
            if not our_games:
                logger.warning("無法取得館藏資料")
                return []

            # 建立 BGG ID 到本地遊戲的映射
            bgg_id_map = {}
            for game in our_games:
                bgg_id = game.get("bgg_id")
                if bgg_id:
                    try:
                        bgg_id_map[int(bgg_id)] = game
                    except (ValueError, TypeError):
                        continue

            # 比對熱門榜
            our_hot_games = []
            for hot_game in hot_list:
                bgg_id = hot_game["id"]
                if bgg_id in bgg_id_map:
                    local_game = bgg_id_map[bgg_id]
                    our_hot_games.append(
                        {
                            "id": bgg_id,
                            "name": hot_game["name"],
                            "hot_rank": hot_game["rank"],
                            "status": local_game.get("status", "未知"),
                            "borrower": local_game.get("borrower", ""),
                            "local_name": local_game.get("name", hot_game["name"]),
                            "thumbnail": hot_game.get("thumbnail", ""),
                            "year": hot_game.get("year"),
                        }
                    )

            logger.info(f"找到 {len(our_hot_games)} 款館藏中的熱門遊戲（檢查前 {limit} 名）")
            return our_hot_games

        except Exception as e:
            logger.error(f"比對館藏熱門遊戲失敗: {e}")
            return []
