"""
Email Notification Service
發送郵件通知 BGG ranks 更新結果
"""
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime
import os
import logging

logger = logging.getLogger(__name__)


class EmailNotifier:
    """郵件通知服務"""
    
    def __init__(self, smtp_server: str = None, smtp_port: int = None, 
                 username: str = None, password: str = None):
        """
        初始化郵件通知服務
        
        Args:
            smtp_server: SMTP 伺服器地址
            smtp_port: SMTP 埠號
            username: 郵件帳號
            password: 郵件密碼
        """
        self.smtp_server = smtp_server or os.getenv('SMTP_SERVER', 'smtp.gmail.com')
        self.smtp_port = smtp_port or int(os.getenv('SMTP_PORT', '587'))
        self.username = username or os.getenv('EMAIL_USERNAME')
        self.password = password or os.getenv('EMAIL_PASSWORD')
        
        if not self.username or not self.password:
            logger.warning("Email credentials not configured")
    
    def send_notification(self, to_email: str, subject: str, content: str, is_html: bool = False):
        """
        發送郵件通知
        
        Args:
            to_email: 收件人郵箱
            subject: 郵件主題
            content: 郵件內容
            is_html: 是否為 HTML 格式
            
        Returns:
            是否發送成功
        """
        if not self.username or not self.password:
            logger.error("Email credentials not configured, cannot send email")
            return False
        
        try:
            # 創建郵件
            msg = MIMEMultipart('alternative')
            msg['From'] = self.username
            msg['To'] = to_email
            msg['Subject'] = subject
            
            # 添加內容
            if is_html:
                msg.attach(MIMEText(content, 'html'))
            else:
                msg.attach(MIMEText(content, 'plain'))
            
            # 發送郵件
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls()
                server.login(self.username, self.password)
                server.send_message(msg)
            
            logger.info(f"✅ Email sent to {to_email}")
            return True
        
        except Exception as e:
            logger.error(f"❌ Failed to send email: {e}")
            return False
    
    def send_import_success(self, to_email: str, total_records: int, errors: int, 
                           import_time: float, db_stats: dict = None):
        """
        發送導入成功通知
        
        Args:
            to_email: 收件人郵箱
            total_records: 導入記錄數
            errors: 錯誤數
            import_time: 導入時間（秒）
            db_stats: 資料庫統計資訊
        """
        subject = f"✅ BGG Ranks 數據導入完成 - {datetime.now().strftime('%Y-%m-%d')}"
        
        content = f"""
BGG Ranks 數據導入成功！

📊 導入統計：
- 成功導入：{total_records:,} 筆記錄
- 錯誤數量：{errors} 筆
- 導入時間：{import_time:.2f} 秒
- 完成時間：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

"""
        
        if db_stats:
            content += f"""
📈 資料庫統計：
- 總遊戲數：{db_stats.get('total_games', 0):,}
- 有排名遊戲：{db_stats.get('ranked_games', 0):,}
- 擴充數量：{db_stats.get('expansions', 0):,}
- 最後更新：{db_stats.get('last_updated', 'N/A')}
"""
        
        content += "\n---\n自動化通知郵件，請勿回覆"
        
        return self.send_notification(to_email, subject, content)
    
    def send_import_failure(self, to_email: str, error_message: str):
        """
        發送導入失敗通知
        
        Args:
            to_email: 收件人郵箱
            error_message: 錯誤訊息
        """
        subject = f"❌ BGG Ranks 數據導入失敗 - {datetime.now().strftime('%Y-%m-%d')}"
        
        content = f"""
BGG Ranks 數據導入失敗！

⚠️ 錯誤訊息：
{error_message}

請查看日誌檔案以獲取詳細資訊。

發生時間：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

---
自動化通知郵件，請勿回覆
"""
        
        return self.send_notification(to_email, subject, content)
    
    def send_download_success(self, to_email: str, filepath: str, file_size: int):
        """
        發送下載成功通知
        
        Args:
            to_email: 收件人郵箱
            filepath: 下載檔案路徑
            file_size: 檔案大小（bytes）
        """
        subject = f"✅ BGG Dumps 下載完成 - {datetime.now().strftime('%Y-%m-%d')}"
        
        content = f"""
BGG Ranks 數據檔案下載成功！

📥 下載資訊：
- 檔案路徑：{filepath}
- 檔案大小：{file_size:,} bytes ({file_size / 1024 / 1024:.2f} MB)
- 下載時間：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

下一步：執行導入腳本將數據導入資料庫

---
自動化通知郵件，請勿回覆
"""
        
        return self.send_notification(to_email, subject, content)


def main():
    """測試郵件發送"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Send test email notification')
    parser.add_argument('to_email', help='Recipient email address')
    parser.add_argument('--subject', default='Test Email', help='Email subject')
    parser.add_argument('--message', default='This is a test email', help='Email message')
    
    args = parser.parse_args()
    
    notifier = EmailNotifier()
    success = notifier.send_notification(args.to_email, args.subject, args.message)
    
    if success:
        print("✅ Email sent successfully")
    else:
        print("❌ Failed to send email")


if __name__ == '__main__':
    main()
