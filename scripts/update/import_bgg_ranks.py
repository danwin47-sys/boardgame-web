"""
BGG Ranks CSV Import Script
將 BGG ranks CSV 檔案導入到 SQLite 資料庫
"""
import csv
import sqlite3
import argparse
from typing import Optional
from datetime import datetime
from pathlib import Path
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def create_database(db_path: str):
    """創建資料庫和表結構"""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # 創建表
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS bgg_ranks (
            bgg_id INTEGER PRIMARY KEY,
            name TEXT NOT NULL,
            year_published INTEGER,
            rank INTEGER,
            bayes_average REAL,
            average REAL,
            users_rated INTEGER,
            is_expansion INTEGER,
            abstracts_rank INTEGER,
            cgs_rank INTEGER,
            childrensgames_rank INTEGER,
            familygames_rank INTEGER,
            partygames_rank INTEGER,
            strategygames_rank INTEGER,
            thematic_rank INTEGER,
            wargames_rank INTEGER,
            updated_date TEXT
        )
    ''')
    
    # 創建索引
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_name ON bgg_ranks(name)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_rank ON bgg_ranks(rank)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_strategygames_rank ON bgg_ranks(strategygames_rank)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_familygames_rank ON bgg_ranks(familygames_rank)')
    
    conn.commit()
    conn.close()
    logger.info(f"Database created: {db_path}")


def parse_int(value: str) -> Optional[int]:
    """安全解析整數"""
    if not value or value.strip() == '':
        return None
    try:
        return int(value)
    except ValueError:
        return None


def parse_float(value: str) -> Optional[float]:
    """安全解析浮點數"""
    if not value or value.strip() == '':
        return None
    try:
        return float(value)
    except ValueError:
        return None


def import_csv(csv_path: str, db_path: str, batch_size: int = 1000):
    """
    導入 CSV 檔案到資料庫
    
    Args:
        csv_path: CSV 檔案路徑
        db_path: SQLite 資料庫路徑
        batch_size: 批次插入大小
    """
    logger.info(f"Starting import from {csv_path}")
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # 清空現有數據
    cursor.execute('DELETE FROM bgg_ranks')
    logger.info("Cleared existing data")
    
    # 讀取 CSV
    records = []
    total_count = 0
    error_count = 0
    current_date = datetime.now().isoformat()
    
    try:
        with open(csv_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            
            for row in reader:
                try:
                    record = (
                        parse_int(row['id']),
                        row['name'],
                        parse_int(row['yearpublished']),
                        parse_int(row['rank']),
                        parse_float(row['bayesaverage']),
                        parse_float(row['average']),
                        parse_int(row['usersrated']),
                        parse_int(row['is_expansion']),
                        parse_int(row['abstracts_rank']),
                        parse_int(row['cgs_rank']),
                        parse_int(row['childrensgames_rank']),
                        parse_int(row['familygames_rank']),
                        parse_int(row['partygames_rank']),
                        parse_int(row['strategygames_rank']),
                        parse_int(row['thematic_rank']),
                        parse_int(row['wargames_rank']),
                        current_date
                    )
                    
                    records.append(record)
                    total_count += 1
                    
                    # 批次插入
                    if len(records) >= batch_size:
                        cursor.executemany('''
                            INSERT OR REPLACE INTO bgg_ranks VALUES 
                            (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                        ''', records)
                        conn.commit()
                        logger.info(f"Imported {total_count} records...")
                        records = []
                
                except Exception as e:
                    logger.error(f"Error processing row: {row.get('id', 'unknown')}: {e}")
                    error_count += 1
                    continue
            
            # 插入剩餘記錄
            if records:
                cursor.executemany('''
                    INSERT OR REPLACE INTO bgg_ranks VALUES 
                    (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', records)
                conn.commit()
        
        conn.close()
        
        logger.info("=" * 60)
        logger.info(f"✅ Import completed!")
        logger.info(f"Total records imported: {total_count}")
        logger.info(f"Errors: {error_count}")
        logger.info(f"Database: {db_path}")
        logger.info("=" * 60)
        
        return total_count, error_count
    
    except Exception as e:
        logger.error(f"Fatal error during import: {e}")
        conn.close()
        raise


def main():
    """主程式"""
    parser = argparse.ArgumentParser(description='Import BGG ranks CSV to SQLite')
    parser.add_argument('csv_file', help='Path to BGG ranks CSV file')
    parser.add_argument('--db', default=None, help='Path to SQLite database (default: data/bgg_ranks/bgg_ranks.db)')
    parser.add_argument('--batch-size', type=int, default=1000, help='Batch size for inserts (default: 1000)')
    
    args = parser.parse_args()
    
    # 確定資料庫路徑
    if args.db:
        db_path = args.db
    else:
        # 預設路徑
        base_dir = Path(__file__).parent.parent.parent
        db_path = base_dir / 'data' / 'bgg_ranks' / 'bgg_ranks.db'
        db_path.parent.mkdir(parents=True, exist_ok=True)
    
    db_path = str(db_path)
    
    # 創建資料庫結構
    create_database(db_path)
    
    # 導入數據
    import_csv(args.csv_file, db_path, args.batch_size)


if __name__ == '__main__':
    main()
