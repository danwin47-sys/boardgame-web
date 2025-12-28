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
            from flask import abort
            abort(500)
            
        with app.test_client() as client:
            response = client.get('/trigger-500')
            assert response.status_code == 500
            data = response.get_json()
            assert data['error_code'] == 'INTERNAL_ERROR'

    def test_generic_exception_handler(self, app):
        """測試未捕獲的通用異常處理"""
        @app.route('/trigger-exception')
        def trigger_exc():
            raise Exception("Unexpected generic error")
            
        with app.test_client() as client:
            response = client.get('/trigger-exception')
            assert response.status_code == 500
            data = response.get_json()
            assert data['error_code'] == 'INTERNAL_ERROR'
            assert data['message'] == '發生未預期的錯誤'

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

    def test_static_path_500_raises(self, app):
        """測試靜態路徑下的 500 錯誤是否直接拋出應用程式錯誤"""
        # 手動模擬 500 錯誤在靜態路徑觸發
        @app.route('/static/test-trigger')
        def trigger_static_500():
            from flask import abort
            abort(500)
            
        with app.test_client() as client:
            # 在 Flask 測試模式下，handle_user_exception 會拋出異常
            # 我們預期它會穿過自定義處理器
            with pytest.raises(Exception):
                client.get('/static/test-trigger')

    def test_static_path_exception_raises(self, app):
        """測試靜態路徑下的未定義異常是否直接拋出"""
        @app.route('/css/test-trigger')
        def trigger_static_exc():
            raise Exception("Static exception")
            
        with app.test_client() as client:
            with pytest.raises(Exception):
                client.get('/css/test-trigger')
