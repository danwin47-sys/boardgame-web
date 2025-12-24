# 🎮 Boardgame-Web

**桌遊管理系統 - 完整的桌遊庫存、借閱和 BGG 整合解決方案**

[![Python](https://img.shields.io/badge/Python-3.9+-blue.svg)](https://www.python.org/)
[![Flask](https://img.shields.io/badge/Flask-3.0+-green.svg)](https://flask.palletsprojects.com/)
[![Redis](https://img.shields.io/badge/Redis-8.0+-red.svg)](https://redis.io/)
[![Coverage](https://img.shields.io/badge/Coverage-80%25-brightgreen.svg)](tests/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

---

## 📊 專案概覽

Boardgame-Web 是一個現代化、高效能的桌遊管理系統，專為桌遊社團設計。它結合了強大的庫存管理功能與流暢的使用者體驗，並針對行動裝置進行了深度優化。

- 📚 **桌遊庫存管理** - 完整的遊戲資料庫與分類系統
- 📱 **行動優先設計** - 專為手機優化的卡片式介面與操作體驗
- 🔍 **BGG 整合** - 自動同步 BoardGameGeek 全球桌遊資料
- 👥 **會員與借閱** - 實時借還系統與歷史記錄追蹤
- 📊 **效能監控** - 內建系統資源與 Redis 快取監控面板
- 🚀 **高效能架構** - 多層快取設計，確保秒級回應

---

## ✨ 最新亮點 (v1.1)

### 📱 手機版 UI 全面進化
- **卡片式佈局**: 手機瀏覽時自動切換為精美的資訊卡片，告別擁擠的表格。
- **2x2 統計網格**: 關鍵數據一目了然，空間利用率最大化。
- **智慧摺疊面板**: 篩選器自動收合，釋放寶貴的螢幕空間。
- **觸控友善設計**: 全面優化按鈕尺寸 (44px+) 與間距，操作不再誤觸。

### 🧪 測試覆蓋率 80%
- **穩健可靠**: 通過 390+ 個自動化測試案例。
- **全面防護**: 核心邏輯、API 端點與擴充服務皆有完整測試保護。

---

## 🚀 主要特性

### 🎯 核心功能

- ✅ **Google Sheets 同步** - 作為易於維護的後端資料來源
- ✅ **BoardGameGeek API** - 自動獲取遊戲評分、機制與難度資訊
- ✅ **批次借還系統** - 支援快速借出與歸還流程
- ✅ **進階搜尋過濾** - 依人數、時間、難度、類別快速篩選
- ✅ **擴充遊戲支援** - 完整的基礎遊戲與擴充包關聯管理
- ✅ **管理員後台** - 便捷的增刪改查 (CRUD) 介面

### ⚡ 效能優化成果

| 指標           | 優化前   | 優化後       | 改善幅度    |
| -------------- | -------- | ------------ | ----------- |
| **頁面載入**   | 3.0s     | **680ms**    | 🚀 **-77%**  |
| **DOM 節點**   | 4,140    | **1,018**    | 📉 **-75%**  |
| **首屏請求**   | 414      | **46**       | 📉 **-89%**  |
| **資料庫查詢** | 全表掃描 | **索引查詢** | ⚡ **+500%** |
| **測試覆蓋率** | 0%       | **80%**      | 🛡️ **+80%**  |

---

## 🛠️ 安裝與啟動

### 環境需求

- Python 3.9+
- Redis 8.0+
- Google Cloud Service Account (用於 Sheets API)

### 快速開始

1. **克隆專案**
   ```bash
   git clone <repository-url>
   cd boardgame-web
   ```

2. **安裝依賴**
   ```bash
   pip install -r requirements.txt
   ```

3. **環境配置**
   建立 `.env` 檔案並填入以下資訊：
   ```env
   SHEET_URL=https://docs.google.com/spreadsheets/d/YOUR_SHEET_ID
   GOOGLE_CREDENTIALS={"type":"service_account",...}
   REDIS_HOST=localhost
   REDIS_PORT=6379
   SECRET_KEY=your-secret-key
   ADMIN_PASSWORD=admin
   ```

4. **啟動服務**
   ```bash
   # 啟動 Redis (如尚未啟動)
   redis-server

   # 啟動應用程式
   python serve.py
   ```

### 🐳 Docker 部署 (推薦)

```bash
# 一鍵啟動所有服務
docker-compose up -d

# 查看即時日誌
docker-compose logs -f
```

---

## 📖 API 文檔

系統提供 RESTful API 供前端與外部系統串接。

|  方法  | 端點                     | 描述                        |
| :----: | :----------------------- | :-------------------------- |
| `GET`  | `/api/games`             | 獲取所有遊戲列表 (支援篩選) |
| `POST` | `/api/borrow`            | 借出遊戲                    |
| `POST` | `/api/return`            | 歸還遊戲                    |
| `GET`  | `/api/bgg/search`        | 搜尋 BGG 資料庫             |
| `GET`  | `/api/monitoring/health` | 系統健康檢查                |
| `GET`  | `/api/metrics/summary`   | 獲取系統統計指標            |

完整 API 文檔請參考：`docs/api/api_reference.md`

---

## 🏗️ 專案架構

```
boardgame-web/
├── app/                    # Flask 應用程式核心
│   ├── blueprints/        # 路由模組 (Main, API, Admin)
│   ├── templates/         # Jinja2 模板 (HTML)
│   └── static/            # 靜態資源 (CSS, JS)
├── core/                  # 核心業務邏輯 (Service Layer)
│   ├── game_service.py   # 遊戲管理服務
│   ├── bgg_service.py    # BGG 整合服務
│   └── redis_cache.py    # 快取管理服務
├── tests/                # 自動化測試
│   ├── unit/            # 單元測試
│   └── integration/     # 整合測試
├── docs/                 # 專案文檔
└── serve.py             # 程式進入點
```

---

## 🧪 測試與驗證

我們採用 `pytest` 進行全方位測試。

```bash
# 執行所有測試
pytest

# 產生覆蓋率報告
pytest --cov=core --cov=app --cov-report=html
```

目前測試覆蓋率已達 **80%**，包含以下關鍵模組：
- `expansion_service`: 93%
- `monitoring`: 87%
- `metrics`: 86%
- `games_api`: 83%

---

## 🤝 貢獻指南

歡迎任何形式的貢獻！

1. Fork 本專案
2. 建立功能分支 (`git checkout -b feature/NewFeature`)
3. 提交變更 (`git commit -m 'Add NewFeature'`)
4. 推送至分支 (`git push origin feature/NewFeature`)
5. 提交 Pull Request

---

## 📝 授權

本專案採用 [MIT License](LICENSE) 授權。

---

**最後更新**: 2025-12-25
**維護者**: Derek Shih
