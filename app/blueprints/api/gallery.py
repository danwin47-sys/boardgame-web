"""
Gallery API Blueprint
處理桌遊展示牆相關的路由
"""
from flask import Blueprint, jsonify, request, current_app
import logging

logger = logging.getLogger(__name__)

# 建立 Blueprint
gallery_bp = Blueprint('gallery', __name__, url_prefix='/api/gallery')


def get_manager():
    """從 app.config 獲取 BoardGameManager"""
    if 'boardgame_manager' not in current_app.config:
        from core.facade import BoardGameManager
        logger.info("正在初始化 Google Sheets 連線...")
        current_app.config['boardgame_manager'] = BoardGameManager()
    return current_app.config['boardgame_manager']


def parse_players_range(players_str):
    """解析人數範圍字串，例如 '2-4' 或 '5+'"""
    if not players_str or players_str == '':
        return None, None
    
    # 處理數字類型（直接轉為單一數字）
    if isinstance(players_str, int):
        return players_str, players_str
    
    # 確保是字串類型
    players_str = str(players_str)
    
    try:
        # 處理 '5+' 格式
        if '+' in players_str:
            min_val = int(players_str.replace('+', '').strip())
            return min_val, 99
        
        # 處理 '2-4' 或 '2~4' 格式
        if '-' in players_str or '~' in players_str:
            separator = '-' if '-' in players_str else '~'
            parts = players_str.split(separator)
            if len(parts) == 2:
                return int(parts[0].strip()), int(parts[1].strip())
        
        # 處理單一數字
        val = int(players_str.strip())
        return val, val
    except (ValueError, AttributeError):
        return None, None


def classify_game_type(game_data):
    """
    根據遊戲資訊自動分類遊戲類型
    
    Args:
        game_data: 遊戲數據字典
        
    Returns:
        類型列表
    """
    types = []
    
    min_players = game_data.get('minPlayers', 1)
    max_players = game_data.get('maxPlayers', 10)
    difficulty = game_data.get('difficulty', '').lower()
    
    # 派對遊戲：6+ 人，通常簡單
    if max_players >= 6:
        types.append('派對遊戲')
    
    # 策略遊戲：困難或中等難度
    if difficulty in ['困難', '中等', '普通']:
        if min_players <= 4 and max_players <= 5:
            types.append('策略遊戲')
    
    # 家庭遊戲：3-6 人，簡單到普通
    if min_players <= 3 and max_players >= 4:
        if difficulty in ['簡單', '普通', '']:
            types.append('家庭遊戲')
    
    # 兒童遊戲：簡單難度
    if difficulty == '簡單' and max_players <= 6:
        types.append('兒童遊戲')
    
    # 如果沒有分類到任何類型，使用預設
    if not types:
        types.append('其他')
    
    return types


@gallery_bp.route('/games', methods=['GET'])
def get_gallery_games():
    """獲取展示牆的桌遊列表"""
    try:
        mgr = get_manager()
        mgr.games = mgr.load_data()
        
        # 處理篩選參數（未來擴展使用）
        status_filter = request.args.get('status', None)
        
        games_list = []
        for game in mgr.games:
            # 基本資訊
            game_data = {
                'id': game.get('name', ''),  # 使用名稱作為 ID
                'name': game.get('name', ''),
                'status': game.get('status', ''),
                'borrower': game.get('borrower', ''),
                'location': game.get('location', ''),
                'difficulty': game.get('diff', ''),
                'custodian': game.get('custodian', ''),
            }
            
            # BGG 相關資訊（所有資料從 Google Sheets 讀取，不調用 BGG API）
            bgg_id = game.get('bgg_id', '')
            if bgg_id:
                game_data['bggId'] = str(bgg_id)
            
            # 圖片資訊（與主頁面機制一致：優先使用 Google Sheets 的 bgg_thumbnail）
            bgg_thumbnail = game.get('bgg_thumbnail', '')
            image = game.get('image', '')
            thumbnail = game.get('thumbnail', '')
            
            # 優先順序：bgg_thumbnail → image → thumbnail
            if bgg_thumbnail:
                game_data['thumbnail'] = bgg_thumbnail
                game_data['image'] = bgg_thumbnail
            elif image:
                game_data['image'] = image
            elif thumbnail:
                game_data['thumbnail'] = thumbnail
            
            # 人數資訊
            players_str = game.get('players', '')
            min_players, max_players = parse_players_range(players_str)
            if min_players is not None:
                game_data['minPlayers'] = min_players
                game_data['maxPlayers'] = max_players
            
            # 遊戲時間（使用預設值，未來可從 Google Sheets 讀取）
            game_data['minMinutes'] = 30
            game_data['maxMinutes'] = 60
            
            # 類型和標籤分類邏輯
            types = classify_game_type(game_data)
            tags = []
            
            # 根據難度加入標籤
            difficulty = game.get('diff', '')
            if difficulty:
                tags.append(difficulty)
            
            # 根據位置加入標籤
            location = game.get('location', '')
            if location and location not in ['', '-']:
                tags.append(f"位置:{location}")
            
            game_data['types'] = types
            game_data['tags'] = tags
            
            # 狀態篩選
            if status_filter and game.get('status') != status_filter:
                continue
            
            games_list.append(game_data)
        
        return jsonify({
            'success': True,
            'games': games_list,
            'total': len(games_list)
        }), 200
        
    except Exception as e:
        logger.error(f"獲取展示牆遊戲列表失敗: {e}", exc_info=True)
        return jsonify({'success': False, 'error': str(e)}), 500
