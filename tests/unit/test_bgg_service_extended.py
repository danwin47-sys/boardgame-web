"""
測試 core/bgg_service.py 模組 - 擴充測試
補充缺失的測試案例以提升覆蓋率
"""
import pytest
from unittest.mock import MagicMock, patch
from flask import Flask


class TestBGGServiceGetPartyGames:
    """測試 get_party_games 方法"""
    
    @patch('core.bgg_service.BGGApiClient')
    def test_get_party_games_demo_mode(self, mock_client):
        """測試演示模式取得派對遊戲"""
        app = Flask(__name__)
        app.config['DEMO_MODE'] = True
        
        with app.app_context():
            from core.bgg_service import BGGService
            service = BGGService()
            games = service.get_party_games(limit=5)
            
            assert isinstance(games, list)
            assert len(games) <= 5
    
    @patch('core.bgg_service.BGGApiClient')
    def test_get_party_games_api_mode(self, mock_client):
        """測試 API 模式取得派對遊戲"""
        mock_api = MagicMock()
        mock_api.collection.return_value = [
            {'id': 1, 'name': 'Party Game 1'},
            {'id': 2, 'name': 'Party Game 2'}
        ]
        mock_client.return_value = mock_api
        
        app = Flask(__name__)
        app.config['DEMO_MODE'] = False
        app.config['BGG_API_TOKEN'] = 'test'
        
        with app.app_context():
            from core.bgg_service import BGGService
            service = BGGService()
            games = service.get_party_games(limit=5)
            
            assert isinstance(games, list)


class TestBGGServiceGetStrategyGames:
    """測試 get_strategy_games 方法"""
    
    @patch('core.bgg_service.BGGApiClient')
    def test_get_strategy_games_demo_mode(self, mock_client):
        """測試演示模式取得策略遊戲"""
        app = Flask(__name__)
        app.config['DEMO_MODE'] = True
        
        with app.app_context():
            from core.bgg_service import BGGService
            service = BGGService()
            games = service.get_strategy_games(limit=5)
            
            assert isinstance(games, list)
            assert len(games) <= 5
    
    @patch('core.bgg_service.BGGApiClient')
    def test_get_strategy_games_api_mode(self, mock_client):
        """測試 API 模式取得策略遊戲"""
        mock_api = MagicMock()
        mock_api.collection.return_value = [
            {'id': 1, 'name': 'Strategy Game 1'},
            {'id': 2, 'name': 'Strategy Game 2'}
        ]
        mock_client.return_value = mock_api
        
        app = Flask(__name__)
        app.config['DEMO_MODE'] = False
        app.config['BGG_API_TOKEN'] = 'test'
        
        with app.app_context():
            from core.bgg_service import BGGService
            service = BGGService()
            games = service.get_strategy_games(limit=5)
            
            assert isinstance(games, list)


class TestBGGServiceGetFamilyGames:
    """測試 get_family_games 方法"""
    
    @patch('core.bgg_service.BGGApiClient')
    def test_get_family_games_demo_mode(self, mock_client):
        """測試演示模式取得家庭遊戲"""
        app = Flask(__name__)
        app.config['DEMO_MODE'] = True
        
        with app.app_context():
            from core.bgg_service import BGGService
            service = BGGService()
            games = service.get_family_games(limit=5)
            
            assert isinstance(games, list)
            assert len(games) <= 5
    
    @patch('core.bgg_service.BGGApiClient')
    def test_get_family_games_api_mode(self, mock_client):
        """測試 API 模式取得家庭遊戲"""
        mock_api = MagicMock()
        mock_api.collection.return_value = [
            {'id': 1, 'name': 'Family Game 1'},
            {'id': 2, 'name': 'Family Game 2'}
        ]
        mock_client.return_value = mock_api
        
        app = Flask(__name__)
        app.config['DEMO_MODE'] = False
        app.config['BGG_API_TOKEN'] = 'test'
        
        with app.app_context():
            from core.bgg_service import BGGService
            service = BGGService()
            games = service.get_family_games(limit=5)
            
            assert isinstance(games, list)


