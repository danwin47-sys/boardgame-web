"""
Member Routes Blueprint
處理社員相關的路由
"""
from flask import Blueprint, jsonify, current_app
import logging

logger = logging.getLogger(__name__)

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
    mgr = get_manager()
    return jsonify(mgr.load_members())
