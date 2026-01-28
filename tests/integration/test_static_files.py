"""
靜態檔案路由測試

測試 main blueprint 中新加入的靜態檔案服務路由：
- /css/<filename>
- /js/<filename>
- /images/<filename>
"""
import pytest
from flask import Flask


class TestStaticFilesRoutes:
    """測試靜態檔案路由"""

    def test_serve_css_success(self, client):
        """測試成功載入 CSS 檔案"""
        response = client.get("/css/style.css")
        assert response.status_code == 200
        assert response.content_type == "text/css; charset=utf-8"

    def test_serve_js_success(self, client):
        """測試成功載入 JavaScript 檔案"""
        response = client.get("/js/script.js")
        assert response.status_code == 200
        assert "javascript" in response.content_type or "text/plain" in response.content_type

    def test_serve_images_success(self, client):
        """測試成功載入圖片檔案"""
        response = client.get("/images/favicon.svg")
        assert response.status_code == 200
        assert "image" in response.content_type or "svg" in response.content_type

    def test_css_file_not_found(self, client):
        """測試 CSS 檔案不存在的情況"""
        response = client.get("/css/nonexistent.css")
        assert response.status_code == 404

    def test_js_file_not_found(self, client):
        """測試 JS 檔案不存在的情況"""
        response = client.get("/js/nonexistent.js")
        assert response.status_code == 404

    def test_images_file_not_found(self, client):
        """測試圖片檔案不存在的情況"""
        response = client.get("/images/nonexistent.png")
        assert response.status_code == 404

    def test_path_traversal_attack_css(self, client):
        """測試路徑穿越攻擊（CSS）"""
        response = client.get("/css/../../../etc/passwd")
        # Flask 的 send_from_directory 會自動防禦路徑穿越
        assert response.status_code in [400, 404]

    def test_path_traversal_attack_js(self, client):
        """測試路徑穿越攻擊（JS）"""
        response = client.get("/js/../../core/config.py")
        assert response.status_code in [400, 404]

    def test_empty_filename(self, client):
        """測試空檔名"""
        response = client.get("/css/")
        assert response.status_code == 404

    def test_special_characters_in_filename(self, client):
        """測試檔名包含特殊字元"""
        response = client.get("/css/style%20with%20spaces.css")
        # 應該回傳 404（檔案不存在）而非 500
        assert response.status_code == 404

    def test_nested_path_css(self, client):
        """測試巢狀路徑（如果有子目錄的CSS）"""
        # 假設可能有 /css/components/button.css 這類檔案
        response = client.get("/css/components/button.css")
        # 無論檔案存在與否，都應該是 200 或 404，不應該是 500
        assert response.status_code in [200, 404]

    def test_cache_headers(self, client):
        """測試靜態檔案是否有適當的快取標頭"""
        response = client.get("/css/style.css")
        if response.status_code == 200:
            # 檢查是否有 Cache-Control 或 ETag
            assert "Cache-Control" in response.headers or "ETag" in response.headers
