from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple

from .constants import (
    FIELD_BORROWER,
    FIELD_BORROWER_ID,
    FIELD_CUSTODIAN,
    FIELD_HISTORY,
    FIELD_MDATE,
    FIELD_NAME,
    FIELD_STATUS,
    GAME_STATUS_AVAILABLE,
    GAME_STATUS_BORROWED,
)
from .member_service import MemberService
from .sheets_client import SheetsClient
from .utils import create_history_entry, format_datetime, get_current_timestamp


class GameService:
    """
    負責桌遊的借出、歸還等核心業務邏輯。
    """

    def __init__(self, sheets_client: SheetsClient, member_service: MemberService):
        self.client = sheets_client
        self.member_service = member_service

    def _get_header_indices(self, header: List[str]) -> Dict[str, int]:
        """建立欄位名稱到索引的映射"""
        indices = {}
        try:
            indices[FIELD_NAME] = header.index(FIELD_NAME)
            indices[FIELD_STATUS] = header.index(FIELD_STATUS)
            indices[FIELD_BORROWER] = header.index(FIELD_BORROWER)
            indices[FIELD_BORROWER_ID] = header.index(FIELD_BORROWER_ID)
            indices[FIELD_MDATE] = header.index(FIELD_MDATE)
            indices[FIELD_HISTORY] = header.index(FIELD_HISTORY)
            # Custodian is optional in some versions, but we should try to find
            # it
            if FIELD_CUSTODIAN in header:
                indices[FIELD_CUSTODIAN] = header.index(FIELD_CUSTODIAN)
        except ValueError as e:
            raise ValueError(f"資料表欄位缺失: {e}")
        return indices

    def borrow_game(self, name: str, user_name: str, user_id: str) -> Tuple[bool, str]:
        """
        借出單一桌遊
        """
        if not self.client.valid:
            return False, "系統連線錯誤"

        try:
            ws = self.client.get_games_worksheet()
            games = ws.get_all_records()

            target_row = -1
            current_game = None

            for i, g in enumerate(games):
                if g.get(FIELD_NAME) == name:
                    target_row = i + 2
                    current_game = g
                    break

            if not current_game:
                return False, "找不到此遊戲"

            if current_game.get(FIELD_STATUS) == GAME_STATUS_BORROWED:
                return False, f"《{name}》已經被 {current_game.get(FIELD_BORROWER)} 借走了"

            ts = get_current_timestamp()

            # 取得 header 以確定欄位索引
            header = ws.row_values(1)
            idx = self._get_header_indices(header)

            batch_updates = []

            # Helper to add update
            def add_update(r, c, val):
                batch_updates.append(self.client.create_batch_update(r, c, val))

            add_update(target_row, idx[FIELD_STATUS], GAME_STATUS_BORROWED)
            add_update(target_row, idx[FIELD_BORROWER], user_name)
            add_update(target_row, idx[FIELD_BORROWER_ID], user_id)
            add_update(target_row, idx[FIELD_MDATE], ts)

            existing_history = current_game.get(FIELD_HISTORY, "")
            history_entry = create_history_entry(user_name, "借閱", ts)
            new_history = f"{existing_history} | {history_entry}" if existing_history else history_entry
            add_update(target_row, idx[FIELD_HISTORY], new_history)

            if batch_updates:
                ws.batch_update(batch_updates)
                self.client.invalidate_games_cache()

            return True, f"成功借出：《{name}》"

        except Exception as e:
            return False, f"借閱失敗: {e}"

    def batch_borrow_games(self, game_names: List[str], member_id: str) -> Tuple[bool, str, List[str], List[Dict[str, str]]]:
        """
        批次借出桌遊
        """
        if not self.client.valid:
            return False, "系統連線錯誤", [], []

        try:
            member = self.member_service.find_member_by_id(member_id)
            if not member:
                return False, "找不到社員", [], []

            ws = self.client.get_games_worksheet()
            all_values = ws.get_all_values()
            if not all_values:
                return False, "讀取遊戲列表失敗", [], []

            header = all_values[0]
            games_data = all_values[1:]

            idx = self._get_header_indices(header)
            name_idx = idx[FIELD_NAME]

            name_to_row = {}
            name_to_data = {}

            for i, row in enumerate(games_data):
                if len(row) > name_idx:
                    g_name = row[name_idx]
                    name_to_row[g_name] = i + 2
                    name_to_data[g_name] = row

            success_list = []
            fail_list = []
            batch_updates = []
            ts = get_current_timestamp()

            for name in game_names:
                if name not in name_to_row:
                    fail_list.append({"name": name, "reason": "找不到此遊戲"})
                    continue

                row_idx = name_to_row[name]
                row_data = name_to_data[name]

                # Check status
                current_status = row_data[idx[FIELD_STATUS]] if len(row_data) > idx[FIELD_STATUS] else ""
                if current_status == GAME_STATUS_BORROWED:
                    current_borrower = row_data[idx[FIELD_BORROWER]] if len(row_data) > idx[FIELD_BORROWER] else "有人"
                    fail_list.append({"name": name, "reason": f"已被 {current_borrower} 借出"})
                    continue

                success_list.append(name)

                def add_update(r, c, val):
                    batch_updates.append(self.client.create_batch_update(r, c, val))

                add_update(row_idx, idx[FIELD_STATUS], GAME_STATUS_BORROWED)
                add_update(row_idx, idx[FIELD_BORROWER], member["name"])
                add_update(row_idx, idx[FIELD_BORROWER_ID], member["id"])
                add_update(row_idx, idx[FIELD_MDATE], ts)

                existing_history = row_data[idx[FIELD_HISTORY]] if len(row_data) > idx[FIELD_HISTORY] else ""
                history_entry = create_history_entry(member["name"], "借閱", ts)
                new_history = f"{existing_history} | {history_entry}" if existing_history else history_entry
                add_update(row_idx, idx[FIELD_HISTORY], new_history)

            if batch_updates:
                ws.batch_update(batch_updates)
                self.client.invalidate_games_cache()

            msg = f"成功借出 {len(success_list)} 個遊戲"
            if fail_list:
                msg += f"，失敗 {len(fail_list)} 個"

            return True, msg, success_list, fail_list

        except Exception as e:
            return False, f"批次借閱失敗: {e}", [], []

    def batch_return_games(self, game_names: List[str]) -> Tuple[bool, str, List[str], List[Dict[str, str]]]:
        """
        批次歸還桌遊
        """
        if not self.client.valid:
            return False, "系統連線錯誤", [], []

        try:
            ws = self.client.get_games_worksheet()
            all_values = ws.get_all_values()
            if not all_values:
                return False, "讀取遊戲列表失敗", [], []

            header = all_values[0]
            games_data = all_values[1:]

            idx = self._get_header_indices(header)
            name_idx = idx[FIELD_NAME]

            name_to_row = {}
            name_to_data = {}

            for i, row in enumerate(games_data):
                if len(row) > name_idx:
                    g_name = row[name_idx]
                    name_to_row[g_name] = i + 2
                    name_to_data[g_name] = row

            # 預先載入所有社員以優化保管人查詢 (避免 N+1)
            members = self.client.load_members()
            members_by_name = {str(m.get("name", "")).strip(): m for m in members}

            success_list = []
            fail_list = []
            batch_updates = []
            ts = get_current_timestamp()

            for name in game_names:
                if name not in name_to_row:
                    fail_list.append({"name": name, "reason": "找不到此遊戲"})
                    continue

                row_idx = name_to_row[name]
                row_data = name_to_data[name]

                current_status = row_data[idx[FIELD_STATUS]] if len(row_data) > idx[FIELD_STATUS] else ""
                if current_status != GAME_STATUS_BORROWED:
                    fail_list.append({"name": name, "reason": "此遊戲未被借出"})
                    continue

                success_list.append(name)
                borrower_name = row_data[idx[FIELD_BORROWER]] if len(row_data) > idx[FIELD_BORROWER] else "未知"

                def add_update(r, c, val):
                    batch_updates.append(self.client.create_batch_update(r, c, val))

                add_update(row_idx, idx[FIELD_STATUS], GAME_STATUS_AVAILABLE)
                add_update(row_idx, idx[FIELD_BORROWER], "")  # 先清空
                add_update(row_idx, idx[FIELD_BORROWER_ID], "")
                add_update(row_idx, idx[FIELD_MDATE], ts)

                # History
                existing_history = row_data[idx[FIELD_HISTORY]] if len(row_data) > idx[FIELD_HISTORY] else ""
                history_entry = create_history_entry(borrower_name, "歸還", ts)
                new_history = f"{existing_history} | {history_entry}" if existing_history else history_entry
                add_update(row_idx, idx[FIELD_HISTORY], new_history)

                # Handle Custodian
                if FIELD_CUSTODIAN in idx:
                    custodian = row_data[idx[FIELD_CUSTODIAN]] if len(row_data) > idx[FIELD_CUSTODIAN] else ""
                    if custodian:
                        add_update(row_idx, idx[FIELD_BORROWER], custodian)
                        # 查找保管人 ID
                        custodian_member = members_by_name.get(str(custodian).strip())
                        if custodian_member:
                            add_update(
                                row_idx,
                                idx[FIELD_BORROWER_ID],
                                custodian_member.get("id", ""),
                            )

            if batch_updates:
                ws.batch_update(batch_updates)
                self.client.invalidate_games_cache()

            msg = f"成功歸還 {len(success_list)} 個遊戲"
            if fail_list:
                msg += f"，失敗 {len(fail_list)} 個"

            return True, msg, success_list, fail_list

        except Exception as e:
            return False, f"批次歸還失敗: {e}", [], []

    def return_game(self, name: str) -> Tuple[bool, str]:
        """
        單一歸還 (Wrapper for batch_return_games)
        """
        success, msg, success_list, fail_list = self.batch_return_games([name])

        if success_list:
            return True, f"成功歸還：《{name}》"
        else:
            if fail_list:
                reason = fail_list[0].get("reason", "未知原因")
                return False, f"歸還失敗：{reason}"
            return False, msg

    def batch_return_games_by_member(self, member_id: str) -> Tuple[bool, str, List[str]]:
        """
        歸還某位社員借出的所有遊戲
        """
        if not self.client.valid:
            return False, "系統連線錯誤", []

        try:
            member = self.member_service.find_member_by_id(member_id)
            if not member:
                return False, "找不到社員", []

            member_name = member["name"]
            games = self.client.load_games()

            # 找出該使用者借閱的所有桌遊
            borrowed_games = [
                g for g in games if g.get(FIELD_STATUS) == GAME_STATUS_BORROWED and g.get(FIELD_BORROWER) == member_name
            ]

            if not borrowed_games:
                return False, f"{member_name} 目前沒有借閱任何桌遊", []

            game_names = [g.get(FIELD_NAME) for g in borrowed_games if g.get(FIELD_NAME)]
            # 過濾掉 None 值，確保類型為 List[str]
            game_names_filtered: List[str] = [name for name in game_names if name is not None]
            success, msg, s_list, f_list = self.batch_return_games(game_names_filtered)

            return success, msg, s_list
        except Exception as e:
            return False, f"批次歸還失敗: {e}", []

    def update_game_expansion_info(self, game_name: str, is_expansion: bool, parent_game: str, storage_mode: str) -> bool:
        """更新遊戲的擴充資訊"""
        return self.client.update_game_expansion_info(game_name, is_expansion, parent_game, storage_mode)
