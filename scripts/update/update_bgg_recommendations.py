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
from core.sheets_client import SheetsClient

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# 分類配置（使用只返回 ID 的方法）
CATEGORIES = {
    'party': 'get_party_game_ids',
    'strategy': 'get_strategy_game_ids',
    'family': 'get_family_game_ids',
    'children': 'get_children_game_ids'
}

# Club 分類配置
CLUB_CATEGORIES = ['party', 'strategy', 'family', 'children']



def update_club_recommendations(sheets_client):
    """更新社團熱門遊戲推薦（使用 ID 列表，不呼叫 BGG API）"""
    logger.info("開始更新社團熱門遊戲推薦...")
    logger.info("[UPDATE] Starting Club Hot Games update")
    
    mgr = BoardGameManager()
    bgg = BGGService()
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
    
    # 對每個分類進行搜尋（直接使用 ID 列表，不呼叫 API）
    success_count = 0
    for category in CLUB_CATEGORIES:
        logger.info(f"正在處理社團 {category} 分類...")
        
        matched_ids = []
        
        # 獲取對應的 BGG Service 方法（ID 列表方法）
        method_name = CATEGORIES.get(category)
        if not method_name:
            logger.warning(f"找不到 {category} 對應的 BGG 方法")
            continue
        
        method = getattr(bgg, method_name)
        
        # 直接獲取所有遊戲 ID（不呼叫 API）
        all_game_ids = method(limit=100)  # 獲取最多 100 個 ID
        
        if not all_game_ids:
            logger.warning(f"{category} 分類未獲取到遊戲 ID")
            continue
        
        logger.info(f"  從 BGG 列表獲取了 {len(all_game_ids)} 個 {category} 遊戲 ID")
        
        # 找出社團擁有的遊戲
        for game_id in all_game_ids:
            if game_id in club_bgg_ids:
                if game_id not in matched_ids:  # 避免重複
                    matched_ids.append(game_id)
                    logger.info(f"  找到匹配: BGG ID {game_id}")
                    
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
    """更新 BGG 全球熱門推薦"""
    logger.info("開始更新 BGG 全球熱門推薦...")
    logger.info("[UPDATE] Starting BGG Hot Games update")
    
    bgg = BGGService()
    success_count = 0
    
    for category, method_name in CATEGORIES.items():
        logger.info(f"正在獲取 {category} 分類...")
        
        method = getattr(bgg, method_name)
        game_ids = method(limit=10)  # 直接獲取 ID 列表，不呼叫 API
        
        if not game_ids:
            logger.warning(f"{category} 分類未獲取到遊戲 ID")
            continue
        
        logger.info(f"  獲取了 {len(game_ids)} 個 {category} 遊戲 ID")
        
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
    logger.info(f"社團熱門更新: {club_success}/{len(CLUB_CATEGORIES)}")
    logger.info("=" * 60)
    
    return 0

if __name__ == '__main__':
    exit(main())
