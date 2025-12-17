"""
生產環境配置
"""
from .base import BaseConfig
import os


class ProductionConfig(BaseConfig):
    """生產環境配置"""
    
    DEBUG = False
    TESTING = False
    
    # 生產環境必須設定 SECRET_KEY
    SECRET_KEY: str = os.environ.get('SECRET_KEY') or ''  # type: ignore[assignment]
    
    # 生產環境日誌級別
    LOG_LEVEL = os.environ.get('LOG_LEVEL', 'WARNING')
    
    # 生產環境安全設定
    SESSION_COOKIE_SECURE = True  # 僅透過 HTTPS 傳送 cookie
    SESSION_COOKIE_HTTPONLY = True  # 防止 JavaScript 存取 cookie
    SESSION_COOKIE_SAMESITE = 'Lax'  # CSRF 保護
    
    # 確保生產環境不使用演示模式
    DEMO_MODE = False
    
    @classmethod
    def init_app(cls, app):
        """生產環境初始化檢查"""
        if not cls.SECRET_KEY:
            raise ValueError("生產環境必須設定 SECRET_KEY 環境變數")
        if not cls.SHEET_URL:
            raise ValueError("生產環境必須設定 SHEET_URL 環境變數")
        if not cls.GOOGLE_CREDENTIALS:
            raise ValueError("生產環境必須設定 GOOGLE_CREDENTIALS 環境變數")
    
    @classmethod
    def get_config_summary(cls):
        summary = super().get_config_summary()
        summary['ENVIRONMENT'] = 'production'
        summary['DEBUG'] = cls.DEBUG
        summary['SECURITY_ENABLED'] = True
        return summary
