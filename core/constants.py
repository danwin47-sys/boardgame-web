# coding: utf-8
"""
常量定義模組
集中管理 boardgame-web 專案的所有常量
"""

# === 快取時間（秒）===
GAMES_CACHE_TTL = 30  # 遊戲列表快取 30 秒
MEMBERS_CACHE_TTL = 3600  # 社員列表快取 1 小時

# === 時間相關 ===
MILLISECONDS_PER_SECOND = 1000
DATETIME_FORMAT = '%Y-%m-%d %H:%M'

# === 桌遊狀態 ===
GAME_STATUS_AVAILABLE = "歸還"
GAME_STATUS_BORROWED = "借出"

# === Google Sheets 工作表名稱 ===
WORKSHEET_GAMES = "games"
WORKSHEET_MEMBERS = "members"

# === 欄位名稱 ===
FIELD_NAME = 'name'
FIELD_STATUS = 'status'
FIELD_BORROWER = 'borrower'
FIELD_BORROWER_ID = 'borrower_id'
FIELD_MDATE = 'mdate'
FIELD_HISTORY = 'history'
FIELD_CUSTODIAN = 'custodian'
FIELD_ID = 'id'

# === 歷史記錄動作 ===
ACTION_BORROW = "借閱"
ACTION_RETURN = "歸還"

# === 環境變數 ===
ENV_SHEET_URL = "SHEET_URL"
ENV_GOOGLE_CREDENTIALS = "GOOGLE_CREDENTIALS"
ENV_ADMIN_PASSWORD = "ADMIN_PASSWORD"

# === 預設值 ===
DEFAULT_ADMIN_PASSWORD = "admin123"
DEFAULT_PORT = 5000
