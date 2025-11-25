"""
Admin Routes Blueprint
處理管理員相關的路由：登入、批次操作
"""
from flask import Blueprint, jsonify, request, current_app
import os
import secrets
import logging

logger = logging.getLogger(__name__)

admin_bp = Blueprint('admin', __name__, url_prefix='/api')


def get_manager():
    """從 app.config 獲取 BoardGameManager"""
    if 'boardgame_manager' not in current_app.config:
        from boardgame_system import BoardGameManager
        logger.info("正在初始化 Google Sheets 連線...")
        current_app.config['boardgame_manager'] = BoardGameManager()
    return current_app.config['boardgame_manager']


@admin_bp.route('/admin-login', methods=['POST'])
def admin_login():
    """管理員登入"""
    data = request.get_json()
    password = data.get('password')
    
    # 簡單密碼驗證（從環境變數讀取，本地開發用預設值）
    admin_password = os.environ.get('ADMIN_PASSWORD', 'admin123')
    
    if password == admin_password:
        # 簡單的 token（實際應用應使用更安全的方式）
        token = secrets.token_hex(16)
        return jsonify({'success': True, 'token': token, 'message': '登入成功'}), 200
    else:
        return jsonify({'success': False, 'message': '密碼錯誤'}), 401


@admin_bp.route('/batch-borrow', methods=['POST'])
def batch_borrow():
    """批次借桌遊"""
    data = request.get_json()
    if not data: 
        return jsonify({'error': 'No data provided'}), 400
    
    game_names = data.get('game_names', [])
    member_id = data.get('member_id')
    
    if not game_names or not member_id: 
        return jsonify({'error': 'Missing fields'}), 400
    
    mgr = get_manager()
    success, msg, success_list, fail_list = mgr.batch_borrow_games(game_names, member_id)
    return jsonify({
        'message': msg, 
        'success': success, 
        'success_games': success_list,
        'failed_games': fail_list
    }), 200 if success else 400


@admin_bp.route('/batch-return', methods=['POST'])
def batch_return():
    """批次還桌遊"""
    data = request.get_json()
    if not data: 
        return jsonify({'error': 'No data provided'}), 400
    
    game_names = data.get('game_names', [])
    
    if not game_names: 
        return jsonify({'error': 'Missing fields'}), 400
    
    mgr = get_manager()
    success, msg, success_list, fail_list = mgr.batch_return_games(game_names)
    return jsonify({
        'message': msg, 
        'success': success, 
        'success_games': success_list,
        'failed_games': fail_list
    }), 200 if success else 400
