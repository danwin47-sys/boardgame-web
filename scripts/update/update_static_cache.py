"""
Update Static Cache Script
Generates static/data/recommendations.json for instant loading of hot games.
"""
import os
import sys
import json
import logging
from datetime import datetime

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from core.facade import BoardGameManager
from core.bgg_service import BGGService

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def update_static_cache():
    logger.info("Starting static cache update...")
    
    mgr = BoardGameManager()
    bgg = BGGService()
    
    # Load internal games for Chinese name mapping
    internal_games = mgr.load_data()
    bgg_id_to_chinese = {}
    for internal_game in internal_games:
        bgg_id = internal_game.get('bgg_id')
        chinese_name = internal_game.get('name')
        if bgg_id and chinese_name:
            try:
                bgg_id_to_chinese[int(bgg_id)] = chinese_name
            except (ValueError, TypeError):
                continue
    
    sources = ['bgg', 'club']
    categories = ['party', 'strategy', 'family', 'children']
    
    cache_data = {
        'updated_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'data': {}
    }
    
    for source in sources:
        for category in categories:
            key = f"{source}-{category}"
            logger.info(f"Processing {key}...")
            
            try:
                # Load IDs from Sheet
                game_ids = mgr.client.load_bgg_recommendations(key)
                
                if not game_ids:
                    logger.warning(f"No data found for {key}")
                    cache_data['data'][key] = []
                    continue
                
                games = []
                for game_id in game_ids:
                    try:
                        game = bgg.get_game_details(game_id)
                        if game:
                            # Add Chinese name if available
                            if game['id'] in bgg_id_to_chinese:
                                game['chinese_name'] = bgg_id_to_chinese[game['id']]
                            games.append(game)
                    except Exception as e:
                        logger.error(f"Error fetching game {game_id}: {e}")
                
                cache_data['data'][key] = games
                logger.info(f"Fetched {len(games)} games for {key}")
                
            except Exception as e:
                logger.error(f"Error processing {key}: {e}")
                cache_data['data'][key] = []

    # Ensure static/data directory exists
    static_data_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), 'static', 'data')
    os.makedirs(static_data_dir, exist_ok=True)
    
    output_file = os.path.join(static_data_dir, 'recommendations.json')
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(cache_data, f, ensure_ascii=False, indent=2)
        
    logger.info(f"Static cache saved to {output_file}")

if __name__ == '__main__':
    update_static_cache()
