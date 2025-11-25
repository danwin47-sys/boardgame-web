from flask import Flask, send_from_directory, jsonify
from flask_cors import CORS
import logging

# 配置 logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# 創建 Flask 應用
app = Flask(__name__, static_folder='static', static_url_path='')
CORS(app)

# 註冊 Blueprints
from api.bgg_routes import bgg_bp
from api.game_routes import game_bp
from api.member_routes import member_bp
from api.admin_routes import admin_bp

app.register_blueprint(bgg_bp)
app.register_blueprint(game_bp)
app.register_blueprint(member_bp)
app.register_blueprint(admin_bp)

logger.info("所有 Blueprints 已註冊")


# 靜態頁面路由
@app.route('/')
def home():
    """首頁"""
    return send_from_directory('static', 'index.html')


@app.route('/favicon.ico')
def favicon():
    """Favicon"""
    return send_from_directory('static', 'favicon.svg', mimetype='image/svg+xml')


# 健康檢查
@app.route('/api/health')
def health_check():
    """健康檢查端點"""
    from boardgame_system import BoardGameManager
    
    # 確保 manager 在 config 中
    if 'boardgame_manager' not in app.config:
        app.config['boardgame_manager'] = BoardGameManager()
    
    mgr = app.config['boardgame_manager']
    return jsonify({
        'status': 'ok', 
        'timestamp': mgr.get_current_timestamp()
    }), 200


if __name__ == '__main__':
    from config import Config
    logger.info(f"啟動 Flask 應用於 {Config.HOST}:{Config.PORT}")
    app.run(host=Config.HOST, port=Config.PORT)