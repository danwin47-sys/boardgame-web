"""
管理員 API Blueprint
處理管理員相關的路由：登入、批次操作
"""
from typing import Tuple
from flask import Blueprint, jsonify, request, Response
import os
import secrets
import logging

from app.utils import get_manager

logger = logging.getLogger(__name__)

# 建立 Blueprint
admin_bp = Blueprint('admin', __name__, url_prefix='/api')


@admin_bp.route('/admin-login', methods=['POST'])
def admin_login() -> Tuple[Response, int]:
    """管理員登入
    
    驗證管理員密碼並生成訪問 token。
    
    Request Body:
        {
            "password": str  # 管理員密碼（必填）
        }
    
    Returns:
        Tuple[Response, int]: JSON 響應和 HTTP 狀態碼
            - 成功時: ({
                'success': True,
                'token': str,
                'message': '登入成功'
              }, 200)
            - 失敗時: ({
                'success': False,
                'message': '密碼錯誤'
              }, 401)
            - 錯誤時: ({
                'success': False,
                'error': '錯誤訊息'
              }, 500)
    
    Note:
        - 管理員密碼從環境變數 ADMIN_PASSWORD 讀取
        - Token 使用簡單的隨機生成（生產環境應使用 JWT）
    
    Raises:
        Exception: 當環境變數未設定或其他系統錯誤時
    """
    try:
        data = request.get_json()
        password = data.get('password')
        
        # 從環境變數讀取管理員密碼（必須設定）
        admin_password = os.environ.get('ADMIN_PASSWORD')
        if not admin_password:
            logger.error("ADMIN_PASSWORD 環境變數未設定")
            return jsonify({'success': False, 'error': '伺服器設定錯誤'}), 500
        
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


@admin_bp.route('/admin/verify', methods=['POST'])
def admin_verify() -> Tuple[Response, int]:
    """管理員密碼驗證
    
    驗證管理員密碼是否正確（用於前端權限檢查）。
    
    Request Body:
        {
            "password": str  # 管理員密碼（選填，空字串視為驗證失敗）
        }
    
    Returns:
        Tuple[Response, int]: JSON 響應和 HTTP 狀態碼
            - 驗證成功: ({'success': True}, 200)
            - 驗證失敗: ({'success': False}, 200)
            - 錯誤時: ({
                'success': False,
                'error': '錯誤訊息'
              }, 500)
    
    Note:
        - 無論驗證成功或失敗，都返回 200 狀態碼
        - 通過 success 欄位區分驗證結果
    
    Raises:
        Exception: 當環境變數未設定或其他系統錯誤時
    """
    try:
        data = request.get_json()
        password = data.get('password', '')
        
        # 從環境變數讀取管理員密碼
        admin_password = os.environ.get('ADMIN_PASSWORD')
        if not admin_password:
            logger.error("ADMIN_PASSWORD 環境變數未設定")
            return jsonify({'success': False, 'error': '伺服器設定錯誤'}), 500
        
        if password == admin_password:
            logger.info("管理員驗證成功")
            return jsonify({'success': True}), 200
        else:
            logger.warning("管理員驗證失敗：密碼錯誤")
            return jsonify({'success': False}), 200
    except Exception as e:
        logger.error(f"管理員驗證異常: {e}", exc_info=True)
        return jsonify({'success': False, 'error': str(e)}), 500


@admin_bp.route('/batch-borrow', methods=['POST'])
def batch_borrow() -> Tuple[Response, int]:
    """批次借出桌遊
    
    同時借出多個桌遊給指定社員。
    
    Request Body:
        {
            "game_names": List[str],  # 桌遊名稱列表（必填）
            "member_id": str          # 社員 ID（必填）
        }
    
    Returns:
        Tuple[Response, int]: JSON 響應和 HTTP 狀態碼
            - 成功時: ({
                'message': str,
                'success': True,
                'success_games': List[str],  # 成功借出的遊戲列表
                'failed_games': List[str]    # 失敗的遊戲列表
              }, 200)
            - 失敗時: ({
                'success': False,
                'error': '錯誤訊息'
              }, 400/500)
    
    Note:
        - 部分成功也會返回 success: True
        - 通過 success_games 和 failed_games 區分結果
    
    Raises:
        Exception: 當資料庫更新失敗或其他系統錯誤時
    """
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
def batch_return() -> Tuple[Response, int]:
    """批次歸還桌遊
    
    同時歸還多個桌遊。
    
    Request Body:
        {
            "game_names": List[str]  # 桌遊名稱列表（必填）
        }
    
    Returns:
        Tuple[Response, int]: JSON 響應和 HTTP 狀態碼
            - 成功時: ({
                'message': str,
                'success': True,
                'success_games': List[str],  # 成功歸還的遊戲列表
                'failed_games': List[str]    # 失敗的遊戲列表
              }, 200)
            - 失敗時: ({
                'success': False,
                'error': '錯誤訊息'
              }, 400/500)
    
    Note:
        - 部分成功也會返回 success: True
        - 通過 success_games 和 failed_games 區分結果
    
    Raises:
        Exception: 當資料庫更新失敗或其他系統錯誤時
    """
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
