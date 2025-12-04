# BGG 連結功能 - API 代碼

請將以下代碼加入到 `flask_app.py` 的第 117 行之後（在 `admin_login` 函數結束後，`if __name__` 之前）：

```python
# ============ BGG 連結功能 API ============

@app.route('/api/games/<game_name>/search-bgg', methods=['GET'])
def search_bgg_for_game(game_name):
    """搜尋 BGG 遊戲（用於連結功能）"""
    try:
        bgg = get_bgg_service()
        results = bgg.search_games(game_name)
        
        return jsonify({
            'success': True,
            'game_name': game_name,
            'results': results
        }), 200
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/games/<game_name>/link-bgg', methods=['POST'])
def link_game_to_bgg(game_name):
    """連結桌遊到 BGG"""
    try:
        data = request.get_json()
        bgg_id = data.get('bgg_id')
        
        if not bgg_id:
            return jsonify({'success': False, 'error': '缺少 bgg_id'}), 400
        
        mgr = get_manager()
        success = mgr.client.update_game_bgg_id(game_name, bgg_id)
        
        if success:
            return jsonify({
                'success': True,
                'message': f'已成功連結「{game_name}」到 BGG (ID: {bgg_id})'
            }), 200
        else:
            return jsonify({
                'success': False,
                'error': '更新失敗，請檢查桌遊名稱是否正確'
            }), 404
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/games/<game_name>/unlink-bgg', methods=['DELETE'])
def unlink_game_from_bgg(game_name):
    """取消桌遊與 BGG 的連結"""
    try:
        mgr = get_manager()
        success = mgr.client.update_game_bgg_id(game_name, None)
        
        if success:
            return jsonify({
                'success': True,
                'message': f'已取消「{game_name}」與 BGG 的連結'
            }), 200
        else:
            return jsonify({
                'success': False,
                'error': '更新失敗，請檢查桌遊名稱是否正確'
            }), 404
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500
```

## 也需要加入 `get_bgg_service()` 函數

在 `get_manager()` 函數之後加入：

```python
def get_bgg_service():
    global global_bgg_service
    if global_bgg_service is None:
        from core.bgg_service import BGGService
        print("正在初始化 BGG API 連線...")
        global_bgg_service = BGGService()
    return global_bgg_service
```

並在檔案開頭的 global 變數區加入：

```python
global_bgg_service = None
```

## 完整插入位置

```
line 13: global_manager = None
line 14: global_bgg_service = None  # 新增這行

line 20: def get_manager():
    ...

line 25: def get_bgg_service():  # 新增這個函數
    ...

line 117: (admin_login 函數結束)

line 118: # ============ BGG 連結功能 API ============  # 新增 API 端點
line 119: @app.route('/api/games/<game_name>/search-bgg', methods=['GET'])
    ...
```
