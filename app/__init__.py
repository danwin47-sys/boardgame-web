"""
Boardgame Web 應用程式工廠模組
"""
import logging
import os

from flask import Flask

logger = logging.getLogger(__name__)


def create_app(config_name=None):
    """
    應用程式工廠函數

    Args:
        config_name: 配置名稱 ('development', 'testing', 'production')
                     如果為 None，從環境變數 FLASK_ENV 讀取，預設為 'development'

    Returns:
        Flask: 配置好的 Flask 應用程式實例
    """
    # 決定配置環境
    if config_name is None:
        config_name = os.environ.get("FLASK_ENV", "development")

    # 建立 Flask 應用程式
    app = Flask(
        __name__,
        template_folder="templates",
        static_folder="../static",
        static_url_path="",
        root_path=os.path.dirname(os.path.abspath(__file__)),
    )

    # 載入配置
    from .config import config

    app.config.from_object(config[config_name])

    logger.info(f"建立應用程式，環境: {config_name}")

    # 初始化擴展
    from .extensions import init_extensions

    init_extensions(app)

    # 註冊錯誤處理器
    from .middleware.error_handlers import register_error_handlers

    register_error_handlers(app)

    # 初始化請求日誌追蹤（為每個請求分配唯一ID）
    from .middleware.request_logger import init_request_logging

    init_request_logging(app)
    logger.info("已啟用請求追蹤日誌")

    # 註冊 Blueprints
    from .blueprints import register_blueprints

    register_blueprints(app)

    # 註冊 Auth Blueprint
    from .blueprints.auth.routes import auth_bp

    app.register_blueprint(auth_bp, url_prefix="/auth")
    logger.info("已註冊 auth blueprint")

    # 初始化 Flask-Login
    from flask_login import LoginManager

    from core.user_model import User

    login_manager = LoginManager()
    login_manager.init_app(app)
    login_manager.login_view = "auth.login"
    login_manager.login_message = "請先登入以存取此頁面"
    login_manager.login_message_category = "warning"

    @login_manager.user_loader
    def load_user(user_id):
        return User.get(user_id)

    # 增強 Cookie 安全性
    app.config.update(
        SESSION_COOKIE_HTTPONLY=True,
        SESSION_COOKIE_SAMESITE="Lax",
        # 生產環境才啟用 Secure，避免本地開發 (HTTP) 出問題
        SESSION_COOKIE_SECURE=config_name == "production",
    )
    logger.info("Flask-Login 已初始化，Cookie 安全性已增強")

    # 初始化 BoardGameManager（全域共享）
    with app.app_context():
        from core.facade import BoardGameManager

        app.config["boardgame_manager"] = BoardGameManager()
        logger.info("BoardGameManager 已初始化")

    logger.info("應用程式初始化完成")

    return app
