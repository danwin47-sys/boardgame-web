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
    from .api.games import game_bp
    from .api.bgg import bgg_bp
    from .api.members import member_bp
    app.register_blueprint(game_bp)
    app.register_blueprint(bgg_bp)
    app.register_blueprint(member_bp)
    logger.info("已註冊 API blueprints (games, bgg, members)")
    
    # 註冊管理員 Blueprint
    from .admin.routes import admin_bp
    app.register_blueprint(admin_bp)
    logger.info("已註冊 admin blueprint")
    
    logger.info(f"所有 Blueprints 已註冊，共 {len(app.blueprints)} 個")
