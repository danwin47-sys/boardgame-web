from waitress import serve
from flask_app import app
from config import Config
import logging

# 設定 logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("waitress")
logger.setLevel(logging.INFO)

if __name__ == '__main__':
    host = Config.HOST
    port = Config.PORT
    
    print(f"Starting Waitress server on http://localhost:{port}")
    logger.info(f"Starting Waitress server on http://{host}:{port}")
    
    serve(app, host=host, port=port, threads=6)
