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

# 分類配置
CATEGORIES = {
    'party': 'get_party_games',
    'strategy': 'get_strategy_games',
    'family': 'get_family_games',
    'children': 'get_children_games'
}

# Club 分類配置
CLUB_CATEGORIES = ['party', 'strategy', 'family', 'children']

def classify_game(game_details):
    """將遊戲分類"""
    categories = []
    
    # 檢查遊戲類別和機制
    game_cats = [c.lower() for c in game_details.get('categories', [])]
    
    # Party: 派對遊戲
    if 'party game' in game_cats or 'party' in game_cats:
        categories.append('party')
        
    # Strategy: 策略遊戲
    if 'strategy game' in game_cats or 'strategy' in game_cats or 'economic' in game_cats:
        categories.append('strategy')
        
    # Family: 家庭遊戲
    if 'family game' in game_cats or 'family' in game_cats:
        categories.append('family')
        
    # Children: 兒童遊戲
    if "children's game" in game_cats or 'children' in game_cats:
        categories.append('children')
        
    return categories

def update_club_recommendations(sheets_client):
    """更新社團熱門遊戲推薦"""
    logger.info("開始更新社團熱門遊戲推薦...")
    logger.info("[UPDATE] Starting Club Hot Games update")
    
    mgr = BoardGameManager()
    bgg = BGGService()
    local_games = mgr.load_data()
    
    # 收集所有有 BGG ID 的遊戲
    games_to_fetch = []
    for game in local_games:
        bgg_id = game.get('bgg_id')
        if bgg_id:
            try:
                games_to_fetch.append(int(bgg_id))
            except:
                pass
    
    logger.info(f"找到 {len(games_to_fetch)} 個有 BGG ID 的社團遊戲")
    
    # 獲取詳細資訊並分類
    categorized_games = {cat: [] for cat in CLUB_CATEGORIES}
    
    count = 0
    for bgg_id in games_to_fetch:
        details = bgg.get_game_details(bgg_id)
        if details:
            cats = classify_game(details)
            for cat in cats:
                if cat in categorized_games:
                    categorized_games[cat].append(details)
            count += 1
            if count % 10 == 0:
                logger.info(f"已處理 {count} 個遊戲...")
                time.sleep(1) # 避免 API 限制

    # 排序並儲存
    success_count = 0
    for category, games in categorized_games.items():
        # 依排名排序 (rank 越小越前面，排除 None)
        games.sort(key=lambda x: x.get('rank') if x.get('rank') else 999999)
        
        # 取前 10 名的 ID
        top_game_ids = [g['id'] for g in games[:10]]
        
        # 儲存到 Google Sheet (使用 club- 前綴區分)
        sheet_category = f"club-{category}"
        if sheets_client.save_bgg_recommendations(sheet_category, top_game_ids):
            logger.info(f"✅ 社團 {category} 完成 - {len(top_game_ids)} 個遊戲")
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
        games = method(10) # 取前 10 名
        
        if not games:
            logger.warning(f"{category} 分類未獲取到遊戲數據")
            continue
            
        game_ids = [g['id'] for g in games]
        
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
