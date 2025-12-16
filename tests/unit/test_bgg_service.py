"""
測試 core/bgg_service.py 模組 (使用 mock)
"""
import pytest
from unittest.mock import MagicMock, patch
from flask import Flask


class TestBGGServiceInit:
    """測試初始化"""
    
    @patch('core.bgg_service.BGGApiClient')
    def test_init_demo_mode(self, mock_client):
        """測試演示模式初始化"""
        app = Flask(__name__)
        app.config['DEMO_MODE'] = True
        
        with app.app_context():
            from core.bgg_service import BGGService
            service = BGGService()
            assert service.demo_mode is True
    
    @patch('core.bgg_service.BGGApiClient')
    def test_init_normal_mode(self, mock_client):
        """測試正常模式初始化"""
        app = Flask(__name__)
        app.config['DEMO_MODE'] = False
        app.config['BGG_API_TOKEN'] = 'test_token'
        
        with app.app_context():
            from core.bgg_service import BGGService
            service = BGGService()
            assert service.demo_mode is False


class TestBGGServiceSearchGames:
    """測試 search_games 方法"""
    
    @patch('core.bgg_service.BGGApiClient')
    def test_search_games_demo_mode(self, mock_client):
        """測試演示模式搜尋"""
        app = Flask(__name__)
        app.config['DEMO_MODE'] = True
        
        with app.app_context():
            from core.bgg_service import BGGService
            service = BGGService()
            results = service.search_games('Catan')
            
            # 演示模式應該返回預設資料
            assert isinstance(results, list)
    
    @patch('core.bgg_service.BGGApiClient')
    def test_search_games_api_mode(self, mock_client):
        """測試 API 模式搜尋"""
        mock_api = MagicMock()
        mock_api.search.return_value = [
            {'id': 13, 'name': 'Catan', 'year': 1995}
        ]
        mock_client.return_value = mock_api
        
        app = Flask(__name__)
        app.config['DEMO_MODE'] = False
        app.config['BGG_API_TOKEN'] = 'test'
        
        with app.app_context():
            from core.bgg_service import BGGService
            service = BGGService()
            results = service.search_games('Catan')
            
            assert isinstance(results, list)
    
    @patch('core.bgg_service.BGGApiClient')
    def test_search_games_empty_query(self, mock_client):
        """測試空查詢"""
        app = Flask(__name__)
        app.config['DEMO_MODE'] = True
        
        with app.app_context():
            from core.bgg_service import BGGService
            service = BGGService()
            results = service.search_games('')
            
            assert results == []


class TestBGGServiceGetGameDetails:
    """測試 get_game_details 方法"""
    
    @patch('core.bgg_service.BGGApiClient')
    def test_get_game_details_demo_mode(self, mock_client):
        """測試演示模式取得詳情"""
        app = Flask(__name__)
        app.config['DEMO_MODE'] = True
        
        with app.app_context():
            from core.bgg_service import BGGService
            service = BGGService()
            details = service.get_game_details(13)
            
            # 演示模式返回預設詳情
            assert isinstance(details, (dict, type(None)))
    
    @patch('core.bgg_service.BGGApiClient')
    def test_get_game_details_api_mode(self, mock_client):
        """測試 API 模式取得詳情"""
        mock_api = MagicMock()
        mock_api.game.return_value = {
            'id': 13,
            'name': 'Catan',
            'rating_average': 7.5,
            'rank': 50
        }
        mock_client.return_value = mock_api
        
        app = Flask(__name__)
        app.config['DEMO_MODE'] = False
        app.config['BGG_API_TOKEN'] = 'test'
        
        with app.app_context():
            from core.bgg_service import BGGService
            service = BGGService()
            details = service.get_game_details(13)
            
            assert isinstance(details, (dict, type(None)))


class TestBGGServiceGetHotGames:
    """測試 get_hot_games 方法"""
    
    @patch('core.bgg_service.BGGApiClient')
    def test_get_hot_games_demo_mode(self, mock_client):
        """測試演示模式熱門遊戲"""
        app = Flask(__name__)
        app.config['DEMO_MODE'] = True
        
        with app.app_context():
            from core.bgg_service import BGGService
            service = BGGService()
            hot = service.get_hot_games(limit=5)
            
            assert isinstance(hot, list)
    
    @patch('core.bgg_service.BGGApiClient')
    def test_get_hot_games_api_mode(self, mock_client):
        """測試 API 模式熱門遊戲"""
        mock_api = MagicMock()
        mock_api.hot_items.return_value = [
            {'id': 13, 'name': 'Catan', 'rank': 1}
        ]
        mock_client.return_value = mock_api
        
        app = Flask(__name__)
        app.config['DEMO_MODE'] = False
        app.config['BGG_API_TOKEN'] = 'test'
        
        with app.app_context():
            from core.bgg_service import BGGService
            service = BGGService()
            hot = service.get_hot_games(limit=5)
            
            assert isinstance(hot, list)


class TestBGGServiceGameCategories:
    """測試遊戲分類方法"""
    
    @patch('core.bgg_service.BGGApiClient')
    def test_get_party_game_ids(self, mock_client):
        """測試取得派對遊戲 ID"""
        app = Flask(__name__)
        app.config['DEMO_MODE'] = True
        
        with app.app_context():
            from core.bgg_service import BGGService
            service = BGGService()
            ids = service.get_party_game_ids(limit=10)
            
            assert isinstance(ids, list)
            assert len(ids) <= 10
    
    @patch('core.bgg_service.BGGApiClient')
    def test_get_strategy_game_ids(self, mock_client):
        """測試取得策略遊戲 ID"""
        app = Flask(__name__)
        app.config['DEMO_MODE'] = True
        
        with app.app_context():
            from core.bgg_service import BGGService
            service = BGGService()
            ids = service.get_strategy_game_ids(limit=10)
            
            assert isinstance(ids, list)
    
    @patch('core.bgg_service.BGGApiClient')
    def test_get_family_game_ids(self, mock_client):
        """測試取得家庭遊戲 ID"""
        app = Flask(__name__)
        app.config['DEMO_MODE'] = True
        
        with app.app_context():
            from core.bgg_service import BGGService
            service = BGGService()
            ids = service.get_family_game_ids(limit=10)
            
            assert isinstance(ids, list)
    
    @patch('core.bgg_service.BGGApiClient')
    def test_get_children_game_ids(self, mock_client):
        """測試取得兒童遊戲 ID"""
        app = Flask(__name__)
        app.config['DEMO_MODE'] = True
        
        with app.app_context():
            from core.bgg_service import BGGService
            service = BGGService()
            ids = service.get_children_game_ids(limit=10)
            
            assert isinstance(ids, list)
