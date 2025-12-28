"""
測試 app/middleware/error_handlers.py 模組
"""
import pytest
from flask import Flask

from app.middleware.error_handlers import register_error_handlers
from core.exceptions import (
    GameNotFoundException,
    MemberNotFoundException,
    GameAlreadyBorrowedException,
    ValidationError
)


@pytest.fixture
def app():
    """建立測試 Flask 應用"""
    app = Flask(__name__)
    app.config['TESTING'] = True
    register_error_handlers(app)
    return app


class TestErrorHandlers:
    """測試全域錯誤處理器"""
    
    def test_404_api_request(self, app):
        """測試 API 路徑的 404 錯誤"""
        with app.test_client() as client:
            response = client.get('/api/nonexistent')
            assert response.status_code == 404
            data = response.get_json()
            assert data['success'] is False
            assert 'error_code' in data
    
    def test_404_page_request(self, app):
        """測試一般頁面的 404 錯誤"""
        with app.test_client() as client:
            response = client.get('/nonexistent')
            assert response.status_code == 404
            # 一般頁面返回 HTML
            assert b'404' in response.data
    
    def test_boardgame_exception_handler(self, app):
        """測試 BoardGameException 處理"""
        @app.route('/test-game-not-found')
        def test_game_not_found():
            raise GameNotFoundException("卡坦島")
        
        with app.test_client() as client:
            response = client.get('/test-game-not-found')
            assert response.status_code == 404
            data = response.get_json()
            assert data['success'] is False
            assert data['error_code'] == 'GAME_NOT_FOUND'
    
    def test_member_not_found_exception(self, app):
        """測試 MemberNotFoundException 處理"""
        @app.route('/test-member-not-found')
        def test_member_not_found():
            raise MemberNotFoundException("A001")
        
        with app.test_client() as client:
            response = client.get('/test-member-not-found')
            assert response.status_code == 404
            data = response.get_json()
            assert data['error_code'] == 'MEMBER_NOT_FOUND'
    
    def test_game_already_borrowed_exception(self, app):
        """測試 GameAlreadyBorrowedException 處理"""
        @app.route('/test-already-borrowed')
        def test_already_borrowed():
            raise GameAlreadyBorrowedException("卡坦島", "張三")
        
        with app.test_client() as client:
            response = client.get('/test-already-borrowed')
            assert response.status_code == 409
            data = response.get_json()
            assert data['error_code'] == 'GAME_ALREADY_BORROWED'
    
    def test_validation_error_exception(self, app):
        """測試 ValidationError 處理"""
        @app.route('/test-validation')
        def test_validation():
            raise ValidationError("缺少必要參數")
        
        with app.test_client() as client:
            response = client.get('/test-validation')
            assert response.status_code == 400
            data = response.get_json()
            assert data['error_code'] == 'VALIDATION_ERROR'

    def test_internal_error_handler(self, app):
        """測試 500 內部錯誤處理"""
        @app.route('/trigger-500')
        def trigger_500():
            raise Exception("Unexpected error")
            
        with app.test_client() as client:
            response = client.get('/trigger-500')
            assert response.status_code == 500
            data = response.get_json()
            assert data['error_code'] == 'INTERNAL_ERROR'

    def test_bad_request_handler(self, app):
        """測試 400 Bad Request 處理"""
        @app.route('/trigger-400')
        def trigger_400():
            from flask import abort
            abort(400)
            
        with app.test_client() as client:
            response = client.get('/trigger-400')
            assert response.status_code == 400
            data = response.get_json()
            assert data['error_code'] == 'BAD_REQUEST'
