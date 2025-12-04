"""
測試 BGGRanksService 查詢功能
"""
from core.bgg_ranks_service import BGGRanksService

def test_party_games():
    service = BGGRanksService()
    games = service.get_by_category_rank('party', 10)
    
    print(f"找到 {len(games)} 款派對遊戲")
    print("\n前5款遊戲：")
    for i, game in enumerate(games[:5]):
        print(f"{i+1}. {game['name']} (BGG ID: {game['bgg_id']}, Rank: {game['partygames_rank']})")
    
    return games

if __name__ == '__main__':
    test_party_games()
