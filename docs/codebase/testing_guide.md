# 🧪 Boardgame-Web 測試指南

**專案**: Boardgame-Web  
**測試框架**: pytest  
**總測試數**: 346 個測試函數  
**最後更新**: 2025-12-21

---

## 📊 測試概覽

### 測試統計

| 類別 | 檔案數 | 測試函數數 | 覆蓋範圍 |
|------|--------|-----------|---------|
| 單元測試 | 21 | 253 | 核心模組 |
| 整合測試 | 10 | 93 | API 端點 |
| 配置檔案 | 4 | - | Fixtures |
| **總計** | **35** | **346** | - |

### 測試分布

```
tests/
├── unit/                    # 單元測試 (253 個測試)
│   ├── test_game_service.py         (22 個測試)
│   ├── test_sheets_client.py        (25 個測試)
│   ├── test_decorators.py           (24 個測試)
│   ├── test_bgg_service_extended.py (20 個測試)
│   ├── test_bgg_api_client.py       (15 個測試)
│   ├── test_search_service.py       (14 個測試)
│   ├── test_gallery_filters.py      (14 個測試)
│   ├── test_exceptions.py           (14 個測試)
│   ├── test_bgg_service.py          (13 個測試)
│   ├── test_schemas.py              (13 個測試)
│   ├── test_bgg_ranks_service.py    (10 個測試)
│   └── ... (其他 10 個檔案)
├── integration/             # 整合測試 (93 個測試)
│   ├── test_search_api.py           (27 個測試)
│   ├── test_admin_routes.py         (16 個測試)
│   ├── test_error_handlers.py       (10 個測試)
│   ├── test_bgg_api_extended.py     (9 個測試)
│   ├── test_bgg_api.py              (6 個測試)
│   ├── test_gallery_api.py          (6 個測試)
│   ├── test_game_api.py             (5 個測試)
│   └── ... (其他 3 個檔案)
└── conftest.py              # 測試配置和 Fixtures

```

---

## 🏗️ 測試架構

### Pytest 配置

**測試配置檔案**: `tests/conftest.py`

提供全域 fixtures：

```python
@pytest.fixture(scope='session')
def app():
    """建立測試應用程式"""
    app = create_app('testing')
    app.config.update({
        'TESTING': True,
        'DEMO_MODE': True,  # 避免實際 API 呼叫
    })
    return app

@pytest.fixture(scope='session')
def client(app):
    """建立測試客戶端"""
    return app.test_client()

@pytest.fixture(scope='function')
def auth_headers():
    """模擬認證標頭"""
    return {
        'Authorization': 'Bearer test-token',
        'Content_Type': 'application/json'
    }

@pytest.fixture(scope='function')
def sample_game():
    """範例遊戲資料"""
    return {
        'name': '測試桌遊',
        'status': '可借',
        'borrower': '',
        'borrower_id': '',
        'custodian': '測試保管人'
    }
```

### Fixture 作用域

- `session`: 整個測試會話共享（app, client）
- `function`: 每個測試函數獨立（auth_headers, sample_game）
- `autouse`: 自動應用（reset_cache）

---

## 🧩 單元測試

### 測試模式

#### 1. Mock 模式

使用 `unittest.mock` 模擬外部依賴：

```python
from unittest.mock import MagicMock, patch

def test_borrow_game_success():
    """測試借用遊戲成功"""
    # 建立 mock 物件
    mock_client = MagicMock()
    mock_client.valid = True
    mock_ws = MagicMock()
    mock_client.get_games_worksheet.return_value = mock_ws
    
    # 設定 mock 回傳值
    mock_ws.get_all_records.return_value = [
        {'name': '卡坦島', 'status': '可借', ...}
    ]
    
    # 執行測試
    service = GameService(mock_client, mock_member_service)
    success, msg = service.borrow_game('卡坦島', '張三', 'A001')
    
    # 驗證結果
    assert success is True
    assert '成功借出' in msg
    mock_ws.batch_update.assert_called_once()
```

#### 2. 異常測試模式

測試錯誤處理：

```python
def test_borrow_game_not_found():
    """測試借用不存在的遊戲"""
    mock_client = MagicMock()
    mock_ws.get_all_records.return_value = []
    
    service = GameService(mock_client, mock_member_service)
    success, msg = service.borrow_game('不存在的遊戲', '張三', 'A001')
    
    assert success is False
    assert '找不到此遊戲' in msg
```

#### 3. 參數化測試

使用 `pytest.mark.parametrize`：

```python
@pytest.mark.parametrize("status,expected", [
    ("可借", True),
    ("借出", False),
    ("維修中", False),
])
def test_game_availability(status, expected):
    """測試遊戲可用性"""
    game = {'status': status}
    assert is_available(game) == expected
```

