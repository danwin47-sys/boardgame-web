# Boardgame-Web 編碼標準與最佳實踐

## Architecture 架構

1. **Service 層隔離**: 所有外部互動（Google Sheets API、BGG API、Email 發送）必須封裝在 `core/` 目錄的服務類別中。
    - *Why?* 這讓服務邏輯與路由邏輯分離，便於測試和維護。

2. **Blueprint 組織**: Flask 路由應按功能分組到 `app/blueprints/` 中的不同藍圖。
    - *Why?* 這提供清晰的模組化結構，便於擴展和維護。

3. **Pydantic 模型**: API 端點使用 `pydantic` 模型來驗證請求和回應。
    - *Why?* 這確保嚴格的資料驗證，並為 API 文檔提供清晰的類型定義。

## Python Style 風格

1. **Type Hints 類型提示**: 所有函數簽名必須使用類型提示。
    - `def my_func(a: int, b: str) -> bool:`

2. **Docstrings 文件字串**: 必須使用 Google 風格的文件字串。
    - 包含 `Args:`、`Returns:` 和 `Raises:` 區段。
    - *Why?* AI 助手使用這些文件字串來理解如何使用工具和服務。

## Flask 設計模式

1. **Blueprint 註冊**: 在 `app/__init__.py` 中註冊所有藍圖。
2. **Config 管理**: 使用環境變數配置，通過 `python-dotenv` 載入 `.env`。
3. **Error Handling 錯誤處理**: 使用 Flask 的錯誤處理器統一處理異常。

## 前端設計

1. **響應式設計**: 所有頁面必須支援桌面和移動裝置。
2. **一致性**: 使用統一的 CSS 變數和命名規範。
3. **無障礙**: 確保適當的 ARIA 標籤和語義化 HTML。

## 測試標準

1. **單元測試**: `tests/unit/` - 測試個別函數和類別。
2. **整合測試**: `tests/integration/` - 測試 API 端點和服務整合。
3. **覆蓋率**: 目標維持 80% 以上的測試覆蓋率。
