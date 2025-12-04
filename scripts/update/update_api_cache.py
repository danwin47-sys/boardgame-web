# -*- coding: utf-8 -*-
"""
修改 bgg_routes.py 以支援3天更新機制
"""
import codecs

# 讀取文件
with codecs.open('c:/python-training/boardgame-web/api/bgg_routes.py', 'r', 'utf-8') as f:
    content = f.read()

# 定義要替換的舊函數
old_function = '''@bgg_bp.route('/category/<category>', methods=['GET'])
def get_category_games(category):
    """取得指定分类的热门游戏"""
    try:
        limit = int(request.args.get('limit', 10))
        logger.debug(f"Fetching category games: {category}, limit: {limit}")
        
        bgg = get_bgg_service()
        
        # 根据分类获取游戏
        if category == 'party':
            games = bgg.get_party_games(limit)
        elif category == 'strategy':
            games = bgg.get_strategy_games(limit)
        elif category == 'family':
            games = bgg.get_family_games(limit)
        elif category == 'children':
            games = bgg.get_children_games(limit)
        else:
            return jsonify({'success': False, 'error': '无效的分类'}), 400
        
        return jsonify({'success': True, 'games': games}), 200
    except Exception as e:
        logger.error(f"Get category games exception: {e}")
        traceback.print_exc()
        return jsonify({'success': False, 'error': str(e)}), 500'''

# 定義新函數（支援3天更新機制）
new_function = '''@bgg_bp.route('/category/<category>', methods=['GET'])
def get_category_games(category):
    """取得指定分類的熱門遊戲（支援3天緩存）"""
    try:
        limit = int(request.args.get('limit', 10))
        logger.debug(f"Fetching category games: {category}, limit: {limit}")
        
        bgg = get_bgg_service()
        
        # 檢查緩存是否需要更新（3天）
        from datetime import datetime, timedelta
        
        update_time_str = mgr.client.get_bgg_recommendations_update_time(category)
        needs_update = True
        
        if update_time_str:
            try:
                last_update = datetime.strptime(update_time_str, '%Y-%m-%d %H:%M:%S')
                days_diff = (datetime.now() - last_update).days
                needs_update = days_diff >= 3
                logger.info(f"{category} 上次更新: {update_time_str}, 已過 {days_diff} 天")
            except Exception as e:
                logger.warning(f"解析更新時間失敗: {e}")
        
        games = None
        
        # 如果未滿3天，從緩存讀取
        if not needs_update:
            game_ids = mgr.client.load_bgg_recommendations(category)
            if game_ids:
                logger.info(f"從緩存讀取 {category}，共 {len(game_ids)} 個遊戲")
                games_list = []
                for game_id in game_ids:
                    try:
                        game = bgg.get_game_details(game_id)
                        if game:
                            games_list.append({
                                'id': game['id'],
                                'name': game['name'],
                                'year': game.get('year'),
                                'thumbnail': game.get('thumbnail'),
                                'rating_average': game.get('rating_average')
                            })
                    except:
                        continue
                games = games_list
        
        # 如果需要更新或緩存讀取失敗，從 BGG API 獲取
        if games is None:
            logger.info(f"從 BGG API 獲取 {category} 推薦")
            if category == 'party':
                games = bgg.get_party_games(limit)
            elif category == 'strategy':
                games = bgg.get_strategy_games(limit)
            elif category == 'family':
                games = bgg.get_family_games(limit)
            elif category == 'children':
                games = bgg.get_children_games(limit)
            else:
                return jsonify({'success': False, 'error': '無效的分類'}), 400
            
            # 儲存到緩存
            if games:
                game_ids = [g['id'] for g in games]
                mgr.client.save_bgg_recommendations(category, game_ids)
                logger.info(f"已儲存 {category} 到緩存")
        
        return jsonify({'success': True, 'games': games}), 200
    except Exception as e:
        logger.error(f"Get category games exception: {e}")
        traceback.print_exc()
        return jsonify({'success': False, 'error': str(e)}), 500'''

# 替換
if old_function in content:
    content = content.replace(old_function, new_function)
    print("✓ 已替換 get_category_games 函數")
else:
    print("✗ 找不到目標函數，可能已經被修改")

# 寫回文件
with codecs.open('c:/python-training/boardgame-web/api/bgg_routes.py', 'w', 'utf-8') as f:
    f.write(content)

print("完成 bgg_routes.py 修改")
