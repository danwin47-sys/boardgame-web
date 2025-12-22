# 📊 Boardgame-Web 資料流程文檔

**專案**: Boardgame-Web  
**最後更新**: 2025-12-21

---

## 🎯 概覽

本文檔描述 Boardgame-Web 系統中的資料流程，包含使用者操作、資料流向和系統互動。

---

## 🏗️ 系統架構圖

```mermaid
graph TB
    User[使用者] --> Browser[瀏覽器]
    Browser --> Flask[Flask 應用程式]
    
    Flask --> Main[Main Blueprint]
    Flask --> API[API Blueprints]
    Flask --> Admin[Admin Blueprint]
    
    API --> Games[Games API]
    API --> BGG[BGG API]
    API --> Members[Members API]
    API --> Search[Search API]
    API --> Gallery[Gallery API]
    
    Games --> GameService[Game Service]
    BGG --> BGGService[BGG Service]
    Members --> MemberService[Member Service]
    Search --> SearchService[Search Service]
    
    GameService --> Sheets[Google Sheets]
    MemberService --> Sheets
    BGGService --> BGGClient[BGG API Client]
    BGGClient --> BGGExternal[BoardGameGeek API]
    
    GameService --> Redis[(Redis Cache)]
    BGGService --> Redis
    
    BGGService --> SQLite[(SQLite DB)]
```

---

## 📱 使用者操作流程

### 1. 瀏覽遊戲列表

```mermaid
sequenceDiagram
    participant U as 使用者
    participant B as 瀏覽器
    participant F as Flask
    participant G as GameService
    participant S as Google Sheets
    participant R as Redis
    
    U->>B: 訪問首頁
    B->>F: GET /
    F->>B: 返回 index.html
    
    B->>F: GET /api/games
    F->>G: load_games()
    
    alt 快取命中
        G->>R: 檢查快取
        R->>G: 返回快取資料
    else 快取未命中
        G->>S: 讀取遊戲資料
        S->>G: 返回遊戲列表
        G->>R: 更新快取
    end
    
    G->>F: 返回遊戲資料
    F->>B: JSON 回應
    B->>U: 顯示遊戲列表
```

### 2. 借用遊戲

```mermaid
sequenceDiagram
    participant U as 使用者
    participant B as 瀏覽器
    participant F as Flask
    participant G as GameService
    participant M as MemberService
    participant S as Google Sheets
    
    U->>B: 點擊「借用」
    B->>F: POST /api/borrow
    Note over B,F: {name, borrower, borrower_id}
    
    F->>G: borrow_game()
    G->>M: find_member_by_id()
    M->>S: 查詢會員
    S->>M: 返回會員資料
    M->>G: 返回會員
    
    G->>S: 檢查遊戲狀態
    S->>G: 返回遊戲資料
    
    alt 遊戲可借
        G->>S: 更新遊戲狀態
        S->>G: 更新成功
        G->>F: {success: true}
    else 遊戲已借出
        G->>F: {success: false, error}
    end
    
    F->>B: JSON 回應
    B->>U: 顯示結果
```

### 3. BGG 遊戲搜尋

```mermaid
sequenceDiagram
    participant U as 使用者
    participant B as 瀏覽器
    participant F as Flask
    participant BGG as BGGService
    participant C as BGG API Client
    participant E as BGG External API
    participant R as Redis
    
    U->>B: 輸入搜尋關鍵字
    B->>F: GET /api/bgg/search?q=卡坦島
    F->>BGG: search_games("卡坦島")
    
    BGG->>R: 檢查快取
    
    alt 快取命中
        R->>BGG: 返回快取結果
    else 快取未命中
        BGG->>C: search("卡坦島")
        C->>E: HTTP GET /search
        E->>C: XML 回應
        C->>BGG: 解析後的資料
        BGG->>R: 儲存快取
    end
    
    BGG->>F: 返回搜尋結果
    F->>B: JSON 回應
    B->>U: 顯示搜尋結果
```

---

## 🔄 資料流向

### 遊戲資料流

```
Google Sheets (來源)
    ↓
SheetsClient (讀取)
    ↓
Redis Cache (快取)
    ↓
GameService (處理)
    ↓
API Endpoint (暴露)
    ↓
前端 JavaScript (渲染)
    ↓
使用者介面 (顯示)
```

### BGG 資料流

