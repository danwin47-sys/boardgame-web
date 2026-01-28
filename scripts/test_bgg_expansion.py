#!/usr/bin/env python3
"""
測試 BGG API 對 Terraforming Mars: Ares Expedition – Discovery 的回應
用於除錯擴充判斷邏輯
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# 載入 .env 檔案
from dotenv import load_dotenv

load_dotenv()

import json

from core.bgg_api_client import BGGApiClient

# 從環境變數讀取 BGG Token
bgg_token = os.getenv("BGG_API_TOKEN", "")

if not bgg_token:
    print("警告: 未設定 BGG_API_TOKEN 環境變數")
    print("請在 .env 檔案中設定 BGG_API_TOKEN")
    sys.exit(1)

# 初始化 BGG API 客戶端
client = BGGApiClient(api_token=bgg_token)

# 測試遊戲
test_games = [
    (358740, "Terraforming Mars: Ares Expedition – Discovery"),
    (358738, "Terraforming Mars: Ares Expedition – Crisis"),
    (346842, "Terraforming Mars: Ares Expedition"),  # 主遊戲
]

for game_id, expected_name in test_games:
    print(f"\n{'='*80}")
    print(f"測試遊戲: {expected_name} (ID: {game_id})")
    print("=" * 80)

    result = client.game(game_id)

    if result:
        print(f"名稱: {result['name']}")
        print(f"Type: {result['type']}")
        print(f"是否為擴充: {result['is_expansion']}")
        print(f"主遊戲: {result.get('parent_game', 'N/A')}")
        print(f"\n類別 (Categories):")
        for cat in result.get("categories", []):
            print(f"  - {cat}")
    else:
        print("❌ 無法取得遊戲資訊")

print(f"\n{'='*80}")
print("測試完成")
