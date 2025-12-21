"""
測試 core/game_service.py 模組 (使用 mock)
"""
import pytest
from unittest.mock import MagicMock, patch

from core.game_service import GameService
from core.exceptions import GameNotFoundException, GameAlreadyBorrowedException
from core.constants import (
    GAME_STATUS_BORROWED,
    GAME_STATUS_AVAILABLE,
    FIELD_NAME,
    FIELD_STATUS,
    FIELD_BORROWER,
    FIELD_BORROWER_ID,
    FIELD_MDATE,
    FIELD_HISTORY,
    FIELD_CUSTODIAN
)


class TestGameServiceInit:
    """測試初始化"""
    
    def test_init(self):
        """測試初始化"""
        mock_client = MagicMock()
        mock_member_service = MagicMock()
        
        service = GameService(mock_client, mock_member_service)
        
        assert service.client == mock_client
        assert service.member_service == mock_member_service


class TestGameServiceGetHeaderIndices:
    """測試 _get_header_indices 方法"""
    
    def test_get_header_indices_success(self):
        """測試成功建立欄位索引映射"""
        mock_client = MagicMock()
        mock_member_service = MagicMock()
        service = GameService(mock_client, mock_member_service)
        
        header = [FIELD_NAME, FIELD_STATUS, FIELD_BORROWER, FIELD_BORROWER_ID, FIELD_MDATE, FIELD_HISTORY, FIELD_CUSTODIAN]
        indices = service._get_header_indices(header)
        
        assert indices[FIELD_NAME] == 0
        assert indices[FIELD_STATUS] == 1
        assert indices[FIELD_BORROWER] == 2
        assert indices[FIELD_BORROWER_ID] == 3
        assert indices[FIELD_MDATE] == 4
        assert indices[FIELD_HISTORY] == 5
        assert indices[FIELD_CUSTODIAN] == 6
    
    def test_get_header_indices_without_custodian(self):
        """測試沒有保管人欄位的情況"""
        mock_client = MagicMock()
        mock_member_service = MagicMock()
        service = GameService(mock_client, mock_member_service)
        
        header = [FIELD_NAME, FIELD_STATUS, FIELD_BORROWER, FIELD_BORROWER_ID, FIELD_MDATE, FIELD_HISTORY]
        indices = service._get_header_indices(header)
        
        assert FIELD_CUSTODIAN not in indices
        assert len(indices) == 6
    
    def test_get_header_indices_missing_field(self):
        """測試缺少必要欄位時拋出異常"""
        mock_client = MagicMock()
        mock_member_service = MagicMock()
        service = GameService(mock_client, mock_member_service)
        
        header = [FIELD_NAME, FIELD_STATUS]  # 缺少其他必要欄位
        
        with pytest.raises(ValueError, match="資料表欄位缺失"):
            service._get_header_indices(header)


class TestGameServiceBorrowGame:
    """測試 borrow_game 方法"""
    
    def test_borrow_game_success(self):
        """測試借用遊戲成功"""
        mock_client = MagicMock()
        mock_client.valid = True
        mock_ws = MagicMock()
        mock_client.get_games_worksheet.return_value = mock_ws
        mock_ws.get_all_records.return_value = [
            {FIELD_NAME: '卡坦島', FIELD_STATUS: GAME_STATUS_AVAILABLE, FIELD_BORROWER: '', FIELD_BORROWER_ID: '', FIELD_MDATE: '', FIELD_HISTORY: ''}
        ]
        mock_ws.row_values.return_value = [FIELD_NAME, FIELD_STATUS, FIELD_BORROWER, FIELD_BORROWER_ID, FIELD_MDATE, FIELD_HISTORY]
        mock_client.create_batch_update.return_value = {'range': 'A1', 'values': [['test']]}
        mock_member_service = MagicMock()
        
        service = GameService(mock_client, mock_member_service)
        success, msg = service.borrow_game('卡坦島', '張三', 'A001')
        
        assert success is True
        assert '成功借出' in msg
        mock_ws.batch_update.assert_called_once()
        mock_client.invalidate_games_cache.assert_called_once()
    
    def test_borrow_game_not_found(self):
        """測試借用不存在的遊戲"""
        mock_client = MagicMock()
        mock_client.valid = True
        mock_ws = MagicMock()
        mock_client.get_games_worksheet.return_value = mock_ws
        mock_ws.get_all_records.return_value = []
        mock_member_service = MagicMock()
        
        service = GameService(mock_client, mock_member_service)
        success, msg = service.borrow_game('不存在的遊戲', '張三', 'A001')
        
        assert success is False
        assert '找不到此遊戲' in msg
    
    def test_borrow_game_already_borrowed(self):
        """測試借用已被借出的遊戲"""
        mock_client = MagicMock()
        mock_client.valid = True
        mock_ws = MagicMock()
        mock_client.get_games_worksheet.return_value = mock_ws
        mock_ws.get_all_records.return_value = [
            {FIELD_NAME: '卡坦島', FIELD_STATUS: GAME_STATUS_BORROWED, FIELD_BORROWER: '李四', FIELD_BORROWER_ID: 'A002'}
        ]
        mock_member_service = MagicMock()
        
        service = GameService(mock_client, mock_member_service)
        success, msg = service.borrow_game('卡坦島', '張三', 'A001')
        
        assert success is False
        assert '已經被' in msg
        assert '李四' in msg
    
    def test_borrow_game_client_invalid(self):
        """測試客戶端無效時"""
        mock_client = MagicMock()
        mock_client.valid = False
        mock_member_service = MagicMock()
        
        service = GameService(mock_client, mock_member_service)
        success, msg = service.borrow_game('卡坦島', '張三', 'A001')
        
        assert success is False
        assert '系統連線錯誤' in msg
    
    def test_borrow_game_exception_handling(self):
        """測試異常處理"""
        mock_client = MagicMock()
        mock_client.valid = True
        mock_client.get_games_worksheet.side_effect = Exception("API Error")
        mock_member_service = MagicMock()
        
        service = GameService(mock_client, mock_member_service)
        success, msg = service.borrow_game('卡坦島', '張三', 'A001')
        
        assert success is False
        assert '借閱失敗' in msg