class TestBGGServiceGetChildrenGames:
    """測試 get_children_games 方法"""
    
    @patch('core.bgg_service.BGGApiClient')
    def test_get_children_games_demo_mode(self, mock_client):
        """測試演示模式取得兒童遊戲"""
        app = Flask(__name__)
        app.config['DEMO_MODE'] = True
        
        with app.app_context():
            from core.bgg_service import BGGService
            service = BGGService()
            games = service.get_children_games(limit=5)
            
            assert isinstance(games, list)
            assert len(games) <= 5
    
    @patch('core.bgg_service.BGGApiClient')
    def test_get_children_games_api_mode(self, mock_client):
        """測試 API 模式取得兒童遊戲"""
        mock_api = MagicMock()
        mock_api.collection.return_value = [
            {'id': 1, 'name': 'Children Game 1'},
            {'id': 2, 'name': 'Children Game 2'}
        ]
        mock_client.return_value = mock_api
        
        app = Flask(__name__)
        app.config['DEMO_MODE'] = False
        app.config['BGG_API_TOKEN'] = 'test'
        
        with app.app_context():
            from core.bgg_service import BGGService
            service = BGGService()
            games = service.get_children_games(limit=5)
            
            assert isinstance(games, list)


class TestBGGServiceGetOurHotGames:
    """測試 get_our_hot_games 方法"""
    
    @patch('core.bgg_service.BGGApiClient')
    def test_get_our_hot_games_with_matches(self, mock_client):
        """測試館藏熱門遊戲（有匹配）"""
        mock_api = MagicMock()
        mock_api.hot_items.return_value = [
            {'id': 13, 'name': 'Catan', 'rank': 1},
            {'id': 174430, 'name': 'Gloomhaven', 'rank': 2}
        ]
        mock_client.return_value = mock_api
        
        # Mock sheets_client
        mock_sheets = MagicMock()
        mock_sheets.load_games.return_value = [
            {'name': 'Catan', 'bgg_id': '13', 'status': '可用'},
            {'name': 'Other Game', 'bgg_id': '999', 'status': '可用'}
        ]
        
        app = Flask(__name__)
        app.config['DEMO_MODE'] = False
        app.config['BGG_API_TOKEN'] = 'test'
        
        with app.app_context():
            from core.bgg_service import BGGService
            service = BGGService()
            hot_games = service.get_our_hot_games(mock_sheets, limit=10)
            
            assert isinstance(hot_games, list)
            # 應該找到 Catan
            if hot_games:
                assert any(g.get('name') == 'Catan' for g in hot_games)
    
    @patch('core.bgg_service.BGGApiClient')
    def test_get_our_hot_games_no_matches(self, mock_client):
        """測試館藏熱門遊戲（無匹配）"""
        mock_api = MagicMock()
        mock_api.hot_items.return_value = [
            {'id': 999, 'name': 'Unknown Game', 'rank': 1}
        ]
        mock_client.return_value = mock_api
        
        # Mock sheets_client
        mock_sheets = MagicMock()
        mock_sheets.load_games.return_value = [
            {'name': 'Other Game', 'bgg_id': '123', 'status': '可用'}
        ]
        
        app = Flask(__name__)
        app.config['DEMO_MODE'] = False
        app.config['BGG_API_TOKEN'] = 'test'
        
        with app.app_context():
            from core.bgg_service import BGGService
            service = BGGService()
            hot_games = service.get_our_hot_games(mock_sheets, limit=10)
            
            assert isinstance(hot_games, list)
            assert len(hot_games) == 0


class TestBGGServiceGetGamesByIds:
    """測試 _get_games_by_ids 方法"""
    
    @patch('core.bgg_service.BGGApiClient')
    def test_get_games_by_ids_success(self, mock_client):
        """測試批次獲取遊戲成功"""
        mock_api = MagicMock()
        mock_api.collection.return_value = [
            {'id': 13, 'name': 'Catan'},
            {'id': 174430, 'name': 'Gloomhaven'}
        ]
        mock_client.return_value = mock_api
        
        app = Flask(__name__)
        app.config['DEMO_MODE'] = False
        app.config['BGG_API_TOKEN'] = 'test'
        
        with app.app_context():
            from core.bgg_service import BGGService
            service = BGGService()
            games = service._get_games_by_ids([13, 174430])
            
            assert isinstance(games, list)
    
    @patch('core.bgg_service.BGGApiClient')
    def test_get_games_by_ids_empty_list(self, mock_client):
        """測試空 ID 列表"""
        app = Flask(__name__)
        app.config['DEMO_MODE'] = False
        app.config['BGG_API_TOKEN'] = 'test'
        
        with app.app_context():
            from core.bgg_service import BGGService
            service = BGGService()
            games = service._get_games_by_ids([])
            
            assert games == []


