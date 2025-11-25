# Boardgame-Web 桌遊管理系統

一個基於 Flask 的桌遊借還管理系統，使用 Google Sheets 作為後端資料庫，適合社團、工作室或個人收藏管理。

## 功能特色

### 📚 桌遊管理

- 瀏覽所有桌遊及狀態
- 查看借出記錄與保管人資訊
- 支援批次借出/歸還操作
- 自動記錄歷史操作

### 👥 社員管理

- 社員資料查詢
- 根據 ID 或姓名快速檢索
- 查看個人借閱紀錄

### 🔒 管理員功能

- 密碼保護的管理頁面
- 批次歸還功能
- 完整操作歷史

### 🌐 現代化 Web UI

- 響應式設計，支援行動裝置
- 即時狀態更新
- 簡潔直觀的操作流程

## 系統需求

- **Python**: 3.8 或以上版本
- **Google Sheets API**: 需要服務帳戶憑證
- **瀏覽器**: 現代瀏覽器 (Chrome, Firefox, Safari, Edge)

## 安裝步驟

### 1. 克隆專案

```bash
git clone https://github.com/danwin47-sys/boardgame-web.git
cd boardgame-web
```

### 2. 安裝依賴套件

```bash
pip install -r requirements.txt
```

**requirements.txt 內容：**

```
flask==3.0.3
flask-cors==5.0.0
gunicorn
gspread
oauth2client
requests
```

### 3. 設定 Google Sheets API

#### 3.1 建立 Google Cloud 專案

1. 前往 [Google Cloud Console](https://console.cloud.google.com/)
2. 建立新專案
3. 啟用 **Google Sheets API**
4. 建立服務帳戶並下載 JSON 憑證檔

#### 3.2 設定 Google Sheets

1. 建立新的 Google 試算表
2. 建立兩個工作表：
   - `games` (桌遊清單)
   - `members` (社員清單)

**games 工作表欄位：**

| name | status | borrower | borrower_id | mdate | history | custodian |
|------|--------|----------|-------------|-------|---------|-----------|
| 桌遊名稱 | 歸還/借出 | 借閱者 | 社員ID | 時間戳 | 操作歷史 | 保管人 |

**members 工作表欄位：**

| id | name |
|----|------|
| M001 | 王小明 |

3. 將服務帳戶的 email 加入試算表的編輯權限

### 4. 配置環境變數

#### 本地開發

將憑證 JSON 檔放在專案根目錄，命名為 `boardgame-bot-XXXXXXXX.json`

#### Render 部署 (線上環境)

在 Render 設定以下環境變數：

- `SHEET_URL`: Google Sheets 連結
- `GOOGLE_CREDENTIALS`: 憑證 JSON 內容 (整個檔案)
- `ADMIN_PASSWORD`: 管理員密碼

## 使用說明

### 本地執行

```bash
python flask_app.py
```

應用程式將在 `http://localhost:5000` 啟動

### 使用者操作

#### 1. 瀏覽桌遊

- 開啟首頁即可看到所有桌遊
- 綠色標籤 = 可借出
- 紅色標籤 = 已借出

#### 2. 借出桌遊

1. 輸入您的社員 ID
2. 點擊想借的桌遊卡片
3. 確認借出

#### 3. 歸還桌遊

1. 點擊已借出的桌遊卡片
2. 確認歸還

### 管理員操作

#### 1. 登入管理頁面

1. 前往 `/admin.html`
2. 輸入管理員密碼
3. 登入後可使用進階功能

#### 2. 批次歸還

- 可一次歸還某位社員的所有桌遊
- 支援多選批次歸還

## API 端點

### 公開 API

- `GET /api/games` - 取得所有桌遊
- `GET /api/members` - 取得所有社員
- `POST /api/borrow` - 借出桌遊
- `POST /api/return` - 歸還桌遊

### 管理員 API

- `POST /api/batch-borrow` - 批次借出
- `POST /api/batch-return` - 批次歸還
- `POST /api/admin-login` - 管理員登入

## 部署到 Render

### 1. 推送至 GitHub

```bash
git push origin master
```

### 2. 在 Render 建立服務

1. 登入 [Render](https://render.com)
2. 新增 **Web Service**
3. 連接 GitHub Repository
4. 環境選擇 **Docker**
5. 設定環境變數 (SHEET_URL, GOOGLE_CREDENTIALS, ADMIN_PASSWORD)

### 3. 部署

Render 會自動偵測 `Dockerfile` 並部署

## 專案架構

```
boardgame-web/
├── flask_app.py            # Flask 應用程式
├── boardgame_system.py     # 業務邏輯 (Facade)
├── core/                   # 核心模組
│   ├── constants.py        # 常量定義
│   ├── utils.py            # 工具函數
│   ├── exceptions.py       # 自定義異常
│   ├── cache.py            # 快取機制
│   ├── decorators.py       # Flask 裝飾器
│   ├── sheets_client.py    # Google Sheets 客戶端
│   ├── game_service.py     # 桌遊業務邏輯
│   └── member_service.py   # 社員業務邏輯
├── static/                 # 前端資源
│   ├── index.html          # 使用者介面
│   ├── admin.html          # 管理員介面
│   ├── script.js           # JavaScript
│   └── style.css           # 樣式表
├── Dockerfile             # Docker 配置
├── requirements.txt       # Python 依賴
└── README.md             # 本文件
```

## 技術亮點

### 後端優化

- **模組化架構**: 採用 Service 模式拆分業務邏輯
- **快取機制**: 減少 API 呼叫，提升效能
- **批次更新**: 優化 Google Sheets API 使用
- **向後相容**: Facade 模式確保平滑升級

### 前端特色

- **響應式設計**: 適配各種螢幕尺寸
- **即時反饋**: 操作結果即時顯示
- **搜尋過濾**: 快速找到目標桌遊

## 安全性

- Admin 密碼保護
- 環境變數管理敏感資訊
- CORS 配置
- 服務帳戶權限最小化

## 效能優化

### 快取策略

- **桌遊列表**: 30 秒 TTL
- **社員列表**: 1 小時 TTL

### 批次操作

- 批次更新減少 API 呼叫
- 預先載入社員資料避免 N+1 查詢

## 常見問題

### Q: 如何重設管理員密碼？

A: 修改 Render 環境變數 `ADMIN_PASSWORD` 或本地 `.env` 檔案

### Q: 如何新增桌遊？

A: 直接在 Google Sheets 的 `games` 工作表新增一列

### Q: 支援多語言嗎？

A: 目前僅支援繁體中文

### Q: 可以離線使用嗎？

A: 不行，需要網路連線存取 Google Sheets

## 授權

本專案採用 MIT 授權條款。

## 貢獻

歡迎提交 Issue 或 Pull Request！

## 聯絡方式

如有問題或建議，歡迎開 Issue 討論。
