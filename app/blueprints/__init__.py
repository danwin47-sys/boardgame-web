"""
Blueprint 註冊中心
集中管理所有 Blueprint 的註冊
"""
import logging

logger = logging.getLogger(__name__)


def register_blueprints(app):
    """
    註冊所有 Blueprints

    Args:
        app: Flask 應用程式實例
    """
    # 註冊主要頁面 Blueprint
    from .main.routes import main_bp

    app.register_blueprint(main_bp)
    logger.info("已註冊 main blueprint")

    # 註冊 API Blueprints
    from .api.games import games_bp
    from .api.bgg import bgg_bp
    from .api.members import members_bp
    from .api.gallery import gallery_bp
    from .api.docs import api_docs_bp
    from .api.search import search_bp
    from .api.monitoring import monitoring_bp
    from .api.metrics import metrics_bp

    app.register_blueprint(games_bp)
    app.register_blueprint(bgg_bp)
    app.register_blueprint(members_bp)
    app.register_blueprint(gallery_bp)
    app.register_blueprint(api_docs_bp)
    app.register_blueprint(search_bp)
    app.register_blueprint(monitoring_bp)
    app.register_blueprint(metrics_bp)
    logger.info(
        "已註冊 API blueprints (games, bgg, members, gallery, docs, search, monitoring, metrics)"
    )

    # 啟用指標收集中介軟體
    from .api.metrics import setup_metrics_middleware
    setup_metrics_middleware(app)

    # 註冊管理員 Blueprint
    from .admin.routes import admin_bp

    app.register_blueprint(admin_bp)
    logger.info("已註冊 admin blueprint")

    logger.info(f"所有 Blueprints 已註冊，共 {len(app.blueprints)} 個")
