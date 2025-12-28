import pytest
from playwright.sync_api import Page, expect
import time
import subprocess
import os
import signal

@pytest.fixture(scope="module", autouse=True)
def test_server():
    """啟動測試用的背景 Flask 伺服器"""
    # 設定環境變數為 DEMO 模式以避免依賴真實 Google Sheets
    env = os.environ.copy()
    env["FLASK_ENV"] = "testing"
    env["DEMO_MODE"] = "True"
    env["PORT"] = "5002"
    
    # 啟動伺服器
    process = subprocess.Popen(
        ["python", "serve.py"],
        env=env,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        preexec_fn=os.setsid
    )
    
    # 等待伺服器啟動
    time.sleep(3)
    
    yield "http://localhost:5002"
    
    # 關閉伺服器
    os.killpg(os.getpgid(process.pid), signal.SIGTERM)

def test_homepage_load_and_interact(page: Page, test_server):
    """測試首頁載入與基本交互"""
    page.goto(test_server)
    
    # 1. 驗證標題
    expect(page).to_have_title("瑞昱桌遊社 - 桌遊管理系統")
    
    # 2. 驗證表格是否載入 (Demo 模式應有預設資料)
    table = page.locator("#game-table-body")
    expect(table).to_be_visible()
    
    # 3. 測試搜尋功能
    search_input = page.locator("#table-search")
    search_input.fill("Catan")
    # 等待過濾邏輯執行 (如果前端有防抖或非同步處理)
    time.sleep(1)
    
    # 4. 測試展開過度效果 (如果有階層資料)
    # 在 Demo 模式中通常會有 'Mars' 或 'Catan' 及其擴充
    # 尋找展開按鈕並點擊
    expand_btns = page.locator(".expand-toggle")
    if expand_btns.count() > 0:
        first_btn = expand_btns.first
        first_btn.click()
        # 驗證是否顯示了擴充列 (通常有特殊的 class 如 .expansion-row)
        expect(page.locator(".expansion-row")).to_be_visible()

def test_borrow_modal_popup(page: Page, test_server):
    """測試借閱對話框是否能彈出"""
    page.goto(test_server)
    
    # 點擊第一個「借閱」按鈕
    borrow_btn = page.locator("button:has-text('借閱')").first
    if borrow_btn.is_visible():
        borrow_btn.click()
        
        # 驗證 SweetAlert2 彈窗是否存在
        expect(page.locator(".swal2-popup")).to_be_visible()
        expect(page.locator(".swal2-title")).to_contain_text("借閱")
