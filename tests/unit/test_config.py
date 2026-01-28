"""
測試應用程式配置模組
"""
import os

import pytest

from app.config import BaseConfig, DevelopmentConfig, ProductionConfig, TestingConfig, config


class TestConfig:
    """測試應用程式配置系統"""

    def test_config_dictionary(self):
        """測試配置字典包含所有環境"""
        assert "development" in config
        assert "testing" in config
        assert "production" in config
        assert "default" in config

    def test_base_config(self):
        """測試基礎配置"""
        assert hasattr(BaseConfig, "PORT")
        assert hasattr(BaseConfig, "HOST")
        assert hasattr(BaseConfig, "BGG_API_TOKEN")
        # PORT 從 .env 讀取為 5001，但在某些測試環境可能為 5000 或 5002 (E2E)
        assert BaseConfig.PORT in [5000, 5001, 5002]

    def test_development_config(self):
        """測試開發環境配置"""
        assert DevelopmentConfig.DEBUG == True
        assert DevelopmentConfig.TESTING == False
        assert DevelopmentConfig.LOG_LEVEL == "DEBUG"

    def test_testing_config(self):
        """測試測試環境配置"""
        assert TestingConfig.DEBUG == True
        assert TestingConfig.TESTING == True
        assert TestingConfig.DEMO_MODE == True
        # 測試環境應該沒有快取
        assert TestingConfig.GAMES_CACHE_TTL == 0

    def test_production_config(self):
        """測試生產環境配置"""
        assert ProductionConfig.DEBUG == False
        assert ProductionConfig.TESTING == False
        assert ProductionConfig.SESSION_COOKIE_SECURE == True

    def test_config_inheritance(self):
        """測試配置繼承"""
        # 所有配置都應該繼承自 BaseConfig
        assert issubclass(DevelopmentConfig, BaseConfig)
        assert issubclass(TestingConfig, BaseConfig)
        assert issubclass(ProductionConfig, BaseConfig)

    def test_get_config_summary(self):
        """測試取得配置摘要"""
        summary = BaseConfig.get_config_summary()
        assert isinstance(summary, dict)
        assert "DEMO_MODE" in summary
        assert "PORT" in summary
