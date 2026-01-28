"""
測試 core/email_notifier.py 模組 (使用 mock)
"""
from unittest.mock import MagicMock, patch

import pytest


class TestEmailNotifierInit:
    """測試初始化"""

    def test_init_default(self):
        """測試預設初始化"""
        from core.email_notifier import EmailNotifier

        notifier = EmailNotifier()

        assert notifier.smtp_server is not None
        assert notifier.smtp_port is not None

    def test_init_custom(self):
        """測試自定義參數初始化"""
        from core.email_notifier import EmailNotifier

        notifier = EmailNotifier(
            smtp_server="custom.server.com",
            smtp_port=465,
            username="test@test.com",
            password="password",
        )

        assert notifier.smtp_server == "custom.server.com"
        assert notifier.smtp_port == 465
        assert notifier.username == "test@test.com"


class TestEmailNotifierSendNotification:
    """測試 send_notification 方法"""

    def test_send_without_credentials(self):
        """測試沒有憑證時發送"""
        from core.email_notifier import EmailNotifier

        notifier = EmailNotifier()

        # 沒有設置 username/password 應該返回 False
        result = notifier.send_notification(
            "test@test.com", "Test Subject", "Test Content"
        )

        # 沒有憑證應該失敗
        assert result is False

    @patch("core.email_notifier.smtplib.SMTP")
    def test_send_success(self, mock_smtp):
        """測試成功發送郵件"""
        mock_server = MagicMock()
        mock_smtp.return_value.__enter__ = MagicMock(return_value=mock_server)
        mock_smtp.return_value.__exit__ = MagicMock(return_value=False)

        from core.email_notifier import EmailNotifier

        notifier = EmailNotifier(
            smtp_server="test.server.com",
            smtp_port=587,
            username="test@test.com",
            password="password",
        )

        result = notifier.send_notification(
            "recipient@test.com", "Test Subject", "Test Content"
        )

        assert result is True

    @patch("core.email_notifier.smtplib.SMTP")
    def test_send_failure(self, mock_smtp):
        """測試發送失敗"""
        mock_smtp.side_effect = Exception("SMTP error")

        from core.email_notifier import EmailNotifier

        notifier = EmailNotifier(
            smtp_server="test.server.com",
            smtp_port=587,
            username="test@test.com",
            password="password",
        )

        result = notifier.send_notification(
            "recipient@test.com", "Test Subject", "Test Content"
        )

        assert result is False


class TestEmailNotifierTemplates:
    """測試郵件模板方法"""

    def test_send_import_success_no_credentials(self):
        """測試導入成功通知（無憑證）"""
        from core.email_notifier import EmailNotifier

        notifier = EmailNotifier()

        result = notifier.send_import_success(
            "test@test.com", total_records=1000, errors=5, import_time=10.5
        )

        # 沒有憑證應該失敗
        assert result is False

    def test_send_import_failure_no_credentials(self):
        """測試導入失敗通知（無憑證）"""
        from core.email_notifier import EmailNotifier

        notifier = EmailNotifier()

        result = notifier.send_import_failure(
            "test@test.com", error_message="Test error"
        )

        assert result is False

    def test_send_download_success_no_credentials(self):
        """測試下載成功通知（無憑證）"""
        from core.email_notifier import EmailNotifier

        notifier = EmailNotifier()

        result = notifier.send_download_success(
            "test@test.com", filepath="/path/to/file", file_size=1024
        )

        assert result is False

    @patch("smtplib.SMTP")
    def test_send_success_with_db_stats(self, mock_smtp):
        """測試帶有資料庫統計資訊的導入成功通知"""
        from core.email_notifier import EmailNotifier

        notifier = EmailNotifier(username="u", password="p")

        with patch.object(
            notifier, "send_notification", return_value=True
        ) as mock_send:
            db_stats = {"total_games": 500, "expansions": 50}
            notifier.send_import_success("to@ex.com", 10, 0, 1.2, db_stats)

            # 驗證 content 中包含統計數字
            content = mock_send.call_args[0][2]
            assert "500" in content
            assert "50" in content

    @patch("smtplib.SMTP")
    def test_send_notification_smtp_exception(self, mock_smtp):
        """測試 SMTP 發送時發生異常"""
        from core.email_notifier import EmailNotifier

        notifier = EmailNotifier(username="u", password="p")

        mock_server = MagicMock()
        mock_server.send_message.side_effect = Exception("SMTP error")
        mock_smtp.return_value.__enter__.return_value = mock_server

        result = notifier.send_notification("to@ex.com", "S", "C")
        assert result is False


class TestEmailNotifierMain:
    """測試 main 函式"""

    @patch("sys.argv", ["test_notifier.py", "test@example.com"])
    @patch("core.email_notifier.EmailNotifier.send_notification", return_value=True)
    def test_main_execution(self, mock_send):
        """測試 main 函式執行"""
        from core.email_notifier import main

        # 確保有憑證
        with patch.dict(
            "os.environ", {"EMAIL_USERNAME": "user", "EMAIL_PASSWORD": "pwd"}
        ):
            main()
            assert mock_send.called
