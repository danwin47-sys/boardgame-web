"""
社員 API Blueprint
處理社員相關的路由
"""
from flask import Blueprint, jsonify, current_app
import logging

logger = logging.getLogger(__name__)

# 建立 Blueprint
member_bp = Blueprint('member', __name__, url_prefix='/api')


def get_manager():
    """從 app.config 獲取 BoardGameManager"""
    if 'boardgame_manager' not in current_app.config:
        from boardgame_system import BoardGameManager
        logger.info("正在初始化 Google Sheets 連線...")
        current_app.config['boardgame_manager'] = BoardGameManager()
    return current_app.config['boardgame_manager']


@member_bp.route('/members', methods=['GET'])
def get_members():
    """獲取社員列表"""
    try:
        mgr = get_manager()
        members = mgr.load_members()
        return jsonify(members), 200
    except Exception as e:
        logger.error(f"獲取社員列表失敗: {e}", exc_info=True)
        return jsonify({'success': False, 'error': str(e)}), 500
