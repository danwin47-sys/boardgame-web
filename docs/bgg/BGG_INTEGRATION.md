# BGG 整合說明文檔

## 已完成的檔案

### 後端

1. ✅ `requirements.txt` - 已加入 `boardgamegeek2`
2. ✅ `core/bgg_service.py` - BGG API 服務模組
3. ✅ `flask_app.py` - 已加入 4 個 BGG API 端點

### 前端  

1. ✅ `static/bgg.js` - BGG JavaScript 功能模組
2. ✅ `static/bgg-style.css` - BGG CSS 樣式
3. ⚠️ `static/bgg-section.html` - HTML 模板（需要手動整合）

## 手動整合步驟

由於 `index.html` 的編輯較為複雜，請按照以下步驟手動整合：

### 步驟 1: 在 index.html 的 `<head>` 區塊加入 CSS

```html
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>瑞昱桌遊社 - Web 版管理系統</title>
    <!-- 引入 CSS 樣式表 -->
    <link rel="stylesheet" href="style.css">
    <!-- 加入這一行 -->
    <link rel="stylesheet" href="bgg-style.css">
</head>
```

### 步驟 2: 在搜尋篩選區塊之後加入 BGG 區塊

在 `<div class="search-filter-container">...</div>` 之後，`<table id="gameTable">` 之前插入：

```html
    <!-- BGG BoardGameGeek 搜尋功能 -->
    <div class="bgg-section">
        <h2>🔍 從 BoardGameGeek 搜尋桌遊</h2>
        
        <div class="bgg-search-container">
            <input type="text" id="bggSearchBox" class="search" placeholder="搜尋 BGG 桌遊名稱...">
            <button id="bggSearchBtn" class="btn primary">搜尋</button>
        </div>
        
        <!-- BGG 搜尋結果 -->
        <div id="bggResults" class="bgg-results" style="display: none;">
            <h3>搜尋結果</h3>
            <div id="bggResultsList" class="bgg-results-list"></div>
        </div>

        <!-- 熱門桌遊推薦 -->
        <div class="bgg-hot-games">
            <h3>🔥 BGG 熱門桌遊</h3>
            <div id="bggHotList" class="bgg-hot-list"></div>
        </div>
    </div>
```

### 步驟 3: 在 `</body>` 前加入 JavaScript

```html
    <!-- 引入 JavaScript 邏輯 -->
    <script src="script.js"></script>
    <!-- 加入這一行 -->
    <script src="bgg.js"></script>
</body>
```

## API 端點清單

### 新增的 BGG API 端點

1. **GET** `/api/bgg/search?q=<query>`
   - 搜尋 BGG 桌遊
   - 參數: `q` (搜尋關鍵字), `exact` (可選，精確搜尋)

2. **GET** `/api/bgg/game/<game_id>`
   - 取得桌遊詳細資訊
   - 參數: `game_id` (BGG 遊戲 ID)

3. **GET** `/api/bgg/hot?limit=10`
   - 取得熱門桌遊列表
   - 參數: `limit` (可選，預設 10)

4. **POST** `/api/bgg/add-to-collection`
   - 從 BGG 加入桌遊到館藏
   - Body: `{"game_id": 123, "custodian": "保管人名稱"}`

## 功能說明

### 1. BGG 搜尋

- 使用者輸入桌遊名稱進行搜尋
- 支援即時搜尋（debounce 500ms）
- 顯示搜尋結果卡片

### 2. 桌遊詳情

- 點擊「查看詳情」開啟 Modal
- 顯示評分、排名、玩家數等資訊
- 包含遊戲簡介、類別、機制等

### 3. 加入館藏

- 從搜尋結果或詳情頁加入
- 自動檢查重複
- 支援設定保管人

### 4. 熱門桌遊

- 自動載入 BGG 前 10 名熱門桌遊
- 顯示縮圖和基本資訊

## 測試指令

```bash
# 1. 安裝依賴
pip install boardgamegeek2

# 2. 啟動服務
python flask_app.py

# 3. 測試 API
curl "http://localhost:5000/api/bgg/search?q=Catan"
curl "http://localhost:5000/api/bgg/game/13"
curl "http://localhost:5000/api/bgg/hot"
```

## 注意事項

- BGG API 有速率限制，使用快取機制（5分鐘）
- 搜尋結果快取 5 分鐘
- 遊戲詳情快取 1 小時
- 熱門桌遊快取 30 分鐘
