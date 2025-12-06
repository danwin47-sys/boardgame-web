"""
遊戲 API Blueprint
處理桌遊相關的路由：列表、借還操作
"""
from typing import Tuple, Any, Optional, Dict
from flask import Blueprint, jsonify, request, Response
import logging

from app.utils import get_manager

logger = logging.getLogger(__name__)

# 建立 Blueprint
games_bp = Blueprint('games', __name__, url_prefix='/api')


@games_bp.route('/games', methods=['GET'])
def get_games() -> Tuple[Response, int]:
    """獲取桌遊列表
    
    從 Google Sheets 讀取所有桌遊資料並返回。
    
    Returns:
        Tuple[Response, int]: JSON 響應包含桌遊列表和 HTTP 狀態碼
            - 成功時: ({'games': [...]}, 200)
            - 失敗時: ({'success': False, 'error': '錯誤訊息'}, 500)
    
    Raises:
        Exception: 當資料庫連線失敗或資料讀取錯誤時
    """
    try:
        mgr = get_manager()
        mgr.games = mgr.load_data()
        return jsonify(mgr.games), 200
    except Exception as e:
        logger.error(f"獲取桌遊列表失敗: {e}", exc_info=True)
        return jsonify({'success': False, 'error': str(e)}), 500


@games_bp.route('/borrow', methods=['POST'])
def borrow_game() -> Tuple[Response, int]:
    """借出桌遊
    
    處理桌遊借出請求，更新桌遊狀態並記錄借閱人資訊。
    
    Request Body:
        {
            "name": str,        # 桌遊名稱
            "member_id": str    # 社員 ID
        }
    
    Returns:
        Tuple[Response, int]: JSON 響應和 HTTP 狀態碼
            - 成功時: ({'message': '訊息', 'success': True}, 200)
            - 失敗時: ({'success': False, 'error': '錯誤訊息'}, 400/404/500)
    
    Raises:
        Exception: 當資料庫更新失敗時
    """
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


@games_bp.route('/return', methods=['POST'])
def return_game() -> Tuple[Response, int]:
    """歸還桌遊
    
    處理桌遊歸還請求，更新桌遊狀態並清除借閱人資訊。
    
    Request Body:
        {
            "name": str  # 桌遊名稱
        }
    
    Returns:
        Tuple[Response, int]: JSON 響應和 HTTP 狀態碼
            - 成功時: ({'message': '訊息', 'success': True}, 200)
            - 失敗時: ({'success': False, 'error': '錯誤訊息'}, 400/500)
    
    Raises:
        Exception: 當資料庫更新失敗時
    """
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
