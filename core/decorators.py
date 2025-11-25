# coding: utf-8
"""
Flask 裝飾器模組
提供請求驗證和錯誤處理的裝飾器
"""
from functools import wraps
from flask import request, jsonify
from typing import Callable, Any


def validate_json(f: Callable) -> Callable:
    """
    驗證請求包含 JSON 資料
    
    使用範例:
        @app.route('/api/endpoint', methods=['POST'])
        @validate_json
        def endpoint():
            data = request.get_json()
            ...
    """
    @wraps(f)
    def decorated_function(*args: Any, **kwargs: Any):
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        return f(*args, **kwargs)
    return decorated_function


def validate_fields(*required_fields: str) -> Callable:
    """
    驗證必要欄位存在
    
    Args:
        required_fields: 必要的欄位名稱列表
    
    使用範例:
        @app.route('/api/borrow', methods=['POST'])
        @validate_json
        @validate_fields('name', 'member_id')
        def borrow_game():
            data = request.get_json()
            # 保證 data['name'] 和 data['member_id'] 存在
            ...
    """
    def decorator(f: Callable) -> Callable:
        @wraps(f)
        def decorated_function(*args: Any, **kwargs: Any):
            data = request.get_json()
            missing = [field for field in required_fields if not data.get(field)]
            if missing:
                return jsonify({'error': f'Missing fields: {", ".join(missing)}'}), 400
            return f(*args, **kwargs)
        return decorated_function
    return decorator


def handle_exceptions(f: Callable) -> Callable:
    """
    統一處理自定義異常
    
    將自定義異常轉換為適當的 JSON 響應
    
    使用範例:
        @app.route('/api/endpoint')
        @handle_exceptions
        def endpoint():
            # 可能拋出自定義異常
            raise GameNotFoundException("Catan")
    """
    @wraps(f)
    def decorated_function(*args: Any, **kwargs: Any):
        try:
            return f(*args, **kwargs)
        except Exception as e:
            # 這裡可以根據不同異常類型返回不同的狀態碼
            from .exceptions import (
                BoardGameException,
                GameNotFoundException,
                MemberNotFoundException,
                GameAlreadyBorrowedException
            )
            
            if isinstance(e, (GameNotFoundException, MemberNotFoundException)):
                return jsonify({'error': str(e), 'success': False}), 404
            elif isinstance(e, GameAlreadyBorrowedException):
                return jsonify({'error': str(e), 'success': False}), 409
            elif isinstance(e, BoardGameException):
                return jsonify({'error': str(e), 'success': False}), 400
            else:
                # 未預期的錯誤
                print(f"Unexpected error: {e}")
                return jsonify({'error': '系統錯誤', 'success': False}), 500
    return decorated_function
