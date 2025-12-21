"""
搜尋 API Routes
處理全站搜尋相關的 API 端點
"""
from typing import Tuple
from flask import Blueprint, jsonify, request, Response
import logging

from app.utils import get_manager

logger = logging.getLogger(__name__)

# 建立 Blueprint
search_bp = Blueprint('search', __name__, url_prefix='/api/search')

# 延遲導入 Search Service
_search_service = None


def get_search_service():
    """
    延遲載入 Search Service
    
    Returns:
        SearchService: 搜尋服務實例
    """
    global _search_service
    if _search_service is None:
        from core.search_service import SearchService
        mgr = get_manager()
        logger.info("正在初始化搜尋服務...")
        _search_service = SearchService(mgr.client, mgr.member_service)
    return _search_service


@search_bp.route('/global', methods=['GET'])
def global_search() -> Tuple[Response, int]:
    """
    全站搜尋（遊戲 + 會員）
    
    Query Parameters:
        q (str): 搜尋關鍵字（必填）
        fuzzy (bool, optional): 是否啟用模糊搜尋，預設為 true
    
    Returns:
        Tuple[Response, int]: JSON 響應和 HTTP 狀態碼
            - 成功時: ({
                'success': True,
                'results': {
                    'games': [...],
                    'members': [...],
                    'total': int
                }
              }, 200)
            - 失敗時: ({'success': False, 'error': '錯誤訊息'}, 400/500)
    """
    try:
        query = request.args.get('q', '').strip()
        if not query:
            return jsonify({'success': False, 'error': '缺少搜尋關鍵字'}), 400
        
        fuzzy = request.args.get('fuzzy', 'true').lower() == 'true'
        
        logger.debug(f"全站搜尋: query='{query}', fuzzy={fuzzy}")
        
        search_service = get_search_service()
        results = search_service.global_search(query, fuzzy)
        
        return jsonify({
            'success': True,
            'results': results
        }), 200
        
    except Exception as e:
        logger.error(f"全站搜尋失敗: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


@search_bp.route('/games', methods=['GET'])
def search_games() -> Tuple[Response, int]:
    """
    搜尋遊戲
    
    Query Parameters:
        q (str): 搜尋關鍵字（必填）
        fuzzy (bool, optional): 是否啟用模糊搜尋，預設為 true
    
    Returns:
        Tuple[Response, int]: JSON 響應和 HTTP 狀態碼
            - 成功時: ({'success': True, 'results': [...]}, 200)
            - 失敗時: ({'success': False, 'error': '錯誤訊息'}, 400/500)
    """
    try:
        query = request.args.get('q', '').strip()
        if not query:
            return jsonify({'success': False, 'error': '缺少搜尋關鍵字'}), 400
        
        fuzzy = request.args.get('fuzzy', 'true').lower() == 'true'
        
        logger.debug(f"搜尋遊戲: query='{query}', fuzzy={fuzzy}")
        
        search_service = get_search_service()
        results = search_service.search_games(query, fuzzy)
        
        return jsonify({
            'success': True,
            'results': results,
            'total': len(results)
        }), 200
        
    except Exception as e:
        logger.error(f"搜尋遊戲失敗: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


@search_bp.route('/members', methods=['GET'])
def search_members() -> Tuple[Response, int]:
    """
    搜尋會員
    
    Query Parameters:
        q (str): 搜尋關鍵字（必填）
        fuzzy (bool, optional): 是否啟用模糊搜尋，預設為 true
    
    Returns:
        Tuple[Response, int]: JSON 響應和 HTTP 狀態碼
            - 成功時: ({'success': True, 'results': [...]}, 200)
            - 失敗時: ({'success': False, 'error': '錯誤訊息'}, 400/500)
    """
    try:
        query = request.args.get('q', '').strip()
        if not query:
            return jsonify({'success': False, 'error': '缺少搜尋關鍵字'}), 400
        
        fuzzy = request.args.get('fuzzy', 'true').lower() == 'true'
        
        logger.debug(f"搜尋會員: query='{query}', fuzzy={fuzzy}")
        
        search_service = get_search_service()
        results = search_service.search_members(query, fuzzy)
        
        return jsonify({
            'success': True,
            'results': results,
            'total': len(results)
        }), 200
        
    except Exception as e:
        logger.error(f"搜尋會員失敗: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500
