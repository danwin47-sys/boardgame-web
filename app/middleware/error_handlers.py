"""
全域錯誤處理器
統一處理應用程式的錯誤回應
"""
from flask import jsonify, render_template_string, request
import logging

from core.exceptions import BoardGameException

logger = logging.getLogger(__name__)


def register_error_handlers(app):
    """
    註冊全域錯誤處理器
    
    Args:
        app: Flask 應用程式實例
    """
    
    @app.errorhandler(BoardGameException)
    def handle_boardgame_exception(error):
        """處理所有 BoardGameException 子類別
        
        自動使用異常的 http_status_code 和 to_dict() 方法回應。
        """
        logger.warning(
            f"{error.error_code}: {error} "
            f"[{request.method} {request.path}]"
        )
        return jsonify(error.to_dict()), error.http_status_code
    
    @app.errorhandler(404)
    def not_found(error):
        """處理 404 錯誤"""
        logger.warning(f"404 錯誤: {request.path}")
        
        # API 請求返回 JSON
        if request.path.startswith('/api/'):
            return jsonify({
                'success': False,
                'error_code': 'NOT_FOUND',
                'message': '找不到請求的資源'
            }), 404
        
        # 一般頁面返回 HTML
        return render_template_string("""
            <!DOCTYPE html>
            <html>
            <head>
                <title>404 - 找不到頁面</title>
                <meta charset="utf-8">
                <style>
                    body { font-family: Arial, sans-serif; text-align: center; padding: 50px; }
                    h1 { color: #333; }
                    a { color: #007bff; text-decoration: none; }
                </style>
            </head>
            <body>
                <h1>404 - 找不到頁面</h1>
                <p>抱歉，您請求的頁面不存在。</p>
                <a href="/">返回首頁</a>
            </body>
            </html>
        """), 404
    
    @app.errorhandler(500)
    def internal_error(error):
        """處理 500 錯誤"""
        logger.error(f"500 錯誤: {error}", exc_info=True)
        
        return jsonify({
            'success': False,
            'error_code': 'INTERNAL_ERROR',
            'message': '伺服器內部錯誤'
        }), 500
    
    @app.errorhandler(400)
    def bad_request(error):
        """處理 400 錯誤"""
        logger.warning(f"400 錯誤: {error}")
        
        return jsonify({
            'success': False,
            'error_code': 'BAD_REQUEST',
            'message': '無效的請求'
        }), 400
    
    @app.errorhandler(Exception)
    def handle_exception(error):
        """處理所有未捕獲的異常"""
        logger.error(f"未捕獲的異常: {error}", exc_info=True)
        
        return jsonify({
            'success': False,
            'error_code': 'INTERNAL_ERROR',
            'message': '發生未預期的錯誤'
        }), 500
    
    logger.info("錯誤處理器已註冊")