class TestGameServiceBatchBorrow:
    """測試批次借用"""
    
    def test_batch_borrow_games_success(self):
        """測試批次借用遊戲成功"""
        mock_client = MagicMock()
        mock_client.valid = True
        mock_ws = MagicMock()
        mock_client.get_games_worksheet.return_value = mock_ws
        mock_ws.get_all_values.return_value = [
            [FIELD_NAME, FIELD_STATUS, FIELD_BORROWER, FIELD_BORROWER_ID, FIELD_MDATE, FIELD_HISTORY],
            ['卡坦島', GAME_STATUS_AVAILABLE, '', '', '', ''],
            ['璀璨寶石', GAME_STATUS_AVAILABLE, '', '', '', '']
        ]
        mock_client.create_batch_update.return_value = {'range': 'A1', 'values': [['test']]}
        mock_member_service = MagicMock()
        mock_member_service.find_member_by_id.return_value = {'id': 'A001', 'name': '張三'}
        
        service = GameService(mock_client, mock_member_service)
        success, msg, s_list, f_list = service.batch_borrow_games(['卡坦島', '璀璨寶石'], 'A001')
        
        assert success is True
        assert len(s_list) == 2
        assert len(f_list) == 0
        mock_ws.batch_update.assert_called_once()
    
    def test_batch_borrow_member_not_found(self):
        """測試會員不存在"""
        mock_client = MagicMock()
        mock_client.valid = True
        mock_member_service = MagicMock()
        mock_member_service.find_member_by_id.return_value = None
        
        service = GameService(mock_client, mock_member_service)
        success, msg, s_list, f_list = service.batch_borrow_games(['卡坦島'], 'A999')
        
        assert success is False
        assert '找不到社員' in msg
        assert len(s_list) == 0
    
    def test_batch_borrow_partial_success(self):
        """測試部分遊戲可借"""
        mock_client = MagicMock()
        mock_client.valid = True
        mock_ws = MagicMock()
        mock_client.get_games_worksheet.return_value = mock_ws
        mock_ws.get_all_values.return_value = [
            [FIELD_NAME, FIELD_STATUS, FIELD_BORROWER, FIELD_BORROWER_ID, FIELD_MDATE, FIELD_HISTORY],
            ['卡坦島', GAME_STATUS_AVAILABLE, '', '', '', ''],
            ['璀璨寶石', GAME_STATUS_BORROWED, '李四', 'A002', '', '']
        ]
        mock_client.create_batch_update.return_value = {'range': 'A1', 'values': [['test']]}
        mock_member_service = MagicMock()
        mock_member_service.find_member_by_id.return_value = {'id': 'A001', 'name': '張三'}
        
        service = GameService(mock_client, mock_member_service)
        success, msg, s_list, f_list = service.batch_borrow_games(['卡坦島', '璀璨寶石'], 'A001')
        
        assert success is True
        assert len(s_list) == 1
        assert len(f_list) == 1
        assert s_list[0] == '卡坦島'
        assert f_list[0]['name'] == '璀璨寶石'
    
    def test_batch_borrow_game_not_found(self):
        """測試遊戲不存在"""
        mock_client = MagicMock()
        mock_client.valid = True
        mock_ws = MagicMock()
        mock_client.get_games_worksheet.return_value = mock_ws
        mock_ws.get_all_values.return_value = [
            [FIELD_NAME, FIELD_STATUS, FIELD_BORROWER, FIELD_BORROWER_ID, FIELD_MDATE, FIELD_HISTORY],
            ['卡坦島', GAME_STATUS_AVAILABLE, '', '', '', '']
        ]
        mock_client.create_batch_update.return_value = {'range': 'A1', 'values': [['test']]}
        mock_member_service = MagicMock()
        mock_member_service.find_member_by_id.return_value = {'id': 'A001', 'name': '張三'}
        
        service = GameService(mock_client, mock_member_service)
        success, msg, s_list, f_list = service.batch_borrow_games(['不存在的遊戲'], 'A001')
        
        assert success is True
        assert len(s_list) == 0
        assert len(f_list) == 1
        assert f_list[0]['reason'] == '找不到此遊戲'
    
    def test_batch_borrow_client_invalid(self):
        """測試客戶端無效時"""
        mock_client = MagicMock()
        mock_client.valid = False
        mock_member_service = MagicMock()
        
        service = GameService(mock_client, mock_member_service)
        success, msg, s_list, f_list = service.batch_borrow_games(['卡坦島'], 'A001')
        
        assert success is False
        assert '系統連線錯誤' in msg


