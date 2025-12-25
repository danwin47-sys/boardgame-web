"""
效能監控 API
提供 Redis 統計、快取統計和系統資訊
"""
from flask import Blueprint, jsonify
from app.utils import error_response
from core.types import ResponseTuple
import logging
import sys
import os
from datetime import datetime

logger = logging.getLogger(__name__)

monitoring_bp = Blueprint("monitoring", __name__, url_prefix="/api/monitoring")


@monitoring_bp.route("/redis-stats", methods=["GET"])
def get_redis_stats():
    """獲取 Redis 統計資訊"""
    try:
        from core.redis_cache import RedisCache
        import os

        # 從環境變數獲取 Redis 配置
        redis_cache = RedisCache(
            host=os.getenv("REDIS_HOST", "localhost"),
            port=int(os.getenv("REDIS_PORT", 6379)),
            db=int(os.getenv("REDIS_DB", 0)),
            password=os.getenv("REDIS_PASSWORD"),
        )

        if not redis_cache.is_available():
            return (
                jsonify(
                    {"success": False, "error": "Redis 未連線", "fallback": "memory_cache"}
                ),
                503,
            )

        # 獲取 Redis 資訊
        info = redis_cache.client.info()

        stats = {
            "success": True,
            "connected": True,
            "version": info.get("redis_version", "unknown"),
            "uptime_seconds": info.get("uptime_in_seconds", 0),
            "connected_clients": info.get("connected_clients", 0),
            "used_memory": info.get("used_memory_human", "0"),
            "used_memory_peak": info.get("used_memory_peak_human", "0"),
            "total_keys": redis_cache.client.dbsize(),
            "keyspace_hits": info.get("keyspace_hits", 0),
            "keyspace_misses": info.get("keyspace_misses", 0),
            "timestamp": datetime.now().isoformat(),
        }

        # 計算命中率
        hits = stats["keyspace_hits"]
        misses = stats["keyspace_misses"]
        total = hits + misses
        stats["hit_rate"] = round((hits / total * 100), 2) if total > 0 else 0

        return jsonify(stats)

    except Exception as e:
        logger.error(f"獲取 Redis 統計失敗: {e}")
        return error_response(str(e), "MONITORING_ERROR", 500)


@monitoring_bp.route("/cache-stats", methods=["GET"])
def get_cache_stats():
    """獲取快取統計資訊"""
    try:
        from core.redis_cache import RedisCache
        import os

        redis_cache = RedisCache(
            host=os.getenv("REDIS_HOST", "localhost"),
            port=int(os.getenv("REDIS_PORT", 6379)),
            db=int(os.getenv("REDIS_DB", 0)),
            password=os.getenv("REDIS_PASSWORD"),
        )

        stats = {
            "success": True,
            "redis_available": redis_cache.is_available(),
            "cache_type": "redis" if redis_cache.is_available() else "memory",
            "timestamp": datetime.now().isoformat(),
        }

        if redis_cache.is_available():
            # Redis 快取統計
            info = redis_cache.client.info()
            stats["total_keys"] = redis_cache.client.dbsize()
            stats["keyspace_hits"] = info.get("keyspace_hits", 0)
            stats["keyspace_misses"] = info.get("keyspace_misses", 0)

            hits = stats["keyspace_hits"]
            misses = stats["keyspace_misses"]
            total = hits + misses
            stats["hit_rate"] = round((hits / total * 100), 2) if total > 0 else 0

            # 獲取快取鍵列表（限制 100 個）
            keys = redis_cache.client.keys("*")[:100]
            stats["sample_keys"] = [
                k.decode("utf-8") if isinstance(k, bytes) else k for k in keys
            ]
        else:
            stats["message"] = "使用記憶體快取（Redis 未連線）"

        return jsonify(stats)

    except Exception as e:
        logger.error(f"獲取快取統計失敗: {e}")
        return error_response(str(e), "MONITORING_ERROR", 500)


@monitoring_bp.route("/system-info", methods=["GET"])
def get_system_info():
    """獲取系統資訊"""
    try:
        import platform
        import psutil

        stats = {
            "success": True,
            "python_version": sys.version,
            "platform": platform.platform(),
            "processor": platform.processor(),
            "cpu_count": psutil.cpu_count(),
            "cpu_percent": psutil.cpu_percent(interval=1),
            "memory": {
                "total": f"{psutil.virtual_memory().total / (1024**3):.2f} GB",
                "available": f"{psutil.virtual_memory().available / (1024**3):.2f} GB",
                "percent": psutil.virtual_memory().percent,
            },
            "disk": {
                "total": f"{psutil.disk_usage('/').total / (1024**3):.2f} GB",
                "used": f"{psutil.disk_usage('/').used / (1024**3):.2f} GB",
                "percent": psutil.disk_usage("/").percent,
            },
            "timestamp": datetime.now().isoformat(),
        }

        return jsonify(stats)

    except Exception as e:
        logger.error(f"獲取系統資訊失敗: {e}")
        return (
            jsonify(
                {
                    "success": False,
                    "error": str(e),
                    "python_version": sys.version,
                    "platform": platform.platform(),
                }
            ),
            500,
        )


@monitoring_bp.route("/health", methods=["GET"])
def health_check():
    """健康檢查"""
    try:
        from core.redis_cache import RedisCache
        import os

        redis_cache = RedisCache(
            host=os.getenv("REDIS_HOST", "localhost"),
            port=int(os.getenv("REDIS_PORT", 6379)),
            db=int(os.getenv("REDIS_DB", 0)),
            password=os.getenv("REDIS_PASSWORD"),
        )

        health = {
            "success": True,
            "status": "healthy",
            "services": {
                "redis": "connected" if redis_cache.is_available() else "disconnected",
                "application": "running",
            },
            "timestamp": datetime.now().isoformat(),
        }

        return jsonify(health)

    except Exception as e:
        logger.error(f"健康檢查失敗: {e}")
        return error_response(str(e), "HEALTH_CHECK_ERROR", 500, details={"status": "unhealthy"})
