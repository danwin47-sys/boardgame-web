# 📡 Boardgame-Web API 參考文檔

**專案**: Boardgame-Web  
**API 版本**: 1.0  
**最後更新**: 2025-12-21

---

## 📋 目錄

1. [概覽](#概覽)
2. [認證](#認證)
3. [遊戲 API](#遊戲-api)
4. [BGG API](#bgg-api)
5. [會員 API](#會員-api)
6. [搜尋 API](#搜尋-api)
7. [圖庫 API](#圖庫-api)
8. [管理員 API](#管理員-api)
9. [系統 API](#系統-api)

---

## 🎯 概覽

### Base URL

```
http://localhost:5001
```

### 回應格式

所有 API 回應均為 JSON 格式：

```json
{
  "success": true,
  "data": {...},
  "error": null
}
```

### HTTP 狀態碼

| 狀態碼 | 說明 |
|--------|------|
| 200 | 成功 |
| 400 | 請求錯誤 |
| 401 | 未授權 |
| 404 | 找不到資源 |
| 500 | 伺服器錯誤 |

---

## 🔐 認證

### 管理員登入

```http
POST /admin-login
```

**請求體**:
```json
{
  "password": "admin_password"
}
```

**回應**:
```json
{
  "success": true,
  "message": "登入成功",
  "token": "session_token"
}
```

### 驗證管理員

```http
POST /admin/verify
```

**請求體**:
```json
{
  "token": "session_token"
}
```

**回應**:
```json
{
  "success": true,
  "valid": true
}
```

---

## 🎮 遊戲 API

### 獲取遊戲列表

```http
GET /api/games
```

**回應**:
```json
[
  {
    "name": "卡坦島",
    "status": "可借",
    "borrower": "",
    "borrower_id": "",
    "custodian": "張三",
    "bgg_id": 13,
    "bgg_thumbnail": "https://...",
    "players": "3-4",
    "mdate": "2025-12-21"
  }
]
```

### 借用遊戲

```http
POST /api/borrow
```

**請求體**:
```json
{
  "name": "卡坦島",
  "borrower": "張三",
  "borrower_id": "A001"
}
```

**回應**:
```json
{
  "success": true,
  "message": "成功借出 卡坦島 給 張三"
}
```

### 歸還遊戲

```http
POST /api/return
```

**請求體**:
```json
{
  "name": "卡坦島"
}
```

**回應**:
```json
{
  "success": true,
  "message": "成功歸還 卡坦島"
}
```

### 獲取遊戲擴充

```http
GET /api/games/{game_name}/expansions
```

**參數**:
- `game_name`: 遊戲名稱

**回應**:
```json
{
  "success": true,
  "expansions": [
    {
      "name": "卡坦島：航海家擴充",
      "status": "可借"
    }
  ]
}
```

### 獲取遊戲家族

```http
GET /api/games/{game_name}/family
```

**回應**:
```json
{
  "success": true,
  "main_game": "卡坦島",
  "expansions": [...]
}
```

### 驗證借用

```http
GET /api/games/{game_name}/validate-borrow
```

**回應**:
```json
{
  "success": true,
  "can_borrow": true,
  "reason": ""
}
```

---

## 🎲 BGG API

### 搜尋遊戲

```http
GET /api/bgg/search?q={query}&exact={exact}
```

**參數**:
- `q`: 搜尋關鍵字（必填）
- `exact`: 精確搜尋（選填，預設 false）

**回應**:
```json
{
  "success": true,
  "results": [
    {
      "id": 13,
      "name": "Catan",
      "year": 1995,
      "type": "boardgame"
    }
  ]
}
```

### 獲取遊戲詳情

```http
GET /api/bgg/games/{game_id}
```

**參數**:
- `game_id`: BGG 遊戲 ID

**回應**:
```json
{
  "success": true,
  "game": {
    "id": 13,
    "name": "Catan",
    "year": 1995,
    "description": "...",
    "image": "https://...",
    "thumbnail": "https://...",
    "min_players": 3,
    "max_players": 4,
    "playing_time": 120,
    "min_age": 10,
    "rating_average": 7.2,
    "rank": 350,
    "categories": ["Family Game"],
    "mechanics": ["Trading", "Dice Rolling"]
  }
}
```

### 獲取熱門遊戲

```http
GET /api/bgg/hot?limit={limit}
```

**參數**:
- `limit`: 數量限制（選填，預設 10）

**回應**:
```json
{
  "success": true,
  "games": [
    {
      "id": 342942,
      "name": "Ark Nova",
      "rank": 1,
      "thumbnail": "https://..."
    }
  ]
}
```

### 獲取館藏熱門遊戲

```http
GET /api/bgg/our-hot-games?limit={limit}
```

**回應**:
```json
{
  "success": true,
  "games": [
    {
      "id": 13,
      "name": "Catan",
      "hot_rank": 15,
      "status": "可借",
      "local_name": "卡坦島"
    }
  ]
}
```

### 獲取推薦遊戲

```http
GET /api/bgg/recommendations?category={category}&limit={limit}
```

**參數**:
- `category`: 分類（party/strategy/family/children）
- `limit`: 數量限制（選填，預設 10）

**回應**:
```json
{
  "success": true,
  "category": "party",
  "games": [
    {
      "id": 178900,
      "name": "Codenames",
      "thumbnail": "https://...",
      "rating_average": 7.8
    }
  ]
}
```

### 批次更新館藏

```http
POST /api/bgg/collection
```

**請求體**:
```json
{
  "games": ["卡坦島", "璀璨寶石"]
}
```

**回應**:
```json
{
  "success": true,
  "updated": 2,
  "failed": 0,
  "details": [...]
}
```

### 搜尋遊戲連結

```http
GET /api/bgg/games/link/search/{game_name}
```

**回應**:
```json
{
  "success": true,
  "results": [
    {
      "id": 13,
      "name": "Catan",
      "year": 1995
    }
  ]
}
```

### 建立遊戲連結

```http
POST /api/bgg/games/link/{game_name}
```

**請求體**:
```json
{
  "bgg_id": 13,
  "thumbnail": "https://...",
  "image": "https://...",
  "players": "3-4"
}
```

**回應**:
```json
{
  "success": true,
  "message": "成功連結 BGG 資料"
}
```

### 刪除遊戲連結

```http
DELETE /api/bgg/games/link/{game_name}
```

**回應**:
```json
{
  "success": true,
  "message": "成功取消連結"
}
```

---

## 👥 會員 API

### 獲取會員列表

```http
GET /api/members
```

**回應**:
```json
[
  {
    "id": "A001",
    "name": "張三",
    "department": "資訊部"
  }
]
```

---

## 🔍 搜尋 API

### 全域搜尋

```http
GET /api/search/global?q={query}
```

**參數**:
- `q`: 搜尋關鍵字

**回應**:
```json
{
  "success": true,
  "games": [...],
  "members": [...]
}
```

### 搜尋遊戲

```http
GET /api/search/games?q={query}&status={status}&custodian={custodian}
```

**參數**:
- `q`: 搜尋關鍵字（選填）
- `status`: 狀態篩選（選填）
- `custodian`: 保管人篩選（選填）

**回應**:
```json
{
  "success": true,
  "results": [...],
  "count": 10
}
```

### 搜尋會員

```http
GET /api/search/members?q={query}
```

**回應**:
```json
{
  "success": true,
  "results": [...],
  "count": 5
}
```

---

## 🖼️ 圖庫 API

### 獲取圖庫遊戲

```http
GET /api/gallery/games?category={category}&sort={sort}&limit={limit}
```

**參數**:
- `category`: 分類篩選（選填）
- `sort`: 排序方式（選填）
- `limit`: 數量限制（選填）

**回應**:
```json
{
  "success": true,
  "games": [
    {
      "name": "卡坦島",
      "bgg_id": 13,
      "thumbnail": "https://...",
      "rating": 7.2
    }
  ]
}
```

---

## 👨‍💼 管理員 API

### 批次借用

```http
POST /batch-borrow
```

**請求體**:
```json
{
  "games": ["卡坦島", "璀璨寶石"],
  "borrower_id": "A001"
}
```

**回應**:
```json
{
  "success": true,
  "message": "成功借出 2 款遊戲",
  "success_list": ["卡坦島", "璀璨寶石"],
  "fail_list": []
}
```

### 批次歸還

```http
POST /batch-return
```

**請求體**:
```json
{
  "games": ["卡坦島", "璀璨寶石"]
}
```

**回應**:
```json
{
  "success": true,
  "message": "成功歸還 2 款遊戲",
  "success_list": ["卡坦島", "璀璨寶石"],
  "fail_list": []
}
```

### 更新遊戲資訊

```http
POST /admin/games/update
```

**請求體**:
```json
{
  "name": "卡坦島",
  "updates": {
    "custodian": "李四",
    "status": "可借"
  }
}
```

**回應**:
```json
{
  "success": true,
  "message": "更新成功"
}
```

---

## 🔧 系統 API

### 健康檢查

```http
GET /api/health
```

**回應**:
```json
{
  "status": "healthy",
  "timestamp": "2025-12-21T19:14:00",
  "services": {
    "google_sheets": "connected",
    "redis": "connected"
  }
}
```

### 系統資訊

```http
GET /api/sys_info
```

**回應**:
```json
{
  "version": "1.0.0",
  "python_version": "3.9.6",
  "environment": "production"
}
```

### API 文檔

```http
GET /api/docs
```

返回 Swagger UI 介面

### OpenAPI 規格

```http
GET /api/openapi.json
```

返回 OpenAPI 3.0 規格文件

---

## 📊 錯誤處理

### 錯誤回應格式

```json
{
  "success": false,
  "error": "錯誤訊息",
  "code": "ERROR_CODE"
}
```

### 常見錯誤碼

| 錯誤碼 | 說明 |
|--------|------|
| `GAME_NOT_FOUND` | 找不到遊戲 |
| `GAME_ALREADY_BORROWED` | 遊戲已被借出 |
| `MEMBER_NOT_FOUND` | 找不到會員 |
| `INVALID_REQUEST` | 無效的請求 |
| `UNAUTHORIZED` | 未授權 |
| `INTERNAL_ERROR` | 內部錯誤 |

---

## 🎯 使用範例

### JavaScript (Fetch API)

```javascript
// 獲取遊戲列表
fetch('/api/games')
  .then(res => res.json())
  .then(games => console.log(games));

// 借用遊戲
fetch('/api/borrow', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json'
  },
  body: JSON.stringify({
    name: '卡坦島',
    borrower: '張三',
    borrower_id: 'A001'
  })
})
  .then(res => res.json())
  .then(data => console.log(data));
```

### Python (requests)

```python
import requests

# 獲取遊戲列表
response = requests.get('http://localhost:5001/api/games')
games = response.json()

# 借用遊戲
response = requests.post('http://localhost:5001/api/borrow', json={
    'name': '卡坦島',
    'borrower': '張三',
    'borrower_id': 'A001'
})
result = response.json()
```

### cURL

```bash
# 獲取遊戲列表
curl http://localhost:5001/api/games

# 借用遊戲
curl -X POST http://localhost:5001/api/borrow \
  -H "Content-Type: application/json" \
  -d '{"name":"卡坦島","borrower":"張三","borrower_id":"A001"}'
```

---

## 📚 相關文檔

- [資料流程文檔](../architecture/data_flow.md)
- [系統設計文檔](../architecture/system_design.md)
- [測試指南](../codebase/testing_guide.md)

---

**文檔建立者**: AI Agent  
**建立時間**: 2025-12-21 19:14  
**API 版本**: 1.0  
**總端點數**: 33
