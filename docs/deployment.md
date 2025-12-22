# 🚀 Boardgame-Web 部署指南

**最後更新**: 2025-12-21

---

## 📋 目錄

1. [環境需求](#環境需求)
2. [Docker 部署](#docker-部署)
3. [環境變數配置](#環境變數配置)
4. [部署步驟](#部署步驟)
5. [驗證部署](#驗證部署)
6. [故障排除](#故障排除)

---

## 🔧 環境需求

### 必要軟體

- **Docker**: 20.10+ 
- **Docker Compose**: 2.0+
- **Git**: 2.0+

### 硬體需求

- **CPU**: 2 核心以上
- **記憶體**: 2 GB 以上
- **磁碟空間**: 5 GB 以上

---

## 🐳 Docker 部署

### 快速開始

```bash
# 1. 克隆專案
git clone <repository-url>
cd boardgame-web

# 2. 配置環境變數
cp .env.example .env
# 編輯 .env 檔案，設置必要的環境變數

# 3. 啟動服務
docker-compose up -d

# 4. 查看日誌
docker-compose logs -f
```

### 服務架構

```
┌─────────────────┐
│   使用者請求     │
└────────┬────────┘
         │
    ┌────▼─────┐
    │  Port    │
    │  5001    │
    └────┬─────┘
         │
┌────────▼────────┐      ┌──────────────┐
│  Flask App      │◄────►│  Redis       │
│  (boardgame-app)│      │  (快取)      │
└─────────────────┘      └──────────────┘
         │
    ┌────▼─────┐
    │  Google  │
    │  Sheets  │
    └──────────┘
```

---

## 🔐 環境變數配置

### 必要變數

建立 `.env` 檔案：

```bash
# Google Sheets 配置
SHEET_URL=https://docs.google.com/spreadsheets/d/YOUR_SHEET_ID
GOOGLE_CREDENTIALS={"type":"service_account",...}

# Redis 配置
REDIS_HOST=redis
REDIS_PORT=6379
REDIS_DB=0
REDIS_PASSWORD=

# 應用程式配置
SECRET_KEY=your-secret-key-here
FLASK_ENV=production
LOG_LEVEL=INFO

# 管理員密碼
ADMIN_PASSWORD=your-admin-password

# 演示模式（選填）
DEMO_MODE=false
```

### 環境變數說明

| 變數 | 說明 | 預設值 |
|------|------|--------|
| `SHEET_URL` | Google Sheets 網址 | 必填 |
| `GOOGLE_CREDENTIALS` | Google 服務帳號憑證 | 必填 |
| `REDIS_HOST` | Redis 主機 | redis |
| `REDIS_PORT` | Redis 端口 | 6379 |
| `SECRET_KEY` | Flask 密鑰 | 必填 |
| `ADMIN_PASSWORD` | 管理員密碼 | 必填 |

---

## 📦 部署步驟

### 1. 準備環境

```bash
# 確認 Docker 已安裝
docker --version
docker-compose --version

# 克隆專案
git clone <repository-url>
cd boardgame-web
```

### 2. 配置環境變數

```bash
# 複製環境變數範例
cp .env.example .env

# 編輯 .env 檔案
nano .env  # 或使用其他編輯器
```

### 3. 建立 Docker 映像

```bash
# 建立映像
docker-compose build

# 查看映像
docker images | grep boardgame
```

### 4. 啟動服務

```bash
# 啟動所有服務（背景執行）
docker-compose up -d

# 查看服務狀態
docker-compose ps

# 查看日誌
docker-compose logs -f app
docker-compose logs -f redis
```

### 5. 停止服務

```bash
# 停止服務
docker-compose stop

# 停止並移除容器
docker-compose down

# 停止並移除容器和資料卷
docker-compose down -v
```

---

## ✅ 驗證部署

### 1. 檢查服務狀態

```bash
# 查看容器狀態
docker-compose ps

# 應該看到：
# boardgame-app    running
# boardgame-redis  running
```

### 2. 測試應用程式

```bash
# 健康檢查
curl http://localhost:5001/api/health

# 預期回應：
# {"status":"healthy","services":{"redis":"connected","application":"running"}}

# 測試遊戲 API
curl http://localhost:5001/api/games

# 測試監控 API
curl http://localhost:5001/api/monitoring/redis-stats
```

### 3. 訪問網頁

開啟瀏覽器訪問：

- **主頁**: http://localhost:5001/
- **管理頁面**: http://localhost:5001/admin.html
- **監控儀表板**: http://localhost:5001/monitoring.html

---

## 🔍 故障排除

### 問題 1: 容器無法啟動

**症狀**: `docker-compose up` 失敗

**解決方案**:
```bash
# 查看詳細錯誤
docker-compose logs app

# 檢查端口是否被佔用
lsof -i :5001
lsof -i :6379

# 清理並重新啟動
docker-compose down
docker-compose up -d
```

### 問題 2: Redis 連線失敗

**症狀**: 應用程式日誌顯示 "Redis 未連線"

**解決方案**:
```bash
# 檢查 Redis 容器狀態
docker-compose ps redis

# 測試 Redis 連線
docker-compose exec redis redis-cli ping
# 應該返回: PONG

# 重啟 Redis
docker-compose restart redis
```

### 問題 3: Google Sheets 連線失敗

**症狀**: 無法讀取遊戲資料

**解決方案**:
1. 檢查 `.env` 中的 `SHEET_URL` 是否正確
2. 檢查 `GOOGLE_CREDENTIALS` 是否有效
3. 確認服務帳號有權限存取 Google Sheets

```bash
# 查看應用程式日誌
docker-compose logs app | grep -i "sheet"
```

### 問題 4: 記憶體不足

**症狀**: 容器頻繁重啟

**解決方案**:
```bash
# 檢查記憶體使用
docker stats

# 增加 Docker 記憶體限制
# 編輯 docker-compose.yml
services:
  app:
    mem_limit: 1g
```

### 問題 5: 資料持久化問題

**症狀**: 重啟後資料遺失

**解決方案**:
```bash
# 確認資料卷存在
docker volume ls | grep boardgame

# 備份資料卷
docker run --rm -v boardgame-web_redis-data:/data -v $(pwd):/backup alpine tar czf /backup/redis-backup.tar.gz /data
```

---

## 🔄 更新部署

### 更新應用程式

```bash
# 1. 拉取最新程式碼
git pull origin main

# 2. 重新建立映像
docker-compose build app

# 3. 重啟服務
docker-compose up -d app

# 4. 驗證更新
curl http://localhost:5001/api/health
```

### 更新環境變數

```bash
# 1. 編輯 .env
nano .env

# 2. 重啟服務
docker-compose restart app
```

---

## 📊 監控和維護

### 查看日誌

```bash
# 即時日誌
docker-compose logs -f

# 最近 100 行
docker-compose logs --tail=100

# 特定服務
docker-compose logs -f app
```

### 效能監控

訪問監控儀表板：
```
http://localhost:5001/monitoring.html
```

監控指標包括：
- Redis 統計
- 快取命中率
- 系統資源使用
- 健康檢查狀態

### 備份

```bash
# 備份 Redis 資料
docker-compose exec redis redis-cli BGSAVE

# 備份資料卷
docker run --rm -v boardgame-web_redis-data:/data -v $(pwd):/backup alpine tar czf /backup/redis-backup-$(date +%Y%m%d).tar.gz /data
```

---

## 🌐 生產環境建議

### 1. 使用反向代理

建議使用 Nginx 作為反向代理：

```nginx
server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://localhost:5001;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

### 2. 啟用 HTTPS

使用 Let's Encrypt 獲取免費 SSL 憑證：

```bash
certbot --nginx -d your-domain.com
```

### 3. 設定自動重啟

在 `docker-compose.yml` 中已設定 `restart: unless-stopped`

### 4. 定期備份

設定 cron 任務定期備份：

```bash
# 每天凌晨 2 點備份
0 2 * * * cd /path/to/boardgame-web && docker-compose exec redis redis-cli BGSAVE
```

---

## 📚 相關文檔

- [系統設計文檔](./architecture/system_design.md)
- [API 參考文檔](./api/api_reference.md)
- [測試指南](./codebase/testing_guide.md)

---

**文檔建立者**: AI Agent  
**建立時間**: 2025-12-21 19:30  
**版本**: 1.0
