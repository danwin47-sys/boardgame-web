"""
應用程式配置模組
支援多環境配置：開發、測試、生產
"""
from .base import BaseConfig
from .development import DevelopmentConfig
from .testing import TestingConfig
from .production import ProductionConfig

# 配置字典，用於工廠函數選擇配置
config = {
    "development": DevelopmentConfig,
    "testing": TestingConfig,
    "production": ProductionConfig,
    "default": DevelopmentConfig,
}

__all__ = [
    "config",
    "BaseConfig",
    "DevelopmentConfig",
    "TestingConfig",
    "ProductionConfig",
]
