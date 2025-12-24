#!/usr/bin/env python3
"""
批次從 BGG 更新遊戲資訊

這個腳本會：
1. 載入所有有 BGG ID 的遊戲
2. 從 BGG API 獲取每個遊戲的詳細資訊
3. 更新 is_expansion 和 parent_game 欄位
4. 將更新後的資料寫回 Google Sheets

注意：由於 BGG API 有速率限制，此腳本會在每次請求之間等待 3 秒
"""

import sys
import os
import time
from dotenv import load_dotenv

# 載入環境變數
load_dotenv()

# 添加專案根目錄到 Python 路徑
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.facade import BoardGameManager
from core.bgg_api_client import BGGApiClient


def main():
    print("=" * 60)
    print("批次從 BGG 更新遊戲資訊")
    print("=" * 60)
    print()
    print("⚠️  注意：此腳本會在每次請求之間等待 3 秒以避免 API 限制")
    print(f"⚠️  預計總耗時：約 20 分鐘（假設有 400 個遊戲）")
    print()
    
    # 初始化管理器
    print("[1/5] 初始化系統...")
    mgr = BoardGameManager()
    
    # 初始化 BGG API Client 並確保載入 Bearer Token
    bgg_token = os.getenv('BGG_API_TOKEN')
    if not bgg_token:
        print("⚠️  警告：未找到 BGG_API_TOKEN 環境變數")
        print("   請確認 .env 檔案中有設定 BGG_API_TOKEN")
        return
    
    bgg_client = BGGApiClient(api_token=bgg_token)
    print(f"   ✓ BGG API Client 已初始化（使用 Bearer Token）")
    
    # 載入所有遊戲
    print("[2/5] 載入遊戲列表...")
    all_games = mgr.load_data()
    print(f"      總共 {len(all_games)} 個遊戲")
    
    # 篩選有 BGG ID 的遊戲
    games_with_bgg = [g for g in all_games if g.get('bgg_id')]
    print(f"      其中 {len(games_with_bgg)} 個有 BGG ID")
    print()
    
    if not games_with_bgg:
        print("沒有遊戲有 BGG ID，結束。")
        return
    
    # 確認是否繼續
    estimated_time = len(games_with_bgg) * 3 / 60  # 分鐘
    response = input(f"確定要更新這 {len(games_with_bgg)} 個遊戲嗎？(預計耗時 {estimated_time:.0f} 分鐘) (y/N): ")
    if response.lower() != 'y':
        print("已取消。")
        return
    
    print()
    print("[3/5] 從 BGG 獲取遊戲資訊...")
    print()
    
    # 建立 BGG ID 到遊戲名稱的映射（用於查找主遊戲的中文名稱）
    bgg_id_to_name = {str(g.get('bgg_id')): g.get('name') for g in all_games if g.get('bgg_id')}
    
    updated_count = 0
    skipped_count = 0
    error_count = 0
    
    for idx, game in enumerate(games_with_bgg, 1):
        game_name = game.get('name', 'Unknown')
        bgg_id = game.get('bgg_id')
        
        print(f"[{idx}/{len(games_with_bgg)}] {game_name} (BGG ID: {bgg_id})")
        
        try:
            # 從 BGG 獲取詳細資訊（直接使用 BGGApiClient 避免快取問題）
            game_info = bgg_client.game(game_id=bgg_id)
            
            if not game_info:
                print(f"      ⚠️  無法從 BGG 獲取資訊")
                error_count += 1
                # 等待更長時間後再繼續
                time.sleep(5)
                continue
            
            is_expansion = game_info.get('is_expansion', False)
            parent_game_bgg_id = game_info.get('parent_game_id')
            parent_game_name = game_info.get('parent_game', '')
            
            # 如果有 parent_game_id，嘗試找到中文名稱
            if parent_game_bgg_id and str(parent_game_bgg_id) in bgg_id_to_name:
                parent_game_name = bgg_id_to_name[str(parent_game_bgg_id)]
                print(f"      ✓ 找到主遊戲中文名稱: {parent_game_name}")
            
            # 檢查是否需要更新
            current_is_expansion = str(game.get('is_expansion', '')).strip().upper()
            current_parent = str(game.get('parent_game', '')).strip()
            
            new_is_expansion = is_expansion
            new_parent = parent_game_name if is_expansion else ''
            
            # 判斷是否需要更新
            needs_update = False
            
            if is_expansion:
                # 如果是擴充
                if current_is_expansion not in ('TRUE', '1') or current_parent != new_parent:
                    needs_update = True
            else:
                # 如果是主遊戲
                if current_is_expansion in ('TRUE', '1') or current_parent != '':
                    needs_update = True
            
            if not needs_update:
                print(f"      → 資料已是最新，跳過")
                skipped_count += 1
                # 即使跳過也要等待，避免請求過快
                time.sleep(3)
                continue
            
            # 更新到 Google Sheets
            print(f"      → 更新中...")
            print(f"         is_expansion: {current_is_expansion} → {'TRUE' if new_is_expansion else 'FALSE'}")
            if is_expansion:
                print(f"         parent_game: '{current_parent}' → '{new_parent}'")
            
            success = mgr.update_game_expansion_info(
                game_name=game_name,
                is_expansion=new_is_expansion,
                parent_game=new_parent,
                storage_mode=game.get('storage_mode', 'independent') if is_expansion else ''
            )
            
            if success:
                print(f"      ✓ 更新成功")
                updated_count += 1
            else:
                print(f"      ✗ 更新失敗")
                error_count += 1
            
            # 避免 API 請求過快 - 等待 3 秒
            print(f"      ⏱  等待 3 秒...")
            time.sleep(3)
            
        except KeyboardInterrupt:
            print()
            print("⚠️  使用者中斷")
            print(f"已處理 {idx}/{len(games_with_bgg)} 個遊戲")
            break
        except Exception as e:
            print(f"      ✗ 錯誤: {e}")
            error_count += 1
            # 發生錯誤時等待更長時間
            time.sleep(5)
        
        print()
    
    print()
    print("=" * 60)
    print("[4/5] 更新完成")
    print(f"      ✓ 成功更新: {updated_count} 個")
    print(f"      → 跳過（已是最新）: {skipped_count} 個")
    print(f"      ✗ 失敗/錯誤: {error_count} 個")
    print("=" * 60)
    print()
    print("[5/5] 重新載入資料以驗證...")
    
    # 重新載入資料
    mgr.client._games_cache = None  # 清除快取
    updated_games = mgr.load_data()
    
    # 統計擴充數量
    expansion_count = sum(1 for g in updated_games if str(g.get('is_expansion', '')).strip().upper() in ('TRUE', '1'))
    main_game_count = len(updated_games) - expansion_count
    
    print(f"      總遊戲數: {len(updated_games)}")
    print(f"      主遊戲: {main_game_count}")
    print(f"      擴充: {expansion_count}")
    print()
    print("✓ 批次更新完成！")


if __name__ == "__main__":
    main()
