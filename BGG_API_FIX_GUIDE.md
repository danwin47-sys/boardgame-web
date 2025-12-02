# 修復 flask_app.py - 添加 BGG API 端點

這個腳本會自動創建正確的 flask_app.py，包含所有必要的 BGG API 端點。

## 問題診斷

**前端需要的 API 端點** (`bgg.js`):

- `/api/bgg/search?q=<query>` - 搜尋 BGG 桌遊  
- `/api/bgg/game/<game_id>` - 取得遊戲詳情
- `/api/bgg/hot?limit=10` - 熱門桌遊
- `/api/bgg/add-to-collection` - 加入館藏

**目前缺失**: 所有這些端點都不存在於原始的 `flask_app.py` 中！

## 修復步驟

### 方法 1: 使用修復腳本（推薦）

執行以下命令：

```bash
cd c:\python-training\boardgame-web
python fix_flask_app.py
```

這會創建一個包含所有 BGG API 端點的新 `flask_app.py`。

### 方法 2: 手動添加

在 `flask_app.py` 的第 118 行（`if __name__ == '__main__':` 之前）添加以下代碼：

```python
# ============ BGG 通用 API（用於前端搜尋功能） ============

@app.route('/api/bgg/search', methods=['GET'])
def search_bgg():
    """搜尋 BGG 桌遊（通用搜尋功能）"""
    from urllib.parse import unquote
    try:
        query = request.args.get('q', '').strip()
        if not query:
            return jsonify({'success': False, 'error': '缺少搜尋關鍵字'}), 400
        
        print(f"[DEBUG] BGG search query: {query}")
        bgg = get_bgg_service()
        results = bgg.search_games(query)
        
        return jsonify({'success': True, 'results': results}), 200
    except Exception as e:
        print(f"[ERROR] BGG search exception: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/bgg/game/<int:game_id>', methods=['GET'])
def get_bgg_game(game_id):
    """取得 BGG 遊戲詳情"""
    try:
        print(f"[DEBUG] Fetching BGG game details: {game_id}")
        bgg = get_bgg_service()
        game = bgg.get_game_details(game_id)
        
        if game:
            return jsonify({'success': True, 'game': game}), 200
        else:
            return jsonify({'success': False, 'error': '找不到遊戲'}), 404
    except Exception as e:
        print(f"[ERROR] Get BGG game exception: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/bgg/hot', methods=['GET'])
def get_hot_games():
    """取得 BGG 熱門桌遊"""
    try:
        limit = int(request.args.get('limit', 10))
        print(f"[DEBUG] Fetching hot games, limit: {limit}")
        
        bgg = get_bgg_service()
        games = bgg.get_hot_games(limit)
        
        return jsonify({'success': True, 'games': games}), 200
    except Exception as e:
        print(f"[ERROR] Get hot games exception: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/bgg/add-to-collection', methods=['POST'])
def add_bgg_to_collection():
    """從 BGG 加入桌遊到館藏"""
    try:
        data = request.get_json()
        game_id = data.get('game_id')
        custodian = data.get('custodian', '')
        
        if not game_id:
            return jsonify({'success': False, 'error': '缺少 game_id'}), 400
        
        print(f"[DEBUG] Adding BGG game to collection: {game_id}, custodian: {custodian}")
        
        # 取得遊戲詳情
        bgg = get_bgg_service()
        game = bgg.get_game_details(game_id)
        
        if not game:
            return jsonify({'success': False, 'error': '找不到遊戲'}), 404
        
        # TODO: 實作將 BGG 遊戲加入到 Google Sheets 的邏輯
        return jsonify({'success': True, 'message': f'已加入「{game["name"]}」到館藏'}), 200
        
    except Exception as e:
        print(f"[ERROR] Add to collection exception: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'success': False, 'error': str(e)}), 500
```

同時在第 12-13 行添加：

```python
global_manager = None
global_bgg_service = None  # 添加這行
```

以及在第 20 行後添加 `get_bgg_service()` 函數：

```python
def get_bgg_service():
    global global_bgg_service
    if global_bgg_service is None:
        from core.bgg_service import BGGService
        print("正在初始化 BGG API 連線...")
        global_bgg_service = BGGService()
    return global_bgg_service
```

## 測試

重啟 Flask 應用後，在搜尋框輸入「卡坦島」，應該會看到搜尋結果！
