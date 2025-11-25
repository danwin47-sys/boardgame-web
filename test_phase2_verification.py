# coding: utf-8
import sys
import os
import unittest
from unittest.mock import MagicMock, patch

# Add project root to path
sys.path.insert(0, os.path.dirname(__file__))

from core.sheets_client import SheetsClient
from core.member_service import MemberService
from core.game_service import GameService
from core.constants import GAME_STATUS_AVAILABLE, GAME_STATUS_BORROWED

class TestPhase2Services(unittest.TestCase):
    
    def setUp(self):
        # Mock SheetsClient to avoid real API calls during unit testing
        self.mock_client = MagicMock(spec=SheetsClient)
        self.mock_client.valid = True
        
        # Mock data
        self.mock_games = [
            {'name': 'Catan', 'status': '歸還', 'borrower': '', 'id': 'G001'},
            {'name': 'Carcassonne', 'status': '借出', 'borrower': 'Alice', 'id': 'G002'}
        ]
        self.mock_members = [
            {'name': 'Alice', 'id': 'M001'},
            {'name': 'Bob', 'id': 'M002'}
        ]
        
        self.mock_client.load_games.return_value = self.mock_games
        self.mock_client.load_members.return_value = self.mock_members
        
        # Initialize services
        self.member_service = MemberService(self.mock_client)
        self.game_service = GameService(self.mock_client, self.member_service)

    def test_member_service_find_by_id(self):
        print("\n[Test] MemberService.find_member_by_id")
        member = self.member_service.find_member_by_id('M001')
        self.assertIsNotNone(member)
        self.assertEqual(member['name'], 'Alice')
        
        member = self.member_service.find_member_by_id('M999')
        self.assertIsNone(member)
        print("[OK] Member lookup by ID works")

    def test_member_service_find_by_name(self):
        print("\n[Test] MemberService.find_member_by_name")
        member = self.member_service.find_member_by_name('Bob')
        self.assertIsNotNone(member)
        self.assertEqual(member['id'], 'M002')
        print("[OK] Member lookup by name works")

    def test_game_service_borrow_success(self):
        print("\n[Test] GameService.borrow_game (Success)")
        
        # Mock worksheet
        mock_ws = MagicMock()
        mock_ws.get_all_records.return_value = self.mock_games
        mock_ws.row_values.return_value = ['name', 'status', 'borrower', 'borrower_id', 'mdate', 'history']
        self.mock_client.get_games_worksheet.return_value = mock_ws
        
        success, msg = self.game_service.borrow_game('Catan', 'Bob', 'M002')
        
        self.assertTrue(success)
        self.assertIn('成功借出', msg)
        mock_ws.batch_update.assert_called_once()
        print("[OK] Borrow game logic works")

    def test_game_service_borrow_fail_already_borrowed(self):
        print("\n[Test] GameService.borrow_game (Fail - Already Borrowed)")
        
        mock_ws = MagicMock()
        mock_ws.get_all_records.return_value = self.mock_games
        self.mock_client.get_games_worksheet.return_value = mock_ws
        
        success, msg = self.game_service.borrow_game('Carcassonne', 'Bob', 'M002')
        
        self.assertFalse(success)
        self.assertIn('已經被', msg)
        print("[OK] Borrowing borrowed game fails as expected")

    def test_game_service_batch_return(self):
        print("\n[Test] GameService.batch_return_games")
        
        mock_ws = MagicMock()
        mock_ws.get_all_values.return_value = [
            ['name', 'status', 'borrower', 'borrower_id', 'mdate', 'history'],
            ['Catan', '歸還', '', '', '', ''],
            ['Carcassonne', '借出', 'Alice', 'M001', '2023-01-01', '']
        ]
        self.mock_client.get_games_worksheet.return_value = mock_ws
        
        success, msg, s_list, f_list = self.game_service.batch_return_games(['Carcassonne'])
        
        self.assertTrue(success)
        self.assertEqual(len(s_list), 1)
        self.assertEqual(s_list[0], 'Carcassonne')
        mock_ws.batch_update.assert_called_once()
        print("[OK] Batch return logic works")

if __name__ == '__main__':
    unittest.main()
