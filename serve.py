"""
應用程式伺服器入口點
支援開發與生產環境
- 開發環境：使用 Flask 內建伺服器（設定 FLASK_ENV=development）
- 生產環境：使用 Waitress WSGI 伺服器（預設）
"""
from waitress import serve
from app import create_app
import logging
import os

# 設定 logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

if __name__ == '__main__':
    # 檢查環境變數
    flask_env = os.getenv('FLASK_ENV', 'production').lower()
    
    # 根據環境建立應用程式
    if flask_env == 'development':
        app = create_app('development')
    else:
        app = create_app('production')
    
    host = app.config.get('HOST', '0.0.0.0')
    port = app.config.get('PORT', 5000)
    
    # 根據環境選擇伺服器
    if flask_env == 'development':
        print(f"🔧 Starting Flask development server on http://localhost:{port}")
        logger.info(f"Starting Flask development server on {host}:{port}")
        app.run(host=host, port=port, debug=True)
    else:
        print(f"🚀 Starting Waitress production server on http://localhost:{port}")
        logger.info(f"Starting Waitress production server on {host}:{port}")
        serve(app, host=host, port=port, threads=6)

