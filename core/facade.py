from typing import List, Dict, Any, Optional

from core.sheets_client import SheetsClient
from core.game_service import GameService
from core.member_service import MemberService
from core.utils import get_current_timestamp

from core.types import GameList, MemberList, MemberDict


class BoardGameManager:
    """
    向後相容的 Facade 類別，將操作委派給核心服務。
    """

    def __init__(self):
        print("[Info] Initializing BoardGameManager (Facade)...")
        self.client = SheetsClient()
        self.member_service = MemberService(self.client)
        self.game_service = GameService(self.client, self.member_service)

        # 用於相容應用程式中的 mgr.games = ...
        self.games = []

    @property
    def valid(self) -> bool:
        """檢查 SheetsClient 是否有效連線"""
        return self.client.valid

    def get_current_timestamp(self) -> str:
        """取得當前時間戳記"""
        return get_current_timestamp()

    def load_data(self) -> GameList:
        """載入所有桌遊資料"""
        return self.client.load_games()

    def load_members(self) -> MemberList:
        """載入所有社員資料"""
        return self.client.load_members()

    def find_member_by_id(self, member_id):
        return self.member_service.find_member_by_id(member_id)

    def find_member_by_name(self, member_name):
        return self.member_service.find_member_by_name(member_name)

    def borrow_game(self, name: str, user_name: str, user_id: str) -> Dict[str, Any]:
        """借出桌遊"""
        return self.game_service.borrow_game(name, user_name, user_id)

    def batch_borrow_games(self, game_names: List[str], member_id: str) -> Dict[str, Any]:
        """批量借出桌遊"""
        return self.game_service.batch_borrow_games(game_names, member_id)

    def return_game(self, name: str) -> Dict[str, Any]:
        """歸還桌遊"""
        return self.game_service.return_game(name)

    def batch_return_games(self, game_names: List[str]) -> Dict[str, Any]:
        """批量歸還桌遊"""
        return self.game_service.batch_return_games(game_names)

    def batch_return_games_by_member(self, member_id: str) -> Dict[str, Any]:
        """歸還特定社員的所有桌遊"""
        return self.game_service.batch_return_games_by_member(member_id)

    def update_game_expansion_info(
        self, game_name: str, is_expansion: bool, parent_game: Optional[str], storage_mode: str
    ) -> Dict[str, Any]:
        """更新桌遊擴充資訊"""
        return self.game_service.update_game_expansion_info(
            game_name, is_expansion, parent_game, storage_mode
        )
