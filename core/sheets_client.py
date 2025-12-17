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
            base_dir = os.path.dirname(
                os.path.dirname(
                    os.path.abspath(__file__)))
            local_creds_path = os.path.join(
                base_dir, 'boardgame-bot-5f6751855184.json')

            if os.path.exists(local_creds_path):
                logger.info(
                    f"Loading credentials from local file: {local_creds_path}")
                try:
                    self.gc = gspread.service_account(
                        filename=local_creds_path)

                    if not sheet_url:
                        # 嘗試從 .env 檔案讀取 (dotenv 可能已載入)
                        from dotenv import load_dotenv
                        load_dotenv()
                        sheet_url = os.environ.get("SHEET_URL")

                        if not sheet_url:
                            logger.error(
                                "SHEET_URL 環境變數未設定！請在 .env 檔案中設定 SHEET_URL")
                            return

                    if sheet_url:
                        self.sh = self.gc.open_by_url(sheet_url)
                        self.valid = True
                        logger.info("Google Sheet connected! (Local)")
                        return
                except Exception as e:
                    logger.error(f"Local credential load failed: {e}")
            else:
                logger.warning(
                    f"Local credentials not found at: {local_creds_path}")

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
                raise SheetConnectionError(
                    f"無法取得工作表 '{WORKSHEET_MEMBERS}': {e}")
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
        if self._games_cache and (current_time -
                                  self._games_cache_time < GAMES_CACHE_TTL):
            return self._games_cache

        try:
            ws = self.get_games_worksheet()
            records = ws.get_all_records()
            self._games_cache = records if records is not None else []
            self._games_cache_time = current_time
            return self._games_cache
        except Exception as e:
            logger.error(f"讀取 games 失敗: {e}")
            # 如果讀取失敗，可能是 token 過期，嘗試重連一次
            logger.info("Attempting to reconnect and retry...")
            self._connect()
            if self.valid:
                try:
                    records = ws.get_all_records()
                    self._games_cache = records if records is not None else []
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
        if self._members_cache and (
                current_time -
                self._members_cache_time < MEMBERS_CACHE_TTL):
            return self._members_cache

        try:
            ws = self.get_members_worksheet()
            records = ws.get_all_records()
            self._members_cache = records if records is not None else []
            self._members_cache_time = current_time
            return self._members_cache
        except Exception as e:
            logger.error(f"讀取 members 失敗: {e}")
            # 如果讀取失敗，可能是 token 過期，嘗試重連一次
            logger.info("Attempting to reconnect and retry...")
            self._connect()
            if self.valid:
                try:
                    records = ws.get_all_records()
                    self._members_cache = records if records is not None else []
                    self._members_cache_time = current_time
                    return self._members_cache
                except Exception as retry_e:
                    logger.error(f"重試讀取 members 失敗: {retry_e}")
            return []

    def invalidate_games_cache(self):
        """強制使 games 快取失效 (通常在更新後呼叫)"""
        self._games_cache = None
        self._games_cache_time = 0

    def add_new_game(self, game_data: Dict[str, Any]) -> bool:
        """
        新增遊戲到 Google Sheets
        
        Args:
            game_data: 遊戲資料字典，包含：
                - name: 遊戲名稱（必填）
                - bgg_id: BGG ID（選填）
                - players: 玩家數（選填）
                - image: 圖片URL（選填）
                - bgg_thumbnail: 縮圖URL（選填）
                - custodian: 保管人（選填）
                - status: 狀態（選填，預設為「可用」）
        
        Returns:
            bool: 是否成功
        """
        from .constants import GAME_STATUS_AVAILABLE
        
        logger.info(f"[UPDATE] Adding new game: {game_data.get('name')}")
        if not self.valid:
            return False
        
        try:
            ws = self.get_games_worksheet()
            
            # 獲取標題列
            headers = ws.row_values(1)
            
            # 準備新遊戲的資料行（按照 headers 順序）
            new_row = []
            for header in headers:
                # 獲取對應的值，如果沒有則使用預設值
                if header == 'status' and 'status' not in game_data:
                    new_row.append(GAME_STATUS_AVAILABLE)
                else:
                    new_row.append(game_data.get(header, ''))
            
            # 添加到工作表
            ws.append_row(new_row)
            
            # 使快取失效
            self.invalidate_games_cache()
            
            logger.info(f"成功新增遊戲：{game_data.get('name')}")
            return True
            
        except Exception as e:
            logger.error(f"新增遊戲失敗: {e}")
            return False

    def create_batch_update(self, row: int, col_idx: int,
                            value: Any) -> Dict[str, Any]:
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
        logger.info(f"[UPDATE] Updating game BGG ID for {game_name}")
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
                        col_idx_players = headers.index(
                            'players') if 'players' in headers else None
                        if col_idx_players is not None:
                            ws.update_cell(
                                row_num, col_idx_players + 1, players_display)
                            logger.info(
                                f"已更新 '{game_name}' 的玩家數: {players_display}")

                    # 使快取失效
                    self.invalidate_games_cache()

                    logger.info(
                        f"已更新 '{game_name}' - ID: {bgg_id}, Thumb: {
                            bool(thumbnail_url)}, Image: {
                            bool(image_url)}, Players: {
                            players_display or 'N/A'}")
                    return True

            logger.warning(f"找不到桌遊: {game_name}")
            return False

        except Exception as e:
            logger.error(f"更新 BGG 資料失敗: {e}")
            return False

    def update_game_playtime(self, game_name: str, min_playtime: int, max_playtime: int) -> bool:
        """更新遊戲的遊玩時間到 Google Sheets
        
        Args:
            game_name: 遊戲名稱
            min_playtime: 最小遊玩時間（分鐘）
            max_playtime: 最大遊玩時間（分鐘）
        
        Returns:
            bool: 更新成功返回 True，失敗返回 False
        """
        logger.info(f"[UPDATE] Updating playtime for {game_name}")
        if not self.valid:
            return False
        
        try:
            ws = self.get_games_worksheet()
            all_records = ws.get_all_records()
            
            # 找到對應的遊戲
            for idx, game in enumerate(all_records):
                if game.get('name') == game_name:
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
                    
                    minplaytime_idx = get_or_create_col('minplaytime')
                    maxplaytime_idx = get_or_create_col('maxplaytime')
                    
                    # 更新遊玩時間
                    row_num = idx + 2
                    ws.update_cell(row_num, minplaytime_idx + 1, min_playtime)
                    ws.update_cell(row_num, maxplaytime_idx + 1, max_playtime)
                    
                    # 使快取失效
                    self.invalidate_games_cache()
                    
                    logger.info(f"已更新 '{game_name}' 的遊玩時間: {min_playtime}-{max_playtime}分鐘")
                    return True
            
            logger.warning(f"找不到遊戲: {game_name}")
            return False
            
        except Exception as e:
            logger.error(f"更新遊戲時間失敗: {e}", exc_info=True)
            return False

    def update_game_expansion_info(self, game_name: str, is_expansion: bool, 
                                  parent_game: str = '', storage_mode: str = '') -> bool:
        """更新遊戲的擴充資訊
        
        Args:
            game_name: 遊戲名稱
            is_expansion: 是否為擴充
            parent_game: 主遊戲名稱 (若非擴充則為空)
            storage_mode: 收納模式 (independent/merged)
        
        Returns:
            bool: 更新成功返回 True，失敗返回 False
        """
        logger.info(f"[UPDATE] Updating expansion info for {game_name}")
        if not self.valid:
            return False
            
        try:
            ws = self.get_games_worksheet()
            all_records = ws.get_all_records()
            
            # 找到對應的遊戲
            for idx, game in enumerate(all_records):
                if game.get('name') == game_name:
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
                    
                    from .constants import (
                        FIELD_IS_EXPANSION, 
                        FIELD_PARENT_GAME, 
                        FIELD_STORAGE_MODE
                    )
                    
                    is_exp_idx = get_or_create_col(FIELD_IS_EXPANSION)
                    parent_idx = get_or_create_col(FIELD_PARENT_GAME)
                    storage_idx = get_or_create_col(FIELD_STORAGE_MODE)
                    
                    # 準備批量更新
                    row_num = idx + 2
                    updates = []
                    
                    # 更新 is_expansion (存為字串 'TRUE' 或 'FALSE')
                    updates.append({
                        'range': rowcol_to_a1(row_num, is_exp_idx + 1),
                        'values': [['TRUE' if is_expansion else 'FALSE']]
                    })
                    
                    # 更新 parent_game
                    updates.append({
                        'range': rowcol_to_a1(row_num, parent_idx + 1),
                        'values': [[parent_game]]
                    })
                    
                    # 更新 storage_mode
                    updates.append({
                        'range': rowcol_to_a1(row_num, storage_idx + 1),
                        'values': [[storage_mode]]
                    })
                    
                    ws.batch_update(updates)
                    
                    # 使快取失效
                    self.invalidate_games_cache()
                    
                    logger.info(f"已更新 '{game_name}' 的擴充資訊")
                    return True
            
            logger.warning(f"找不到遊戲: {game_name}")
            return False
            
        except Exception as e:
            logger.error(f"更新擴充資訊失敗: {e}", exc_info=True)
            return False

    # ============ BGG 推薦快取功能 ============

    def get_bgg_cache_worksheet(self):
        """取得 BGG 推薦快取工作表"""
        if not self.valid:
            return None

        try:
            # 嘗試取得現有工作表
            try:
                ws = self.sh.worksheet('BGG推薦快取')
                return ws
            except gspread.exceptions.WorksheetNotFound:
                # 工作表不存在，創建新的
                logger.info("建立 BGG推薦快取 工作表")
                ws = self.sh.add_worksheet(title='BGG推薦快取', rows=100, cols=52)

                # 設定標題列 - 擴展到50個遊戲ID
                headers = ['分類']
                for i in range(1, 51):
                    headers.append(f'BGG_ID_{i}')
                headers.append('更新時間')

                ws.update('A1:AZ1', [headers])

                return ws
        except Exception as e:
            logger.error(f"取得 BGG 快取工作表失敗: {e}")
            return None

    def save_bgg_recommendations(
            self,
            category: str,
            game_ids: List[int]) -> bool:
        """
        儲存 BGG 推薦快取

        Args:
            category: 分類名稱 (party/strategy/family/children)
            game_ids: BGG ID 列表（最多50個）

        Returns:
            bool: 是否成功
        """
        logger.info(f"[UPDATE] Saving BGG recommendations for {category}")
        if not self.valid:
            return False

        try:
            ws = self.get_bgg_cache_worksheet()
            if not ws:
                return False

            # 取得所有記錄
            records = ws.get_all_records()

            # 準備資料（補齊到50個ID）
            padded_ids = (game_ids + [0] * 50)[:50]
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
                ws.update(f'A{row_num}:AZ{row_num}', [row_data])
            else:
                # 新增記錄
                ws.append_row(row_data)

            logger.info(f"已儲存 {category} 的推薦快取，共 {len(game_ids)} 個遊戲")
            return True

        except Exception as e:
            logger.error(f"儲存 BGG 推薦快取失敗: {e}")
            return False

    def load_bgg_recommendations(self, category: str) -> Optional[List[int]]:
        """
        讀取 BGG 推薦快取

        Args:
            category: 分類名稱

        Returns:
            BGG ID 列表，如果沒有快取則返回 None
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
                    # 提取所有 BGG ID（排除 0，擴展到50）
                    game_ids = []
                    for i in range(1, 51):
                        game_id = record.get(f'BGG_ID_{i}', 0)
                        if game_id and int(game_id) > 0:
                            game_ids.append(int(game_id))

                    logger.info(f"從快取讀取 {category}，共 {len(game_ids)} 個遊戲")
                    return game_ids if game_ids else None

            return None

        except Exception as e:
            logger.error(f"讀取 BGG 推薦快取失敗: {e}")
            return None

    def get_bgg_recommendations_update_time(
            self, category: str) -> Optional[str]:
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
