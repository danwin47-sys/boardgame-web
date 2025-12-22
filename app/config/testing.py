"""
測試環境配置
"""
from .base import BaseConfig


class TestingConfig(BaseConfig):
    """測試環境配置"""

    DEBUG = True
    TESTING = True

    # 測試環境強制使用演示模式
    DEMO_MODE = True

    # 測試環境不使用快取
    GAMES_CACHE_TTL = 0
    MEMBERS_CACHE_TTL = 0
    BGG_SEARCH_CACHE_TTL = 0
    BGG_DETAILS_CACHE_TTL = 0
    BGG_HOT_CACHE_TTL = 0

    @classmethod
    def get_config_summary(cls):
        summary = super().get_config_summary()
        summary["ENVIRONMENT"] = "testing"
        summary["TESTING"] = cls.TESTING
        return summary
