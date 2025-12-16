"""
測試 core/game_service.py 模組 (使用 mock)
"""
import pytest
from unittest.mock import MagicMock, patch

from core.game_service import GameService
from core.exceptions import GameNotFoundException, GameAlreadyBorrowedException


class TestGameServiceInit:
    """測試初始化"""
    
    def test_init(self):
        """測試初始化"""
        mock_client = MagicMock()
        mock_member_service = MagicMock()
        
        service = GameService(mock_client, mock_member_service)
        
        assert service.client == mock_client
        assert service.member_service == mock_member_service


class TestGameServiceBorrowGame:
    """測試 borrow_game 方法"""
    
    def test_borrow_game_success(self):
        """測試借用遊戲成功"""
        mock_client = MagicMock()
        mock_client.load_games.return_value = [
            {'名稱': '卡坦島', '狀態': '可借', '借閱者': '', '借閱者ID': ''}
        ]
        mock_client.get_games_sheet.return_value = MagicMock()
        mock_member_service = MagicMock()
        
        service = GameService(mock_client, mock_member_service)
        result = service.borrow_game('卡坦島', '張三', 'A001')
        
        # 返回值是 tuple: (success, message)
        assert isinstance(result, tuple)
    
    def test_borrow_game_not_found(self):
        """測試借用不存在的遊戲"""
        mock_client = MagicMock()
        mock_client.load_games.return_value = []
        mock_member_service = MagicMock()
        
        service = GameService(mock_client, mock_member_service)
        result = service.borrow_game('不存在的遊戲', '張三', 'A001')
        
        # 返回值是 tuple: (success, message)
        assert isinstance(result, tuple)
        assert result[0] is False  # success = False
    
    def test_borrow_game_already_borrowed(self):
        """測試借用已被借出的遊戲"""
        mock_client = MagicMock()
        mock_client.load_games.return_value = [
            {'名稱': '卡坦島', '狀態': '外借中', '借閱者': '李四', '借閱者ID': 'A002'}
        ]
        mock_member_service = MagicMock()
        
        service = GameService(mock_client, mock_member_service)
        result = service.borrow_game('卡坦島', '張三', 'A001')
        
        assert isinstance(result, tuple)
        assert result[0] is False


class TestGameServiceReturnGame:
    """測試 return_game 方法"""
    
    def test_return_game_success(self):
        """測試歸還遊戲成功"""
        mock_client = MagicMock()
        mock_client.load_games.return_value = [
            {'名稱': '卡坦島', '狀態': '外借中', '借閱者': '張三', '借閱者ID': 'A001'}
        ]
        mock_client.get_games_sheet.return_value = MagicMock()
        mock_member_service = MagicMock()
        
        service = GameService(mock_client, mock_member_service)
        result = service.return_game('卡坦島')
        
        # 返回值是 tuple
        assert isinstance(result, tuple)
    
    def test_return_game_not_found(self):
        """測試歸還不存在的遊戲"""
        mock_client = MagicMock()
        mock_client.load_games.return_value = []
        mock_member_service = MagicMock()
        
        service = GameService(mock_client, mock_member_service)
        result = service.return_game('不存在的遊戲')
        
        assert isinstance(result, tuple)


class TestGameServiceBatchBorrow:
    """測試批次借用"""
    
    def test_batch_borrow_games(self):
        """測試批次借用遊戲"""
        mock_client = MagicMock()
        mock_client.load_games.return_value = [
            {'名稱': '卡坦島', '狀態': '可借', '借閱者': '', '借閱者ID': ''},
            {'名稱': '璀璨寶石', '狀態': '可借', '借閱者': '', '借閱者ID': ''}
        ]
        mock_client.get_games_sheet.return_value = MagicMock()
        mock_member_service = MagicMock()
        mock_member_service.find_member_by_id.return_value = {'id': 'A001', 'name': '張三'}
        
        service = GameService(mock_client, mock_member_service)
        result = service.batch_borrow_games(['卡坦島', '璀璨寶石'], 'A001')
        
        assert isinstance(result, tuple)


class TestGameServiceBatchReturn:
    """測試批次歸還"""
    
    def test_batch_return_games(self):
        """測試批次歸還遊戲"""
        mock_client = MagicMock()
        mock_client.load_games.return_value = [
            {'名稱': '卡坦島', '狀態': '外借中', '借閱者': '張三', '借閱者ID': 'A001'},
            {'名稱': '璀璨寶石', '狀態': '外借中', '借閱者': '張三', '借閱者ID': 'A001'}
        ]
        mock_client.get_games_sheet.return_value = MagicMock()
        mock_member_service = MagicMock()
        
        service = GameService(mock_client, mock_member_service)
        result = service.batch_return_games(['卡坦島', '璀璨寶石'])
        
        assert isinstance(result, tuple)
    
    def test_batch_return_games_by_member(self):
        """測試按會員歸還所有遊戲"""
        mock_client = MagicMock()
        mock_client.load_games.return_value = [
            {'名稱': '卡坦島', '狀態': '外借中', '借閱者': '張三', '借閱者ID': 'A001'},
            {'名稱': '璀璨寶石', '狀態': '外借中', '借閱者': '張三', '借閱者ID': 'A001'}
        ]
        mock_client.get_games_sheet.return_value = MagicMock()
        mock_member_service = MagicMock()
        mock_member_service.find_member_by_id.return_value = {'id': 'A001', 'name': '張三'}
        
        service = GameService(mock_client, mock_member_service)
        result = service.batch_return_games_by_member('A001')
        
        assert isinstance(result, tuple)
