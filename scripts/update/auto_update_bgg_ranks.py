"""
BGG Ranks Complete Automation Script
完整的自動化流程：下載 → 導入 → 通知
"""
import argparse
import logging
import time
from pathlib import Path
from download_bgg_dumps import BGGDumpsDownloader
from import_bgg_ranks import import_csv, create_database
import sys
import os

# 添加 core 目錄到 Python 路徑
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from core.email_notifier import EmailNotifier
from core.bgg_ranks_service import BGGRanksService

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def run_automation(output_dir='data/bgg_ranks', notify_email=None, 
                   skip_download=False, csv_file=None):
    """
    執行完整的自動化流程
    
    Args:
        output_dir: 數據目錄
        notify_email: 通知郵箱
        skip_download: 跳過下載（使用現有檔案）
        csv_file: 指定 CSV 檔案路徑（如果跳過下載）
        
    Returns:
        是否成功
    """
    start_time = time.time()
    notifier = EmailNotifier() if notify_email else None
    
    try:
        # ===== 步驟 1: 下載數據 =====
        if not skip_download:
            logger.info("=" * 60)
            logger.info("步驟 1/3: 下載 BGG ranks 數據")
            logger.info("=" * 60)
            
            downloader = BGGDumpsDownloader()
            csv_file = downloader.download_latest(output_dir)
            
            if not csv_file:
                error_msg = "下載失敗"
                logger.error(error_msg)
                if notifier:
                    notifier.send_import_failure(notify_email, error_msg)
                return False
            
            logger.info(f"✅ 下載完成: {csv_file}")
            
            # 發送下載成功通知
            if notifier:
                file_size = Path(csv_file).stat().st_size
                notifier.send_download_success(notify_email, csv_file, file_size)
        
        else:
            logger.info("跳過下載步驟，使用現有檔案")
            if not csv_file:
                raise ValueError("必須指定 CSV 檔案路徑（--csv-file）")
        
        # ===== 步驟 2: 導入資料庫 =====
        logger.info("=" * 60)
        logger.info("步驟 2/3: 導入數據到 SQLite")
        logger.info("=" * 60)
        
        # 確定資料庫路徑
        db_path = Path(output_dir) / 'bgg_ranks.db'
        db_path.parent.mkdir(parents=True, exist_ok=True)
        
        # 創建資料庫結構
        create_database(str(db_path))
        
        # 導入數據
        import_start = time.time()
        total_records, errors = import_csv(csv_file, str(db_path))
        import_time = time.time() - import_start
        
        logger.info(f"✅ 導入完成: {total_records} 筆記錄，{errors} 個錯誤")
        
        # ===== 步驟 3: 獲取統計資訊 =====
        logger.info("=" * 60)
        logger.info("步驟 3/3: 獲取資料庫統計")
        logger.info("=" * 60)
        
        ranks_service = BGGRanksService(str(db_path))
        db_stats = ranks_service.get_stats()
        
        logger.info(f"總遊戲數: {db_stats.get('total_games', 0):,}")
        logger.info(f"有排名遊戲: {db_stats.get('ranked_games', 0):,}")
        logger.info(f"擴充數量: {db_stats.get('expansions', 0):,}")
        
        # ===== 完成 =====
        total_time = time.time() - start_time
        
        logger.info("=" * 60)
        logger.info("✅ 自動化流程完成！")
        logger.info(f"總耗時: {total_time:.2f} 秒")
        logger.info("=" * 60)
        
        # 發送成功通知
        if notifier:
            notifier.send_import_success(
                notify_email, 
                total_records, 
                errors, 
                import_time, 
                db_stats
            )
        
        return True
    
    except Exception as e:
        logger.error(f"❌ 自動化流程失敗: {e}", exc_info=True)
        
        # 發送失敗通知
        if notifier:
            notifier.send_import_failure(notify_email, str(e))
        
        return False


def main():
    """主程式"""
    parser = argparse.ArgumentParser(description='BGG Ranks 完整自動化流程')
    parser.add_argument('--output-dir', default='data/bgg_ranks', help='數據目錄')
    parser.add_argument('--notify-email', help='通知郵箱')
    parser.add_argument('--skip-download', action='store_true', help='跳過下載步驟')
    parser.add_argument('--csv-file', help='CSV 檔案路徑（如果跳過下載）')
    
    args = parser.parse_args()
    
    success = run_automation(
        output_dir=args.output_dir,
        notify_email=args.notify_email,
        skip_download=args.skip_download,
        csv_file=args.csv_file
    )
    
    exit(0 if success else 1)


if __name__ == '__main__':
    main()
