"""
整合測試：Main 路由
"""
import json

import pytest


@pytest.mark.integration
class TestMainRoutes:
    """測試主要路由端點"""

    def test_home_page(self, client):
        """測試首頁"""
        response = client.get("/")
        assert response.status_code == 200

    def test_favicon(self, client):
        """測試 favicon"""
        response = client.get("/favicon.ico")
        # 可能返回 200 或 404，取決於檔案是否存在
        assert response.status_code in [200, 404]

    def test_health_check(self, client):
        """測試健康檢查端點"""
        response = client.get("/api/health")

        assert response.status_code == 200
        data = json.loads(response.data)
        assert data["status"] == "ok"
        assert "timestamp" in data

    def test_sys_info(self, client):
        """測試系統資訊端點"""
        response = client.get("/api/sys_info")

        assert response.status_code == 200
        data = json.loads(response.data)
        assert isinstance(data, dict)
        assert "cwd" in data or "error" in data

    def test_404_not_found(self, client):
        """測試 404 錯誤處理"""
        response = client.get("/nonexistent-path")
        assert response.status_code == 404

    def test_pages_render(self, client):
        """測試所有主頁面是否能正常渲染"""
        for path in ["/admin.html", "/gallery.html", "/monitoring.html"]:
            response = client.get(path)
            assert response.status_code == 200

    def test_serve_static_resources(self, client):
        """測試靜態資源服務"""
        # 注意：實際測試時檔案可能不存在，但我們要觸發函式執行
        # 這裡測試路徑是否正確對接到 send_from_directory
        assert client.get("/css/style.css").status_code in [200, 404]
        assert client.get("/js/script.js").status_code in [200, 404]
        assert client.get("/images/favicon.svg").status_code in [200, 404]

    def test_sys_info_load_error(self, client, mocker):
        """測試 sys_info 中資料載入失敗的路徑"""
        # Mock get_manager().load_data 拋出異常
        mock_mgr = mocker.patch("app.blueprints.main.routes.get_manager")
        mock_mgr.return_value.load_data.side_effect = Exception("Load Failed")
        mock_mgr.return_value.valid = True
        mock_mgr.return_value.client.valid = True

        response = client.get("/api/sys_info")
        assert response.status_code == 200
        data = response.get_json()
        assert data["load_error"] == "Load Failed"

    def test_sys_info_global_error(self, client, mocker):
        """測試 sys_info 中全局異常的路徑"""
        # Mock os.getcwd 拋出異常來觸發最外層 try-except
        mocker.patch("os.getcwd", side_effect=RuntimeError("OS Error"))

        response = client.get("/api/sys_info")
        assert response.status_code == 200
        data = response.get_json()
        assert "OS Error" in data["error"]
