"""
Flask 擴展初始化模組
集中管理所有 Flask 擴展的初始化
"""
from flask_cors import CORS
import logging

logger = logging.getLogger(__name__)


def init_extensions(app):
    """
    初始化所有 Flask 擴展

    Args:
        app: Flask 應用程式實例
    """
    # 初始化 CORS
    CORS(app)
    logger.info("CORS 已啟用")

    # 未來可以在此加入其他擴展
    # 例如: SQLAlchemy, Redis, Celery 等
