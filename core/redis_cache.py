"""
Redis 快取服務

提供分散式快取支援，取代記憶體快取。
支援 TTL、鍵值對存取、模式匹配刪除等功能。

Author: Boardgame-Web Team
Date: 2025-12-21
"""

import redis
from typing import Any, Optional, Dict
import json
import logging
from functools import wraps

logger = logging.getLogger(__name__)


class RedisCache:
    """
    Redis 快取客戶端

    提供分散式快取功能，支援：
    - TTL (Time To Live) 過期機制
    - JSON 序列化/反序列化
    - 連線失敗降級（返回 None）
    - 模式匹配刪除
    """

    def __init__(
        self,
        host: str = "localhost",
        port: int = 6379,
        db: int = 0,
        ttl: int = 300,
        password: Optional[str] = None,
    ):
        """
        初始化 Redis 連線

        Args:
            host: Redis 主機位址
            port: Redis 埠號
            db: Redis 資料庫編號 (0-15)
            ttl: 預設存活時間（秒）
            password: Redis 密碼（可選）
        """
        self.ttl = ttl
        self.client = None

        try:
            self.client = redis.Redis(
                host=host,
                port=port,
                db=db,
                password=password,
                decode_responses=True,
                socket_connect_timeout=2,
                socket_timeout=2,
            )
            # 測試連線
            self.client.ping()
            logger.info(f"✅ Redis 連線成功: {host}:{port} (DB: {db})")
        except redis.ConnectionError as e:
            logger.warning(f"⚠️ Redis 連線失敗，降級使用記憶體快取: {e}")
            self.client = None
        except Exception as e:
            logger.error(f"❌ Redis 初始化錯誤: {e}")
            self.client = None

    def is_available(self) -> bool:
        """檢查 Redis 是否可用"""
        return self.client is not None

    def get(self, key: str) -> Optional[Any]:
        """
        取得快取資料

        Args:
            key: 快取鍵

        Returns:
            快取的資料，若不存在或過期則返回 None
        """
        if not self.client:
            return None

        try:
            data = self.client.get(key)
            if data is None:
                return None

            # JSON 反序列化
            return json.loads(data)
        except json.JSONDecodeError as e:
            logger.error(f"❌ JSON 解析錯誤 (key: {key}): {e}")
            # 刪除損壞的快取
            self.delete(key)
            return None
        except Exception as e:
            logger.error(f"❌ Redis get 錯誤 (key: {key}): {e}")
            return None

    def set(self, key: str, value: Any, ttl: Optional[int] = None) -> bool:
        """
        設置快取資料

        Args:
            key: 快取鍵
            value: 要快取的資料（會自動 JSON 序列化）
            ttl: 存活時間（秒），若為 None 則使用預設值

        Returns:
            是否成功設置
        """
        if not self.client:
            return False

        try:
            ttl = ttl or self.ttl
            serialized = json.dumps(value, ensure_ascii=False)
            self.client.setex(key, ttl, serialized)
            logger.debug(f"✅ Redis set: {key} (TTL: {ttl}s)")
            return True
        except (TypeError, ValueError) as e:
            logger.error(f"❌ JSON 序列化錯誤 (key: {key}): {e}")
            return False
        except Exception as e:
            logger.error(f"❌ Redis set 錯誤 (key: {key}): {e}")
            return False

    def delete(self, key: str) -> bool:
        """
        刪除快取

        Args:
            key: 快取鍵

        Returns:
            是否成功刪除
        """
        if not self.client:
            return False

        try:
            self.client.delete(key)
            logger.debug(f"🗑️ Redis delete: {key}")
            return True
        except Exception as e:
            logger.error(f"❌ Redis delete 錯誤 (key: {key}): {e}")
            return False

    def clear_pattern(self, pattern: str) -> int:
        """
        清除符合模式的所有快取

        Args:
            pattern: 鍵的模式（支援 * 萬用字元）
                    例如: "games:*", "bgg:*"

        Returns:
            刪除的鍵數量
        """
        if not self.client:
            return 0

        try:
            keys = self.client.keys(pattern)
            if keys:
                deleted = self.client.delete(*keys)
                logger.info(f"🗑️ Redis 清除模式 '{pattern}': {deleted} 個鍵")
                return deleted
            return 0
        except Exception as e:
            logger.error(f"❌ Redis clear_pattern 錯誤 (pattern: {pattern}): {e}")
            return 0

    def exists(self, key: str) -> bool:
        """
        檢查鍵是否存在

        Args:
            key: 快取鍵

        Returns:
            是否存在
        """
        if not self.client:
            return False

        try:
            return self.client.exists(key) > 0
        except Exception as e:
            logger.error(f"❌ Redis exists 錯誤 (key: {key}): {e}")
            return False

    def get_ttl(self, key: str) -> int:
        """
        取得鍵的剩餘存活時間

        Args:
            key: 快取鍵

        Returns:
            剩餘秒數，-1 表示永久，-2 表示不存在
        """
        if not self.client:
            return -2

        try:
            return self.client.ttl(key)
        except Exception as e:
            logger.error(f"❌ Redis get_ttl 錯誤 (key: {key}): {e}")
            return -2

    def get_stats(self) -> Dict[str, Any]:
        """
        取得 Redis 統計資訊

        Returns:
            統計資訊字典
        """
        if not self.client:
            return {"available": False}

        try:
            info = self.client.info()
            return {
                "available": True,
                "connected_clients": info.get("connected_clients", 0),
                "used_memory_human": info.get("used_memory_human", "N/A"),
                "total_keys": self.client.dbsize(),
                "uptime_in_seconds": info.get("uptime_in_seconds", 0),
            }
        except Exception as e:
            logger.error(f"❌ Redis get_stats 錯誤: {e}")
            return {"available": False, "error": str(e)}


def redis_cache_decorator(
    key_prefix: str, ttl: int = 300, redis_client: Optional[RedisCache] = None
):
    """
    Redis 快取裝飾器

    自動快取函數結果到 Redis。

    Args:
        key_prefix: 快取鍵前綴
        ttl: 存活時間（秒）
        redis_client: Redis 客戶端實例（可選）

    Example:
        @redis_cache_decorator("bgg_game", ttl=3600)
        def get_game_details(game_id):
            # 昂貴的操作
            return fetch_from_api(game_id)
    """

    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # 如果沒有提供 redis_client，嘗試從全域取得
            client = redis_client
            if client is None:
                try:
                    from core.cache import get_redis_cache

                    client = get_redis_cache()
                except ImportError:
                    # 降級：直接執行函數
                    return func(*args, **kwargs)

            if not client or not client.is_available():
                # Redis 不可用，直接執行函數
                return func(*args, **kwargs)

            # 生成快取鍵（包含參數）
            cache_key = f"{key_prefix}:{args}:{kwargs}"

            # 嘗試從快取取得
            cached = client.get(cache_key)
            if cached is not None:
                logger.debug(f"🎯 快取命中: {cache_key}")
                return cached

            # 執行函數
            result = func(*args, **kwargs)

            # 儲存到快取
            client.set(cache_key, result, ttl)

            return result

        return wrapper

    return decorator