```
BoardGameGeek API (外部)
    ↓
BGG API Client (請求)
    ↓
BGGService (處理)
    ↓
Redis Cache (快取)
    ↓
API Endpoint (暴露)
    ↓
前端 JavaScript (渲染)
    ↓
使用者介面 (顯示)
```

### 排名資料流

```
SQLite Database (本地)
    ↓
BGGRanksService (查詢)
    ↓
索引優化 (加速)
    ↓
API Endpoint (暴露)
    ↓
前端 JavaScript (渲染)
    ↓
使用者介面 (顯示)
```

---

## 🎨 前端資料流

### 頁面載入流程

```
1. 使用者訪問 → index.html 載入
2. CSS 載入 → 樣式渲染
3. JavaScript 載入 → 初始化
4. API 請求 → /api/games
5. 資料接收 → JSON 解析
6. 分頁處理 → 每頁 50 筆
7. DOM 渲染 → 顯示第 1 頁
8. 圖片懶載入 → 可見區域圖片
```

### 搜尋流程

```
1. 使用者輸入 → 防抖處理 (300ms)
2. 篩選條件 → 狀態、保管人等
3. 本地篩選 → JavaScript 過濾
4. 分頁重置 → 回到第 1 頁
5. DOM 更新 → 顯示結果
```

---

## 💾 快取策略

### Redis 快取

**快取鍵格式**:
- 遊戲列表: `games:all`
- BGG 搜尋: `bgg:search:{query}`
- BGG 詳情: `bgg:game:{game_id}`
- 推薦遊戲: `bgg:recommendations:{category}`

**TTL 設定**:
- 遊戲列表: 300 秒 (5 分鐘)
- BGG 搜尋: 300 秒 (5 分鐘)
- BGG 詳情: 3600 秒 (1 小時)
- 推薦遊戲: 1800 秒 (30 分鐘)

### HTTP 快取

**靜態資源**:
- Cache-Control: max-age=31536000 (1 年)
- ETag: MD5 hash

**API 端點**:
- /api/games: max-age=300 (5 分鐘)
- /api/bgg/*: max-age=3600 (1 小時)
- /api/members: max-age=300 (5 分鐘)

---

## 🔐 認證流程

### 管理員登入

```mermaid
sequenceDiagram
    participant U as 管理員
    participant B as 瀏覽器
    participant F as Flask
    participant S as Session
    
    U->>B: 輸入密碼
    B->>F: POST /admin-login
    Note over B,F: {password}
    
    F->>F: 驗證密碼
    
    alt 密碼正確
        F->>S: 建立 session
        F->>B: {success: true, token}
        B->>B: 儲存 token
        B->>U: 導向管理頁面
    else 密碼錯誤
        F->>B: {success: false}
        B->>U: 顯示錯誤
    end
```

---

## 📊 批次操作流程

### 批次借用

```
1. 選擇多個遊戲 → 遊戲名稱列表
2. 輸入借用人 → 會員 ID
3. 驗證會員 → MemberService
4. 檢查遊戲狀態 → 逐一驗證
5. 建立批次更新 → batch_update
6. 執行更新 → Google Sheets API
7. 清除快取 → Redis
8. 返回結果 → 成功/失敗列表
```

---

## 🎯 效能優化流程

### 並發請求

```
傳統流程:
遊戲 1 → 請求 → 回應 (3s)
遊戲 2 → 請求 → 回應 (3s)
遊戲 3 → 請求 → 回應 (3s)
總時間: 9 秒

並發流程:
遊戲 1 ┐
遊戲 2 ├→ ThreadPoolExecutor → 並發請求 → 回應
遊戲 3 ┘
總時間: 3 秒
```

### 分頁渲染

```
優化前:
414 筆遊戲 → 全部渲染 → 4,140 DOM 節點 → 800ms

優化後:
414 筆遊戲 → 分頁 (50/頁) → 1,018 DOM 節點 → 100ms
```

---

## 🔍 錯誤處理流程

```
1. 錯誤發生 → Exception
2. 記錄日誌 → Logger
3. 錯誤處理器 → Error Handler
4. 格式化回應 → JSON
5. HTTP 狀態碼 → 4xx/5xx
6. 返回前端 → 顯示錯誤訊息
```

---

**文檔建立者**: AI Agent  
**建立時間**: 2025-12-21 19:03  
**版本**: 1.0