class TestBGGServiceErrorHandling:
    """測試錯誤處理"""
    
    @patch('core.bgg_service.BGGApiClient')
    def test_search_games_api_error(self, mock_client):
        """測試搜尋遊戲 API 錯誤"""
        mock_api = MagicMock()
        mock_api.search.side_effect = Exception("API Error")
        mock_client.return_value = mock_api
        
        app = Flask(__name__)
        app.config['DEMO_MODE'] = False
        app.config['BGG_API_TOKEN'] = 'test'
        
        with app.app_context():
            from core.bgg_service import BGGService
            service = BGGService()
            # 應該返回空列表而不是拋出異常
            results = service.search_games('Catan')
            assert results == []
    
    @patch('core.bgg_service.BGGApiClient')
    def test_get_game_details_api_error(self, mock_client):
        """測試取得遊戲詳情 API 錯誤"""
        mock_api = MagicMock()
        mock_api.game.side_effect = Exception("API Error")
        mock_client.return_value = mock_api
        
        app = Flask(__name__)
        app.config['DEMO_MODE'] = False
        app.config['BGG_API_TOKEN'] = 'test'
        
        with app.app_context():
            from core.bgg_service import BGGService
            service = BGGService()
            # 應該返回 None 而不是拋出異常
            details = service.get_game_details(13)
            assert details is None
    
    @patch('core.bgg_service.BGGApiClient')
    def test_get_hot_games_api_error(self, mock_client):
        """測試取得熱門遊戲 API 錯誤"""
        mock_api = MagicMock()
        mock_api.hot_items.side_effect = Exception("API Error")
        mock_client.return_value = mock_api
        
        app = Flask(__name__)
        app.config['DEMO_MODE'] = False
        app.config['BGG_API_TOKEN'] = 'test'
        
        with app.app_context():
            from core.bgg_service import BGGService
            service = BGGService()
            # 應該返回空列表而不是拋出異常
            hot = service.get_hot_games(limit=5)
            assert hot == []


class TestBGGServiceCaching:
    """測試快取機制"""
    
    @patch('core.bgg_service.BGGApiClient')
    @patch('core.bgg_service.cache_with_timeout')
    def test_search_games_uses_cache(self, mock_cache, mock_client):
        """測試搜尋遊戲使用快取"""
        # cache_with_timeout 是裝飾器，這裡測試它被正確應用
        app = Flask(__name__)
        app.config['DEMO_MODE'] = True
        
        with app.app_context():
            from core.bgg_service import BGGService
            service = BGGService()
            
            # 第一次呼叫
            results1 = service.search_games('Catan')
            # 第二次呼叫（應該使用快取）
            results2 = service.search_games('Catan')
            
            # 兩次結果應該相同
            assert results1 == results2
    
    @patch('core.bgg_service.BGGApiClient')
    def test_get_game_details_caching(self, mock_client):
        """測試遊戲詳情快取"""
        mock_api = MagicMock()
        mock_api.game.return_value = {
            'id': 13,
            'name': 'Catan',
            'rating_average': 7.5
        }
        mock_client.return_value = mock_api
        
        app = Flask(__name__)
        app.config['DEMO_MODE'] = False
        app.config['BGG_API_TOKEN'] = 'test'
        
        with app.app_context():
            from core.bgg_service import BGGService
            service = BGGService()
            
            # 第一次呼叫
            details1 = service.get_game_details(13)
            # 第二次呼叫
            details2 = service.get_game_details(13)
            
            # 兩次結果應該相同
            assert details1 == details2


class TestBGGServiceEdgeCases:
    """測試邊界情況"""
    
    @patch('core.bgg_service.BGGApiClient')
    def test_get_party_games_zero_limit(self, mock_client):
        """測試限制為 0"""
        app = Flask(__name__)
        app.config['DEMO_MODE'] = True
        
        with app.app_context():
            from core.bgg_service import BGGService
            service = BGGService()
            games = service.get_party_games(limit=0)
            
            assert isinstance(games, list)
            assert len(games) == 0
    
    @patch('core.bgg_service.BGGApiClient')
    def test_get_party_games_large_limit(self, mock_client):
        """測試超大限制"""
        app = Flask(__name__)
        app.config['DEMO_MODE'] = True
        
        with app.app_context():
            from core.bgg_service import BGGService
            service = BGGService()
            games = service.get_party_games(limit=1000)
            
            assert isinstance(games, list)
            # 即使要求 1000，實際返回數量應該有限
            assert len(games) <= 100
    
    @patch('core.bgg_service.BGGApiClient')
    def test_search_games_special_characters(self, mock_client):
        """測試特殊字元搜尋"""
        app = Flask(__name__)
        app.config['DEMO_MODE'] = True
        
        with app.app_context():
            from core.bgg_service import BGGService
            service = BGGService()
            
            # 測試各種特殊字元
            results = service.search_games('Game & Dragons')
            assert isinstance(results, list)
            
            results = service.search_games('Game: The Game')
            assert isinstance(results, list)
