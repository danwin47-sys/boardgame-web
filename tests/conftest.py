"""
Pytest 測試夾具和配置
"""
import os
import sys

import pytest

# 確保可以匯入專案模組
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app import create_app


@pytest.fixture(scope="session")
def app():
    """建立測試應用程式"""
    app = create_app("testing")

    # 設定測試配置
    app.config.update(
        {
            "TESTING": True,
            "DEMO_MODE": True,  # 使用演示模式避免實際 API 呼叫
        }
    )

    # 設定測試用管理員密碼
    os.environ["ADMIN_PASSWORD"] = "admin123"

    yield app


@pytest.fixture(scope="session")
def client(app):
    """建立測試客戶端"""
    return app.test_client()


@pytest.fixture(scope="session")
def runner(app):
    """建立 CLI runner"""
    return app.test_cli_runner()


@pytest.fixture(scope="function")
def auth_headers():
    """模擬認證標頭"""
    return {"Authorization": "Bearer test-token", "Content-Type": "application/json"}


@pytest.fixture(scope="function")
def sample_game():
    """範例遊戲資料"""
    return {
        "name": "測試桌遊",
        "status": "可借",
        "borrower": "",
        "borrower_id": "",
        "custodian": "測試保管人",
    }


@pytest.fixture(scope="function")
def sample_member():
    """範例社員資料"""
    return {"id": "TEST001", "name": "測試社員", "department": "測試部門"}


@pytest.fixture(autouse=True)
def reset_cache():
    """每個測試後重置快取"""
    yield
    # 測試後清理（如果需要）
    pass
