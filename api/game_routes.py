"""
Game Routes Blueprint
處理桌遊相關的路由：列表、借還操作
"""
from flask import Blueprint, jsonify, request, current_app
import logging

logger = logging.getLogger(__name__)

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
    mgr = get_manager()
    mgr.games = mgr.load_data()
    return jsonify(mgr.games)


@game_bp.route('/borrow', methods=['POST'])
def borrow_game():
    """借桌遊"""
    data = request.get_json()
    if not data: 
        return jsonify({'error': 'No data provided'}), 400
    
    name = data.get('name')
    member_id = data.get('member_id')
    
    if not name or not member_id: 
        return jsonify({'error': 'Missing fields'}), 400
    
    mgr = get_manager()
    member = mgr.find_member_by_id(member_id)
    if not member: 
        return jsonify({'error': '找不到社員'}), 404
    
    success, msg = mgr.borrow_game(name, member['name'], member['id'])
    return jsonify({'message': msg, 'success': success}), 200 if success else 400


@game_bp.route('/return', methods=['POST'])
def return_game():
    """還桌遊"""
    data = request.get_json()
    name = data.get('name')
    if not name: 
        return jsonify({'error': 'Missing name'}), 400
    
    mgr = get_manager()
    success, msg = mgr.return_game(name)
    return jsonify({'message': msg, 'success': success}), 200 if success else 400
