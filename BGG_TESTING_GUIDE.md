# BGG 整合測試指南

## 🎉 整合狀態：完成

所有 BGG (BoardGameGeek) 功能已成功整合到系統中。

## ✅ 已驗證的組件

### 後端 (Backend)

- ✅ Flask 伺服器運行正常 (<http://127.0.0.1:5000>)
- ✅ BGG API 端點響應正常 (HTTP 200)
- ✅ BGG Service 正常運作
- ✅ 快取機制已整合

### 前端 (Frontend)

- ✅ index.html 已整合 BGG 區塊
- ✅ bgg-style.css 已加入
- ✅ bgg.js 已載入

## 📋 手動測試步驟

### 1. 確認 Flask 伺服器運行中

```powershell
# 如果未運行，請啟動：
cd c:\python-training\boardgame-web
python flask_app.py
```

應該會看到：

```
* Running on http://127.0.0.1:5000
```

### 2. 開啟瀏覽器測試

1. **打開瀏覽器**
   - 訪問: <http://localhost:5000>

2. **強制重新整理（重要！）**
   - Windows: 按 `Ctrl + Shift + R` 或 `Ctrl + F5`
   - Mac: 按 `Cmd + Shift + R`
   - 或者：右鍵點擊重新整理按鈕 → 選擇「清空快取並強制重新整理」

3. **尋找 BGG 區塊**
   - 向下滾動頁面
   - 在搜尋篩選區塊之後，桌遊表格之前
   - 應該會看到：**「🔍 從 BoardGameGeek 搜尋桌遊」**

### 3. 測試 BGG 搜尋功能

#### A. 搜尋桌遊

1. 在 BGG 搜尋框輸入：`Catan`
2. 點擊「搜尋」按鈕
3. 等待 3-5 秒
4. 應該會顯示搜尋結果

#### B. 查看詳細資訊

1. 點擊任一搜尋結果的「查看詳情」按鈕
2. 會彈出 Modal 顯示：
   - 遊戲封面圖片
   - 評分和排名
   - 玩家人數
   - 遊戲時間
   - 類別和機制

#### C. 加入館藏

1. 點擊「加入館藏」按鈕
2. 輸入保管人名稱（可選）
3. 確認加入
4. 系統會自動寫入 Google Sheets

#### D. 查看熱門桌遊

- 頁面載入時會自動顯示 BGG 前 10 名熱門桌遊
- 每個遊戲都有縮圖和名稱
- 點擊「查看」按鈕可查看詳情

## 🧪 API 測試

### 使用 PowerShell 測試

```powershell
# 1. 測試搜尋 API
Invoke-WebRequest "http://localhost:5000/api/bgg/search?q=Catan"

# 2. 測試遊戲詳情 API（Catan 的 BGG ID 是 13）
Invoke-WebRequest "http://localhost:5000/api/bgg/game/13"

# 3. 測試熱門桌遊 API
Invoke-WebRequest "http://localhost:5000/api/bgg/hot?limit=10"

# 4. 測試加入館藏 API
Invoke-WebRequest -Method POST -Uri "http://localhost:5000/api/bgg/add-to-collection" `
  -ContentType "application/json" `
  -Body '{"game_id": 13, "custodian": "測試者"}'
```

### 使用瀏覽器開發者工具測試

1. 按 `F12` 開啟開發者工具
2. 切換到「Console」分頁
3. 執行以下 JavaScript：

```javascript
// 測試搜尋
fetch('/api/bgg/search?q=Catan')
  .then(r => r.json())
  .then(d => console.log(d));

// 測試熱門桌遊
fetch('/api/bgg/hot?limit=10')
  .then(r => r.json())
  .then(d => console.log(d));
```

## 🐛 疑難排解

### 問題 1: 看不到 BGG 區塊

**解決方案：**

1. 確保已強制重新整理瀏覽器（Ctrl + Shift + R）
2. 檢查瀏覽器開發者工具的 Console 是否有錯誤
3. 確認 bgg-style.css 和 bgg.js 是否成功載入

### 問題 2: 搜尋無結果

**可能原因：**

- BGG API 響應較慢（需等待 5-10 秒）
- 網路連線問題
- BGG 伺服器暫時無法訪問

**解決方案：**

- 耐心等待
- 嘗試不同的搜尋關鍵字
- 檢查網路連線

### 問題 3: 熱門桌遊不顯示

**解決方案：**

1. 打開開發者工具 Console
2. 檢查是否有 JavaScript 錯誤
3. 嘗試手動呼叫：

   ```javascript
   loadHotGames();
   ```

### 問題 4: 加入館藏失敗

**可能原因：**

- Google Sheets API 權限問題
- 桌遊名稱已存在

**解決方案：**

- 檢查 Flask 伺服器終端的錯誤訊息
- 確認 Google Sheets 連線正常

## 📊 預期測試結果

### 成功指標

- ✅ BGG 搜尋區塊可見
- ✅ 熱門桌遊列表自動載入（10個遊戲）
- ✅ 搜尋功能正常運作
- ✅ Modal 詳情正常顯示
- ✅ 加入館藏功能正常

### API 響應範例

**搜尋 API：**

```json
{
  "success": true,
  "query": "Catan",
  "count": 10,
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

**熱門桌遊 API：**

```json
{
  "success": true,
  "count": 10,
  "games": [
    {
      "id": 123456,
      "name": "某熱門桌遊",
      "year": 2023,
      "rank": 1,
      "thumbnail": "https://..."
    }
  ]
}
```

## 📝 測試完成檢查表

請完成以下測試：

- [ ] Flask 伺服器成功啟動
- [ ] 瀏覽器成功打開 <http://localhost:5000>
- [ ] 使用 Ctrl+Shift+R 強制重新整理
- [ ] 看到「🔍 從 BoardGameGeek 搜尋桌遊」區塊
- [ ] 看到「🔥 BGG 熱門桌遊」區塊
- [ ] 熱門桌遊列表已載入（至少顯示幾個遊戲）
- [ ] 搜尋功能測試（搜尋 "Catan"）
- [ ] 搜尋結果正常顯示
- [ ] 點擊「查看詳情」顯示 Modal
- [ ] Modal 顯示遊戲資訊（評分、排名等）
- [ ] 測試「加入館藏」功能
- [ ] 確認桌遊成功加入 Google Sheets

## 🎯 下一步

測試完成後，您可以：

1. **調整樣式**
   - 修改 `bgg-style.css` 調整外觀
   - 修改顏色、間距、字體等

2. **擴展功能**
   - 加入收藏功能
   - 加入更多篩選選項
   - 顯示更多遊戲資訊

3. **優化效能**
   - 調整快取時間
   - 優化圖片載入
   - 加入載入動畫

4. **部署到正式環境**
   - 更新 requirements.txt
   - 推送到 GitHub
   - 部署到 Render 或其他平台

## 📞 需要協助？

如有任何問題，請檢查：

- Flask 伺服器終端的錯誤訊息
- 瀏覽器開發者工具 Console
- 網路連線狀態

祝測試順利！🎲
