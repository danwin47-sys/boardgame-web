import logging
from boardgame_system import BoardGameManager
from core.bgg_service import BGGService

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def debug_club_games():
    mgr = BoardGameManager()
    bgg = BGGService()
    local_games = mgr.load_data()
    
    # Check for duplicates in local games
    bgg_ids = [g.get('bgg_id') for g in local_games if g.get('bgg_id')]
    unique_ids = set(bgg_ids)
    print(f"Total local games with BGG ID: {len(bgg_ids)}")
    print(f"Unique BGG IDs: {len(unique_ids)}")
    
    if len(bgg_ids) != len(unique_ids):
        print("Duplicates found in local games list!")
    
    # Fetch details for a sample of games to check categories
    print("\nChecking categories for first 20 unique games...")
    count = 0
    for bgg_id in list(unique_ids)[:20]:
        try:
            details = bgg.get_game_details(int(bgg_id))
            if details:
                cats = [c.lower() for c in details.get('categories', [])]
                ranks = details.get('rank')
                print(f"ID: {bgg_id}, Name: {details['name']}")
                print(f"  Categories: {cats}")
                print(f"  Rank: {ranks}")
                
                # Test classification
                is_family = 'family game' in cats or 'family' in cats
                print(f"  Is Family? {is_family}")
                
                if not is_family:
                    # Check if it *should* be family (heuristic)
                    # Maybe check 'subdomain' if available? BGGService doesn't seem to expose subdomain explicitly in 'categories' list usually, 
                    # but let's see what's in 'ranks' or if 'family' appears elsewhere.
                    pass
                print("-" * 20)
                count += 1
        except Exception as e:
            print(f"Error fetching {bgg_id}: {e}")

if __name__ == "__main__":
    debug_club_games()
