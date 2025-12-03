"""
生產環境伺服器入口點
使用 Waitress WSGI 伺服器
"""
from waitress import serve
from app import create_app
import logging

# 設定 logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("waitress")
logger.setLevel(logging.INFO)

if __name__ == '__main__':
    # 建立應用程式（生產環境）
    app = create_app('production')
    
    host = app.config.get('HOST', '0.0.0.0')
    port = app.config.get('PORT', 5000)
    
    print(f"Starting Waitress server on http://localhost:{port}")
    logger.info(f"Starting Waitress server on http://{host}:{port}")
    
    serve(app, host=host, port=port, threads=6)