class TestGameServiceReturnGame:
    """測試 return_game 方法"""
    
    def test_return_game_success(self):
        """測試歸還遊戲成功"""
        mock_client = MagicMock()
        mock_client.valid = True
        mock_ws = MagicMock()
        mock_client.get_games_worksheet.return_value = mock_ws
        mock_ws.get_all_values.return_value = [
            [FIELD_NAME, FIELD_STATUS, FIELD_BORROWER, FIELD_BORROWER_ID, FIELD_MDATE, FIELD_HISTORY],
            ['卡坦島', GAME_STATUS_BORROWED, '張三', 'A001', '', '']
        ]
        mock_client.load_members.return_value = []
        mock_client.create_batch_update.return_value = {'range': 'A1', 'values': [['test']]}
        mock_member_service = MagicMock()
        
        service = GameService(mock_client, mock_member_service)
        success, msg = service.return_game('卡坦島')
        
        assert success is True
        assert '成功歸還' in msg
    
    def test_return_game_not_found(self):
        """測試歸還不存在的遊戲"""
        mock_client = MagicMock()
        mock_client.valid = True
        mock_ws = MagicMock()
        mock_client.get_games_worksheet.return_value = mock_ws
        mock_ws.get_all_values.return_value = [
            [FIELD_NAME, FIELD_STATUS, FIELD_BORROWER, FIELD_BORROWER_ID, FIELD_MDATE, FIELD_HISTORY]
        ]
        mock_client.load_members.return_value = []
        mock_member_service = MagicMock()
        
        service = GameService(mock_client, mock_member_service)
        success, msg = service.return_game('不存在的遊戲')
        
        assert success is False
        assert '找不到此遊戲' in msg


