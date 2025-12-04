# Boardgame-Web 桌遊管理系統

一個基於 Flask 的桌遊借還管理系統，使用 Google Sheets 作為後端資料庫，整合 BoardGameGeek (BGG) 資料，提供完整的桌遊收藏管理解決方案。適合社團、工作室或個人收藏管理。

## ✨ 功能特色

### 📚 桌遊管理

- **即時狀態**：瀏覽所有桌遊，即時查看借出/在庫狀態
- **借還操作**：支援單一或批次借出與歸還
- **歷史記錄**：自動記錄所有操作與保管人資訊
- **圖庫牆 (Gallery Wall)**：視覺化的桌遊展示介面，支援多條件過濾

### 🔒 管理員後台

- **權限控管**：密碼保護的管理介面
- **批次處理**：支援大量歸還與強制操作
- **完整紀錄**：查看系統所有操作流水帳
- **Email 通知**：關鍵更新與錯誤的郵件通知功能

### 🎲 BGG 整合

- **熱門遊戲**：即時顯示 BoardGameGeek (BGG) 熱門排行榜
- **智慧推薦**：根據分類（派對、策略、家庭、兒童）推薦適合的桌遊
- **本地資料庫**：整合 BGG Ranks 離線資料庫，提供快速查詢與排名資訊
- **資料連結**：將庫存桌遊連結至 BGG 資料庫，自動抓取封面圖與詳細資訊
- **進階搜尋**：支援模糊搜尋與精確搜尋，快速找到對應的 BGG 條目
- **自動更新**：定期自動下載最新的 BGG 排名資料

### 🏆 成就系統

- **追蹤成就**：記錄教學、參與、借閱等多種成就
- **視覺化呈現**：清晰顯示個人成就進度
- **詳細參考**：完整的成就系統說明文檔

### 👥 社員管理

- **快速檢索**：支援 ID 或姓名搜尋
- **個人紀錄**：查看每位社員的當前借閱與歷史紀錄
- **成就追蹤**：查看個人成就與貢獻統計

## 🚀 系統需求

- **Python**: 3.8+
- **Google Sheets API**: 需設定 Service Account
- **資料庫**: Google Sheets (作為資料庫使用)

## 🛠️ 安裝與設定

### 1. 取得專案

```bash
git clone https://github.com/danwin47-sys/boardgame-web.git
cd boardgame-web
```

### 2. 安裝依賴

```bash
pip install -r requirements.txt
```

### 3. Google Sheets 設定

1. 建立 Google Cloud 專案並啟用 **Google Sheets API**。
2. 建立 Service Account 並下載 JSON 憑證。
3. 建立 Google Sheet，新增 `games` (桌遊) 與 `members` (社員) 兩個工作表。
4. 將 Service Account Email 加入 Google Sheet 的編輯者。

### 4. 環境變數

建立 `.env` 檔案（系統會自動讀取）：

1. 複製範本：`cp .env.example .env`
2. 編輯 `.env` 填入以下資訊：

**必要設定：**

- `SHEET_URL`: Google Sheet 的完整網址
- `GOOGLE_CREDENTIALS`: JSON 憑證內容（或將檔案命名為 `boardgame-bot-*.json` 放在根目錄）
- `ADMIN_PASSWORD`: 管理員登入密碼

**選用設定：**

- `BGG_API_TOKEN`: 用於 BGG API 的 Token（若無則使用 Demo 模式）
- `EMAIL_SENDER`: Email 通知的寄件者地址
- `EMAIL_PASSWORD`: Email 帳號密碼
- `EMAIL_RECIPIENT`: 接收通知的 Email 地址

### 5. BGG Ranks 資料庫（選用）

若要使用 BGG Ranks 離線查詢功能：

```bash
# 下載最新的 BGG 資料
python scripts/update/download_bgg_dumps.py

# 匯入到本地資料庫
python scripts/update/import_bgg_ranks.py
```

### 6. 部署 (Render)

若部署至 Render.com，請使用 **Secret Files** 設定環境變數：

1. 進入 Render Dashboard > Environment
2. 點擊 **Add Secret File**
3. Filename 輸入 `.env`
4. 內容貼上您的 `.env` 檔案內容（包含密碼與 Token）
5. 儲存後 Render 會自動重新部署

## 📖 使用說明

### 啟動伺服器

```bash
# Windows 快速啟動
./start.ps1

# 或直接使用 Python
python serve.py
```

伺服器將於 `http://localhost:5000` 啟動。

### 連結 BGG 資料

1. 在首頁點擊桌遊旁的「連結」按鈕
2. 系統會自動搜尋 BGG 資料庫
3. 選擇正確的遊戲條目進行連結
4. 連結後將自動更新封面圖與遊戲資訊

### 使用圖庫牆 (Gallery Wall)

1. 點擊首頁的「圖庫牆」連結或訪問 `/gallery.html`
2. 使用上方的過濾器進行篩選：
   - **人數過濾**：依玩家數量篩選遊戲
   - **類型過濾**：依遊戲類型（派對、策略、家庭等）
   - **標籤過濾**：依特殊標籤分類
