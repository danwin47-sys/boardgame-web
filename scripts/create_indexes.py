#!/usr/bin/env python3
"""
SQLite 索引優化腳本

為 BGG Ranks 資料庫添加索引以提升查詢效能
"""
import sqlite3
import logging
from pathlib import Path

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def create_indexes():
    """建立資料庫索引"""
    # 資料庫路徑
    base_dir = Path(__file__).parent.parent
    db_path = base_dir / "data" / "bgg_ranks" / "bgg_ranks.db"
    
    if not db_path.exists():
        logger.error(f"資料庫檔案不存在: {db_path}")
        return False
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # 索引定義
        indexes = [
            ("idx_bgg_ranks_bgg_id", "bgg_ranks", "bgg_id", "BGG ID 查詢"),
            ("idx_bgg_ranks_rank", "bgg_ranks", "rank", "排名排序"),
            ("idx_bgg_ranks_name", "bgg_ranks", "name", "名稱搜尋"),
            ("idx_bgg_ranks_is_expansion", "bgg_ranks", "is_expansion", "擴充篩選"),
        ]
        
        created_count = 0
        skipped_count = 0
        
        for index_name, table_name, column_name, description in indexes:
            try:
                # 檢查索引是否已存在
                cursor.execute(
                    "SELECT name FROM sqlite_master WHERE type='index' AND name=?",
                    (index_name,)
                )
                if cursor.fetchone():
                    logger.info(f"⏭️  索引已存在: {index_name} ({description})")
                    skipped_count += 1
                    continue
                
                # 建立索引
                sql = f"CREATE INDEX IF NOT EXISTS {index_name} ON {table_name}({column_name})"
                cursor.execute(sql)
                logger.info(f"✅ 已建立索引: {index_name} ({description})")
                created_count += 1
                
            except Exception as e:
                logger.error(f"❌ 建立索引失敗 {index_name}: {e}")
        
        conn.commit()
        conn.close()
        
        logger.info(f"\n📊 索引建立完成:")
        logger.info(f"   新建: {created_count} 個")
        logger.info(f"   跳過: {skipped_count} 個")
        logger.info(f"   總計: {created_count + skipped_count} 個")
        
        return True
        
    except Exception as e:
        logger.error(f"資料庫連線失敗: {e}")
        return False


def verify_indexes():
    """驗證索引是否成功建立"""
    base_dir = Path(__file__).parent.parent
    db_path = base_dir / "data" / "bgg_ranks" / "bgg_ranks.db"
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # 列出所有索引
        cursor.execute(
            "SELECT name, tbl_name FROM sqlite_master WHERE type='index' AND tbl_name='bgg_ranks'"
        )
        indexes = cursor.fetchall()
        
        logger.info("\n📋 當前索引列表:")
        for idx_name, tbl_name in indexes:
            logger.info(f"   - {idx_name} (表格: {tbl_name})")
        
        conn.close()
        return True
        
    except Exception as e:
        logger.error(f"驗證失敗: {e}")
        return False


if __name__ == "__main__":
    logger.info("🚀 開始建立資料庫索引...")
    
    if create_indexes():
        logger.info("\n🔍 驗證索引...")
        verify_indexes()
        logger.info("\n✅ 索引優化完成！")
    else:
        logger.error("\n❌ 索引優化失敗")
