"""
Test BGG Ranks Service
測試 BGG Ranks 查詢服務
"""
import sys
from pathlib import Path

# 添加專案根目錄到 Python 路徑
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from core.bgg_ranks_service import BGGRanksService


def test_service():
    """測試服務功能"""
    print("=" * 60)
    print("BGG Ranks Service 測試")
    print("=" * 60)
    
    service = BGGRanksService()
    
    # 1. 測試統計資訊
    print("\n1. 資料庫統計：")
    stats = service.get_stats()
    print(f"   總遊戲數: {stats.get('total_games', 0):,}")
    print(f"   有排名遊戲: {stats.get('ranked_games', 0):,}")
    print(f"   擴充數量: {stats.get('expansions', 0):,}")
    print(f"   最後更新: {stats.get('last_updated', 'N/A')}")
    
    # 2. 測試 Top 5 遊戲
    print("\n2. BGG Top 5 遊戲：")
    top5 = service.get_top_games(5)
    for game in top5:
        print(f"   {game['rank']:3d}. {game['name']:40s} ({game['year_published']}) - {game['average']:.2f}")
    
    # 3. 測試按 ID 查詢
    print("\n3. 按 ID 查詢（BGG ID: 224517）：")
    game = service.get_by_id(224517)
    if game:
        print(f"   名稱: {game['name']}")
        print(f"   排名: {game['rank']}")
        print(f"   評分: {game['average']}")
        print(f"   評分人數: {game['users_rated']:,}")
    
    # 4. 測試名稱搜尋
    print("\n4. 搜尋名稱包含 'Pandemic' 的遊戲：")
    results = service.search_by_name('Pandemic', limit=3)
    for game in results:
        rank_str = str(game['rank']) if game['rank'] else 'N/A'
        print(f"   {rank_str:>5s}. {game['name']:40s} - {game['average']:.2f}")
    
    # 5. 測試分類排名
    print("\n5. Strategy 遊戲 Top 3：")
    strategy_games = service.get_by_category_rank('strategy', limit=3)
    for game in strategy_games:
        print(f"   Strategy #{game['strategygames_rank']:3d}: {game['name']:40s}")
    
    print("\n" + "=" * 60)
    print("✅ 測試完成！")
    print("=" * 60)


if __name__ == '__main__':
    test_service()
