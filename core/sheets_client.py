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
        
        # 2. 本地開發 Fallback
        if not creds_json:
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

        # 3. 使用環境變數連線
        if not self.valid and sheet_url and creds_json:
            try:
                creds_dict = json.loads(creds_json)
                self.gc = gspread.service_account_from_dict(creds_dict)
                self.sh = self.gc.open_by_url(sheet_url)
                self.valid = True
                logger.info("Google Sheet connected! (Env)")
            except Exception as e:
                logger.error(f"Google Sheet connection failed: {e}")
                self.valid = False
        
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
    
    def update_game_bgg_id(self, game_name: str, bgg_id: Optional[int]) -> bool:
        """
        更新指定桌遊的 BGG ID
        
        Args:
            game_name: 桌遊名稱 (使用 'name' 欄位)
            bgg_id: BGG 遊戲 ID (None 表示取消連結)
            
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
                    # 找到 bgg_id 欄位的索引
                    headers = ws.row_values(1)
                    
                    # 如果 bgg_id 欄位不存在，需要先新增
                    if 'bgg_id' not in headers:
                        # 在最後一欄新增 bgg_id
                        col_idx = len(headers)
                        ws.update_cell(1, col_idx + 1, 'bgg_id')
                        logger.info("已新增 bgg_id 欄位到 Google Sheets")
                    else:
                        col_idx = headers.index('bgg_id')
                    
                    # 更新該桌遊的 bgg_id (idx + 2 因為：0-based -> 1-based，且跳過 header row)
                    row_num = idx + 2
                    value = bgg_id if bgg_id is not None else ""
                    ws.update_cell(row_num, col_idx + 1, value)
                    
                    # 使快取失效
                    self.invalidate_games_cache()
                    
                    logger.info(f"已更新 '{game_name}' 的 BGG ID 為: {bgg_id}")
                    return True
            
            logger.warning(f"找不到桌遊: {game_name}")
            return False
            
        except Exception as e:
            logger.error(f"更新 BGG ID 失敗: {e}")
            return False
