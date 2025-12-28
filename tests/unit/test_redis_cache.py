"""
測試 core/redis_cache.py 模組
"""
import pytest
import sys
import json
from unittest.mock import MagicMock, patch

# Mock redis module to ensure core.redis_cache can be imported
mock_redis = MagicMock()
class MockConnectionError(Exception): pass
mock_redis.ConnectionError = MockConnectionError
sys.modules['redis'] = mock_redis

# 由於 redis 是可選依賴，但我們現在已經 mock 了它，所以可以安全導入
from core.redis_cache import RedisCache
REDIS_AVAILABLE = True


@pytest.mark.skipif(not REDIS_AVAILABLE, reason="Redis not available")
class TestRedisCacheInit:
    """測試初始化"""
    
    @patch('core.redis_cache.redis')
    def test_init_success(self, mock_redis):
        """測試初始化成功"""
        # ... setup skipped, assuming method body is mostly fine or handled by class structure
        # But wait, replace_file_content replaces the BLOCK.
        # I cannot replace disjoint blocks easily without multi_replace.
        pass

# I need to use MULTI_REPLACE because errors are scattered.
REDIS_AVAILABLE = True


@pytest.mark.skipif(not REDIS_AVAILABLE, reason="Redis not available")
class TestRedisCacheInit:
    """測試初始化"""
    
    @patch('core.redis_cache.redis')
    def test_init_success(self, mock_redis):
        """測試成功初始化"""
        mock_client = MagicMock()
        mock_redis.Redis.return_value = mock_client
        
        cache = RedisCache(host='localhost', port=6379)
        
        assert cache.client == mock_client
        mock_redis.Redis.assert_called_once()
    
    @patch('core.redis_cache.redis')
    def test_init_connection_error(self, mock_redis):
        """測試連接失敗"""
        # 確保 ConnectionError 是例外類別
        class MockConnectionError(Exception): pass
        mock_redis.ConnectionError = MockConnectionError
        mock_redis.Redis.side_effect = MockConnectionError("Connection failed")
        
        cache = RedisCache()
        
        assert cache.client is None


class TestRedisCacheSetGet:
    """測試 set 和 get 方法"""
    
    def setup_method(self):
        self.mock_client = MagicMock()
        
        with patch('core.redis_cache.redis') as mock_redis:
            mock_redis.Redis.return_value = self.mock_client
            self.cache = RedisCache()
            self.cache.client = self.mock_client
    
    def test_set_get_string(self):
        """測試設定和取得字串"""
        self.mock_client.setex.return_value = True
        self.mock_client.get.return_value = b'"test_value"'
        
        result = self.cache.set('test_key', 'test_value', ttl=300)
        assert result is True
        
        value = self.cache.get('test_key')
        assert value == 'test_value'
    
    def test_set_get_dict(self):
        """測試設定和取得字典"""
        test_data = {'name': 'Catan', 'players': '3-4'}
        self.mock_client.setex.return_value = True
        self.mock_client.get.return_value = json.dumps(test_data).encode()
        
        self.cache.set('game:1', test_data)
        value = self.cache.get('game:1')
        
        assert value == test_data
    
    def test_get_not_found(self):
        """測試取得不存在的鍵"""
        self.mock_client.get.return_value = None
        
        value = self.cache.get('nonexistent')
        
        assert value is None
    
    def test_set_connection_error(self):
        """測試設定時連接錯誤"""
        self.mock_client.setex.side_effect = Exception("Connection lost")
        
        result = self.cache.set('key', 'value')
        
        assert result is False
    
    def test_get_connection_error(self):
        """測試取得時連接錯誤"""
        self.mock_client.get.side_effect = Exception("Connection lost")
        
        value = self.cache.get('key')
        
        assert value is None


@pytest.mark.skipif(not REDIS_AVAILABLE, reason="Redis not available")
class TestRedisCacheDelete:
    """測試 delete 方法"""
    
    def setup_method(self):
        self.mock_client = MagicMock()
        
        with patch('core.redis_cache.redis') as mock_redis:
            mock_redis.Redis.return_value = self.mock_client
            self.cache = RedisCache()
            self.cache.client = self.mock_client
    
    def test_delete_success(self):
        """測試成功刪除"""
        self.mock_client.delete.return_value = 1
        
        result = self.cache.delete('test_key')
        
        assert result is True
        self.mock_client.delete.assert_called_with('test_key')
    
    def test_delete_not_found(self):
        """測試刪除不存在的鍵"""
        self.mock_client.delete.return_value = 0
        
        result = self.cache.delete('nonexistent')
        
        assert result is True
    
    def test_delete_error(self):
        """測試刪除時錯誤"""
        self.mock_client.delete.side_effect = Exception("Connection lost")
        
        result = self.cache.delete('key')
        
        assert result is False


@pytest.mark.skipif(not REDIS_AVAILABLE, reason="Redis not available")
class TestRedisCacheExists:
    """測試 exists 方法"""
    
    def setup_method(self):
        self.mock_client = MagicMock()
        
        with patch('core.redis_cache.redis') as mock_redis:
            mock_redis.Redis.return_value = self.mock_client
            self.cache = RedisCache()
            self.cache.client = self.mock_client
    
    def test_exists_true(self):
        """測試鍵存在"""
        self.mock_client.exists.return_value = 1
        
        result = self.cache.exists('test_key')
        
        assert result is True
    
    def test_exists_false(self):
        """測試鍵不存在"""
        self.mock_client.exists.return_value = 0
        
        result = self.cache.exists('nonexistent')
        
        assert result is False
    
    def test_exists_error(self):
        """測試檢查時錯誤"""
        self.mock_client.exists.side_effect = Exception("Connection lost")
        
        result = self.cache.exists('key')
        
        assert result is False


@pytest.mark.skipif(not REDIS_AVAILABLE, reason="Redis not available")
class TestRedisCacheClear:
    """測試 clear 方法"""
    
    def setup_method(self):
        self.mock_client = MagicMock()
        
        with patch('core.redis_cache.redis') as mock_redis:
            mock_redis.Redis.return_value = self.mock_client
            self.cache = RedisCache()
            self.cache.client = self.mock_client
    
    def test_clear_pattern(self):
        """測試按模式清除"""
        self.mock_client.keys.return_value = [b'user:1', b'user:2']
        self.mock_client.delete.return_value = 2
        
        result = self.cache.clear_pattern('user:*')
        
        assert result == 2
        self.mock_client.keys.assert_called_with('user:*')
    
    def test_clear_no_match(self):
        """測試清除無匹配"""
        self.mock_client.keys.return_value = []
        
        result = self.cache.clear_pattern('nonexistent:*')
        
        assert result == 0  # 沒有匹配也算成功，回傳 0
    
        assert result == 0


class TestRedisCacheAdvanced:
    """測試 RedisCache 的進階功能"""
    
    def setup_method(self):
        self.mock_client = MagicMock()
        with patch('core.redis_cache.redis') as mock_redis:
            mock_redis.Redis.return_value = self.mock_client
            self.cache = RedisCache()
            self.cache.client = self.mock_client

    def test_ttl_success(self):
        """測試取得鍵的 TTL"""
        self.mock_client.ttl.return_value = 3600
        assert self.cache.get_ttl('test_key') == 3600
        
    def test_get_stats_success(self):
        """測試取得統計資訊"""
        self.mock_client.info.return_value = {'used_memory_human': '1KB', 'connected_clients': 5}
        self.mock_client.dbsize.return_value = 10
        
        stats = self.cache.get_stats()
        assert stats['used_memory_human'] == '1KB'
        assert stats['total_keys'] == 10
