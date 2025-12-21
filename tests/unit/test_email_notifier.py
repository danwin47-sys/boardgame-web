"""
測試 core/email_notifier.py 模組 (使用 mock)
"""
import pytest
from unittest.mock import MagicMock, patch


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
            smtp_server='custom.server.com',
            smtp_port=465,
            username='test@test.com',
            password='password'
        )
        
        assert notifier.smtp_server == 'custom.server.com'
        assert notifier.smtp_port == 465
        assert notifier.username == 'test@test.com'


class TestEmailNotifierSendNotification:
    """測試 send_notification 方法"""
    
    def test_send_without_credentials(self):
        """測試沒有憑證時發送"""
        from core.email_notifier import EmailNotifier
        notifier = EmailNotifier()
        
        # 沒有設置 username/password 應該返回 False
        result = notifier.send_notification(
            'test@test.com',
            'Test Subject',
            'Test Content'
        )
        
        # 沒有憑證應該失敗
        assert result is False
    
    @patch('core.email_notifier.smtplib.SMTP')
    def test_send_success(self, mock_smtp):
        """測試成功發送郵件"""
        mock_server = MagicMock()
        mock_smtp.return_value.__enter__ = MagicMock(return_value=mock_server)
        mock_smtp.return_value.__exit__ = MagicMock(return_value=False)
        
        from core.email_notifier import EmailNotifier
        notifier = EmailNotifier(
            smtp_server='test.server.com',
            smtp_port=587,
            username='test@test.com',
            password='password'
        )
        
        result = notifier.send_notification(
            'recipient@test.com',
            'Test Subject',
            'Test Content'
        )
        
        assert result is True
    
    @patch('core.email_notifier.smtplib.SMTP')
    def test_send_failure(self, mock_smtp):
        """測試發送失敗"""
        mock_smtp.side_effect = Exception("SMTP error")
        
        from core.email_notifier import EmailNotifier
        notifier = EmailNotifier(
            smtp_server='test.server.com',
            smtp_port=587,
            username='test@test.com',
            password='password'
        )
        
        result = notifier.send_notification(
            'recipient@test.com',
            'Test Subject',
            'Test Content'
        )
        
        assert result is False


class TestEmailNotifierTemplates:
    """測試郵件模板方法"""
    
    def test_send_import_success_no_credentials(self):
        """測試導入成功通知（無憑證）"""
        from core.email_notifier import EmailNotifier
        notifier = EmailNotifier()
        
        result = notifier.send_import_success(
            'test@test.com',
            total_records=1000,
            errors=5,
            import_time=10.5
        )
        
        # 沒有憑證應該失敗
        assert result is False
    
    def test_send_import_failure_no_credentials(self):
        """測試導入失敗通知（無憑證）"""
        from core.email_notifier import EmailNotifier
        notifier = EmailNotifier()
        
        result = notifier.send_import_failure(
            'test@test.com',
            error_message='Test error'
        )
        
        assert result is False
    
    def test_send_download_success_no_credentials(self):
        """測試下載成功通知（無憑證）"""
        from core.email_notifier import EmailNotifier
        notifier = EmailNotifier()
        
        result = notifier.send_download_success(
            'test@test.com',
            filepath='/path/to/file',
            file_size=1024
        )
        
        assert result is False
