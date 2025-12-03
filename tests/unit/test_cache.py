"""
測試快取模組
"""
import pytest
import time
from core.cache import SimpleCache


class TestSimpleCache:
    """測試 core/cache.py 中的快取功能"""
    
    def test_cache_set_and_get(self):
        """測試快取設定和取得"""
        cache = SimpleCache(ttl=10)
        cache.set('test_value')
        
        value = cache.get()
        assert value == 'test_value'
    
    def test_cache_expiration(self):
        """測試快取過期"""
        cache = SimpleCache(ttl=1)  # 1 秒 TTL
        cache.set('test_value')
        
        # 立即取得應該有值
        assert cache.get() == 'test_value'
        
        # 等待過期
        time.sleep(1.5)
        
        # 應該已過期
        assert cache.get() is None
    
    def test_cache_invalidate(self):
        """測試快取失效"""
        cache = SimpleCache(ttl=10)
        cache.set('test_value')
        cache.invalidate()
        
        assert cache.get() is None
    
    def test_cache_is_valid(self):
        """測試快取有效性檢查"""
        cache = SimpleCache(ttl=10)
        
        # 未設定時應無效
        assert cache.is_valid() == False
        
        # 設定後應有效
        cache.set('test_value')
        assert cache.is_valid() == True
