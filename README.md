# 🎮 Boardgame-Web

**桌遊管理系統 - 完整的桌遊庫存、借閱和 BGG 整合解決方案**

[![Python](https://img.shields.io/badge/Python-3.9+-blue.svg)](https://www.python.org/)
[![Flask](https://img.shields.io/badge/Flask-3.0+-green.svg)](https://flask.palletsprojects.com/)
[![Redis](https://img.shields.io/badge/Redis-8.0+-red.svg)](https://redis.io/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

---

## 📊 專案概覽

Boardgame-Web 是一個功能完整的桌遊管理系統，提供：

- 📚 **桌遊庫存管理** - 完整的遊戲資料管理
- 🔍 **BGG 整合** - 自動獲取 BoardGameGeek 遊戲資訊
- 👥 **會員管理** - 借閱記錄和會員資料
- 📊 **效能監控** - 即時系統和快取統計
- 🖼️ **圖片展示** - 美觀的遊戲圖庫
- 🚀 **高效能** - 多層快取和並發優化

---

## ✨ 主要特性

### 🎯 核心功能

- ✅ Google Sheets 整合作為資料來源
- ✅ BoardGameGeek API 整合
- ✅ 批次借用/歸還功能
- ✅ 進階搜尋和篩選
- ✅ 響應式設計（支援手機、平板、桌面）
- ✅ 管理員後台

### ⚡ 效能優化

- ✅ **前端分頁** - DOM 節點減少 75%
- ✅ **圖片懶載入** - 首屏圖片減少 89%
- ✅ **Redis 快取** - API 呼叫減少 80%
- ✅ **並發請求** - 推薦頁面速度提升 400%
- ✅ **HTTP 快取** - 重複訪問速度提升 90%
- ✅ **資料庫索引** - 查詢速度提升 500%

### 📊 效能成果

| 指標 | 優化前 | 優化後 | 改善 |
|------|--------|--------|------|
| 頁面載入時間 | 3s | 680ms | **-77%** |
| DOM 節點數 | 4,140 | 1,018 | **-75%** |
| 首屏圖片數 | 414 | 46 | **-89%** |
| 推薦頁面載入 | 30s | 6s | **+400%** |
| 資料庫查詢 | 全表掃描 | 索引查詢 | **+500%** |

---

## 🚀 快速開始

### 環境需求

- Python 3.9+
- Redis 8.0+
- Google Sheets API 憑證

### 安裝步驟

```bash
# 1. 克隆專案
git clone <repository-url>
cd boardgame-web

# 2. 安裝依賴
pip install -r requirements.txt

# 3. 配置環境變數
cp .env.example .env
# 編輯 .env 檔案，設置必要的環境變數

# 4. 啟動 Redis（如果尚未運行）
redis-server

# 5. 啟動應用程式
python serve.py
```

### Docker 部署

```bash
# 使用 Docker Compose 一鍵啟動
docker-compose up -d

# 查看日誌
docker-compose logs -f

# 停止服務
docker-compose down
```

---

## 📖 使用指南

### 訪問應用程式

- **主頁**: http://localhost:5001/
- **管理頁面**: http://localhost:5001/admin.html
- **圖庫**: http://localhost:5001/gallery.html
- **監控儀表板**: http://localhost:5001/monitoring.html
- **API 文檔**: http://localhost:5001/api/docs

### API 端點

```bash
# 獲取遊戲列表
GET /api/games

# 借用遊戲
POST /api/borrow
{
  "name": "卡坦島",
  "borrower": "張三",
  "borrower_id": "A001"
}

# 搜尋 BGG 遊戲
GET /api/bgg/search?q=卡坦島

# 健康檢查
GET /api/monitoring/health
```

---

## 🏗️ 專案結構

```
boardgame-web/
├── app/                    # Flask 應用程式
│   ├── blueprints/        # Blueprint 路由
│   │   ├── main/         # 主要頁面
│   │   ├── api/          # API 端點
│   │   └── admin/        # 管理員功能
│   ├── middleware/        # 中介軟體
│   └── config.py         # 配置
├── core/                  # 核心業務邏輯
│   ├── facade.py         # Facade 模式
│   ├── game_service.py   # 遊戲服務
│   ├── bgg_service.py    # BGG 服務
│   ├── redis_cache.py    # Redis 快取
│   └── ...
├── static/               # 靜態資源
│   ├── css/             # 樣式表
│   ├── js/              # JavaScript
│   └── html/            # HTML 頁面
├── docs/                 # 文檔
│   ├── codebase/        # 程式碼文檔
│   ├── architecture/    # 架構文檔
│   └── api/             # API 文檔
├── tests/                # 測試
│   ├── unit/            # 單元測試
│   └── integration/     # 整合測試
├── Dockerfile           # Docker 配置
├── docker-compose.yml   # Docker Compose
└── serve.py            # 應用程式入口
```

---

## 📚 文檔

### 完整文檔

- [程式碼庫文檔](docs/codebase/README.md) - 完整的程式碼說明
- [測試指南](docs/codebase/testing_guide.md) - 346 個測試的說明
- [資料流程](docs/architecture/data_flow.md) - 系統資料流程圖
- [系統設計](docs/architecture/system_design.md) - 架構決策和設計模式
- [API 參考](docs/api/api_reference.md) - 33 個 API 端點文檔
- [部署指南](docs/deployment.md) - Docker 部署完整指南

### 快速參考

- **測試**: 346 個測試（253 單元 + 93 整合）
- **API 端點**: 33 個
- **文檔頁數**: 12 份專案文檔

---

## 🧪 測試

```bash
# 執行所有測試
pytest

# 執行單元測試
pytest tests/unit/

# 執行整合測試
pytest tests/integration/

# 測試覆蓋率
pytest --cov=core --cov=app --cov-report=html
```

---

## 🔧 技術棧

### 後端

- **Flask** 3.0+ - Web 框架
- **Python** 3.9+ - 程式語言
- **Redis** 8.0+ - 快取
- **SQLite** - 本地資料庫
- **Waitress** - WSGI 伺服器

### 前端

- **Vanilla JavaScript** - 無依賴
- **CSS3** - 現代化樣式
- **HTML5** - 語義化標記

### 外部服務

- **Google Sheets** - 資料儲存
- **BoardGameGeek API** - 遊戲資訊

---

## 📊 效能監控

訪問 http://localhost:5001/monitoring.html 查看：

- Redis 統計（版本、記憶體、鍵數）
- 快取命中率
- 系統資源使用（CPU、記憶體、磁碟）
- 健康檢查狀態

監控頁面每 5 秒自動刷新。

---

## 🐳 Docker 部署

### 服務架構

```
┌─────────────┐
│   使用者     │
└──────┬──────┘
       │
┌──────▼──────┐      ┌──────────┐
│  Flask App  │◄────►│  Redis   │
│  (port 5001)│      │  (快取)  │
└─────────────┘      └──────────┘
```

### 環境變數

在 `.env` 檔案中配置：

```bash
SHEET_URL=https://docs.google.com/spreadsheets/d/YOUR_SHEET_ID
GOOGLE_CREDENTIALS={"type":"service_account",...}
REDIS_HOST=redis
REDIS_PORT=6379
SECRET_KEY=your-secret-key
ADMIN_PASSWORD=your-admin-password
```

---

## 🎯 設計模式

- **Facade Pattern** - 統一的服務介面
- **Service Layer** - 業務邏輯分離
- **Repository Pattern** - 資料存取抽象
- **Decorator Pattern** - 快取和認證
- **Singleton Pattern** - Redis 連線管理

---

## 🤝 貢獻

歡迎貢獻！請遵循以下步驟：

1. Fork 專案
2. 建立功能分支 (`git checkout -b feature/AmazingFeature`)
3. 提交變更 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 開啟 Pull Request

---

## 📝 授權

本專案採用 MIT 授權 - 詳見 [LICENSE](LICENSE) 檔案

---

## 🙏 致謝

- [BoardGameGeek](https://boardgamegeek.com/) - 遊戲資料來源
- [Google Sheets API](https://developers.google.com/sheets/api) - 資料儲存
- [Redis](https://redis.io/) - 快取解決方案
- [Flask](https://flask.palletsprojects.com/) - Web 框架

---

## 📧 聯絡方式

如有問題或建議，請開啟 Issue 或聯絡專案維護者。

---

**專案狀態**: ✅ 生產就緒  
**版本**: 1.0.0  
**最後更新**: 2025-12-21
