from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS
import os
import secrets
from boardgame_system import BoardGameManager

# 設定 static 資料夾
app = Flask(__name__, static_folder='static', static_url_path='')
CORS(app)

# --- 延遲載入 ---
global_manager = None

def get_manager():
    global global_manager
    if global_manager is None:
        print("正在初始化 Google Sheets 連線...")
        global_manager = BoardGameManager()
    return global_manager

@app.route('/api/health')
def health_check():
    return jsonify({'status': 'ok', 'timestamp': get_manager().get_current_timestamp()}), 200

@app.route('/')
def home():
    return send_from_directory('static', 'index.html')

@app.route('/api/games', methods=['GET'])
def get_games():
    mgr = get_manager()
    mgr.games = mgr.load_data()
    return jsonify(mgr.games)

@app.route('/api/members', methods=['GET'])
def get_members():
    mgr = get_manager()
    return jsonify(mgr.load_members())

@app.route('/api/borrow', methods=['POST'])
def borrow_game():
    data = request.get_json()
    if not data: return jsonify({'error': 'No data provided'}), 400
    
    name = data.get('name')
    member_id = data.get('member_id')
    
    if not name or not member_id: return jsonify({'error': 'Missing fields'}), 400
    
    mgr = get_manager()
    member = mgr.find_member_by_id(member_id)
    if not member: return jsonify({'error': '找不到社員'}), 404
    
    success, msg = mgr.borrow_game(name, member['name'], member['id'])
    return jsonify({'message': msg, 'success': success}), 200 if success else 400

@app.route('/api/batch-borrow', methods=['POST'])
def batch_borrow():
    data = request.get_json()
    if not data: return jsonify({'error': 'No data provided'}), 400
    
    game_names = data.get('game_names', [])
    member_id = data.get('member_id')
    
    if not game_names or not member_id: return jsonify({'error': 'Missing fields'}), 400
    
    mgr = get_manager()
    success, msg, success_list, fail_list = mgr.batch_borrow_games(game_names, member_id)
    return jsonify({
        'message': msg, 
        'success': success, 
        'success_games': success_list,
        'failed_games': fail_list
    }), 200 if success else 400

@app.route('/api/return', methods=['POST'])
def return_game():
    data = request.get_json()
    name = data.get('name')
    if not name: return jsonify({'error': 'Missing name'}), 400
    
    mgr = get_manager()
    success, msg = mgr.return_game(name)
    return jsonify({'message': msg, 'success': success}), 200 if success else 400

@app.route('/api/batch-return', methods=['POST'])
def batch_return():
    data = request.get_json()
    if not data: return jsonify({'error': 'No data provided'}), 400
    
    game_names = data.get('game_names', [])
    
    if not game_names: return jsonify({'error': 'Missing fields'}), 400
    
    mgr = get_manager()
    success, msg, success_list, fail_list = mgr.batch_return_games(game_names)
    return jsonify({
        'message': msg, 
        'success': success, 
        'success_games': success_list,
        'failed_games': fail_list
    }), 200 if success else 400

@app.route('/api/admin-login', methods=['POST'])
def admin_login():
    data = request.get_json()
    password = data.get('password')
    
    # 簡單密碼驗證（從環境變數讀取，本地開發用預設值）
    admin_password = os.environ.get('ADMIN_PASSWORD', 'admin123')
    
    if password == admin_password:
        # 簡單的 token（實際應用應使用更安全的方式）
        token = secrets.token_hex(16)
        return jsonify({'success': True, 'token': token, 'message': '登入成功'}), 200
    else:
        return jsonify({'success': False, 'message': '密碼錯誤'}), 401

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)