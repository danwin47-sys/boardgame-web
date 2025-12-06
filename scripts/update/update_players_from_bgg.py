"""
批次更新已連結遊戲的玩家數資料

此腳本會：
1. 掃描所有已連結 BGG 的遊戲（有 bgg_id）
2. 從 BGG API 獲取玩家數資訊
3. 更新 Google Sheet 的 players 欄位
"""
from core.facade import BoardGameManager
from core.bgg_service import BGGService
import time
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def update_players_for_linked_games():
    """為所有已連結 BGG 的遊戲更新玩家數"""
    print("=" * 60)
    print("批次更新 BGG 玩家數資料")
    print("=" * 60)
    
    # 初始化服務
    logger.info("初始化服務...")
    logger.info("[UPDATE] Starting players update for linked games")
    mgr = BoardGameManager()
    bgg = BGGService()
    
    if not mgr.valid:
        logger.error("無法連接到 Google Sheets")
        return
    
    # 載入所有遊戲
    logger.info("載入遊戲列表...")
    games = mgr.load_data()
    
    # 篩選已連結 BGG 的遊戲
    linked_games = [g for g in games if g.get('bgg_id')]
    
    print(f"\n找到 {len(linked_games)} 個已連結 BGG 的遊戲")
    print(f"總共 {len(games)} 個遊戲")
    
    if not linked_games:
        print("沒有已連結的遊戲需要更新")
        return
    
    # 確認
    response = input(f"\n是否要更新這 {len(linked_games)} 個遊戲的玩家數? (y/n): ")
    if response.lower() != 'y':
        print("操作已取消")
        return
    
    # 開始更新
    print("\n開始更新...")
    success_count = 0
    error_count = 0
    skipped_count = 0
    
    for i, game in enumerate(linked_games, 1):
        game_name = game.get('name', 'Unknown')
        bgg_id = game.get('bgg_id')
        current_players = game.get('players', '')
        
        print(f"\n[{i}/{len(linked_games)}] 處理: {game_name}")
        print(f"  BGG ID: {bgg_id}")
        print(f"  目前玩家數: {current_players or '(空'}")
        
        try:
            # 獲取 BGG 詳情
            game_details = bgg.get_game_details(int(bgg_id))
            
            if not game_details:
                logger.warning(f"  ⚠️ 無法從 BGG 獲取遊戲詳情")
                error_count += 1
                continue
            
            players_display = game_details.get('players_display')
            
            if not players_display or players_display == 'N/A':
                logger.info(f"  ⏭️ BGG 沒有玩家數資訊，跳過")
                skipped_count += 1
                continue
            
            print(f"  BGG 玩家數: {players_display}")
            
            # 如果與目前值相同，跳過
            if current_players == players_display:
                logger.info(f"  ⏭️ 玩家數已是最新，跳過")
                skipped_count += 1
                continue
            
            # 更新 Google Sheet
            success = mgr.client.update_game_bgg_id(
                game_name,
                bgg_id, 
                None,  # 不更新 thumbnail
                None,  # 不更新 image
                players_display  # 只更新玩家數
            )
            
            if success:
                print(f"  ✅ 成功更新: {current_players or '(空)'} → {players_display}")
                success_count += 1
            else:
                print(f"  ❌ 更新失敗")
                error_count += 1
            
            # 避免 API 限流，稍微延遲
            if i < len(linked_games):
                time.sleep(0.5)
                
        except Exception as e:
            logger.error(f"  ❌ 處理失敗: {e}")
            error_count += 1
    
    # 總結
    print("\n" + "=" * 60)
    print("更新完成")
    print("=" * 60)
    print(f"成功: {success_count}")
    print(f"跳過: {skipped_count}")
    print(f"失敗: {error_count}")
    print(f"總計: {len(linked_games)}")
    print("=" * 60)

if __name__ == '__main__':
    try:
        update_players_for_linked_games()
    except KeyboardInterrupt:
        print("\n\n操作已中斷")
    except Exception as e:
        logger.error(f"發生錯誤: {e}", exc_info=True)
