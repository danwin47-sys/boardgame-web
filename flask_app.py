"""
Flask 應用程式入口點
使用應用程式工廠模式建立應用程式
"""
from app import create_app
import logging

# 建立應用程式實例
app = create_app()

# 設定日誌
logger = logging.getLogger(__name__)

if __name__ == '__main__':
    host = app.config.get('HOST', '0.0.0.0')
    port = app.config.get('PORT', 5000)
    logger.info(f"啟動 Flask 應用於 {host}:{port}")
    app.run(host=host, port=port, debug=True)