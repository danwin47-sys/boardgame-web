"""
基礎配置類別
包含所有環境共用的配置項目
"""
import os
from datetime import timedelta


class BaseConfig:
    """應用程式基礎配置"""

    # ===== Flask 基本設定 =====
    SECRET_KEY = os.environ.get(
        "SECRET_KEY", "dev-secret-key-please-change-in-production"
    )
    
    # Session 過期時間（7 天）
    PERMANENT_SESSION_LIFETIME = timedelta(days=7)

    # ===== Google Sheets 設定 =====
    SHEET_URL = os.environ.get("SHEET_URL", "")
    GOOGLE_CREDENTIALS = os.environ.get("GOOGLE_CREDENTIALS", "")

    # ===== 管理員設定 =====
    # 注意：必須從環境變數設定，不提供預設密碼
    ADMIN_PASSWORD = os.environ.get("ADMIN_PASSWORD")

    # ===== 伺服器設定 =====
    PORT = int(os.environ.get("PORT", 5000))
    HOST = os.environ.get("HOST", "0.0.0.0")

    # ===== BGG API 設定 =====
    # 注意：BGG_API_TOKEN 必須從環境變數設定
    BGG_API_TOKEN = os.environ.get("BGG_API_TOKEN")
    DEMO_MODE = os.environ.get("DEMO_MODE", "False").lower() in ("true", "1", "yes")
    BGG_TIMEOUT = int(os.environ.get("BGG_TIMEOUT", 15))
    BGG_RETRIES = int(os.environ.get("BGG_RETRIES", 2))

    # ===== 快取設定 (秒) =====
    GAMES_CACHE_TTL = int(os.environ.get("GAMES_CACHE_TTL", 30))  # 30 秒
    MEMBERS_CACHE_TTL = int(os.environ.get("MEMBERS_CACHE_TTL", 3600))  # 1 小時
    BGG_SEARCH_CACHE_TTL = int(os.environ.get("BGG_SEARCH_CACHE_TTL", 300))  # 5 分鐘
    BGG_DETAILS_CACHE_TTL = int(os.environ.get("BGG_DETAILS_CACHE_TTL", 3600))  # 1 小時
    BGG_HOT_CACHE_TTL = int(os.environ.get("BGG_HOT_CACHE_TTL", 1800))  # 30 分鐘

    # ===== 工作表名稱 =====
    WORKSHEET_GAMES = "games"
    WORKSHEET_MEMBERS = "members"

    # ===== 日期時間格式 =====
    DATETIME_FORMAT = "%Y-%m-%d %H:%M"

    # ===== 日誌設定 =====
    LOG_LEVEL = os.environ.get("LOG_LEVEL", "INFO")
    LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"

    # ===== JSON 設定 =====
    JSON_AS_ASCII = False  # 支援中文等非 ASCII 字元
    JSON_SORT_KEYS = False

    @classmethod
    def get_config_summary(cls):
        """取得配置摘要（隱藏敏感資訊）"""
        return {
            "DEMO_MODE": cls.DEMO_MODE,
            "PORT": cls.PORT,
            "HOST": cls.HOST,
            "GAMES_CACHE_TTL": cls.GAMES_CACHE_TTL,
            "MEMBERS_CACHE_TTL": cls.MEMBERS_CACHE_TTL,
            "HAS_SHEET_URL": bool(cls.SHEET_URL),
            "HAS_CREDENTIALS": bool(cls.GOOGLE_CREDENTIALS),
            "LOG_LEVEL": cls.LOG_LEVEL,
        }
