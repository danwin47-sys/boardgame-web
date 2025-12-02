"""
BGG (BoardGameGeek) API Routes
處理所有 BGG 相關的 API 端點
"""
from flask import Blueprint, jsonify, request
from urllib.parse import unquote
import logging
import traceback

logger = logging.getLogger(__name__)

# 建立 Blueprint
bgg_bp = Blueprint('bgg', __name__, url_prefix='/api/bgg')

# 延遲導入 BGG Service，避免循環依賴
_bgg_service = None

def get_bgg_service():
    """延遲載入 BGG Service"""
    global _bgg_service
    if _bgg_service is None:
        from core.bgg_service import BGGService
        logger.info("正在初始化 BGG API 連線...")
        _bgg_service = BGGService()
    return _bgg_service


# ============ BGG 通用 API ============

@bgg_bp.route('/search', methods=['GET'])
def search_bgg():
    """搜尋 BGG 桌遊"""
    try:
        query = request.args.get('q', '').strip()
        if not query:
            return jsonify({'success': False, 'error': '缺少搜尋關鍵字'}), 400
        
        logger.debug(f"BGG search query: {query}")
        bgg = get_bgg_service()
        results = bgg.search_games(query)
        
        return jsonify({'success': True, 'results': results}), 200
    except Exception as e:
        logger.error(f"BGG search exception: {e}")
        traceback.print_exc()
        return jsonify({'success': False, 'error': str(e)}), 500


@bgg_bp.route('/games/<int:game_id>', methods=['GET'])
def get_bgg_game(game_id):
    """取得 BGG 遊戲詳情"""
    try:
        logger.debug(f"Fetching BGG game details: {game_id}")
        bgg = get_bgg_service()
        game = bgg.get_game_details(game_id)
        
        if game:
            return jsonify({'success': True, 'game': game}), 200
        else:
            return jsonify({'success': False, 'error': '找不到遊戲'}), 404
    except Exception as e:
        logger.error(f"Get BGG game exception: {e}")
        traceback.print_exc()
        return jsonify({'success': False, 'error': str(e)}), 500


@bgg_bp.route('/hot', methods=['GET'])
def get_hot_games():
    """取得 BGG 熱門桌遊"""
    try:
        limit = int(request.args.get('limit', 10))
        logger.debug(f"Fetching hot games, limit: {limit}")
        
        bgg = get_bgg_service()
        games = bgg.get_hot_games(limit)
        
        return jsonify({'success': True, 'games': games}), 200
    except Exception as e:
        logger.error(f"Get hot games exception: {e}")
        traceback.print_exc()
        return jsonify({'success': False, 'error': str(e)}), 500


@bgg_bp.route('/collection', methods=['POST'])
def add_to_collection():
    """從 BGG 加入桌遊到館藏"""
    try:
        data = request.get_json()
        game_id = data.get('game_id')
        custodian = data.get('custodian', '')
        
        if not game_id:
            return jsonify({'success': False, 'error': '缺少 game_id'}), 400
        
        logger.debug(f"Adding BGG game to collection: {game_id}, custodian: {custodian}")
        
        # 取得遊戲詳情
        bgg = get_bgg_service()
        game = bgg.get_game_details(game_id)
        
        if not game:
            return jsonify({'success': False, 'error': '找不到遊戲'}), 404
        
        # TODO: 實作將 BGG 遊戲加入到 Google Sheets 的邏輯
        return jsonify({'success': True, 'message': f'已加入「{game["name"]}」到館藏'}), 200
        
    except Exception as e:
        logger.error(f"Add to collection exception: {e}")
        traceback.print_exc()
        return jsonify({'success': False, 'error': str(e)}), 500


# ============ BGG 遊戲連結 API ============

@bgg_bp.route('/games/link/search/<game_name>', methods=['GET'])
def search_for_linking(game_name):
    """搜尋 BGG 遊戲（用於連結功能）"""
    try:
        decoded_game_name = unquote(game_name)
        logger.debug(f"search_for_linking - Original: {game_name}, Decoded: {decoded_game_name}")
        
        bgg = get_bgg_service()
        results = bgg.search_games(decoded_game_name)
        
        return jsonify({
            'success': True,
            'game_name': decoded_game_name,
            'results': results
        }), 200
    except Exception as e:
        logger.error(f"search_for_linking exception: {e}")
        traceback.print_exc()
        return jsonify({'success': False, 'error': str(e)}), 500


@bgg_bp.route('/games/link/<game_name>', methods=['POST'])
def link_game(game_name):
    """連結桌遊到 BGG"""
    try:
        from boardgame_system import BoardGameManager
        
        decoded_game_name = unquote(game_name)
        logger.debug(f"link_game - Original: {game_name}")
        logger.debug(f"link_game - Decoded: {decoded_game_name}")
        
        data = request.get_json()
        bgg_id = data.get('bgg_id')
        
        if not bgg_id:
            return jsonify({'success': False, 'error': '缺少 bgg_id'}), 400
        
        # 使用全局 manager（與 flask_app.py 共享）
        from flask import current_app
        mgr = current_app.config.get('boardgame_manager')
        if not mgr:
            mgr = BoardGameManager()
        
        all_games = mgr.load_data()
        all_game_names = [g.get('name', '') for g in all_games]
        logger.debug(f"Available games: {all_game_names}")
        logger.debug(f"Looking for: '{decoded_game_name}'")
        
        success = mgr.client.update_game_bgg_id(decoded_game_name, bgg_id)
        
        if success:
            return jsonify({
                'success': True,
                'message': f'已成功連結「{decoded_game_name}」到 BGG (ID: {bgg_id})'
            }), 200
        else:
            game_list = '、'.join(all_game_names[:5])
            return jsonify({
                'success': False,
                'error': f'找不到桌遊「{decoded_game_name}」，請確認名稱是否正確。可用的桌遊: {game_list}...'
            }), 404
    except Exception as e:
        logger.error(f"link_game exception: {e}")
        traceback.print_exc()
        return jsonify({'success': False, 'error': str(e)}), 500


@bgg_bp.route('/games/link/<game_name>', methods=['DELETE'])
def unlink_game(game_name):
    """取消桌遊與 BGG 的連結"""
    try:
        from boardgame_system import BoardGameManager
        
        decoded_game_name = unquote(game_name)
        logger.debug(f"unlink_game - Original: {game_name}, Decoded: {decoded_game_name}")
        
        # 使用全局 manager
        from flask import current_app
        mgr = current_app.config.get('boardgame_manager')
        if not mgr:
            mgr = BoardGameManager()
        
        success = mgr.client.update_game_bgg_id(decoded_game_name, None)
        
        if success:
            return jsonify({
                'success': True,
                'message': f'已取消「{decoded_game_name}」與 BGG 的連結'
            }), 200
        else:
            return jsonify({
                'success': False,
                'error': f'找不到桌遊「{decoded_game_name}」，請確認名稱是否正確'
            }), 404
    except Exception as e:
        logger.error(f"unlink_game exception: {e}")
        traceback.print_exc()
        return jsonify({'success': False, 'error': str(e)}), 500
