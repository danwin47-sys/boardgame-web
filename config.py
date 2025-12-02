"""
應用程式配置管理模組
統一管理所有環境變數和應用設定
"""
import os


class Config:
    """應用程式配置類別"""
    
    # ===== Google Sheets 設定 =====
    SHEET_URL = os.environ.get("SHEET_URL", "")
    GOOGLE_CREDENTIALS = os.environ.get("GOOGLE_CREDENTIALS", "")
    
    # ===== 管理員設定 =====
    ADMIN_PASSWORD = os.environ.get("ADMIN_PASSWORD", "admin123")
    
    # ===== 伺服器設定 =====
    PORT = int(os.environ.get("PORT", 5000))
    HOST = os.environ.get("HOST", "0.0.0.0")
    
    # ===== BGG API 設定 =====
    # BGG_API_TOKEN: Bearer Token for BGG XML API v2 authentication
    BGG_API_TOKEN = os.environ.get("BGG_API_TOKEN", "")
    # DEMO_MODE: True = 使用演示數據, False = 使用真實 BGG API
    DEMO_MODE = os.environ.get("DEMO_MODE", "True").lower() in ('true', '1', 'yes')
    BGG_TIMEOUT = int(os.environ.get("BGG_TIMEOUT", 15))
    BGG_RETRIES = int(os.environ.get("BGG_RETRIES", 2))
    
    # ===== 快取設定 =====
    GAMES_CACHE_TTL = int(os.environ.get("GAMES_CACHE_TTL", 30))      # 30 秒
    MEMBERS_CACHE_TTL = int(os.environ.get("MEMBERS_CACHE_TTL", 3600))  # 1 小時
    BGG_SEARCH_CACHE_TTL = int(os.environ.get("BGG_SEARCH_CACHE_TTL", 300))    # 5 分鐘
    BGG_DETAILS_CACHE_TTL = int(os.environ.get("BGG_DETAILS_CACHE_TTL", 3600))  # 1 小時
    BGG_HOT_CACHE_TTL = int(os.environ.get("BGG_HOT_CACHE_TTL", 1800))         # 30 分鐘
    
    # ===== 工作表名稱 =====
    WORKSHEET_GAMES = "games"
    WORKSHEET_MEMBERS = "members"
    
    # ===== 日期時間格式 =====
    DATETIME_FORMAT = '%Y-%m-%d %H:%M'
    
    @classmethod
    def get_config_summary(cls):
        """取得配置摘要（隱藏敏感資訊）"""
        return {
            'DEMO_MODE': cls.DEMO_MODE,
            'PORT': cls.PORT,
            'GAMES_CACHE_TTL': cls.GAMES_CACHE_TTL,
            'MEMBERS_CACHE_TTL': cls.MEMBERS_CACHE_TTL,
            'HAS_SHEET_URL': bool(cls.SHEET_URL),
            'HAS_CREDENTIALS': bool(cls.GOOGLE_CREDENTIALS),
        }