### 主要測試檔案

#### test_game_service.py (22 個測試)

測試遊戲服務的核心功能：

- ✅ 借用遊戲（單筆、批次）
- ✅ 歸還遊戲（單筆、批次）
- ✅ 按會員歸還
- ✅ 錯誤處理

**測試類別**:
- `TestGameServiceInit` - 初始化測試
- `TestGameServiceBorrowGame` - 借用測試
- `TestGameServiceBatchBorrow` - 批次借用測試
- `TestGameServiceReturnGame` - 歸還測試
- `TestGameServiceBatchReturn` - 批次歸還測試

#### test_sheets_client.py (25 個測試)

測試 Google Sheets 客戶端：

- ✅ 連線管理
- ✅ 資料讀取（遊戲、會員）
- ✅ 快取機制
- ✅ 批次更新

#### test_bgg_service.py (13 個測試)

測試 BGG API 服務：

- ✅ 遊戲搜尋
- ✅ 遊戲詳情
- ✅ 熱門遊戲
- ✅ 推薦遊戲

#### test_decorators.py (24 個測試)

測試裝飾器功能：

- ✅ 快取裝飾器
- ✅ 認證裝飾器
- ✅ 錯誤處理裝飾器

#### test_schemas.py (13 個測試)

測試 Pydantic 資料模型：

- ✅ 資料驗證
- ✅ 序列化/反序列化
- ✅ 欄位驗證

---

## 🔗 整合測試

### 測試模式

#### 1. API 端點測試

測試 HTTP 端點：

```python
@pytest.mark.integration
@pytest.mark.api
class TestGameAPI:
    """測試遊戲相關的 API 端點"""
    
    def test_get_games(self, client):
        """測試獲取桌遊列表"""
        response = client.get('/api/games')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert isinstance(data, list)
    
    def test_borrow_game_missing_data(self, client):
        """測試借桌遊時缺少資料"""
        response = client.post('/api/borrow', 
                              data=json.dumps({}),
                              content_type='application/json')
        
        assert response.status_code == 400
        data = json.loads(response.data)
        assert data['success'] == False
```

#### 2. 路由測試

測試頁面路由：

```python
def test_index_page(client):
    """測試首頁"""
    response = client.get('/')
    assert response.status_code == 200
    assert b'<!DOCTYPE html>' in response.data
```

#### 3. 錯誤處理測試

測試錯誤處理機制：

```python
def test_404_error(client):
    """測試 404 錯誤"""
    response = client.get('/nonexistent')
    assert response.status_code == 404
```

### 主要測試檔案

#### test_search_api.py (27 個測試)

測試搜尋 API：

- ✅ 基本搜尋
- ✅ 進階搜尋
- ✅ 篩選功能
- ✅ 排序功能

#### test_admin_routes.py (16 個測試)

測試管理員路由：

- ✅ 管理員登入
- ✅ 管理員頁面
- ✅ 權限控制

#### test_error_handlers.py (10 個測試)

測試錯誤處理：

- ✅ 404 錯誤
- ✅ 500 錯誤
- ✅ 自定義錯誤

#### test_bgg_api.py (6 個測試)

測試 BGG API 端點：

- ✅ 搜尋遊戲
- ✅ 獲取詳情
- ✅ 推薦遊戲

---

## 🚀 執行測試

### 基本命令

```bash
# 執行所有測試
pytest

# 執行特定檔案
pytest tests/unit/test_game_service.py

# 執行特定測試類別
pytest tests/unit/test_game_service.py::TestGameServiceBorrowGame

# 執行特定測試函數
pytest tests/unit/test_game_service.py::TestGameServiceBorrowGame::test_borrow_game_success

# 顯示詳細輸出
pytest -v

# 顯示測試覆蓋率
pytest --cov=core --cov=app

# 只執行單元測試
pytest tests/unit/

# 只執行整合測試
pytest tests/integration/

# 使用標記執行
pytest -m integration
pytest -m api
```

### 進階選項

```bash
# 平行執行（需要 pytest-xdist）
pytest -n auto

# 失敗時停止
pytest -x

# 重新執行失敗的測試
pytest --lf

# 生成 HTML 報告
pytest --html=report.html

# 測試覆蓋率報告
pytest --cov=core --cov=app --cov-report=html
```

---

## 📋 測試最佳實踐

### 1. 測試命名

```python
# ✅ 好的命名
def test_borrow_game_success():
    """測試借用遊戲成功"""
    pass

def test_borrow_game_not_found():
    """測試借用不存在的遊戲"""
    pass

# ❌ 不好的命名
def test_1():
    pass

def test_borrow():
    pass
```