class TestGameServiceBatchReturn:
    """測試批次歸還"""
    
    def test_batch_return_games_success(self):
        """測試批次歸還遊戲成功"""
        mock_client = MagicMock()
        mock_client.valid = True
        mock_ws = MagicMock()
        mock_client.get_games_worksheet.return_value = mock_ws
        mock_ws.get_all_values.return_value = [
            [FIELD_NAME, FIELD_STATUS, FIELD_BORROWER, FIELD_BORROWER_ID, FIELD_MDATE, FIELD_HISTORY],
            ['卡坦島', GAME_STATUS_BORROWED, '張三', 'A001', '', ''],
            ['璀璨寶石', GAME_STATUS_BORROWED, '張三', 'A001', '', '']
        ]
        mock_client.load_members.return_value = []
        mock_client.create_batch_update.return_value = {'range': 'A1', 'values': [['test']]}
        mock_member_service = MagicMock()
        
        service = GameService(mock_client, mock_member_service)
        success, msg, s_list, f_list = service.batch_return_games(['卡坦島', '璀璨寶石'])
        
        assert success is True
        assert len(s_list) == 2
        assert len(f_list) == 0
        mock_ws.batch_update.assert_called_once()
    
    def test_batch_return_partial_success(self):
        """測試部分遊戲可歸還"""
        mock_client = MagicMock()
        mock_client.valid = True
        mock_ws = MagicMock()
        mock_client.get_games_worksheet.return_value = mock_ws
        mock_ws.get_all_values.return_value = [
            [FIELD_NAME, FIELD_STATUS, FIELD_BORROWER, FIELD_BORROWER_ID, FIELD_MDATE, FIELD_HISTORY],
            ['卡坦島', GAME_STATUS_BORROWED, '張三', 'A001', '', ''],
            ['璀璨寶石', GAME_STATUS_AVAILABLE, '', '', '', '']
        ]
        mock_client.load_members.return_value = []
        mock_client.create_batch_update.return_value = {'range': 'A1', 'values': [['test']]}
        mock_member_service = MagicMock()
        
        service = GameService(mock_client, mock_member_service)
        success, msg, s_list, f_list = service.batch_return_games(['卡坦島', '璀璨寶石'])
        
        assert success is True
        assert len(s_list) == 1
        assert len(f_list) == 1
        assert f_list[0]['reason'] == '此遊戲未被借出'
    
    def test_batch_return_with_custodian(self):
        """測試歸還時處理保管人邏輯"""
        mock_client = MagicMock()
        mock_client.valid = True
        mock_ws = MagicMock()
        mock_client.get_games_worksheet.return_value = mock_ws
        mock_ws.get_all_values.return_value = [
            [FIELD_NAME, FIELD_STATUS, FIELD_BORROWER, FIELD_BORROWER_ID, FIELD_MDATE, FIELD_HISTORY, FIELD_CUSTODIAN],
            ['卡坦島', GAME_STATUS_BORROWED, '張三', 'A001', '', '', '李四']
        ]
        mock_client.load_members.return_value = [{'id': 'A002', 'name': '李四'}]
        mock_client.create_batch_update.return_value = {'range': 'A1', 'values': [['test']]}
        mock_member_service = MagicMock()
        
        service = GameService(mock_client, mock_member_service)
        success, msg, s_list, f_list = service.batch_return_games(['卡坦島'])
        
        assert success is True
        assert len(s_list) == 1
        # 驗證保管人邏輯有被執行（透過 batch_update 的呼叫）
        mock_ws.batch_update.assert_called_once()
    
    def test_batch_return_games_by_member_success(self):
        """測試按會員歸還所有遊戲"""
        mock_client = MagicMock()
        mock_client.valid = True
        mock_client.load_games.return_value = [
            {FIELD_NAME: '卡坦島', FIELD_STATUS: GAME_STATUS_BORROWED, FIELD_BORROWER: '張三', FIELD_BORROWER_ID: 'A001'}
        ]
        mock_ws = MagicMock()
        mock_client.get_games_worksheet.return_value = mock_ws
        mock_ws.get_all_values.return_value = [
            [FIELD_NAME, FIELD_STATUS, FIELD_BORROWER, FIELD_BORROWER_ID, FIELD_MDATE, FIELD_HISTORY],
            ['卡坦島', GAME_STATUS_BORROWED, '張三', 'A001', '', '']
        ]
        mock_client.load_members.return_value = []
        mock_client.create_batch_update.return_value = {'range': 'A1', 'values': [['test']]}
        mock_member_service = MagicMock()
        mock_member_service.find_member_by_id.return_value = {'id': 'A001', 'name': '張三'}
        
        service = GameService(mock_client, mock_member_service)
        success, msg, s_list = service.batch_return_games_by_member('A001')
        
        assert success is True
        assert len(s_list) >= 1
    
    def test_batch_return_by_member_not_found(self):
        """測試會員不存在"""
        mock_client = MagicMock()
        mock_client.valid = True
        mock_member_service = MagicMock()
        mock_member_service.find_member_by_id.return_value = None
        
        service = GameService(mock_client, mock_member_service)
        success, msg, s_list = service.batch_return_games_by_member('A999')
        
        assert success is False
        assert '找不到社員' in msg
    
    def test_batch_return_by_member_no_games(self):
        """測試會員無借閱遊戲"""
        mock_client = MagicMock()
        mock_client.valid = True
        mock_client.load_games.return_value = []
        mock_member_service = MagicMock()
        mock_member_service.find_member_by_id.return_value = {'id': 'A001', 'name': '張三'}
        
        service = GameService(mock_client, mock_member_service)
        success, msg, s_list = service.batch_return_games_by_member('A001')
        
        assert success is False
        assert '沒有借閱任何桌遊' in msg
