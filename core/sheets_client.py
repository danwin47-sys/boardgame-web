import os
import json
import time
import gspread
from typing import List, Dict, Any, Optional
from gspread.utils import rowcol_to_a1
import logging

from .constants import (
    GAMES_CACHE_TTL,
    MEMBERS_CACHE_TTL,
    WORKSHEET_GAMES,
    WORKSHEET_MEMBERS
)
from .exceptions import SheetConnectionError

logger = logging.getLogger(__name__)

class SheetsClient:
    """
    負責處理 Google Sheets 的連線、工作表存取與資料快取。
    """
    
    def __init__(self):
        self.valid = False
        self.gc = None
        self.sh = None
        
        # 快取存儲
        self._games_cache: Optional[List[Dict[str, Any]]] = None
        self._games_cache_time = 0
        self._members_cache: Optional[List[Dict[str, Any]]] = None
        self._members_cache_time = 0
        
        # 工作表物件快取
        self.games_ws = None
        self.members_ws = None
        
        self._connect()

    def _connect(self):
        """建立 Google Sheets 連線"""
        # 1. 從環境變數讀取
        sheet_url = os.environ.get("SHEET_URL")
        creds_json = os.environ.get("GOOGLE_CREDENTIALS")
        
        # 2. 嘗試使用環境變數連線
        if creds_json:
            try:
                creds_dict = json.loads(creds_json)
                self.gc = gspread.service_account_from_dict(creds_dict)
                if sheet_url:
                    self.sh = self.gc.open_by_url(sheet_url)
                    self.valid = True
                    logger.info("Google Sheet connected! (Env)")
            except Exception as e:
                logger.error(f"Google Sheet connection failed (Env): {e}")
                self.valid = False

        # 3. 本地開發 Fallback (如果尚未連線成功)
        if not self.valid:
            # 使用相對於專案根目錄的路徑
            base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            local_creds_path = os.path.join(base_dir, 'boardgame-bot-5f6751855184.json')
            
            if os.path.exists(local_creds_path):
                logger.info(f"Loading credentials from local file: {local_creds_path}")
                try:
                    self.gc = gspread.service_account(filename=local_creds_path)
                    
                    if not sheet_url:
                        # 本地測試用的 Hardcoded URL
                        sheet_url = "https://docs.google.com/spreadsheets/d/1n2cCI1glkErCq835kNJD5hXyk1iR7IptPlnKKPm0_0Y/edit?gid=0#gid=0"
                        logger.info(f"Using hardcoded Sheet URL: {sheet_url}")
                    
                    if sheet_url:
                        self.sh = self.gc.open_by_url(sheet_url)
                        self.valid = True
                        logger.info("Google Sheet connected! (Local)")
                        return
                except Exception as e:
                    logger.error(f"Local credential load failed: {e}")
            else:
                logger.warning(f"Local credentials not found at: {local_creds_path}")
        
        if not self.valid:
            logger.error("Failed to initialize Google Sheet connection.")

    def get_games_worksheet(self):
        """取得 games 工作表物件"""
        if not self.valid:
            raise SheetConnectionError("Google Sheets 未連線")
            
        if not self.games_ws:
            try:
                self.games_ws = self.sh.worksheet(WORKSHEET_GAMES)
            except Exception as e:
                raise SheetConnectionError(f"無法取得工作表 '{WORKSHEET_GAMES}': {e}")
        return self.games_ws

    def get_members_worksheet(self):
        """取得 members 工作表物件"""
        if not self.valid:
            raise SheetConnectionError("Google Sheets 未連線")
            
        if not self.members_ws:
            try:
                self.members_ws = self.sh.worksheet(WORKSHEET_MEMBERS)
            except Exception as e:
                raise SheetConnectionError(f"無法取得工作表 '{WORKSHEET_MEMBERS}': {e}")
        return self.members_ws

    def load_games(self) -> List[Dict[str, Any]]:
        """
        讀取所有桌遊資料 (含快取)
        """
        # 如果未連線，嘗試重新連線
        if not self.valid:
            logger.info("SheetsClient not valid, attempting to reconnect...")
            self._connect()
            
        if not self.valid:
            return []
        
        current_time = time.time()
        # 檢查快取是否有效
        if self._games_cache and (current_time - self._games_cache_time < GAMES_CACHE_TTL):
            return self._games_cache

        try:
            ws = self.get_games_worksheet()
            self._games_cache = ws.get_all_records()
            self._games_cache_time = current_time
            return self._games_cache
        except Exception as e:
            logger.error(f"讀取 games 失敗: {e}")
            # 如果讀取失敗，可能是 token 過期，嘗試重連一次
            logger.info("Attempting to reconnect and retry...")
            self._connect()
            if self.valid:
                try:
                    ws = self.get_games_worksheet()
                    self._games_cache = ws.get_all_records()
                    self._games_cache_time = current_time
                    return self._games_cache
                except Exception as retry_e:
                    logger.error(f"重試讀取 games 失敗: {retry_e}")
            return []

    def load_members(self) -> List[Dict[str, Any]]:
        """
        讀取所有社員資料 (含快取)
        """
        # 如果未連線，嘗試重新連線
        if not self.valid:
            logger.info("SheetsClient not valid, attempting to reconnect...")
            self._connect()

        if not self.valid:
            return []
        
        current_time = time.time()
        # 檢查快取是否有效
        if self._members_cache and (current_time - self._members_cache_time < MEMBERS_CACHE_TTL):
            return self._members_cache

        try:
            ws = self.get_members_worksheet()
            self._members_cache = ws.get_all_records()
            self._members_cache_time = current_time
            return self._members_cache
        except Exception as e:
            logger.error(f"讀取 members 失敗: {e}")
            # 如果讀取失敗，可能是 token 過期，嘗試重連一次
            logger.info("Attempting to reconnect and retry...")
            self._connect()
            if self.valid:
                try:
                    ws = self.get_members_worksheet()
                    self._members_cache = ws.get_all_records()
                    self._members_cache_time = current_time
                    return self._members_cache
                except Exception as retry_e:
                    logger.error(f"重試讀取 members 失敗: {retry_e}")
            return []

    def invalidate_games_cache(self):
        """強制使 games 快取失效 (通常在更新後呼叫)"""
        self._games_cache = None
        self._games_cache_time = 0

    def create_batch_update(self, row: int, col_idx: int, value: Any) -> Dict[str, Any]:
        """
        建立單個儲存格的 batch update 請求結構
        
        Args:
            row: 列號 (1-based)
            col_idx: 欄位索引 (0-based)
            value: 要寫入的值
        """
        return {
            'range': rowcol_to_a1(row, col_idx + 1),
            'values': [[value]]
        }
    
    def update_game_bgg_id(self, game_name: str, bgg_id: Optional[int], 
                           thumbnail_url: Optional[str] = None, 
                           image_url: Optional[str] = None,
                           players_display: Optional[str] = None) -> bool:
        """
        更新指定桌遊的 BGG ID、縮圖、大圖和玩家數
        
        Args:
            game_name: 桌遊名稱 (使用 'name' 欄位)
            bgg_id: BGG 遊戲 ID (None 表示取消連結)
            thumbnail_url: BGG 縮圖網址 (選填)
            image_url: BGG 大圖網址 (選填)
            players_display: BGG 玩家數 (選填，如 "2-4")
            
        Returns:
            bool: 是否更新成功
        """
        if not self.valid:
            return False
            
        try:
            ws = self.get_games_worksheet()
            all_records = ws.get_all_records()
            
            # 找到對應的桌遊
            for idx, game in enumerate(all_records):
                if game.get('name') == game_name:
                    # 找到 bgg_id, bgg_thumbnail, image 欄位的索引
                    headers = ws.row_values(1)
                    
                    # Helper function to get or create column index
                    def get_or_create_col(header_name):
                        if header_name not in headers:
                            col_idx = len(headers)
                            ws.update_cell(1, col_idx + 1, header_name)
                            headers.append(header_name)
                            logger.info(f"已新增 {header_name} 欄位到 Google Sheets")
                            return col_idx
                        return headers.index(header_name)

                    col_idx_id = get_or_create_col('bgg_id')
                    col_idx_thumb = get_or_create_col('bgg_thumbnail')
                    col_idx_image = get_or_create_col('image')
                    
                    # 更新該桌遊的資料
                    row_num = idx + 2
                    
                    # 更新 ID
                    value_id = bgg_id if bgg_id is not None else ""
                    ws.update_cell(row_num, col_idx_id + 1, value_id)
                    
                    # 更新 Thumbnail
                    value_thumb = thumbnail_url if thumbnail_url is not None else ""
                    ws.update_cell(row_num, col_idx_thumb + 1, value_thumb)

                    # 更新 Image
                    value_image = image_url if image_url is not None else ""
                    ws.update_cell(row_num, col_idx_image + 1, value_image)
                    
                    # 更新玩家數（如果提供）
                    if players_display is not None:
                        col_idx_players = headers.index('players') if 'players' in headers else None
                        if col_idx_players is not None:
                            ws.update_cell(row_num, col_idx_players + 1, players_display)
                            logger.info(f"已更新 '{game_name}' 的玩家數: {players_display}")
                    
                    # 使快取失效
                    self.invalidate_games_cache()
                    
                    logger.info(f"已更新 '{game_name}' - ID: {bgg_id}, Thumb: {bool(thumbnail_url)}, Image: {bool(image_url)}, Players: {players_display or 'N/A'}")
                    return True
            
            logger.warning(f"找不到桌遊: {game_name}")
            return False
            
        except Exception as e:
            logger.error(f"更新 BGG 資料失敗: {e}")
            return False

    # ============ BGG 推薦緩存功能 ============
    
    def get_bgg_cache_worksheet(self):
        """取得 BGG 推薦緩存工作表"""
        if not self.valid:
            return None
        
        try:
            # 嘗試取得現有工作表
            try:
                ws = self.sh.worksheet('BGG推薦緩存')
                return ws
            except gspread.exceptions.WorksheetNotFound:
                # 工作表不存在，創建新的
                logger.info("創建 BGG推薦緩存 工作表")
                ws = self.sh.add_worksheet(title='BGG推薦緩存', rows=100, cols=10)
                
                # 設定標題列
                headers = ['分類', 'BGG_ID_1', 'BGG_ID_2', 'BGG_ID_3', 'BGG_ID_4', 
                          'BGG_ID_5', 'BGG_ID_6', 'BGG_ID_7', 'BGG_ID_8', 'BGG_ID_9', 
                          'BGG_ID_10', '更新時間']
                ws.update('A1:L1', [headers])
                
                return ws
        except Exception as e:
            logger.error(f"取得 BGG 緩存工作表失敗: {e}")
            return None
    
    def save_bgg_recommendations(self, category: str, game_ids: List[int]) -> bool:
        """
        儲存 BGG 推薦緩存
        
        Args:
            category: 分類名稱 (party/strategy/family/children)
            game_ids: BGG ID 列表（最多10個）
            
        Returns:
            bool: 是否成功
        """
        if not self.valid:
            return False
        
        try:
            ws = self.get_bgg_cache_worksheet()
            if not ws:
                return False
            
            # 取得所有記錄
            records = ws.get_all_records()
            
            # 準備資料（補齊到10個ID）
            padded_ids = (game_ids + [0] * 10)[:10]
            from datetime import datetime
            update_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            
            row_data = [category] + padded_ids + [update_time]
            
            # 查找是否已有此分類的記錄
            row_num = None
            for idx, record in enumerate(records):
                if record.get('分類') == category:
                    row_num = idx + 2  # +2 因為第1行是標題，索引從0開始
                    break
            
            if row_num:
                # 更新現有記錄
                ws.update(f'A{row_num}:L{row_num}', [row_data])
            else:
                # 新增記錄
                ws.append_row(row_data)
            
            logger.info(f"已儲存 {category} 的推薦緩存，共 {len(game_ids)} 個遊戲")
            return True
            
        except Exception as e:
            logger.error(f"儲存 BGG 推薦緩存失敗: {e}")
            return False
    
    def load_bgg_recommendations(self, category: str) -> Optional[List[int]]:
        """
        讀取 BGG 推薦緩存
        
        Args:
            category: 分類名稱
            
        Returns:
            BGG ID 列表，如果沒有緩存則返回 None
        """
        if not self.valid:
            return None
        
        try:
            ws = self.get_bgg_cache_worksheet()
            if not ws:
                return None
            
            records = ws.get_all_records()
            
            for record in records:
                if record.get('分類') == category:
                    # 提取所有 BGG ID（排除 0）
                    game_ids = []
                    for i in range(1, 11):
                        game_id = record.get(f'BGG_ID_{i}', 0)
                        if game_id and int(game_id) > 0:
                            game_ids.append(int(game_id))
                    
                    logger.info(f"從緩存讀取 {category}，共 {len(game_ids)} 個遊戲")
                    return game_ids if game_ids else None
            
            return None
            
        except Exception as e:
            logger.error(f"讀取 BGG 推薦緩存失敗: {e}")
            return None
    
    def get_bgg_recommendations_update_time(self, category: str) -> Optional[str]:
        """
        取得 BGG 推薦的上次更新時間
        
        Args:
            category: 分類名稱
            
        Returns:
            更新時間字串，如果沒有記錄則返回 None
        """
        if not self.valid:
            return None
        
        try:
            ws = self.get_bgg_cache_worksheet()
            if not ws:
                return None
            
            records = ws.get_all_records()
            
            for record in records:
                if record.get('分類') == category:
                    return record.get('更新時間')
            
            return None
            
        except Exception as e:
            logger.error(f"取得更新時間失敗: {e}")
            return None
