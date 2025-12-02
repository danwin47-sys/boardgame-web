# BGG XML API 使用條款和規範

## 官方文件連結

- **XML API 使用條款**：<https://boardgamegeek.com/wiki/page/XML_API_Terms_of_Use>
- **BGG XML API2 技術文件**：<https://boardgamegeek.com/wiki/page/BGG_XML_API2>
- **API 使用說明**：<https://boardgamegeek.com/using_the_xml_api>

---

## 📋 使用條款摘要

### 1. 註冊要求

> [!IMPORTANT]
> **所有使用 XML API 的應用程式都必須註冊**

- 前往 <https://boardgamegeek.com/applications> 註冊應用程式
- 填寫應用程式資訊（名稱、用途、類型等）
- 等待 BGG 審核（可能需要一週以上）
- 審核通過後才能合法使用 API

**例外情況：**

- 僅下載自己的收藏（登入狀態）
- 下載 CSV dump of all games（登入狀態）

### 2. 授權類型

#### 商業授權

- 需要明確說明商業用途
- 可能需要額外審核

#### 非商業授權

- 個人專案、研究、教育用途
- 不得用於盈利目的

### 3. 授權限制

BGG 可能拒絕或撤銷以下類型的應用程式：

- 與 BGG 業務競爭的應用
- 損害 BGG 利益的應用
- 幫助管理會展票務的應用

---

## 🔐 認證要求

### Bearer Token 認證

**格式：**

```
Authorization: Bearer {your-token-here}
```

**取得方式：**

1. 前往 <https://boardgamegeek.com/applications>
2. 找到您已註冊的應用程式
3. 點擊「Tokens」按鈕
4. 建立新的 Bearer Token
5. **立即複製（只會顯示一次）**

**重要事項：**

- Token 格式：`Bearer` + 空格 + token（不需要冒號）
- 必須使用 `boardgamegeek.com`（**不含 www**）
- 必須使用 HTTPS
- 目前 Token 不需要更新，但政策可能變更

---

## ⚖️ 使用限制

### 請求頻率限制

**官方建議：**

- 請求間隔至少 **5 秒**
- 避免過於頻繁的請求
- 當收到 500 或 503 錯誤時，表示請求過於頻繁

**我們的實作：**

- 使用快取減少請求次數
- 搜尋結果快取 5 分鐘
- 遊戲詳情快取 1 小時

### 架構要求

> [!WARNING]
> **強烈建議使用伺服器端請求**

- 所有請求應從伺服器發送，並快取結果
- 避免從客戶端（瀏覽器或 App）直接請求
- 客戶端請求可能導致流量過大，授權可能被暫停

**我們的實作：**

- ✅ 所有請求從 Flask 後端發送
- ✅ 使用 `@cache_decorator` 快取結果
- ✅ 前端透過 `/api/bgg/*` 端點呼叫

---

## 📝 公開應用程式要求

### "Powered by BGG" 標誌

**強制要求：**

- 所有公開應用程式必須顯示 "Powered by BGG" 標誌
- 標誌必須連結回 BoardGameGeek
- 文字必須清晰可讀

**標誌下載：**
<https://drive.google.com/drive/folders/1k3VgEIpNEY59iTVnpTibt31JcO0rEaSw>

**我們的實作：**

```html
<a href="https://boardgamegeek.com" target="_blank">
    <img src="powered-by-bgg.png" alt="Powered by BoardGameGeek">
</a>
```

---

## 🌐 支援的 API 端點

### 我們使用的端點

| 端點 | 用途 | 實作狀態 |
|------|------|---------|
| `/xmlapi2/search` | 搜尋桌遊 | ✅ 已實作 |
| `/xmlapi2/thing` | 取得遊戲詳情 | ✅ 已實作 |
| `/xmlapi2/hot` | 取得熱門遊戲 | ✅ 已實作 |

### 其他可用端點

- `/xmlapi2/family` - 系列資訊
- `/xmlapi2/collection` - 使用者收藏
- `/xmlapi2/plays` - 遊戲紀錄
- `/xmlapi2/user` - 使用者資料
- `/xmlapi2/guild` - 工會資訊
- `/xmlapi2/forumlist` - 論壇列表
- `/xmlapi2/thread` - 討論串

---

## 📊 CSV 下載

BGG 提供完整的遊戲資料 CSV 下載：

- **下載位置**：<https://boardgamegeek.com/data_dumps/bg_ranks>
- **內容**：所有遊戲的名稱、ID、排名、平均評分
- **授權**：視為 XML API 的一部分
- **要求**：需要已註冊的應用程式

---

## ⚠️ 風險與責任

> [!CAUTION]
> **XML API 和政策可能隨時變更**

### 使用風險

- BGG 可隨時修改 API 結構
- 授權政策可能更新
- Token 認證方式可能改變

### 建議措施

1. 定期檢查官方文件更新
2. 訂閱 BGG API 公告
3. 準備應對 API 變更的計劃
4. 保持與 BGG 社群的溝通

---

## 🔒 安全最佳實踐

### Token 保護

> [!WARNING]
> **絕不將 Bearer Token 提交到公開 repository**

**保護措施：**

1. ✅ 使用 `.env` 檔案儲存 Token
2. ✅ 確保 `.env` 在 `.gitignore` 中
3. ✅ 在部署環境設定環境變數
4. ✅ 定期輪替 Token

### 客戶端請求風險

如果必須從客戶端請求：

- Token 可能被擷取
- 授權可能被撤銷
- 需要重新產生 Token

**我們的解決方案：**

- ✅ 所有請求從伺服器端發送
- ✅ Token 不暴露給客戶端

---

## 📚 第三方函式庫注意事項

### 函式庫開發者

如果開發供他人使用的函式庫：

- 應提供配置讓使用者設定自己的 Token
- 每個使用函式庫的應用程式應有自己的 Token
- 不應要求非程式設計師的使用者自行取得 Token

### 終端使用者應用

如果是終端使用者應用：

- 應用程式應內建 Token
- 不應要求使用者自行註冊和取得 Token

---

## ✅ 我們的合規狀態

| 要求 | 狀態 |
|------|------|
| 應用程式已註冊 | ✅ 已完成 |
| 使用 Bearer Token 認證 | ✅ 已實作 |
| 請求從伺服器端發送 | ✅ 已實作 |
| 使用快取減少請求 | ✅ 已實作 |
| 顯示 "Powered by BGG" 標誌 | ✅ 已實作 |
| Token 安全保護 | ✅ 已實作 |
| User-Agent 標頭 | ✅ 已實作 |
| 正確的 API 端點格式 | ✅ 已實作 |

---

## 📞 技術支援

如遇到 API 相關問題：

1. 查閱官方 Wiki：<https://boardgamegeek.com/wiki/page/BGG_XML_API2>
2. 檢查論壇討論：<https://boardgamegeek.com/forums/thing/84749>
3. 聯繫 BGG 支援團隊

---

## 📅 最後更新

- **文件版本**：1.0
- **更新日期**：2025-12-02
- **下次檢視**：建議每季度檢查一次官方文件更新