### 2. 測試結構（AAA 模式）

```python
def test_example():
    # Arrange（準備）
    mock_client = MagicMock()
    service = GameService(mock_client)
    
    # Act（執行）
    result = service.do_something()
    
    # Assert（驗證）
    assert result == expected_value
```

### 3. Mock 使用

```python
# ✅ 使用 Mock 隔離外部依賴
def test_with_mock():
    mock_client = MagicMock()
    mock_client.get_data.return_value = {'key': 'value'}
    
    service = MyService(mock_client)
    result = service.process()
    
    assert result is not None
    mock_client.get_data.assert_called_once()

# ❌ 不要在測試中呼叫真實 API
def test_without_mock():
    client = RealAPIClient()  # 不好
    result = client.fetch_data()  # 會實際呼叫 API
```

### 4. 測試獨立性

```python
# ✅ 每個測試獨立
def test_independent_1():
    data = create_test_data()  # 自己建立資料
    result = process(data)
    assert result == expected

def test_independent_2():
    data = create_test_data()  # 不依賴其他測試
    result = process(data)
    assert result == expected

# ❌ 測試之間有依賴
shared_data = None

def test_dependent_1():
    global shared_data
    shared_data = create_data()  # 不好

def test_dependent_2():
    result = process(shared_data)  # 依賴前一個測試
```

### 5. 異常測試

```python
# ✅ 使用 pytest.raises
def test_exception_handling():
    with pytest.raises(ValueError, match="Invalid input"):
        process_invalid_data()

# ✅ 測試錯誤訊息
def test_error_message():
    try:
        risky_operation()
    except CustomError as e:
        assert "expected message" in str(e)
```

---

## 🎯 測試覆蓋率

### 當前覆蓋率（估算）

| 模組 | 覆蓋率 | 測試數 |
|------|--------|--------|
| core/game_service.py | ~90% | 22 |
| core/sheets_client.py | ~85% | 25 |
| core/bgg_service.py | ~80% | 33 |
| core/cache.py | ~75% | 12 |
| app/blueprints/ | ~70% | 93 |

### 提升覆蓋率建議

1. **增加邊界測試**
   - 空值測試
   - 極端值測試
   - 無效輸入測試

2. **增加整合測試**
   - 端到端流程測試
   - 多模組互動測試

3. **增加效能測試**
   - 大量資料測試
   - 並發測試

---

## 🐛 常見問題

### Q1: 測試執行失敗

**問題**: `ImportError: No module named 'core'`

**解決**:
```bash
# 確保在專案根目錄執行
cd /path/to/boardgame-web
pytest
```

### Q2: Mock 不生效

**問題**: Mock 設定後仍然呼叫真實方法

**解決**:
```python
# 確保 Mock 在正確的位置
with patch('core.game_service.SheetsClient') as mock:
    mock.return_value.get_data.return_value = test_data
```

### Q3: Fixture 找不到

**問題**: `fixture 'client' not found`

**解決**:
```bash
# 確保 conftest.py 在正確位置
tests/conftest.py  # ✅ 正確
tests/unit/conftest.py  # ❌ 錯誤
```

---

## 📚 參考資源

### 官方文檔

- [Pytest 官方文檔](https://docs.pytest.org/)
- [unittest.mock 文檔](https://docs.python.org/3/library/unittest.mock.html)
- [Flask Testing](https://flask.palletsprojects.com/en/2.3.x/testing/)

### 測試工具

- `pytest` - 測試框架
- `pytest-cov` - 覆蓋率報告
- `pytest-xdist` - 平行執行
- `pytest-mock` - Mock 輔助

### 相關文檔

- [程式碼文檔](./README.md)
- [核心模組文檔](./core_modules.md)
- [API 文檔](../api/api_reference.md)

---

## 🎉 總結

**Boardgame-Web 擁有完整的測試套件！**

### 測試統計

- ✅ **346 個測試函數**
- ✅ **35 個測試檔案**
- ✅ **253 個單元測試**
- ✅ **93 個整合測試**

### 測試特色

- 🎯 **完整覆蓋**: 核心功能全面測試
- 🔧 **Mock 隔離**: 避免外部依賴
- 📊 **清晰結構**: AAA 模式
- 🚀 **易於執行**: 簡單命令
- 📝 **良好文檔**: 清晰註解

**所有測試都遵循最佳實踐，確保程式碼品質！** 🎊

---

**文檔建立者**: AI Agent  
**建立時間**: 2025-12-21 17:32  
**測試框架**: pytest  
**總測試數**: 346 個
