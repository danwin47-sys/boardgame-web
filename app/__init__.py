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
        config_name = os.environ.get('FLASK_ENV', 'development')
    
    # 建立 Flask 應用程式
    app = Flask(__name__, 
                template_folder='templates',
                static_folder='../static', 
                static_url_path='',
                root_path=os.path.dirname(os.path.abspath(__file__)))
    
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
    
    # 初始化 BoardGameManager（全域共享）
    with app.app_context():
        from core.facade import BoardGameManager
        app.config['boardgame_manager'] = BoardGameManager()
        logger.info("BoardGameManager 已初始化")
    
    logger.info("應用程式初始化完成")
    
    return app
