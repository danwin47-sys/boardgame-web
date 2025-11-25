import gspread
import json
import os
import time
from datetime import datetime
from gspread.utils import rowcol_to_a1

class BoardGameManager:
    def __init__(self):
        # 從 Render 環境變數讀取設定
        self.sheet_url = os.environ.get("SHEET_URL")
        creds_json = os.environ.get("GOOGLE_CREDENTIALS")
        
        self.valid = False
        
        # Cache initialization
        self._games_cache = None
        self._games_cache_time = 0
        self._members_cache = None
        self._members_cache_time = 0
        
        # Worksheet Cache
        self.games_ws = None
        self.members_ws = None
        
        # --- Local Development Fallback ---
        if not creds_json:
            local_creds_path = 'boardgame-bot-5f6751855184.json'
            if os.path.exists(local_creds_path):
                print(f"[Info] Loading credentials from local file: {local_creds_path}")
                try:
                    self.gc = gspread.service_account(filename=local_creds_path)
                    
                    # If we have creds but no URL, use the known URL
                    if not self.sheet_url:
                        # Hardcoded for local testing to avoid input() blocking Flask
                        self.sheet_url = "https://docs.google.com/spreadsheets/d/1n2cCI1glkErCq835kNJD5hXyk1iR7IptPlnKKPm0_0Y/edit?gid=0#gid=0"
                        print(f"[Info] Using hardcoded Sheet URL: {self.sheet_url}")
                    
                    if self.sheet_url:
                        self.sh = self.gc.open_by_url(self.sheet_url)
                        self.valid = True
                        print("[Info] Google Sheet connected!")
                except Exception as e:
                    print(f"[Error] Local credential load failed: {e}")
        # ----------------------------------

        # If still not valid (env vars case), try loading from env vars
        if not self.valid and self.sheet_url and creds_json:
            try:
                # 將 JSON 字串轉回字典，並連線 Google Sheet
                creds_dict = json.loads(creds_json)
                self.gc = gspread.service_account_from_dict(creds_dict)
                self.sh = self.gc.open_by_url(self.sheet_url)
                self.valid = True
                print("[Info] Google Sheet connected!")
            except Exception as e:
                print(f"[Error] Google Sheet connection failed: {e}")
                self.valid = False
        
        if not self.valid:
            print("[Error] Failed to initialize Google Sheet connection.")

    def _get_games_ws(self):
        if not self.games_ws:
            self.games_ws = self.sh.worksheet("games")
        return self.games_ws

    def _get_members_ws(self):
        if not self.members_ws:
            self.members_ws = self.sh.worksheet("members")
        return self.members_ws

    def load_data(self):
        """讀取 'games' 分頁 (含快取 30s)"""
        if not self.valid: return []
        
        current_time = time.time()
        if self._games_cache and (current_time - self._games_cache_time < 30):
            return self._games_cache

        try:
            ws = self._get_games_ws()
            self._games_cache = ws.get_all_records()
            self._games_cache_time = current_time
            return self._games_cache
        except Exception as e:
            print(f"讀取 games 失敗: {e}")
            return []

    def load_members(self):
        """讀取 'members' 分頁 (含快取 1小時)"""
        if not self.valid: return []
        
        current_time = time.time()
        if self._members_cache and (current_time - self._members_cache_time < 3600):
            return self._members_cache

        try:
            ws = self._get_members_ws()
            self._members_cache = ws.get_all_records()
            self._members_cache_time = current_time
            return self._members_cache
        except Exception as e:
            print(f"讀取 members 失敗: {e}")
            return []

    def get_current_timestamp(self):
        return int(time.time() * 1000)

    def find_member_by_id(self, member_id):
        members = self.load_members()
        for m in members:
            # 確保比對時都是字串
            if str(m.get('id', '')).strip() == str(member_id).strip():
                return m
        return None

    def find_member_by_name(self, member_name):
        """根據姓名查詢社員資料"""
        members = self.load_members()
        for m in members:
            if str(m.get('name', '')).strip() == str(member_name).strip():
                return m
        return None

    def borrow_game(self, name, user_name, user_id):
        if not self.valid: return False, "系統連線錯誤"
        
        try:
            ws = self._get_games_ws()
            games = ws.get_all_records()
            
            target_row = -1
            current_game = None
            
            for i, g in enumerate(games):
                if g['name'] == name:
                    target_row = i + 2
                    current_game = g
                    break
            
            if not current_game:
                return False, "找不到此遊戲"

            if current_game['status'] == "借出":
                return False, f"《{name}》已經被 {current_game['borrower']} 借走了"
            
            ts = self.get_current_timestamp()
            date_str = datetime.fromtimestamp(ts / 1000).strftime('%Y-%m-%d %H:%M')
            
            header = ws.row_values(1)
            batch_updates = []
            
            def add_cell_update(r, c_idx, val):
                batch_updates.append({
                    'range': rowcol_to_a1(r, c_idx + 1),
                    'values': [[val]]
                })

            status_idx = header.index('status')
            borrower_idx = header.index('borrower')
            bid_idx = header.index('borrower_id')
            mdate_idx = header.index('mdate')
            history_idx = header.index('history')

            add_cell_update(target_row, status_idx, "借出")
            add_cell_update(target_row, borrower_idx, user_name)
            add_cell_update(target_row, bid_idx, user_id)
            add_cell_update(target_row, mdate_idx, ts)
            
            existing_history = current_game.get('history', '')
            history_entry = f"[{date_str}] {user_name} 借閱"
            new_history = f"{existing_history} | {history_entry}" if existing_history else history_entry
            add_cell_update(target_row, history_idx, new_history)

            if batch_updates:
                ws.batch_update(batch_updates)
                self._games_cache = None
            
            return True, f"成功借出：《{name}》"

        except Exception as e:
            return False, f"借閱失敗: {e}"

    def batch_borrow_games(self, game_names, member_id):
        if not self.valid: return False, "系統連線錯誤", [], []
        
        try:
            member = self.find_member_by_id(member_id)
            if not member:
                return False, "找不到社員", [], []
            
            ws = self._get_games_ws()
            all_values = ws.get_all_values()
            if not all_values: return False, "讀取遊戲列表失敗", [], []
            
            header = all_values[0]
            games_data = all_values[1:]
            
            name_to_row = {}
            name_to_data = {}
            try:
                name_idx = header.index('name')
                for idx, row in enumerate(games_data):
                    game_name = row[name_idx]
                    name_to_row[game_name] = idx + 2
                    name_to_data[game_name] = row
            except ValueError:
                return False, "資料表格式錯誤 (找不到 name 欄位)", [], []

            success_list = []
            fail_list = []
            batch_updates = []
            ts = self.get_current_timestamp()
            date_str = datetime.fromtimestamp(ts / 1000).strftime('%Y-%m-%d %H:%M')
            
            try:
                status_idx = header.index('status')
                borrower_idx = header.index('borrower')
                bid_idx = header.index('borrower_id')
                mdate_idx = header.index('mdate')
                history_idx = header.index('history')
            except ValueError as e:
                return False, f"資料表欄位缺失: {e}", [], []

            for name in game_names:
                if name not in name_to_row:
                    fail_list.append({'name': name, 'reason': '找不到此遊戲'})
                    continue
                
                row_idx = name_to_row[name]
                row_data = name_to_data[name]
                
                current_status = row_data[status_idx]
                if current_status == "借出":
                    current_borrower = row_data[borrower_idx]
                    fail_list.append({'name': name, 'reason': f'已被 {current_borrower} 借出'})
                    continue
                
                success_list.append(name)
                
                def add_cell_update(r, c_idx, val):
                    batch_updates.append({
                        'range': rowcol_to_a1(r, c_idx + 1),
                        'values': [[val]]
                    })

                add_cell_update(row_idx, status_idx, "借出")
                add_cell_update(row_idx, borrower_idx, member['name'])
                add_cell_update(row_idx, bid_idx, member['id'])
                add_cell_update(row_idx, mdate_idx, ts)
                
                existing_history = row_data[history_idx] if len(row_data) > history_idx else ""
                history_entry = f"[{date_str}] {member['name']} 借閱"
                new_history = f"{existing_history} | {history_entry}" if existing_history else history_entry
                add_cell_update(row_idx, history_idx, new_history)

            if batch_updates:
                ws.batch_update(batch_updates)
                self._games_cache = None
            
            msg = f"成功借出 {len(success_list)} 個遊戲"
            if fail_list:
                msg += f"，失敗 {len(fail_list)} 個"
                
            return True, msg, success_list, fail_list

        except Exception as e:
            return False, f"批次借閱失敗: {e}", [], []

    def batch_return_games(self, game_names):
        if not self.valid: return False, "系統連線錯誤", [], []
        
        try:
            ws = self._get_games_ws()
            
            # 1. 讀取所有資料 (一次 API)
            all_values = ws.get_all_values()
            if not all_values: return False, "讀取遊戲列表失敗", [], []
            
            header = all_values[0]
            games_data = all_values[1:]
            
            name_to_row = {}
            name_to_data = {}
            try:
                name_idx = header.index('name')
                for idx, row in enumerate(games_data):
                    game_name = row[name_idx]
                    name_to_row[game_name] = idx + 2
                    name_to_data[game_name] = row
            except ValueError:
                return False, "資料表格式錯誤 (找不到 name 欄位)", [], []

            success_list = []
            fail_list = []
            batch_updates = []
            ts = self.get_current_timestamp()
            date_str = datetime.fromtimestamp(ts / 1000).strftime('%Y-%m-%d %H:%M')
            
            try:
                status_idx = header.index('status')
                borrower_idx = header.index('borrower')
                bid_idx = header.index('borrower_id')
                mdate_idx = header.index('mdate')
                history_idx = header.index('history')
                custodian_idx = header.index('custodian')
            except ValueError as e:
                return False, f"資料表欄位缺失: {e}", [], []

            for name in game_names:
                if name not in name_to_row:
                    fail_list.append({'name': name, 'reason': '找不到此遊戲'})
                    continue
                
                row_idx = name_to_row[name]
                row_data = name_to_data[name]
                
                current_status = row_data[status_idx]
                if current_status != "借出":
                    fail_list.append({'name': name, 'reason': '此遊戲未被借出'})
                    continue
                
                success_list.append(name)
                borrower_name = row_data[borrower_idx]
                
                def add_cell_update(r, c_idx, val):
                    batch_updates.append({
                        'range': rowcol_to_a1(r, c_idx + 1),
                        'values': [[val]]
                    })

                add_cell_update(row_idx, status_idx, "歸還")
                add_cell_update(row_idx, borrower_idx, "") # 先清空，後面看有沒有保管人
                
                add_cell_update(row_idx, bid_idx, "")
                add_cell_update(row_idx, mdate_idx, ts)
                
                # History
                existing_history = row_data[history_idx] if len(row_data) > history_idx else ""
                history_entry = f"[{date_str}] {borrower_name} 歸還"
                new_history = f"{existing_history} | {history_entry}" if existing_history else history_entry
                add_cell_update(row_idx, history_idx, new_history)
                
                # Handle Custodian
                custodian = row_data[custodian_idx] if len(row_data) > custodian_idx else ""
                if custodian:
                    add_cell_update(row_idx, borrower_idx, custodian)
                    # 這裡為了效能，我們不每一個都去查 member sheet，
                    # 而是假設保管人資料正確，或者之後再補。
                    # 但為了完整性，我們還是得查 ID。
                    # 為了避免 N+1 問題，我們應該先讀取所有 members (有 cache)
                    custodian_member = self.find_member_by_name(custodian)
                    if custodian_member:
                        add_cell_update(row_idx, bid_idx, custodian_member.get('id', ''))

            if batch_updates:
                ws.batch_update(batch_updates)
                self._games_cache = None # Invalidate cache
            
            msg = f"成功歸還 {len(success_list)} 個遊戲"
            if fail_list:
                msg += f"，失敗 {len(fail_list)} 個"
                
            return True, msg, success_list, fail_list

        except Exception as e:
            return False, f"批次歸還失敗: {e}", [], []

    def batch_return_games_by_member(self, member_id):
        if not self.valid: return False, "系統連線錯誤", []
        
        try:
            member = self.find_member_by_id(member_id)
            if not member:
                return False, "找不到社員", [], []
            
            member_name = member['name']
            games = self.load_data()
            
            # 找出該使用者借閱的所有桌遊
            borrowed_games = [g for g in games if g.get('status') == '借出' and g.get('borrower') == member_name]
            
            if not borrowed_games:
                return False, f"{member_name} 目前沒有借閱任何桌遊", []
            
            success_list = []
            fail_list = []
            
            # 這裡為了簡單，還是呼叫 batch_return_games
            # 雖然會多一次 load_data，但邏輯比較乾淨
            game_names = [g['name'] for g in borrowed_games]
            success, msg, s_list, f_list = self.batch_return_games(game_names)
            
            return success, msg, s_list
        except Exception as e:
            return False, f"批次歸還失敗: {e}", []

    def return_game(self, name):
        """
        單一歸還 (Wrapper for batch_return_games)
        """
        success, msg, success_list, fail_list = self.batch_return_games([name])
        
        # 如果成功列表有東西，就算成功
        if success_list:
            return True, f"成功歸還：《{name}》"
        else:
            # 如果失敗，回傳失敗原因
            if fail_list:
                reason = fail_list[0].get('reason', '未知原因')
                return False, f"歸還失敗：{reason}"
            return False, msg