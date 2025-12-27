# coding: utf-8
"""
常量定義模組
集中管理 boardgame-web 專案的所有常量
"""

# === 快取時間（秒）===
GAMES_CACHE_TTL = 300  # 遊戲列表快取 5 分鐘（優化：減少 API 呼叫）
MEMBERS_CACHE_TTL = 1800  # 社員列表快取 30 分鐘（優化：平衡即時性與效能）

# === 時間相關 ===
MILLISECONDS_PER_SECOND = 1000
DATETIME_FORMAT = "%Y-%m-%d %H:%M"

# === 桌遊狀態（狀態值，非動作）===
GAME_STATUS_AVAILABLE = "在庫"  # 桌遊可借用
GAME_STATUS_BORROWED = "借出"  # 桌遊已被借走

# === Google Sheets 工作表名稱 ===
WORKSHEET_GAMES = "games"
WORKSHEET_MEMBERS = "members"

# === 欄位名稱（英文，程式碼內部使用）===
FIELD_NAME = "name"
FIELD_STATUS = "status"
FIELD_BORROWER = "borrower"
FIELD_BORROWER_ID = "borrower_id"
FIELD_MDATE = "mdate"
FIELD_HISTORY = "history"
FIELD_CUSTODIAN = "custodian"
FIELD_ID = "id"

# 擴充管理欄位
FIELD_IS_EXPANSION = "is_expansion"
FIELD_PARENT_GAME = "parent_game"
FIELD_STORAGE_MODE = "storage_mode"

# === 欄位名稱（中文，Google Sheets 實際欄位名）===
FIELD_NAME_ZH = "名稱"
FIELD_STATUS_ZH = "狀態"
FIELD_BORROWER_ZH = "借閱人"
FIELD_BORROWER_ID_ZH = "借閱人ID"
FIELD_CUSTODIAN_ZH = "保管人"
FIELD_LOCATION_ZH = "位置"
FIELD_DIFFICULTY_ZH = "困難度"
FIELD_PLAYERS_ZH = "人數"

# === 歷史記錄動作 ===
ACTION_BORROW = "借閱"
ACTION_RETURN = "歸還"

# === 擴充收納模式 ===
STORAGE_MODE_MERGED = "merged"  # 合併收納（借出主遊戲時自動連動擴充）
STORAGE_MODE_INDEPENDENT = "independent"  # 獨立收納（擴充可單獨借出）

# === 環境變數 ===
ENV_SHEET_URL = "SHEET_URL"
ENV_GOOGLE_CREDENTIALS = "GOOGLE_CREDENTIALS"
ENV_ADMIN_PASSWORD = "ADMIN_PASSWORD"

# === 預設值 ===
DEFAULT_PORT = 5000
