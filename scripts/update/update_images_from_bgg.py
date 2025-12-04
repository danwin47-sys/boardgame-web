"""
Script to update game images and thumbnails from BGG for games that are already linked.
"""
import time
import logging
from app import create_app
from core.bgg_service import BGGService

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def update_images():
    """
    Iterate through all games, check for BGG ID, fetch details from BGG,
    and update image/thumbnail in Google Sheets.
    """
    app = create_app('development')
    logger.info("[UPDATE] Starting images update")
    
    with app.app_context():
        manager = app.config['boardgame_manager']
        sheets_client = manager.client
        bgg_service = BGGService()
        
        # Force reload games to get fresh data
        sheets_client.invalidate_games_cache()
        games = sheets_client.load_games()
        
        logger.info(f"Loaded {len(games)} games from Google Sheets.")
        
        updated_count = 0
        skipped_count = 0
        error_count = 0
        
        for game in games:
            game_name = game.get('name')
            bgg_id = game.get('bgg_id')
            
            # Check if game has BGG ID
            if not bgg_id:
                logger.debug(f"Skipping '{game_name}': No BGG ID linked.")
                skipped_count += 1
                continue
                
            try:
                bgg_id_int = int(bgg_id)
            except ValueError:
                logger.warning(f"Skipping '{game_name}': Invalid BGG ID '{bgg_id}'")
                skipped_count += 1
                continue
                
            logger.info(f"Processing '{game_name}' (BGG ID: {bgg_id_int})...")
            
            # Fetch details from BGG
            details = bgg_service.get_game_details(bgg_id_int)
            
            if not details:
                logger.warning(f"Could not fetch details for BGG ID {bgg_id_int}")
                error_count += 1
                continue
            
            image_url = details.get('image')
            thumbnail_url = details.get('thumbnail')
            players_display = details.get('players_display')
            
            if not image_url and not thumbnail_url:
                logger.info(f"No images found for BGG ID {bgg_id_int}")
            
            # Update Google Sheet
            # We re-supply the bgg_id to ensure it stays consistent
            success = sheets_client.update_game_bgg_id(
                game_name=game_name,
                bgg_id=bgg_id_int,
                thumbnail_url=thumbnail_url,
                image_url=image_url,
                players_display=players_display
            )
            
            if success:
                logger.info(f"Successfully updated '{game_name}'")
                updated_count += 1
            else:
                logger.error(f"Failed to update '{game_name}' in Google Sheets")
                error_count += 1
            
            # Sleep briefly to be nice to BGG API and Google Sheets API
            time.sleep(1.5)
            
        logger.info("="*30)
        logger.info(f"Update Complete.")
        logger.info(f"Total Games: {len(games)}")
        logger.info(f"Updated: {updated_count}")
        logger.info(f"Skipped (No ID/Invalid): {skipped_count}")
        logger.info(f"Errors: {error_count}")
        logger.info("="*30)

if __name__ == "__main__":
    update_images()
