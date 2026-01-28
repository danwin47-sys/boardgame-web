import json
import sys
from unittest.mock import MagicMock, patch

# Mock redis and psutil modules before importing core.redis_cache or patching
sys.modules["redis"] = MagicMock()
sys.modules["psutil"] = MagicMock()
import core.redis_cache


class TestMonitoringAPI:
    """測試 Monitoring API"""

    @patch("core.redis_cache.RedisCache")
    def test_redis_stats_connected(self, mock_redis_class, client):
        """測試 Redis 統計 - 已連線"""
        mock_cache = MagicMock()
        mock_cache.is_available.return_value = True
        mock_cache.client.info.return_value = {
            "redis_version": "6.0.0",
            "uptime_in_seconds": 3600,
            "connected_clients": 10,
            "used_memory_human": "10M",
            "used_memory_peak_human": "12M",
            "keyspace_hits": 100,
            "keyspace_misses": 10,
        }
        mock_cache.client.dbsize.return_value = 50
        mock_redis_class.return_value = mock_cache

        response = client.get("/api/monitoring/redis-stats")

        assert response.status_code == 200
        data = json.loads(response.data)
        assert data["success"] is True
        assert data["version"] == "6.0.0"
        # 命中率 100 / 110 * 100 = 90.91
        assert data["hit_rate"] == 90.91

    @patch("core.redis_cache.RedisCache")
    def test_redis_stats_disconnected(self, mock_redis_class, client):
        """測試 Redis 統計 - 未連線"""
        mock_cache = MagicMock()
        mock_cache.is_available.return_value = False
        mock_redis_class.return_value = mock_cache

        response = client.get("/api/monitoring/redis-stats")

        assert response.status_code == 503
        data = json.loads(response.data)
        assert data["success"] is False
        assert "未連線" in data["error"]

    @patch("core.redis_cache.RedisCache")
    def test_cache_stats_redis(self, mock_redis_class, client):
        """測試快取統計 - 使用 Redis"""
        mock_cache = MagicMock()
        mock_cache.is_available.return_value = True
        mock_cache.client.info.return_value = {
            "keyspace_hits": 200,
            "keyspace_misses": 50,
        }
        mock_cache.client.dbsize.return_value = 150
        mock_cache.client.keys.return_value = [b"key1", b"key2"]
        mock_redis_class.return_value = mock_cache

        response = client.get("/api/monitoring/cache-stats")

        assert response.status_code == 200
        data = json.loads(response.data)
        assert data["success"] is True
        assert data["cache_type"] == "redis"
        assert data["total_keys"] == 150
        assert len(data["sample_keys"]) > 0

    @patch("core.redis_cache.RedisCache")
    def test_cache_stats_memory(self, mock_redis_class, client):
        """測試快取統計 - 使用記憶體"""
        mock_cache = MagicMock()
        mock_cache.is_available.return_value = False
        mock_redis_class.return_value = mock_cache

        response = client.get("/api/monitoring/cache-stats")

        assert response.status_code == 200
        data = json.loads(response.data)
        assert data["success"] is True
        assert data["cache_type"] == "memory"

    @patch("psutil.cpu_count")
    @patch("psutil.cpu_percent")
    @patch("psutil.virtual_memory")
    @patch("psutil.disk_usage")
    def test_system_info(
        self, mock_disk, mock_mem, mock_cpu_pct, mock_cpu_count, client
    ):
        """測試系統資訊"""
        mock_cpu_count.return_value = 8
        mock_cpu_pct.return_value = 45.5

        mock_disk_obj = MagicMock()
        mock_disk_obj.total = 1000 * 1024**3
        mock_disk_obj.used = 500 * 1024**3
        mock_disk_obj.percent = 50.0
        mock_disk.return_value = mock_disk_obj

        mock_mem_obj = MagicMock()
        mock_mem_obj.total = 16 * 1024**3
        mock_mem_obj.available = 8 * 1024**3
        mock_mem_obj.percent = 50.0
        mock_mem.return_value = mock_mem_obj

        response = client.get("/api/monitoring/system-info")

        assert response.status_code == 200
        data = json.loads(response.data)
        assert data["success"] is True
        assert data["cpu_count"] == 8
        assert data["cpu_percent"] == 45.5
        assert "python_version" in data

    @patch("core.redis_cache.RedisCache")
    def test_health_check_healthy(self, mock_redis_class, client):
        """測試健康檢查 - 健康"""
        mock_cache = MagicMock()
        mock_cache.is_available.return_value = True
        mock_redis_class.return_value = mock_cache

        response = client.get("/api/monitoring/health")

        assert response.status_code == 200
        data = json.loads(response.data)
        assert data["status"] == "healthy"
        assert data["services"]["redis"] == "connected"

    @patch("core.redis_cache.RedisCache")
    def test_health_check_error(self, mock_redis_class, client):
        """測試健康檢查 - 發生例外"""
        mock_redis_class.side_effect = Exception("Critical failure")

        response = client.get("/api/monitoring/health")

        assert response.status_code == 500
        data = json.loads(response.data)
        assert data["success"] is False
        assert data["status"] == "unhealthy"
