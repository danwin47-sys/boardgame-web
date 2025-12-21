"""
Boardgame Web 應用程式工廠模組
"""
from flask import Flask
from flask_cors import CORS
import logging
import os

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

    # 註冊 Blueprints
    from .blueprints import register_blueprints

    register_blueprints(app)

    # 添加 HTTP 快取標頭中介軟體
    @app.after_request
    def add_cache_headers(response):
        """
        添加 HTTP 快取標頭以優化重複訪問效能

        策略：
        - 靜態資源（CSS, JS, 圖片）：1 年快取
        - API 端點：根據資料類型設置不同快取時間
        - HTML 頁面：不快取，確保總是最新
        """
        from flask import request
        import hashlib

        # 靜態資源（CSS, JS, 圖片）
        if (
            request.path.startswith("/static/")
            or request.path.startswith("/css/")
            or request.path.startswith("/js/")
        ):
            # 1 年快取
            response.cache_control.max_age = 31536000
            response.cache_control.public = True

            # 添加 ETag 支援
            if (
                response.data and len(response.data) < 1024 * 1024
            ):  # 只為 < 1MB 的檔案生成 ETag
                etag = hashlib.md5(response.data).hexdigest()
                response.set_etag(etag)

        # API 端點
        elif request.path.startswith("/api/"):
            # 根據端點設置不同的快取策略
            if "/api/games" in request.path and request.method == "GET":
                # 遊戲列表：5 分鐘快取
                response.cache_control.max_age = 300
                response.cache_control.public = True
            elif "/api/bgg/" in request.path:
                # BGG 資料：1 小時快取
                response.cache_control.max_age = 3600
                response.cache_control.public = True
            elif "/api/members" in request.path and request.method == "GET":
                # 會員列表：5 分鐘快取
                response.cache_control.max_age = 300
                response.cache_control.public = True
            else:
                # 其他 API：不快取（POST, PUT, DELETE 等）
                response.cache_control.no_cache = True

        # HTML 頁面
        else:
            # 不快取 HTML（確保總是最新）
            response.cache_control.no_cache = True
            response.cache_control.must_revalidate = True

        return response

    # 初始化 BoardGameManager（全域共享）
    with app.app_context():
        from core.facade import BoardGameManager

        app.config["boardgame_manager"] = BoardGameManager()
        logger.info("BoardGameManager 已初始化")

    logger.info("應用程式初始化完成")

    return app
