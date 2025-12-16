"""
測試 app/config 模組
"""
import pytest
import os


class TestProductionConfig:
    """測試生產環境配置"""
    
    def test_production_config_load(self):
        """測試生產環境配置載入"""
        from app.config.production import ProductionConfig
        
        assert ProductionConfig.DEBUG is False
        assert ProductionConfig.TESTING is False
    
    def test_production_config_demo_mode(self):
        """測試演示模式設定"""
        from app.config.production import ProductionConfig
        
        # DEMO_MODE 預設應該存在
        assert hasattr(ProductionConfig, 'DEMO_MODE')


class TestDevelopmentConfig:
    """測試開發環境配置"""
    
    def test_development_config_load(self):
        """測試開發環境配置載入"""
        from app.config.development import DevelopmentConfig
        
        assert DevelopmentConfig.DEBUG is True
    
    def test_development_config_has_demo_mode(self):
        """測試 DEMO_MODE 屬性存在"""
        from app.config.development import DevelopmentConfig
        
        assert hasattr(DevelopmentConfig, 'DEMO_MODE')


class TestTestingConfig:
    """測試測試環境配置"""
    
    def test_testing_config_load(self):
        """測試測試環境配置載入"""
        from app.config.testing import TestingConfig
        
        assert TestingConfig.TESTING is True
    
    def test_testing_config_demo_mode(self):
        """測試演示模式設定"""
        from app.config.testing import TestingConfig
        
        assert TestingConfig.DEMO_MODE is True


class TestBaseConfig:
    """測試基礎配置"""
    
    def test_base_config_attributes(self):
        """測試基礎配置屬性"""
        from app.config.base import BaseConfig
        
        assert hasattr(BaseConfig, 'SECRET_KEY')
        assert hasattr(BaseConfig, 'DEMO_MODE')
    
    def test_config_factory(self):
        """測試配置工廠"""
        from app.config import config
        
        assert 'testing' in config
        assert 'development' in config
        assert 'production' in config

