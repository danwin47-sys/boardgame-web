import os
import secrets
from typing import Any, Dict, Optional, Tuple

import jwt
import requests
from flask import current_app, session

from .sheets_client import SheetsClient
from .types import ResponseTuple


class AuthService:
    """處理認證相關邏輯的服務層"""

    def __init__(self, sheets_client: SheetsClient = None):
        self.sheets_client = sheets_client or SheetsClient()
        self.channel_id = os.environ.get("LINE_CHANNEL_ID")
        self.channel_secret = os.environ.get("LINE_CHANNEL_SECRET")
        self.callback_url = os.environ.get("LINE_CALLBACK_URL")

        # LINE API Endpoints
        self.LINE_TOKEN_URL = "https://api.line.me/oauth2/v2.1/token"

    def generate_login_url(self) -> str:
        """產生 LINE Login 授權網址"""
        state = secrets.token_urlsafe(16)
        nonce = secrets.token_urlsafe(16)

        # 存入 session 以供 callback 驗證
        session["oauth_state"] = state
        session["oauth_nonce"] = nonce

        scope = "openid profile"  # 這裡只請求 openid 和基本 profile (不含 email)

        login_url = (
            f"https://access.line.me/oauth2/v2.1/authorize"
            f"?response_type=code"
            f"&client_id={self.channel_id}"
            f"&redirect_uri={self.callback_url}"
            f"&state={state}"
            f"&scope={scope}"
            f"&nonce={nonce}"
        )
        return login_url

    def handle_callback(self, code: str, state: str) -> Tuple[bool, Optional[Dict[str, Any]], Optional[str]]:
        """
        處理 LINE Login 回調

        Returns:
            (is_success, user_profile, error_message)
        """
        # 1. 驗證 State (防止 CSRF)
        stored_state = session.get("oauth_state")
        if state != stored_state:
            current_app.logger.warning(f"[AUTH] State mismatch: received '{state}' vs stored '{stored_state}'")
            return False, None, "Invalid state parameter"

        # 2. 用 Code 換取 Token
        try:
            headers = {"Content-Type": "application/x-www-form-urlencoded"}
            data = {
                "grant_type": "authorization_code",
                "code": code,
                "redirect_uri": self.callback_url,
                "client_id": self.channel_id,
                "client_secret": self.channel_secret,
            }

            response = requests.post(self.LINE_TOKEN_URL, headers=headers, data=data)
            response.raise_for_status()
            token_data = response.json()

            # 3. 解析 ID Token
            id_token = token_data.get("id_token")
            if not id_token:
                return False, None, "No id_token found"

            # 解碼 ID Token (驗證簽名需要完整的 JWT lib，這裡簡化處理先只解碼 payload)
            # 在生產環境建議完整驗證 issuer 和 audience
            # 加入 leeway=60 容許 60 秒的時間誤差，解決 'token is not yet valid' 問題
            decoded = jwt.decode(
                id_token,
                self.channel_secret,
                audience=self.channel_id,
                issuer="https://access.line.me",
                algorithms=["HS256"],
                leeway=60,
            )

            # 驗證 nonce
            if decoded.get("nonce") != session.get("oauth_nonce"):
                return False, None, "Invalid nonce"

            user_profile = {
                "line_user_id": decoded.get("sub"),
                "name": decoded.get("name"),
                "picture": decoded.get("picture"),
            }

            return True, user_profile, None

        except Exception as e:
            current_app.logger.error(f"[AUTH] LINE Login callback failed: {e}")
            return False, None, str(e)

    def check_user_exists(self, line_user_id: str) -> Optional[Dict[str, Any]]:
        """檢查此 LINE ID 是否已綁定社員"""
        return self.sheets_client.get_user_by_line_id(line_user_id)

    def bind_student_id(self, line_user_id: str, student_id: str) -> Tuple[bool, str]:
        """
        綁定工號

        Returns:
            (success, message)
        """
        # 1. 檢查工號是否存在
        member = self.sheets_client.get_user_by_student_id(student_id)
        if not member:
            return False, "找不到此工號，請確認是否已入社"

        # 2. 檢查此工號是否已被其他 LINE 帳號綁定
        current_binding = str(member.get("line_user_id", ""))
        if current_binding and current_binding != line_user_id:
            return False, "此工號已被其他 LINE 帳號綁定，請聯繫管理員"

        # 3. 執行綁定
        success = self.sheets_client.bind_user_to_line_id(student_id, line_user_id)
        if success:
            return True, "綁定成功！"
        else:
            return False, "綁定失敗，請稍後再試"
