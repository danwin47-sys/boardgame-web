import pytest
import requests
from unittest.mock import MagicMock, patch
from core.bgg_api_client import BGGApiClient
import xml.etree.ElementTree as ET

class TestBGGApiClientExtended:
    """針對 BGGApiClient 剩餘覆蓋率缺口的延伸測試"""

    def setup_method(self):
        self.client = BGGApiClient(retries=0)

    @patch('requests.Session.get')
    def test_make_request_non_200_status(self, mock_get):
        """測試 API 返回非 200 且非 429 的狀態碼 (L87-88)"""
        mock_response = MagicMock()
        mock_response.status_code = 500
        mock_get.return_value = mock_response
        
        result = self.client._make_request("thing", {"id": 1})
        assert result is None

    @patch('requests.Session.get')
    def test_make_request_generic_exception(self, mock_get):
        """測試發送請求時發生泛型異常 (L106-112)"""
        mock_get.side_effect = requests.exceptions.RequestException("Connection error")
        
        result = self.client._make_request("thing", {"id": 1})
        assert result is None

    @patch('core.bgg_api_client.BGGApiClient._make_request')
    def test_search_parsing_error(self, mock_make_request):
        """測試搜尋結果解析時發生錯誤 (L154-156)"""
        # 建立一個會引發 ValueError 的 XML (年份為非法字串)
        xml_str = '''
        <items>
            <item id="1">
                <name value="Catan" />
                <yearpublished value="abc" />
            </item>
        </items>
        '''
        mock_make_request.return_value = ET.fromstring(xml_str)
        
        # 解析應會跳過該項目並記錄警告
        results = self.client.search("Catan")
        assert len(results) == 0

    @patch('core.bgg_api_client.BGGApiClient._make_request')
    def test_game_details_fallback_name(self, mock_make_request):
        """測試當無初級名稱時的 Fallback 名稱解析 (L193-194)"""
        xml_str = '''
        <items>
            <item id="1">
                <name type="alternate" value="Second Name" />
            </item>
        </items>
        '''
        mock_make_request.return_value = ET.fromstring(xml_str)
        
        details = self.client.game(1)
        assert details['name'] == 'Second Name'

    @patch('core.bgg_api_client.BGGApiClient._make_request')
    def test_game_details_parsing_exception(self, mock_make_request):
        """測試遊戲詳情解析時發生異常 (L375-377)"""
        # 提供一個缺少關鍵欄位導致 int() 轉換失敗的 XML
        xml_str = '<items><item id="abc"></item></items>'
        mock_make_request.return_value = ET.fromstring(xml_str)
        
        details = self.client.game(1)
        assert details is None

    @patch('core.bgg_api_client.BGGApiClient._make_request')
    def test_hot_items_parsing_error(self, mock_make_request):
        """測試熱門項目解析異常 (L422-424)"""
        # id="invalid" 會導致 int(item.get("id")) 拋出 ValueError
        xml_str = '<items><item id="invalid"></item></items>'
        mock_make_request.return_value = ET.fromstring(xml_str)
        
        items = self.client.hot_items()
        assert len(items) == 0

class TestLoggingConfig:
    """測試 core/logging_config.py"""
    
    def test_setup_logging_production(self):
        """測試生產環境下的日誌設定"""
        from core.logging_config import setup_logging
        # 傳入正確的字串參數
        setup_logging(level="INFO", simple_format=True)

    def test_setup_logging_with_file(self, tmp_path):
        """測試帶有檔案輸出的日誌設定"""
        log_file = tmp_path / "test.log"
        from core.logging_config import setup_logging
        setup_logging(level="DEBUG", log_file=str(log_file))
        assert log_file.exists()

    def test_get_logger(self):
        """測試 get_logger 函式"""
        from core.logging_config import get_logger
        logger = get_logger("test_logger")
        assert logger.name == "test_logger"
