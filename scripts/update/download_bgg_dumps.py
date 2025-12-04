"""
BGG Data Dumps Auto Downloader
自動下載 BGG ranks 數據檔案（需要處理登入）
"""
import requests
from requests.auth import HTTPBasicAuth
import os
from pathlib import Path
from datetime import datetime
import logging
import time
import zipfile
import io

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class BGGDumpsDownloader:
    """BGG Data Dumps 下載器"""
    
    BASE_URL = "https://boardgamegeek.com/data_dumps/bg_ranks"
    DOWNLOAD_URL_TEMPLATE = "https://boardgamegeek.com/data_dumps/download/bg_ranks/{date}"
    
    def __init__(self, username: str = None, password: str = None):
        """
        初始化下載器
        
        Args:
            username: BGG 用戶名（從環境變數讀取）
            password: BGG 密碼（從環境變數讀取）
        """
        self.username = username or os.getenv('BGG_USERNAME')
        self.password = password or os.getenv('BGG_PASSWORD')
        
        if not self.username or not self.password:
            logger.warning("BGG credentials not provided. Will try without authentication.")
        
        self.session = requests.Session()
        if self.username and self.password:
            self.session.auth = HTTPBasicAuth(self.username, self.password)
    
    def login(self):
        """
        登入 BGG（如果需要）
        
        Note: BGG data dumps 可能不需要登入，但保留此功能以防萬一
        """
        if not self.username or not self.password:
            logger.info("Skipping login (no credentials)")
            return True
        
        try:
            # BGG 登入端點（如果需要）
            login_url = "https://boardgamegeek.com/login"
            payload = {
                'username': self.username,
                'password': self.password
            }
            
            response = self.session.post(login_url, data=payload)
            
            if response.status_code == 200:
                logger.info("✅ Logged in to BGG")
                return True
            else:
                logger.error(f"❌ Login failed: {response.status_code}")
                return False
        
        except Exception as e:
            logger.error(f"Login error: {e}")
            return False
    
    def get_latest_dump_date(self):
        """
        獲取最新的 dumps 日期
        
        Returns:
            最新 dump 的日期字符串 (YYYY-MM-DD)
        """
        # BGG dumps 通常在每月 2 號更新
        today = datetime.now()
        
        # 如果今天是 2 號或之後，使用本月 2 號
        if today.day >= 2:
            dump_date = datetime(today.year, today.month, 2)
        else:
            # 否則使用上個月 2 號
            if today.month == 1:
                dump_date = datetime(today.year - 1, 12, 2)
            else:
                dump_date = datetime(today.year, today.month - 1, 2)
        
        return dump_date.strftime('%Y-%m-%d')
    
    def download_dump(self, output_dir: str, date: str = None):
        """
        下載 BGG ranks dump
        
        Args:
            output_dir: 輸出目錄
            date: 指定日期 (YYYY-MM-DD)，None 則使用最新日期
            
        Returns:
            下載的檔案路徑，失敗則返回 None
        """
        if date is None:
            date = self.get_latest_dump_date()
        
        logger.info(f"Downloading BGG ranks dump for {date}")
        
        # 構建下載 URL
        # 注意：實際 URL 可能需要根據 BGG 網站調整
        download_url = f"https://boardgamegeek.com/data_dumps/download/bg_ranks/{date}"
        
        try:
            response = self.session.get(download_url, stream=True, timeout=30)
            
            if response.status_code != 200:
                logger.error(f"Download failed: HTTP {response.status_code}")
                
                # 嘗試備用 URL 格式
                alt_url = f"https://boardgamegeek.com/data_dumps/bg_ranks/{date}.csv"
                logger.info(f"Trying alternative URL: {alt_url}")
                response = self.session.get(alt_url, stream=True, timeout=30)
                
                if response.status_code != 200:
                    logger.error(f"Alternative download also failed: HTTP {response.status_code}")
                    return None
            
            # 創建輸出目錄
            output_path = Path(output_dir)
            output_path.mkdir(parents=True, exist_ok=True)
            
            # 確定檔案名稱
            filename = f"boardgames_ranks_{date}.csv"
            filepath = output_path / filename
            
            # 儲存檔案
            with open(filepath, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
            
            file_size = filepath.stat().st_size
            logger.info(f"✅ Downloaded: {filepath} ({file_size:,} bytes)")
            
            return str(filepath)
        
        except Exception as e:
            logger.error(f"Download error: {e}")
            return None
    
    def download_latest(self, output_dir: str = 'data/bgg_ranks'):
        """
        下載最新的 BGG ranks dump
        
        Args:
            output_dir: 輸出目錄
            
        Returns:
            下載的檔案路徑
        """
        latest_date = self.get_latest_dump_date()
        return self.download_dump(output_dir, latest_date)


def main():
    """主程式"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Download BGG ranks data dumps')
    parser.add_argument('--output-dir', default='data/bgg_ranks', help='Output directory')
    parser.add_argument('--date', help='Specific date (YYYY-MM-DD), default: latest')
    parser.add_argument('--username', help='BGG username (or set BGG_USERNAME env var)')
    parser.add_argument('--password', help='BGG password (or set BGG_PASSWORD env var)')
    
    args = parser.parse_args()
    
    downloader = BGGDumpsDownloader(args.username, args.password)
    
    # 登入（如果需要）
    downloader.login()
    
    # 下載
    if args.date:
        filepath = downloader.download_dump(args.output_dir, args.date)
    else:
        filepath = downloader.download_latest(args.output_dir)
    
    if filepath:
        print(f"\n✅ Download completed: {filepath}")
    else:
        print("\n❌ Download failed")
        exit(1)


if __name__ == '__main__':
    main()
