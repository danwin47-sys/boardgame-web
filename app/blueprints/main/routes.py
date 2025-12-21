"""
主要路由 Blueprint
處理首頁、靜態資源、健康檢查等基本路由
"""
from typing import Tuple, Dict, Any
from flask import Blueprint, send_from_directory, jsonify, Response
import logging

from app.utils import get_manager

logger = logging.getLogger(__name__)

# 建立 Blueprint
main_bp = Blueprint('main', __name__)


@main_bp.route('/')
def home() -> Response:
    """首頁
    
    返回主頁面 HTML 文件。
    
    Returns:
        Response: index.html 文件響應
    """
    return send_from_directory('../static/html', 'index.html')


@main_bp.route('/admin.html')
def admin_page() -> Response:
    """管理員頁面
    
    返回管理員後台 HTML 文件。
    
    Returns:
        Response: admin.html 文件響應
    """
    return send_from_directory('../static/html', 'admin.html')


@main_bp.route('/gallery.html')
def gallery_page() -> Response:
    """展示牆頁面
    
    返回桌遊展示牆 HTML 文件。
    
    Returns:
        Response: gallery.html 文件響應
    """
    return send_from_directory('../static/html', 'gallery.html')


@main_bp.route('/favicon.ico')
def favicon() -> Response:
    """網站圖標
    
    返回網站 favicon（SVG 格式）。
    
    Returns:
        Response: favicon.svg 文件響應
    """
    return send_from_directory('../static/images', 'favicon.svg', mimetype='image/svg+xml')


@main_bp.route('/api/health')
def health_check() -> Tuple[Response, int]:
    """健康檢查端點
    
    檢查應用程式是否正常運行，返回狀態和當前時間戳。
    
    Returns:
        Tuple[Response, int]: JSON 響應和 HTTP 狀態碼
            - 成功時: ({
                'status': 'ok',
                'timestamp': str
              }, 200)
    
    Note:
        - 用於監控系統健康狀態
        - 返回的 timestamp 可用於檢查系統時間
    """
    mgr = get_manager()
    return jsonify({
        'status': 'ok', 
        'timestamp': mgr.get_current_timestamp()
    }), 200


@main_bp.route('/api/sys_info')
def sys_info() -> Response:
    """系統狀態診斷
    
    返回詳細的系統診斷資訊，包括：
    - 當前工作目錄
    - Manager 初始化狀態
    - 資料庫連線狀態
    - 桌遊數量
    - 憑證文件狀態
    - 配置環境
    
    Returns:
        Response: JSON 響應包含系統診斷資訊
            {
                'cwd': str,                    # 當前工作目錄
                'manager_initialized': str,     # Manager 狀態
                'manager_valid': bool,          # Manager 是否有效
                'client_valid': bool,           # 客戶端是否有效
                'games_count': int,             # 桌遊數量
                'first_game': str,              # 第一個桌遊名稱
                'creds_path': str,              # 憑證文件路徑
                'creds_exists': bool,           # 憑證文件是否存在
                'config': str,                  # 配置環境
                'load_error': str,              # 載入錯誤（如果有）
                'error': str                    # 系統錯誤（如果有）
            }
    
    Note:
        - 用於除錯和系統診斷
        - 包含敏感路徑資訊，生產環境應謹慎使用
    """
    from flask import current_app
    import os
    
    info: Dict[str, Any] = {}
    try:
        info['cwd'] = os.getcwd()
        
        mgr = get_manager()
        info['manager_initialized'] = 'OK'
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
