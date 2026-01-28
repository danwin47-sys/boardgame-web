# coding: utf-8
"""
快取模組
提供簡單的 TTL 快取功能
"""
import time
from functools import wraps
from typing import Any, Optional


class SimpleCache:
    """
    簡單的 TTL（Time To Live）快取

    用於暫存需要頻繁讀取但變化不大的資料
    """

    def __init__(self, ttl: int):
        """
        初始化快取

        Args:
            ttl: 快取存活時間（秒）
        """
        self.ttl = ttl
        self._data: Optional[Any] = None
        self._timestamp: float = 0

    def get(self) -> Optional[Any]:
        """
        取得快取資料（若未過期）

        Returns:
            快取的資料，若快取過期或為空則返回 None
        """
        if self._data is not None and (time.time() - self._timestamp < self.ttl):
            return self._data
        return None

    def set(self, data: Any) -> None:
        """
        設置快取資料

        Args:
            data: 要快取的資料
        """
        self._data = data
        self._timestamp = time.time()

    def invalidate(self) -> None:
        """使快取失效（清空快取）"""
        self._data = None
        self._timestamp = 0

    def is_valid(self) -> bool:
        """
        檢查快取是否有效

        Returns:
            bool: 快取是否仍在有效期內
        """
        return self._data is not None and (time.time() - self._timestamp < self.ttl)


# 全局快取字典用於裝飾器
_decorator_caches = {}


def cache_with_timeout(seconds: int):
    """
    函式快取裝飾器，使用 TTL 機制

    Args:
        seconds: 快取過期時間（秒）

    Returns:
        裝飾器函式
    """

    def decorator(func):
        cache_key = f"{func.__module__}.{func.__qualname__}"

        @wraps(func)
        def wrapper(*args, **kwargs):
            # 建立快取鍵（包含實例 hash 以區分不同實例）
            if args and hasattr(args[0], "__class__"):
                instance_key = f"{cache_key}_{id(args[0])}"
            else:
                instance_key = cache_key

            # 加入參數到快取鍵
            params_key = str(args[1:]) + str(sorted(kwargs.items()))
            full_key = f"{instance_key}_{params_key}"

            # 檢查快取
            if full_key not in _decorator_caches:
                _decorator_caches[full_key] = SimpleCache(seconds)

            cache = _decorator_caches[full_key]
            cached_result = cache.get()

            if cached_result is not None:
                return cached_result

            # 執行函式並快取結果
            result = func(*args, **kwargs)
            cache.set(result)
            return result

        return wrapper

    return decorator


# ============ Redis 快取支援 ============

_redis_cache_instance = None


def get_redis_cache():
    """
    取得 Redis 快取實例（單例模式）

    如果 Redis 不可用，返回 None

    Returns:
        RedisCache 實例或 None
    """
    global _redis_cache_instance

    if _redis_cache_instance is None:
        try:
            import os

            from core.redis_cache import RedisCache

            # 從環境變數讀取 Redis 配置
            redis_host = os.getenv("REDIS_HOST", "localhost")
            redis_port = int(os.getenv("REDIS_PORT", 6379))
            redis_db = int(os.getenv("REDIS_DB", 0))
            redis_password = os.getenv("REDIS_PASSWORD", None)

            _redis_cache_instance = RedisCache(
                host=redis_host,
                port=redis_port,
                db=redis_db,
                password=redis_password,
                ttl=300,  # 預設 5 分鐘
            )

            if not _redis_cache_instance.is_available():
                _redis_cache_instance = None

        except ImportError:
            # redis_cache 模組不存在
            _redis_cache_instance = None
        except Exception as e:
            import logging

            logging.warning(f"Redis 初始化失敗: {e}")
            _redis_cache_instance = None

    return _redis_cache_instance


def get_cache_backend(ttl=300):
    """
    取得快取後端（Redis 優先，降級到記憶體快取）

    Args:
        ttl: 快取存活時間（秒）

    Returns:
        快取實例（RedisCache 或 SimpleCache）
    """
    # 嘗試使用 Redis
    redis_cache = get_redis_cache()
    if redis_cache and redis_cache.is_available():
        return redis_cache

    # 降級到記憶體快取
    import logging

    logging.info("使用記憶體快取（Redis 不可用）")
    return SimpleCache(ttl)
