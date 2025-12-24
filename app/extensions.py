"""
Flask 擴展初始化模組
集中管理所有 Flask 擴展的初始化
"""
from flask_cors import CORS
from flask_static_digest import FlaskStaticDigest
import logging

logger = logging.getLogger(__name__)

# 初始化擴展實例
static_digest = FlaskStaticDigest()


def init_extensions(app):
    """
    初始化所有 Flask 擴展

    Args:
        app: Flask 應用程式實例
    """
    # 初始化 CORS
    CORS(app)
    logger.info("CORS 已啟用")

    # 初始化 Flask-Static-Digest (開發時暫時停用以避免快取問題)
    # static_digest.init_app(app)
    # logger.info("Flask-Static-Digest 已初始化")

    # 未來可以在此加入其他擴展
    # 例如: SQLAlchemy, Redis, Celery 等
