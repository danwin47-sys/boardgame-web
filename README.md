# Boardgame-Web 桌遊管理系統

一個基於 Flask 的桌遊借還管理系統，使用 Google Sheets 作為後端資料庫，適合社團、工作室或個人收藏管理。

## ✨ 功能特色

### 📚 桌遊管理

- **即時狀態**：瀏覽所有桌遊，即時查看借出/在庫狀態。
- **借還操作**：支援單一或批次借出與歸還。
- **歷史記錄**：自動記錄所有操作與保管人資訊。

### 🎲 BGG 整合 (v2.0 新功能)

- **熱門遊戲**：即時顯示 BoardGameGeek (BGG) 熱門排行榜。
- **推薦清單**：根據分類 (派對、策略、家庭、兒童) 推薦熱門遊戲。
- **資料連結**：將庫存桌遊連結至 BGG 資料庫，自動抓取封面圖與詳細資訊。
- **進階搜尋**：支援模糊搜尋與精確搜尋，快速找到對應的 BGG 條目。

### 👥 社員管理

- **快速檢索**：支援 ID 或姓名搜尋。
- **個人紀錄**：查看每位社員的當前借閱與歷史紀錄。

### 🔒 管理員後台

- **權限控管**：密碼保護的管理介面。
- **批次處理**：支援大量歸還與強制操作。
- **完整紀錄**：查看系統所有操作流水帳。

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

建立 `.env` 檔案或設定系統環境變數：

- `SHEET_URL`: Google Sheet 的完整網址
- `GOOGLE_CREDENTIALS`: JSON 憑證內容 (或將檔案命名為 `boardgame-bot-*.json` 放在根目錄)
- `ADMIN_PASSWORD`: 管理員登入密碼
- `BGG_API_TOKEN`: (選填) 用於 BGG API 的 Token，若無則使用 Demo 模式

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

1. 在首頁點擊桌遊旁的「連結」按鈕。
2. 系統會自動搜尋 BGG 資料庫。
3. 選擇正確的遊戲條目進行連結。
4. 連結後將自動更新封面圖與遊戲資訊。

## 📂 專案架構

本專案採用模組化架構設計，詳細的檔案用途說明請參考：
👉 **[專案結構與檔案用途說明 (docs/PROJECT_STRUCTURE.md)](docs/PROJECT_STRUCTURE.md)**

簡要結構：

```
boardgame-web/
├── app/                 # Web 應用程式核心 (Flask Blueprints)
├── core/                # 核心業務邏輯 (Services, Clients)
├── static/              # 前端資源 (CSS, JS, HTML)
├── scripts/             # 維護與更新工具
├── tests/               # 測試套件
├── serve.py             # 程式進入點
└── requirements.txt     # 依賴套件
```

## 🧪 測試

本專案包含完整的單元測試與整合測試。

```bash
# 安裝測試依賴
pip install -r requirements-dev.txt

# 執行測試
pytest
```

詳細測試說明請參考 [測試文檔](docs/TESTING.md)。

## 📄 授權

本專案採用 MIT 授權條款。

## 🤝 貢獻

歡迎提交 Issue 或 Pull Request！如有任何問題，請查閱 [架構說明](docs/ARCHITECTURE.md) 或直接聯絡開發團隊。
