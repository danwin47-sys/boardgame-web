"""
測試 app/blueprints/api/monitoring.py 模組
"""
import pytest
from unittest.mock import MagicMock, patch
import json


class TestMonitoringHealth:
    """測試 health_check 端點"""
    
    @patch('app.blueprints.api.monitoring.RedisCache')
    def test_health_check_redis_connected(self, mock_redis_class, client):
        """測試健康檢查 - Redis 已連線"""
        mock_cache = MagicMock()
        mock_cache.is_available.return_value = True
        mock_redis_class.return_value = mock_cache
        
        response = client.get('/api/monitoring/health')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['success'] is True
        assert data['status'] == 'healthy'
        assert data['services']['redis'] == 'connected'
        assert data['services']['application'] == 'running'
    
    @patch('app.blueprints.api.monitoring.RedisCache')
    def test_health_check_redis_disconnected(self, mock_redis_class, client):
        """測試健康檢查 - Redis 未連線"""
        mock_cache = MagicMock()
        mock_cache.is_available.return_value = False
        mock_redis_class.return_value = mock_cache
        
        response = client.get('/api/monitoring/health')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['success'] is True
        assert data['services']['redis'] == 'disconnected'
    
    @patch('app.blueprints.api.monitoring.RedisCache')
    def test_health_check_error(self, mock_redis_class, client):
        """測試健康檢查 - 錯誤"""
        mock_redis_class.side_effect = Exception("Connection error")
        
        response = client.get('/api/monitoring/health')
        
        assert response.status_code == 500
        data = json.loads(response.data)
        assert data['success'] is False
        assert data['status'] == 'unhealthy'


class TestMonitoringRedisStats:
    """測試 get_redis_stats 端點"""
    
    @patch('app.blueprints.api.monitoring.RedisCache')
    def test_redis_stats_success(self, mock_redis_class, client):
        """測試 Redis 統計 - 成功"""
        mock_cache = MagicMock()
        mock_cache.is_available.return_value = True
        mock_cache.client.info.return_value = {
            'redis_version': '6.2.0',
            'uptime_in_seconds': 86400,
            'connected_clients': 5,
            'used_memory_human': '1.5M',
            'used_memory_peak_human': '2.0M',
            'keyspace_hits': 1000,
            'keyspace_misses': 100,
        }
        mock_cache.client.dbsize.return_value = 50
        mock_redis_class.return_value = mock_cache
        
        response = client.get('/api/monitoring/redis-stats')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['success'] is True
        assert data['connected'] is True
        assert data['version'] == '6.2.0'
        assert data['total_keys'] == 50
        assert 'hit_rate' in data
    
    @patch('app.blueprints.api.monitoring.RedisCache')
    def test_redis_stats_not_available(self, mock_redis_class, client):
        """測試 Redis 統計 - Redis 未連線"""
        mock_cache = MagicMock()
        mock_cache.is_available.return_value = False
        mock_redis_class.return_value = mock_cache
        
        response = client.get('/api/monitoring/redis-stats')
        
        assert response.status_code == 503
        data = json.loads(response.data)
        assert data['success'] is False
        assert data['error'] == 'Redis 未連線'
    
    @patch('app.blueprints.api.monitoring.RedisCache')
    def test_redis_stats_error(self, mock_redis_class, client):
        """測試 Redis 統計 - 錯誤"""
        mock_redis_class.side_effect = Exception("Connection failed")
        
        response = client.get('/api/monitoring/redis-stats')
        
        assert response.status_code == 500
        data = json.loads(response.data)
        assert data['success'] is False


class TestMonitoringCacheStats:
    """測試 get_cache_stats 端點"""
    
    @patch('app.blueprints.api.monitoring.RedisCache')
    def test_cache_stats_redis_available(self, mock_redis_class, client):
        """測試快取統計 - Redis 可用"""
        mock_cache = MagicMock()
        mock_cache.is_available.return_value = True
        mock_cache.client.info.return_value = {
            'keyspace_hits': 2000,
            'keyspace_misses': 200,
        }
        mock_cache.client.dbsize.return_value = 100
        mock_cache.client.keys.return_value = [b'key1', b'key2']
        mock_redis_class.return_value = mock_cache
        
        response = client.get('/api/monitoring/cache-stats')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['success'] is True
        assert data['redis_available'] is True
        assert data['cache_type'] == 'redis'
        assert data['total_keys'] == 100
        assert 'hit_rate' in data
        assert 'sample_keys' in data
    
    @patch('app.blueprints.api.monitoring.RedisCache')
    def test_cache_stats_redis_unavailable(self, mock_redis_class, client):
        """測試快取統計 - Redis 不可用"""
        mock_cache = MagicMock()
        mock_cache.is_available.return_value = False
        mock_redis_class.return_value = mock_cache
        
        response = client.get('/api/monitoring/cache-stats')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['success'] is True
        assert data['redis_available'] is False
        assert data['cache_type'] == 'memory'
        assert 'message' in data
    
    @patch('app.blueprints.api.monitoring.RedisCache')
    def test_cache_stats_error(self, mock_redis_class, client):
        """測試快取統計 - 錯誤"""
        mock_redis_class.side_effect = Exception("Failed")
        
        response = client.get('/api/monitoring/cache-stats')
        
        assert response.status_code == 500
        data = json.loads(response.data)
        assert data['success'] is False


class TestMonitoringSystemInfo:
    """測試 get_system_info 端點"""
    
    @patch('app.blueprints.api.monitoring.psutil')
    def test_system_info_success(self, mock_psutil, client):
        """測試系統資訊 - 成功"""
        # Mock psutil
        mock_psutil.cpu_count.return_value = 4
        mock_psutil.cpu_percent.return_value = 25.5
        
        mock_vm = MagicMock()
        mock_vm.total = 8 * 1024**3  # 8 GB
        mock_vm.available = 4 * 1024**3  # 4 GB
        mock_vm.percent = 50.0
        mock_psutil.virtual_memory.return_value = mock_vm
        
        mock_disk = MagicMock()
        mock_disk.total = 500 * 1024**3  # 500 GB
        mock_disk.used = 250 * 1024**3  # 250 GB
        mock_disk.percent = 50.0
        mock_psutil.disk_usage.return_value = mock_disk
        
        response = client.get('/api/monitoring/system-info')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['success'] is True
        assert 'python_version' in data
        assert 'platform' in data
        assert data['cpu_count'] == 4
        assert data['cpu_percent'] == 25.5
        assert 'memory' in data
        assert 'disk' in data
    
    @patch('app.blueprints.api.monitoring.psutil')
    def test_system_info_error(self, mock_psutil, client):
        """測試系統資訊 - 錯誤"""
        mock_psutil.cpu_count.side_effect = Exception("System error")
        
        response = client.get('/api/monitoring/system-info')
        
        assert response.status_code == 500
        data = json.loads(response.data)
        assert data['success'] is False
        assert 'error' in data
        # 即使錯誤，也應該有基本資訊
        assert 'python_version' in data
        assert 'platform' in data
