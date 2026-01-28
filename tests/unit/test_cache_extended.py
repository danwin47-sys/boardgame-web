"""
測試 core/cache.py 擴展測試
"""
import time
from unittest.mock import MagicMock, patch

import pytest

from core.cache import SimpleCache, cache_with_timeout


class TestCacheWithTimeout:
    """測試 cache_with_timeout 裝飾器"""

    def test_cache_hit(self):
        """測試快取命中"""
        call_count = 0

        @cache_with_timeout(60)
        def expensive_function():
            nonlocal call_count
            call_count += 1
            return "result"

        # 第一次呼叫
        result1 = expensive_function()
        assert call_count == 1

        # 第二次呼叫應該使用快取
        result2 = expensive_function()
        assert call_count == 1  # 沒有增加
        assert result1 == result2

    def test_cache_with_args(self):
        """測試帶參數的快取"""
        call_count = 0

        @cache_with_timeout(60)
        def function_with_args(x, y):
            nonlocal call_count
            call_count += 1
            return x + y

        result1 = function_with_args(1, 2)
        result2 = function_with_args(1, 2)  # 快取命中
        result3 = function_with_args(3, 4)  # 新參數

        assert call_count == 2
        assert result1 == 3
        assert result3 == 7

    def test_cache_with_kwargs(self):
        """測試帶關鍵字參數的快取"""

        @cache_with_timeout(60)
        def function_with_kwargs(name="default"):
            return f"Hello, {name}"

        result1 = function_with_kwargs(name="Alice")
        result2 = function_with_kwargs(name="Alice")  # 快取命中
        result3 = function_with_kwargs(name="Bob")  # 新參數

        assert result1 == "Hello, Alice"
        assert result3 == "Hello, Bob"

    def test_cache_on_method(self):
        """測試類別方法的快取"""

        class MyClass:
            call_count = 0

            @cache_with_timeout(60)
            def my_method(self):
                self.call_count += 1
                return "result"

        obj1 = MyClass()
        obj2 = MyClass()

        obj1.my_method()
        obj1.my_method()  # 快取命中
        obj2.my_method()  # 不同實例

        # 每個實例應該各自有快取
        assert obj1.call_count == 1
        assert obj2.call_count == 1


class TestSimpleCacheExtended:
    """SimpleCache 擴展測試"""

    def test_cache_ttl_zero(self):
        """測試 TTL 為 0 的快取（永遠過期）"""
        cache = SimpleCache(ttl=0)
        cache.set("data")

        time.sleep(0.01)
        assert cache.get() is None

    def test_cache_ttl_long(self):
        """測試長 TTL 的快取"""
        cache = SimpleCache(ttl=3600)
        cache.set("data")

        assert cache.get() == "data"
        assert cache.is_valid() is True

    def test_cache_multiple_set(self):
        """測試多次設置快取"""
        cache = SimpleCache(ttl=60)
        cache.set("first")
        cache.set("second")

        assert cache.get() == "second"

    def test_cache_none_value(self):
        """測試快取 None 值的行為"""
        cache = SimpleCache(ttl=60)
        cache.set(None)

        # None 值會被視為沒有快取
        assert cache.get() is None
