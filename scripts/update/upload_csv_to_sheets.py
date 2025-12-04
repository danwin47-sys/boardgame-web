"""
Upload BGG Ranks CSV to Google Sheets
將 BGG Ranks CSV 數據直接上傳到 Google Sheets 分頁
"""
import csv
import sys
from pathlib import Path
import logging
import argparse
from datetime import datetime

# 添加專案根目錄到 Python 路徑
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from core.sheets_client import SheetsClient

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def upload_csv_to_sheet(csv_path: str, worksheet_name: str = 'BGG排名資料', 
                         batch_size: int = 1000):
    """
    上傳 CSV 到 Google Sheets
    
    Args:
        csv_path: CSV 檔案路徑
        worksheet_name: 工作表名稱
        batch_size: 批次大小
        
    Returns:
        是否成功
    """
    logger.info(f"開始上傳 {csv_path} 到 Google Sheets")
    logger.info(f"工作表名稱: {worksheet_name}")
    
    try:
        # 初始化 Sheets 客戶端
        client = SheetsClient()
        
        if not client.valid:
            logger.error("Google Sheets 連線失敗")
            return False
        
        # 讀取 CSV
        logger.info("讀取 CSV 檔案...")
        with open(csv_path, 'r', encoding='utf-8') as f:
            reader = csv.reader(f)
            data = list(reader)
        
        total_rows = len(data)
        logger.info(f"CSV 資料：{total_rows} 行 x {len(data[0])} 列")
        
        # 檢查是否已有此工作表
        try:
            ws = client.sh.worksheet(worksheet_name)
            logger.info(f"工作表 '{worksheet_name}' 已存在，將覆蓋數據")
            ws.clear()
        except:
            # 創建新工作表
            logger.info(f"創建新工作表 '{worksheet_name}'")
            ws = client.sh.add_worksheet(
                title=worksheet_name, 
                rows=total_rows + 100,  # 多給一些空間
                cols=len(data[0])
            )
        
        # 批次上傳數據
        logger.info(f"開始上傳數據（批次大小: {batch_size}）...")
        
        for i in range(0, total_rows, batch_size):
            batch_end = min(i + batch_size, total_rows)
            batch_data = data[i:batch_end]
            
            # 計算儲存格範圍
            start_row = i + 1
            end_row = batch_end
            start_col = 'A'
            end_col = chr(ord('A') + len(data[0]) - 1)
            
            cell_range = f'{start_col}{start_row}:{end_col}{end_row}'
            
            # 更新數據
            ws.update(cell_range, batch_data, value_input_option='RAW')
            
            logger.info(f"已上傳 {batch_end}/{total_rows} 行 ({batch_end/total_rows*100:.1f}%)")
        
        # 凍結標題行
        ws.freeze(rows=1)
        logger.info("已凍結標題行")
        
        # 成功
        logger.info("=" * 60)
        logger.info("✅ 上傳完成！")
        logger.info(f"工作表連結: {client.sh.url}")
        logger.info(f"總行數: {total_rows:,}")
        logger.info(f"總列數: {len(data[0])}")
        logger.info("=" * 60)
        
        return True
    
    except Exception as e:
        logger.error(f"❌ 上傳失敗: {e}", exc_info=True)
        return False


def main():
    """主程式"""
    parser = argparse.ArgumentParser(description='Upload BGG ranks CSV to Google Sheets')
    parser.add_argument('csv_file', help='Path to BGG ranks CSV file')
    parser.add_argument('--worksheet', default='BGG排名資料', help='Worksheet name (default: BGG排名資料)')
    parser.add_argument('--batch-size', type=int, default=1000, help='Batch size (default: 1000)')
    
    args = parser.parse_args()
    
    # 驗證檔案存在
    csv_path = Path(args.csv_file)
    if not csv_path.exists():
        print(f"❌ 檔案不存在: {args.csv_file}")
        exit(1)
    
    # 上傳
    success = upload_csv_to_sheet(
        str(csv_path),
        args.worksheet,
        args.batch_size
    )
    
    exit(0 if success else 1)


if __name__ == '__main__':
    main()
