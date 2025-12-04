"""
主要路由 Blueprint
處理首頁、靜態資源、健康檢查等基本路由
"""
from flask import Blueprint, send_from_directory, jsonify
import logging

logger = logging.getLogger(__name__)

# 建立 Blueprint
main_bp = Blueprint('main', __name__)


@main_bp.route('/')
def home():
    """首頁"""
    return send_from_directory('../static/html', 'index.html')

@main_bp.route('/admin.html')
def admin_page():
    """管理員頁面"""
    return send_from_directory('../static/html', 'admin.html')

@main_bp.route('/gallery.html')
def gallery_page():
    """展示牆頁面"""
    return send_from_directory('../static/html', 'gallery.html')


@main_bp.route('/favicon.ico')
def favicon():
    """Favicon"""
    return send_from_directory('../static/images', 'favicon.svg', mimetype='image/svg+xml')


@main_bp.route('/api/health')
def health_check():
    """健康檢查端點"""
    from flask import current_app
    from core.facade import BoardGameManager
    
    # 確保 manager 在 config 中
    if 'boardgame_manager' not in current_app.config:
        current_app.config['boardgame_manager'] = BoardGameManager()
    
    mgr = current_app.config['boardgame_manager']
    return jsonify({
        'status': 'ok', 
        'timestamp': mgr.get_current_timestamp()
    }), 200


@main_bp.route('/api/sys_info')
def sys_info():
    """系統狀態診斷"""
    from flask import current_app
    import os
    
    info = {}
    try:
        from core.facade import BoardGameManager
        
        info['cwd'] = os.getcwd()
        
        if 'boardgame_manager' not in current_app.config:
            current_app.config['boardgame_manager'] = BoardGameManager()
            info['manager_initialized'] = 'Just Now'
        else:
            info['manager_initialized'] = 'Already Existed'
            
        mgr = current_app.config['boardgame_manager']
        info['manager_valid'] = mgr.valid
        info['client_valid'] = mgr.client.valid
        
        # Try to load games
        try:
            games = mgr.load_data()
            info['games_count'] = len(games)
            if len(games) > 0:
                info['first_game'] = games[0].get('name', 'N/A')
        except Exception as e:
            info['load_error'] = str(e)
            
        # Check credentials file
        base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        json_path = os.path.join(base_dir, 'boardgame-bot-5f6751855184.json')
        info['creds_path'] = json_path
        info['creds_exists'] = os.path.exists(json_path)
        
        # Configuration info
        info['config'] = current_app.config.get('ENV', 'unknown')
        
    except Exception as e:
        info['error'] = str(e)
        logger.error(f"系統資訊錯誤: {e}", exc_info=True)
        
    return jsonify(info)
