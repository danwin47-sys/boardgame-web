"""
開發環境配置
"""
from .base import BaseConfig


class DevelopmentConfig(BaseConfig):
    """開發環境配置"""
    
    DEBUG = True
    TESTING = False
    
    # 開發環境使用較短的快取時間，方便測試
    GAMES_CACHE_TTL = 10  # 10 秒
    
    # 開發環境日誌級別
    LOG_LEVEL = 'DEBUG'
    
    @classmethod
    def get_config_summary(cls):
        summary = super().get_config_summary()
        summary['ENVIRONMENT'] = 'development'
        summary['DEBUG'] = cls.DEBUG
        return summary
