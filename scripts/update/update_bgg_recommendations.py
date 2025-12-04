"""
BGG 推薦清單更新腳本
定期運行此腳本來更新 Google Sheet 中的 BGG 熱門桌遊推薦清單
"""
import os
import logging
import time
from datetime import datetime
import sys

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from boardgame_system import BoardGameManager
from core.bgg_service import BGGService
from core.bgg_ranks_service import BGGRanksService
from core.sheets_client import SheetsClient

# 嘗試導入 update_static_cache，如果失敗則定義為 None
try:
    from update_static_cache import update_static_cache
except ImportError:
    update_static_cache = None

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# 分類配置（從本地資料庫讀取）
CATEGORIES = ['party', 'strategy', 'family', 'children']



def update_club_recommendations(sheets_client):
    """更新社團熱門遊戲推薦（從本地資料庫讀取排名）"""
    logger.info("開始更新社團熱門遊戲推薦...")
    logger.info("[UPDATE] Starting Club Hot Games update (from local database)")
    
    mgr = BoardGameManager()
    ranks_service = BGGRanksService()
    local_games = mgr.load_data()
    
    # 建立社團遊戲的 BGG ID 集合
    club_bgg_ids = set()
    for game in local_games:
        bgg_id = game.get('bgg_id')
        if bgg_id:
            try:
                club_bgg_ids.add(int(bgg_id))
            except:
                pass
    
    logger.info(f"找到 {len(club_bgg_ids)} 個有 BGG ID 的社團遊戲")
    
    # 對每個分類進行搜尋（從本地資料庫讀取排名）
    success_count = 0
    for category in CATEGORIES:
        logger.info(f"正在處理社團 {category} 分類...")
        
        matched_ids = []
        
        # 從本地資料庫查詢該分類的排名資料（獲取更多以確保能找到 10 款社團遊戲）
        games = ranks_service.get_by_category_rank(category, limit=100)
        
        if not games:
            logger.warning(f"{category} 分類未找到遊戲資料")
            continue
        
        logger.info(f"  從資料庫獲取了 {len(games)} 個 {category} 遊戲")
        
        # 找出社團擁有的遊戲（按 BGG 排名順序）
        for game in games:
            game_id = game['bgg_id']
            if game_id in club_bgg_ids:
                if game_id not in matched_ids:  # 避免重複
                    matched_ids.append(game_id)
                    logger.info(f"  找到匹配: BGG ID {game_id} ({game['name']})")
                    
                    if len(matched_ids) >= 10:
                        logger.info(f"  已找到 10 款遊戲，停止搜尋")
                        break
        
        logger.info(f"  累計找到 {len(matched_ids)} 款社團擁有的遊戲")
        
        # 儲存到 Google Sheet
        sheet_category = f"club-{category}"
        if sheets_client.save_bgg_recommendations(sheet_category, matched_ids):
            logger.info(f"✅ 社團 {category} 完成 - {len(matched_ids)} 個遊戲")
            success_count += 1
        else:
            logger.error(f"❌ 社團 {category} 儲存失敗")
    
    return success_count

def update_bgg_recommendations(sheets_client):
    """更新 BGG 全球熱門推薦（從本地資料庫讀取）"""
    logger.info("開始更新 BGG 全球熱門推薦...")
    logger.info("[UPDATE] Starting BGG Hot Games update (from local database)")
    
    ranks_service = BGGRanksService()
    success_count = 0
    
    for category in CATEGORIES:
        logger.info(f"正在從本地資料庫獲取 {category} 分類...")
        
        # 從本地資料庫查詢該分類的排名資料
        games = ranks_service.get_by_category_rank(category, limit=10)
        
        if not games:
            logger.warning(f"{category} 分類未找到遊戲資料")
            continue
        
        # 提取 BGG ID
        game_ids = [game['bgg_id'] for game in games]
        logger.info(f"  找到 {len(game_ids)} 個 {category} 遊戲 ID")
        
        # 儲存到 Google Sheet (使用 bgg- 前綴區分)
        sheet_category = f"bgg-{category}"
        if sheets_client.save_bgg_recommendations(sheet_category, game_ids):
            logger.info(f"✅ BGG {category} 完成 - {len(game_ids)} 個遊戲")
            success_count += 1
        else:
            logger.error(f"❌ BGG {category} 儲存失敗")
            
    return success_count

def main():
    """主函數"""
    logger.info("=" * 60)
    logger.info("開始更新 BGG 推薦清單至 Google Sheet")
    logger.info("=" * 60)
    
    sheets_client = SheetsClient()
    if not sheets_client.valid:
        logger.error("無法連接到 Google Sheets，請檢查憑證")
        return 1
        
    # 更新 BGG 全球熱門
    bgg_success = update_bgg_recommendations(sheets_client)
    
    # 更新社團熱門
    club_success = update_club_recommendations(sheets_client)
    
    logger.info("=" * 60)
    logger.info(f"完成！")
    logger.info(f"BGG 全球熱門更新: {bgg_success}/{len(CATEGORIES)}")
    logger.info(f"社團熱門更新: {club_success}/{len(CATEGORIES)}")
    logger.info("=" * 60)
    
    # 自動更新靜態緩存
    logger.info("")
    logger.info("=" * 60)
    logger.info("自動更新靜態緩存...")
    logger.info("=" * 60)
    
    try:
        update_static_cache()
        logger.info("✅ 靜態緩存更新成功")
    except Exception as e:
        logger.error(f"❌ 靜態緩存更新失敗: {e}")
        logger.warning("建議手動運行 update_static_cache.py")
    
    return 0

if __name__ == '__main__':
    exit(main())
