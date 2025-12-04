import os
import time
import logging
from dotenv import load_dotenv
from core.sheets_client import SheetsClient
from core.bgg_service import BGGService

# 設定 logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def main():
    # 載入環境變數
    load_dotenv()
    
    logger.info("開始執行批次連結 BGG...")
    
    # 初始化服務
    try:
        sheets = SheetsClient()
        bgg = BGGService()
    except Exception as e:
        logger.error(f"初始化失敗: {e}")
        return

    # 讀取所有遊戲
    games = sheets.load_games()
    logger.info(f"共讀取到 {len(games)} 款遊戲")
    
    updated_count = 0
    skipped_count = 0
    failed_count = 0
    
    for i, game in enumerate(games):
        game_name = game.get('name')
        current_bgg_id = game.get('bgg_id')
        
        logger.info(f"[{i+1}/{len(games)}] 處理遊戲: {game_name}")
        
        try:
            # 情況 1: 已經有 BGG ID -> 更新圖片資料
            if current_bgg_id:
                logger.info(f"  - 已有 BGG ID ({current_bgg_id})，正在更新圖片資料...")
                details = bgg.get_game_details(int(current_bgg_id))
                
                if details:
                    sheets.update_game_bgg_id(
                        game_name, 
                        details['id'], 
                        details.get('thumbnail'), 
                        details.get('image')
                    )
                    updated_count += 1
                else:
                    logger.warning(f"  - 無法從 BGG 取得 ID {current_bgg_id} 的資料")
                    failed_count += 1
                    
            # 情況 2: 沒有 BGG ID -> 搜尋並連結
            else:
                logger.info(f"  - 無 BGG ID，正在搜尋...")
                results = bgg.search_games(game_name)
                
                if results:
                    # 選取第一個結果
                    first_match = results[0]
                    logger.info(f"  - 找到匹配: {first_match['name']} (ID: {first_match['id']})")
                    
                    # 取得詳細資料以獲取圖片
                    details = bgg.get_game_details(first_match['id'])
                    
                    if details:
                        sheets.update_game_bgg_id(
                            game_name, 
                            details['id'], 
                            details.get('thumbnail'), 
                            details.get('image')
                        )
                        updated_count += 1
                    else:
                        logger.warning(f"  - 無法取得詳細資料")
                        failed_count += 1
                else:
                    logger.warning(f"  - BGG 搜尋不到任何結果")
                    failed_count += 1
            
            # 避免觸發 API 限制
            time.sleep(1.5)
            
        except Exception as e:
            logger.error(f"  - 處理失敗: {e}")
            failed_count += 1
            
    logger.info("="*30)
    logger.info(f"處理完成!")
    logger.info(f"更新成功: {updated_count}")
    logger.info(f"失敗/未找到: {failed_count}")
    logger.info("="*30)

if __name__ == "__main__":
    main()
