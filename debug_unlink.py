import logging
import sys
import os

# 配置 logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 確保可以導入 core 模組
sys.path.append(os.getcwd())

from core.sheets_client import SheetsClient

def test_unlink():
    client = SheetsClient()
    
    # 假設我們要測試的遊戲名稱
    # 這裡我們用 "Catan" 來測試，因為之前我們連結過它
    # 或者我們可以列出所有遊戲來看看 "蓋亞計畫" 的確切名稱
    
    print("Loading games...")
    games = client.load_games()
    
    target_game_name = "Gaia Project" # 假設是英文名
    found = False
    for game in games:
        if "Gaia" in game['name'] or "蓋亞" in game['name']:
            target_game_name = game['name']
            print(f"Found target game: {target_game_name}")
            print(f"Current BGG ID: {game.get('bgg_id')}")
            print(f"Current Thumbnail: {game.get('bgg_thumbnail')}")
            found = True
            break
    
    if not found:
        print("Could not find Gaia Project in the list.")
        return

    print(f"\nAttempting to unlink '{target_game_name}'...")
    
    # 呼叫 update_game_bgg_id，傳入 None 來取消連結
    # 注意：thumbnail_url 預設為 None，所以也會被清除
    success = client.update_game_bgg_id(target_game_name, None)
    
    if success:
        print("Unlink successful!")
        
        # 驗證是否真的清除了
        client.invalidate_games_cache()
        games = client.load_games()
        for game in games:
            if game['name'] == target_game_name:
                print(f"Verifying {target_game_name}:")
                print(f"BGG ID: '{game.get('bgg_id')}' (Should be empty string or None)")
                print(f"Thumbnail: '{game.get('bgg_thumbnail')}' (Should be empty string or None)")
                break
    else:
        print("Unlink failed.")

if __name__ == "__main__":
    test_unlink()
