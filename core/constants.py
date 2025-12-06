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

# === 桌遊狀態（狀態值，非動作）===
GAME_STATUS_AVAILABLE = "可用"      # 桌遊可借用
GAME_STATUS_BORROWED = "已借出"     # 桌遊已被借走

# 向後相容的舊值（Google Sheets 中仍使用這些值）
GAME_STATUS_AVAILABLE_LEGACY = "歸還"
GAME_STATUS_BORROWED_LEGACY = "借出"

# === Google Sheets 工作表名稱 ===
WORKSHEET_GAMES = "games"
WORKSHEET_MEMBERS = "members"

# === 欄位名稱（英文，程式碼內部使用）===
FIELD_NAME = 'name'
FIELD_STATUS = 'status'
FIELD_BORROWER = 'borrower'
FIELD_BORROWER_ID = 'borrower_id'
FIELD_MDATE = 'mdate'
FIELD_HISTORY = 'history'
FIELD_CUSTODIAN = 'custodian'
FIELD_ID = 'id'

# === 欄位名稱（中文，Google Sheets 實際欄位名）===
FIELD_NAME_ZH = '名稱'
FIELD_STATUS_ZH = '狀態'
FIELD_BORROWER_ZH = '借閱人'
FIELD_BORROWER_ID_ZH = '借閱人ID'
FIELD_CUSTODIAN_ZH = '保管人'
FIELD_LOCATION_ZH = '位置'
FIELD_DIFFICULTY_ZH = '困難度'
FIELD_PLAYERS_ZH = '人數'

# === 歷史記錄動作 ===
ACTION_BORROW = "借閱"
ACTION_RETURN = "歸還"

# === 環境變數 ===
ENV_SHEET_URL = "SHEET_URL"
ENV_GOOGLE_CREDENTIALS = "GOOGLE_CREDENTIALS"
ENV_ADMIN_PASSWORD = "ADMIN_PASSWORD"

# === 預設值 ===
DEFAULT_PORT = 5000
