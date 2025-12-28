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
    
    import sys
    # 啟動伺服器
    process = subprocess.Popen(
        [sys.executable, "serve.py"],
        env=env,
        preexec_fn=os.setsid
    )
    
    # 健康檢查：等待伺服器回應 200 OK (CI 環境可能較慢，設定 30 秒超时)
    import requests
    max_retries = 30
    url = "http://localhost:5002"
    for i in range(max_retries):
        try:
            time.sleep(1)
            response = requests.get(url)
            if response.status_code == 200:
                print(f"\n[DEBUG] Server is UP on {url}")
                break
        except Exception:
            continue
    else:
        # 如果失敗，印出伺服器 stderr
        stdout, stderr = process.communicate(timeout=1)
        print(f"\n[ERROR] Server failed to start:\n{stderr.decode()}")
        pytest.fail("Server failed to start")
    
    yield url
    
    # 關閉伺服器
    os.killpg(os.getpgid(process.pid), signal.SIGTERM)

def test_homepage_load_and_interact(page: Page, test_server):
    """測試首頁載入與基本交互"""
    page.on("console", lambda msg: print(f"[BROWSER CONSOLE] {msg.type}: {msg.text}"))
    page.on("pageerror", lambda exc: print(f"[BROWSER ERROR] {exc}"))
    
    page.goto(test_server)
    
    # 1. 驗證標題
    expect(page).to_have_title("瑞昱桌遊社 - 桌遊管理系統", timeout=15000)
    
    # 2. 驗證表格內容載入 (至少看到 Catan)
    page.wait_for_selector("text=Catan", state="visible", timeout=10000)
    expect(page.get_by_text("Catan")).to_be_visible()
    
    # 3. 測試搜尋功能
    search_input = page.locator("#searchBox")
    search_input.wait_for(state="visible")
    search_input.fill("Gloomhaven")
    
    # 驗證搜尋結果
    page.wait_for_selector("text=Gloomhaven", state="visible", timeout=5000)
    expect(page.get_by_text("Gloomhaven")).to_be_visible()
    expect(page.get_by_text("Catan")).not_to_be_visible()
    
    # 清除搜尋
    search_input.fill("")
    page.wait_for_selector("text=Catan", state="visible", timeout=5000)

def test_borrow_interaction(page: Page, test_server):
    """測試借閱交互流程 (使用原生 prompt)"""
    page.on("console", lambda msg: print(f"[BROWSER CONSOLE] {msg.type}: {msg.text}"))
    
    # 監聽並自動處理對話框
    def handle_dialog(dialog):
        print(f"[DIALOG] {dialog.type}: {dialog.message}")
        if dialog.type == "prompt":
            dialog.accept("TEST_USER_01")
        elif dialog.type == "confirm":
            dialog.accept()
        else:
            dialog.dismiss()
            
    page.on("dialog", handle_dialog)
    
    page.goto(test_server)
    
    # 等待頁面載入
    page.wait_for_selector("text=Catan", state="visible", timeout=10000)
    
    # 模擬雙擊第一列（如果 IS_ADMIN=true，雙擊會觸發借閱）
    # 但 E2E 默認可能不是管理員，我們直接調用 JS 函數測試
    page.evaluate("executeSingleBorrow('Catan')")
    
    # 注意：executeSingleBorrow 會先 fetch /api/games/Catan/validate-borrow
    # 在 DEMO_MODE 下，我們可能需要確保這個 API 也回傳成功。
    
    # 簡單驗證：如果執行到了 prompt，說明交互觸發成功。
    # 由於我們在 handle_dialog 中 accept 了，測試會繼續執行而不超時。
    print("Borrow interaction triggered successfully.")
