"""
測試 core/bgg_api_client.py 模組 (使用 mock)
"""
import pytest
from unittest.mock import patch, MagicMock
import xml.etree.ElementTree as ET

from core.bgg_api_client import BGGApiClient


class TestBGGApiClientInit:
    """測試 BGGApiClient 初始化"""
    
    def test_init_with_token(self):
        """測試帶 token 初始化"""
        client = BGGApiClient(api_token="test_token")
        assert client.api_token == "test_token"
        assert 'Authorization' in client.session.headers
    
    def test_init_without_token(self):
        """測試不帶 token 初始化"""
        client = BGGApiClient()
        assert client.api_token == ""
        assert 'Authorization' not in client.session.headers
        assert 'User-Agent' in client.session.headers
    
    def test_init_custom_timeout(self):
        """測試自定義超時"""
        client = BGGApiClient(timeout=30, retries=5)
        assert client.timeout == 30
        assert client.retries == 5


class TestBGGApiClientSearch:
    """測試 search 方法"""
    
    @patch.object(BGGApiClient, '_make_request')
    def test_search_success(self, mock_request):
        """測試搜尋成功"""
        # 模擬 XML 回應
        xml_str = '''
        <items>
            <item id="13" type="boardgame">
                <name value="Catan"/>
                <yearpublished value="1995"/>
            </item>
        </items>
        '''
        mock_request.return_value = ET.fromstring(xml_str)
        
        client = BGGApiClient()
        results = client.search("Catan")
        
        assert len(results) == 1
        assert results[0]['id'] == 13
        assert results[0]['name'] == "Catan"
        assert results[0]['year'] == 1995
    
    @patch.object(BGGApiClient, '_make_request')
    def test_search_no_results(self, mock_request):
        """測試搜尋無結果"""
        xml_str = '<items/>'
        mock_request.return_value = ET.fromstring(xml_str)
        
        client = BGGApiClient()
        results = client.search("nonexistent_game_xyz")
        
        assert results == []
    
    @patch.object(BGGApiClient, '_make_request')
    def test_search_failure(self, mock_request):
        """測試搜尋失敗"""
        mock_request.return_value = None
        
        client = BGGApiClient()
        results = client.search("test")
        
        assert results == []
    
    @patch.object(BGGApiClient, '_make_request')
    def test_search_exact(self, mock_request):
        """測試精確搜尋"""
        mock_request.return_value = ET.fromstring('<items/>')
        
        client = BGGApiClient()
        client.search("Catan", exact=True)
        
        # 確認呼叫參數
        call_args = mock_request.call_args
        assert call_args[0][0] == 'search'
        assert call_args[0][1]['exact'] == '1'


class TestBGGApiClientGame:
    """測試 game 方法"""
    
    @patch.object(BGGApiClient, '_make_request')
    def test_game_success(self, mock_request):
        """測試取得遊戲詳情成功"""
        xml_str = '''
        <items>
            <item id="13" type="boardgame">
                <name type="primary" value="Catan"/>
                <yearpublished value="1995"/>
                <description>A strategy game</description>
                <image>https://example.com/image.jpg</image>
                <minplayers value="3"/>
                <maxplayers value="4"/>
                <playingtime value="90"/>
                <statistics>
                    <ratings>
                        <average value="7.5"/>
                        <usersrated value="50000"/>
                    </ratings>
                </statistics>
            </item>
        </items>
        '''
        mock_request.return_value = ET.fromstring(xml_str)
        
        client = BGGApiClient()
        game = client.game(13)
        
        assert game is not None
        assert game['name'] == "Catan"
        assert game['year'] == 1995
        assert game['min_players'] == 3
        assert game['max_players'] == 4
    
    @patch.object(BGGApiClient, '_make_request')
    def test_game_not_found(self, mock_request):
        """測試遊戲不存在"""
        xml_str = '<items/>'
        mock_request.return_value = ET.fromstring(xml_str)
        
        client = BGGApiClient()
        game = client.game(99999999)
        
        assert game is None
    
    @patch.object(BGGApiClient, '_make_request')
    def test_game_failure(self, mock_request):
        """測試請求失敗"""
        mock_request.return_value = None
        
        client = BGGApiClient()
        game = client.game(13)
        
        assert game is None


class TestBGGApiClientHotItems:
    """測試 hot_items 方法"""
    
    @patch.object(BGGApiClient, '_make_request')
    def test_hot_items_success(self, mock_request):
        """測試熱門項目成功"""
        xml_str = '''
        <items>
            <item id="13" rank="1">
                <name value="Catan"/>
                <yearpublished value="1995"/>
                <thumbnail value="https://example.com/thumb.jpg"/>
            </item>
            <item id="14" rank="2">
                <name value="Wingspan"/>
                <yearpublished value="2019"/>
            </item>
        </items>
        '''
        mock_request.return_value = ET.fromstring(xml_str)
        
        client = BGGApiClient()
        items = client.hot_items()
        
        assert len(items) == 2
        assert items[0]['name'] == "Catan"
        assert items[0]['rank'] == 1
        assert items[1]['name'] == "Wingspan"
    
    @patch.object(BGGApiClient, '_make_request')
    def test_hot_items_empty(self, mock_request):
        """測試無熱門項目"""
        mock_request.return_value = ET.fromstring('<items/>')
        
        client = BGGApiClient()
        items = client.hot_items()
        
        assert items == []


class TestMakeRequest:
    """測試 _make_request 方法"""
    
    @patch('core.bgg_api_client.requests.Session')
    def test_make_request_success(self, mock_session_class):
        """測試請求成功"""
        mock_session = MagicMock()
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.content = b'<items/>'
        mock_session.get.return_value = mock_response
        mock_session_class.return_value = mock_session
        
        client = BGGApiClient()
        result = client._make_request('test')
        
        assert result is not None
    
    @patch('core.bgg_api_client.requests.Session')
    def test_make_request_401(self, mock_session_class):
        """測試 401 未授權"""
        mock_session = MagicMock()
        mock_response = MagicMock()
        mock_response.status_code = 401
        mock_session.get.return_value = mock_response
        mock_session_class.return_value = mock_session
        
        client = BGGApiClient()
        result = client._make_request('test')
        
        assert result is None
    
    @patch('core.bgg_api_client.requests.Session')
    def test_make_request_500(self, mock_session_class):
        """測試 500 錯誤"""
        mock_session = MagicMock()
        mock_response = MagicMock()
        mock_response.status_code = 500
        mock_session.get.return_value = mock_response
        mock_session_class.return_value = mock_session
        
        client = BGGApiClient()
        result = client._make_request('test')
        
        assert result is None
