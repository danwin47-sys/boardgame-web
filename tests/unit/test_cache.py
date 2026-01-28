"""
測試快取模組
"""
import time
from unittest.mock import patch

import pytest

from core.cache import SimpleCache


class TestSimpleCache:
    """測試 core/cache.py 中的快取功能"""

    def test_cache_set_and_get(self):
        """測試快取設定和取得"""
        cache = SimpleCache(ttl=10)
        cache.set("test_value")

        value = cache.get()
        assert value == "test_value"

    def test_cache_expiration(self):
        """測試快取過期"""
        cache = SimpleCache(ttl=1)  # 1 秒 TTL
        cache.set("test_value")

        # 立即取得應該有值
        assert cache.get() == "test_value"

        # 等待過期
        time.sleep(1.5)

        # 應該已過期
        assert cache.get() is None

    def test_cache_invalidate(self):
        """測試快取失效"""
        cache = SimpleCache(ttl=10)
        cache.set("test_value")
        cache.invalidate()

        assert cache.get() is None

    def test_cache_is_valid(self):
        """測試快取有效性檢查"""
        cache = SimpleCache(ttl=10)

        # 未設定時應無效
        assert cache.is_valid() == False

        cache.set("test_value")
        assert cache.is_valid() == True


def test_cache_with_timeout_decorator():
    """測試 cache_with_timeout 裝飾器"""
    from core.cache import cache_with_timeout

    call_count = 0

    @cache_with_timeout(60)
    def cached_func(x):
        nonlocal call_count
        call_count += 1
        return x * 2

    # 第一次執行
    assert cached_func(5) == 10
    assert call_count == 1

    # 第二次執行（應命中快取）
    assert cached_func(5) == 10
    assert call_count == 1


def test_get_redis_cache_logic():
    """測試獲取 Redis 快取的邏輯"""
    from core.cache import SimpleCache, get_redis_cache
    from core.redis_cache import RedisCache

    # 這裡我們主要驗證是否能正常呼叫且不拋出未捕獲異常
    cache = get_redis_cache()
    # 在測試環境中可能會回傳 SimpleCache (Fallback) 或 RedisCache
    assert isinstance(cache, (SimpleCache, RedisCache))


def test_get_redis_cache_error_handling():
    """測試 get_redis_cache 發生異常時的處理"""
    import core.cache
    from core.cache import get_redis_cache

    # 模擬 RedisCache 初始化時拋出異常
    with patch("core.redis_cache.RedisCache", side_effect=Exception("Epic fail")):
        # 清除單例狀態
        core.cache._redis_cache_instance = None
        cache = get_redis_cache()
        assert cache is None


def test_get_cache_backend_fallback():
    """測試 get_cache_backend 當 Redis 不可用時的降級邏輯"""
    from core.cache import SimpleCache, get_cache_backend

    with patch("core.cache.get_redis_cache", return_value=None):
        cache = get_cache_backend(ttl=123)
        assert isinstance(cache, SimpleCache)
        assert cache.ttl == 123
