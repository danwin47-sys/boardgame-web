"""
管理員 API Blueprint
處理管理員相關的路由：登入、批次操作
"""
from flask import Blueprint, jsonify, request, current_app
import os
import secrets
import logging

logger = logging.getLogger(__name__)

# 建立 Blueprint
admin_bp = Blueprint('admin', __name__, url_prefix='/api')


def get_manager():
    """從 app.config 獲取 BoardGameManager"""
    if 'boardgame_manager' not in current_app.config:
        from core.facade import BoardGameManager
        logger.info("正在初始化 Google Sheets 連線...")
        current_app.config['boardgame_manager'] = BoardGameManager()
    return current_app.config['boardgame_manager']


@admin_bp.route('/admin-login', methods=['POST'])
def admin_login():
    """管理員登入"""
    try:
        data = request.get_json()
        password = data.get('password')
        
        # 從配置讀取管理員密碼
        admin_password = current_app.config.get('ADMIN_PASSWORD', 'admin123')
        
        if password == admin_password:
            # 簡單的 token（實際應用應使用 JWT 或更安全的方式）
            token = secrets.token_hex(16)
            logger.info("管理員登入成功")
            return jsonify({'success': True, 'token': token, 'message': '登入成功'}), 200
        else:
            logger.warning("管理員登入失敗：密碼錯誤")
            return jsonify({'success': False, 'message': '密碼錯誤'}), 401
    except Exception as e:
        logger.error(f"管理員登入異常: {e}", exc_info=True)
        return jsonify({'success': False, 'error': str(e)}), 500


@admin_bp.route('/batch-borrow', methods=['POST'])
def batch_borrow():
    """批次借桌遊"""
    try:
        data = request.get_json()
        if not data: 
            return jsonify({'success': False, 'error': '缺少請求資料'}), 400
        
        game_names = data.get('game_names', [])
        member_id = data.get('member_id')
        
        if not game_names or not member_id: 
            return jsonify({'success': False, 'error': '缺少必要欄位'}), 400
        
        mgr = get_manager()
        success, msg, success_list, fail_list = mgr.batch_borrow_games(game_names, member_id)
        
        logger.info(f"批次借出：成功 {len(success_list)} 個，失敗 {len(fail_list)} 個")
        
        return jsonify({
            'message': msg, 
            'success': success, 
            'success_games': success_list,
            'failed_games': fail_list
        }), 200 if success else 400
    except Exception as e:
        logger.error(f"批次借出失敗: {e}", exc_info=True)
        return jsonify({'success': False, 'error': str(e)}), 500


@admin_bp.route('/batch-return', methods=['POST'])
def batch_return():
    """批次還桌遊"""
    try:
        data = request.get_json()
        if not data: 
            return jsonify({'success': False, 'error': '缺少請求資料'}), 400
        
        game_names = data.get('game_names', [])
        
        if not game_names: 
            return jsonify({'success': False, 'error': '缺少必要欄位'}), 400
        
        mgr = get_manager()
        success, msg, success_list, fail_list = mgr.batch_return_games(game_names)
        
        logger.info(f"批次歸還：成功 {len(success_list)} 個，失敗 {len(fail_list)} 個")
        
        return jsonify({
            'message': msg, 
            'success': success, 
            'success_games': success_list,
            'failed_games': fail_list
        }), 200 if success else 400
    except Exception as e:
        logger.error(f"批次歸還失敗: {e}", exc_info=True)
        return jsonify({'success': False, 'error': str(e)}), 500
