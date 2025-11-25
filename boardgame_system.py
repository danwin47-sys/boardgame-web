from core.sheets_client import SheetsClient
from core.game_service import GameService
from core.member_service import MemberService
from core.utils import get_current_timestamp

class BoardGameManager:
    """
    向後相容的 Facade 類別，將操作委派給核心服務。
    """
    
    def __init__(self):
        print("[Info] Initializing BoardGameManager (Facade)...")
        self.client = SheetsClient()
        self.member_service = MemberService(self.client)
        self.game_service = GameService(self.client, self.member_service)
        
        # 用於相容 flask_app.py 中的 mgr.games = ...
        self.games = []

    @property
    def valid(self):
        return self.client.valid

    def get_current_timestamp(self):
        return get_current_timestamp()

    def load_data(self):
        return self.client.load_games()

    def load_members(self):
        return self.client.load_members()

    def find_member_by_id(self, member_id):
        return self.member_service.find_member_by_id(member_id)

    def find_member_by_name(self, member_name):
        return self.member_service.find_member_by_name(member_name)

    def borrow_game(self, name, user_name, user_id):
        return self.game_service.borrow_game(name, user_name, user_id)

    def batch_borrow_games(self, game_names, member_id):
        return self.game_service.batch_borrow_games(game_names, member_id)

    def return_game(self, name):
        return self.game_service.return_game(name)

    def batch_return_games(self, game_names):
        return self.game_service.batch_return_games(game_names)

    def batch_return_games_by_member(self, member_id):
        return self.game_service.batch_return_games_by_member(member_id)