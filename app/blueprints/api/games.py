"""
遊戲 API Blueprint
處理桌遊相關的路由：列表、借還操作
"""
from flask import Blueprint, jsonify, request, current_app
import logging

logger = logging.getLogger(__name__)

# 建立 Blueprint
game_bp = Blueprint('game', __name__, url_prefix='/api')


def get_manager():
    """從 app.config 獲取 BoardGameManager"""
    if 'boardgame_manager' not in current_app.config:
        from boardgame_system import BoardGameManager
        logger.info("正在初始化 Google Sheets 連線...")
        current_app.config['boardgame_manager'] = BoardGameManager()
    return current_app.config['boardgame_manager']


@game_bp.route('/games', methods=['GET'])
def get_games():
    """獲取桌遊列表"""
    try:
        mgr = get_manager()
        mgr.games = mgr.load_data()
        return jsonify(mgr.games), 200
    except Exception as e:
        logger.error(f"獲取桌遊列表失敗: {e}", exc_info=True)
        return jsonify({'success': False, 'error': str(e)}), 500


@game_bp.route('/borrow', methods=['POST'])
def borrow_game():
    """借桌遊"""
    try:
        data = request.get_json()
        if not data: 
            return jsonify({'success': False, 'error': '缺少請求資料'}), 400
        
        name = data.get('name')
        member_id = data.get('member_id')
        
        if not name or not member_id: 
            return jsonify({'success': False, 'error': '缺少必要欄位'}), 400
        
        mgr = get_manager()
        member = mgr.find_member_by_id(member_id)
        if not member: 
            return jsonify({'success': False, 'error': '找不到社員'}), 404
        
        success, msg = mgr.borrow_game(name, member['name'], member['id'])
        return jsonify({'message': msg, 'success': success}), 200 if success else 400
    except Exception as e:
        logger.error(f"借桌遊失敗: {e}", exc_info=True)
        return jsonify({'success': False, 'error': str(e)}), 500


@game_bp.route('/return', methods=['POST'])
def return_game():
    """還桌遊"""
    try:
        data = request.get_json()
        name = data.get('name')
        if not name: 
            return jsonify({'success': False, 'error': '缺少桌遊名稱'}), 400
        
        mgr = get_manager()
        success, msg = mgr.return_game(name)
        return jsonify({'message': msg, 'success': success}), 200 if success else 400
    except Exception as e:
        logger.error(f"歸還桌遊失敗: {e}", exc_info=True)
        return jsonify({'success': False, 'error': str(e)}), 500
