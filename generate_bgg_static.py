"""
BGG 推薦靜態 JSON 生成器
定期運行此腳本來更新 BGG 熱門桌遊的靜態 JSON 文件
"""
import os
import json
import logging
from datetime import datetime
from boardgame_system import BoardGameManager
from core.bgg_service import BGGService

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# 靜態文件輸出目錄
OUTPUT_DIR = os.path.join('static', 'data')

# 分類配置
CATEGORIES = {
    'party': 'get_party_games',
    'strategy': 'get_strategy_games',
    'family': 'get_family_games',
    'children': 'get_children_games'
}

def ensure_output_dir():
    """確保輸出目錄存在"""
    if not os.path.exists(OUTPUT_DIR):
        os.makedirs(OUTPUT_DIR)
        logger.info(f"創建輸出目錄: {OUTPUT_DIR}")

def get_chinese_name_mapping():
    """獲取 BGG ID 到中文名稱的映射"""
    mgr = BoardGameManager()
    internal_games = mgr.load_data()
    
    bgg_id_to_chinese = {}
    for game in internal_games:
        bgg_id = game.get('bgg_id')
        chinese_name = game.get('name')
        if bgg_id and chinese_name:
            try:
                bgg_id_to_chinese[int(bgg_id)] = chinese_name
            except (ValueError, TypeError):
                continue
    
    logger.info(f"載入 {len(bgg_id_to_chinese)} 個 BGG ID 映射")
    return bgg_id_to_chinese

def generate_category_json(category, limit=10):
    """生成單個分類的 JSON 文件"""
    logger.info(f"正在生成 {category} 分類...")
    
    # 初始化服務
    bgg = BGGService()
    
    # 獲取遊戲數據
    method_name = CATEGORIES[category]
    method = getattr(bgg, method_name)
    games = method(limit)
    
    if not games:
        logger.warning(f"{category} 分類未獲取到遊戲數據")
        return False
    
    # 加入中文名稱映射
    chinese_mapping = get_chinese_name_mapping()
    for game in games:
        game_id = game.get('id')
        if game_id in chinese_mapping:
            game['chinese_name'] = chinese_mapping[game_id]
    
    # 準備輸出數據
    output_data = {
        'category': category,
        'updated_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'count': len(games),
        'games': games
    }
    
    # 寫入 JSON 文件
    output_file = os.path.join(OUTPUT_DIR, f'bgg-{category}.json')
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(output_data, f, ensure_ascii=False, indent=2)
    
    logger.info(f"✅ {category} 完成 - {len(games)} 個遊戲 - 輸出: {output_file}")
    return True

def main():
    """主函數"""
    logger.info("=" * 60)
    logger.info("開始生成 BGG 推薦靜態 JSON 文件")
    logger.info("=" * 60)
    
    # 確保輸出目錄存在
    ensure_output_dir()
    
    # 生成各分類的 JSON
    success_count = 0
    for category in CATEGORIES.keys():
        try:
            if generate_category_json(category):
                success_count += 1
        except Exception as e:
            logger.error(f"生成 {category} 時發生錯誤: {e}", exc_info=True)
    
    # 輸出總結
    logger.info("=" * 60)
    logger.info(f"完成！成功生成 {success_count}/{len(CATEGORIES)} 個分類")
    logger.info(f"輸出目錄: {os.path.abspath(OUTPUT_DIR)}")
    logger.info("=" * 60)
    
    if success_count == len(CATEGORIES):
        logger.info("🎉 所有分類生成成功！")
        return 0
    else:
        logger.warning("⚠️ 部分分類生成失敗，請檢查日誌")
        return 1

if __name__ == '__main__':
    exit(main())