3. 點擊遊戲卡片查看詳細資訊

### 更新 BGG 推薦

```bash
# 手動更新 BGG 推薦清單
python scripts/update/update_bgg_recommendations.py

# 自動更新 BGG Ranks 資料庫（每週自動執行）
python scripts/update/auto_update_bgg_ranks.py
```

## 📂 專案架構

本專案採用模組化架構設計，詳細的檔案用途說明請參考：
👉 **[專案結構與檔案用途說明 (docs/PROJECT_STRUCTURE.md)](docs/PROJECT_STRUCTURE.md)**

簡要結構：

```plaintext
boardgame-web/
├── app/                       # Web 應用程式核心
│   ├── blueprints/           # Flask Blueprints
│   │   ├── api/              # API 端點
│   │   │   ├── bgg.py        # BGG 資料整合 API
│   │   │   ├── gallery.py    # 圖庫牆 API
│   │   │   └── ...
│   │   └── routes.py         # 主要路由
│   └── utils/                # 工具函數
├── core/                      # 核心業務邏輯
│   ├── bgg_service.py        # BGG API 服務
│   ├── bgg_ranks_service.py  # BGG Ranks 資料庫服務
│   ├── sheets_client.py      # Google Sheets 客戶端
│   ├── email_notifier.py     # Email 通知服務
│   └── ...
├── data/                      # 本地資料庫
│   └── bgg_ranks/            # BGG 排名資料庫
│       └── bgg_ranks.db      # SQLite 資料庫
├── static/                    # 前端資源
│   ├── index.html            # 主頁面
│   ├── gallery.html          # 圖庫牆頁面
│   ├── gallery.js            # 圖庫牆功能
│   ├── gallery.css           # 圖庫牆樣式
│   └── data/                 # 靜態資料
│       └── recommendations.json  # 推薦遊戲快取
├── scripts/                   # 維護與更新工具
│   ├── update/               # 資料更新腳本
│   │   ├── update_bgg_recommendations.py  # 更新 BGG 推薦
│   │   ├── auto_update_bgg_ranks.py       # 自動更新排名
│   │   ├── download_bgg_dumps.py          # 下載 BGG 資料
│   │   ├── import_bgg_ranks.py            # 匯入排名資料
│   │   └── upload_csv_to_sheets.py        # 上傳 CSV 至 Sheets
│   └── tools/                # 其他工具
├── tests/                     # 測試套件
│   ├── unit/                 # 單元測試
│   │   └── test_gallery_filters.py
│   └── integration/          # 整合測試
│       └── test_gallery_api.py
├── docs/                      # 文檔
│   ├── ACHIEVEMENTS_REFERENCE.md  # 成就系統參考
│   ├── PROJECT_STRUCTURE.md       # 專案結構說明
│   └── ...
├── serve.py                   # 程式進入點
└── requirements.txt           # 依賴套件
```

## 🧪 測試

本專案包含完整的單元測試與整合測試。

```bash
# 安裝測試依賴
pip install -r requirements-dev.txt

# 執行所有測試
pytest

# 執行特定測試模組
pytest tests/unit/test_gallery_filters.py
pytest tests/integration/test_gallery_api.py

# 產生測試覆蓋率報告
pytest --cov=app --cov=core
```

詳細測試說明請參考 [測試文檔](docs/TESTING.md)。

## � 詳細文檔

- **[成就系統參考](docs/ACHIEVEMENTS_REFERENCE.md)** - 完整的成就系統說明與追蹤指南
- **[專案結構](docs/PROJECT_STRUCTURE.md)** - 詳細的目錄結構與檔案用途
- **[架構說明](docs/ARCHITECTURE.md)** - 系統架構與設計理念
- **[測試指南](docs/TESTING.md)** - 測試策略與最佳實踐

## 🎯 主要功能亮點

### Gallery Wall 圖庫牆

視覺化的桌遊展示介面，提供：

- 美觀的網格布局展示
- 多條件同時過濾（人數、類型、標籤）
- 即時搜尋與篩選
- 響應式設計，支援各種螢幕尺寸

### BGG Ranks 本地資料庫

整合 BoardGameGeek 完整排名資料：

- 30 萬+ 桌遊資料本地查詢
- 支援按名稱、BGG ID、排名、類別查詢
- 離線可用，查詢速度快
- 自動定期更新最新資料

### 自動化更新系統

- 自動下載 BGG 最新資料 dump
- 智慧匯入與資料庫更新
- Email 通知關鍵更新與錯誤
- 完整的錯誤處理與日誌記錄

## �📄 授權

本專案採用 MIT 授權條款。

## 🤝 貢獻

歡迎提交 Issue 或 Pull Request！如有任何問題，請查閱相關文檔或直接聯絡開發團隊。

### 開發指南

1. Fork 本專案
2. 建立您的功能分支 (`git checkout -b feature/AmazingFeature`)
3. 提交您的更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 開啟 Pull Request

---

**最後更新：** 2025-12-04  
**版本：** 3.0 (Gallery Wall & BGG Ranks Integration)
