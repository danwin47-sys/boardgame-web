# coding: utf-8
"""
擴充管理服務模組
處理桌遊擴充的相關邏輯，包含合併收納與獨立收納模式
"""
from typing import List, Dict, Optional, Tuple, Any
from .constants import (
    FIELD_NAME,
    FIELD_IS_EXPANSION,
    FIELD_PARENT_GAME,
    FIELD_STORAGE_MODE,
    FIELD_STATUS,
    STORAGE_MODE_MERGED,
    STORAGE_MODE_INDEPENDENT,
    GAME_STATUS_BORROWED
)


class ExpansionService:
    """擴充管理服務"""
    
    def __init__(self, sheets_client):
        """
        初始化擴充服務
        
        Args:
            sheets_client: Google Sheets 客戶端
        """
        self.client = sheets_client
    
    def get_expansions(self, parent_game_name: str, all_games: List[Dict]) -> List[Dict]:
        """
        取得主遊戲的所有擴充
        
        Args:
            parent_game_name: 主遊戲名稱
            all_games: 所有遊戲列表
            
        Returns:
            擴充遊戲列表
        """
        expansions = []
        for game in all_games:
            is_expansion = str(game.get(FIELD_IS_EXPANSION, '')).strip()
            parent = str(game.get(FIELD_PARENT_GAME, '')).strip()
            
            # 檢查是否為此主遊戲的擴充
            if is_expansion in ('1', 'TRUE', 'True', 'true') and parent == parent_game_name:
                expansions.append(game)
        
        return expansions
    
    def get_parent_game(self, expansion_name: str, all_games: List[Dict]) -> Optional[Dict]:
        """
        取得擴充的主遊戲
        
        Args:
            expansion_name: 擴充名稱
            all_games: 所有遊戲列表
            
        Returns:
            主遊戲資料，如果不是擴充則返回 None
        """
        # 先找到擴充本身
        expansion = None
        for game in all_games:
            if game.get(FIELD_NAME) == expansion_name:
                expansion = game
                break
        
        if not expansion:
            return None
        
        # 檢查是否為擴充
        is_expansion = str(expansion.get(FIELD_IS_EXPANSION, '')).strip()
        if is_expansion not in ('1', 'TRUE', 'True', 'true'):
            return None
        
        # 找主遊戲
        parent_name = expansion.get(FIELD_PARENT_GAME, '').strip()
        if not parent_name:
            return None
        
        for game in all_games:
            if game.get(FIELD_NAME) == parent_name:
                return game
        
        return None
    
    def get_game_family(self, game_name: str, all_games: List[Dict]) -> Dict[str, Any]:
        """
        取得遊戲家族（主遊戲 + 所有擴充）
        
        Args:
            game_name: 遊戲名稱
            all_games: 所有遊戲列表
            
        Returns:
            包含 parent (主遊戲) 和 expansions (擴充列表) 的字典
        """
        # 找到遊戲本身
        target_game = None
        for game in all_games:
            if game.get(FIELD_NAME) == game_name:
                target_game = game
                break
        
        if not target_game:
            return {'parent': None, 'expansions': []}
        
        # 檢查是否為擴充
        is_expansion = str(target_game.get(FIELD_IS_EXPANSION, '')).strip()
        
        if is_expansion in ('1', 'TRUE', 'True', 'true'):
            # 如果是擴充，找主遊戲
            parent = self.get_parent_game(game_name, all_games)
            if parent:
                parent_name = parent.get(FIELD_NAME)
                if parent_name:
                    expansions = self.get_expansions(parent_name, all_games)
                    return {'parent': parent, 'expansions': expansions}
            return {'parent': None, 'expansions': []}
        else:
            # 如果是主遊戲，找所有擴充
            expansions = self.get_expansions(game_name, all_games)
            return {'parent': target_game, 'expansions': expansions}
    
    def get_merged_expansions(self, parent_game_name: str, all_games: List[Dict]) -> List[Dict]:
        """
        取得主遊戲的所有「合併收納」擴充
        
        Args:
            parent_game_name: 主遊戲名稱
            all_games: 所有遊戲列表
            
        Returns:
            合併收納的擴充列表
        """
        all_expansions = self.get_expansions(parent_game_name, all_games)
        merged_expansions = []
        
        for exp in all_expansions:
            storage_mode = exp.get(FIELD_STORAGE_MODE, '').strip()
            if storage_mode == STORAGE_MODE_MERGED:
                merged_expansions.append(exp)
        
        return merged_expansions
    
    def validate_borrow(self, game_name: str, all_games: List[Dict]) -> Tuple[bool, str, Optional[Dict]]:
        """
        驗證借出操作（檢查擴充依賴）
        
        Args:
            game_name: 要借出的遊戲名稱
            all_games: 所有遊戲列表
            
        Returns:
            (是否可借出, 提示訊息, 相關資訊)
        """
        # 找到遊戲
        target_game = None
        for game in all_games:
            if game.get(FIELD_NAME) == game_name:
                target_game = game
                break
        
        if not target_game:
            return (False, f"找不到遊戲「{game_name}」", None)
        
        # 檢查是否為擴充
        is_expansion = str(target_game.get(FIELD_IS_EXPANSION, '')).strip()
        
        if is_expansion in ('1', 'TRUE', 'True', 'true'):
            # 如果是擴充，檢查主遊戲狀態
            parent = self.get_parent_game(game_name, all_games)
            
            if not parent:
                return (True, f"警告：擴充「{game_name}」未連結到主遊戲", None)
            
            parent_status = parent.get(FIELD_STATUS, '')
            parent_name = parent.get(FIELD_NAME, '')
            
            # 檢查收納模式
            storage_mode = target_game.get(FIELD_STORAGE_MODE, '').strip()
            
            if storage_mode == STORAGE_MODE_INDEPENDENT:
                # 獨立收納：提示需要主遊戲
                if parent_status == GAME_STATUS_BORROWED:
                    return (True, f"提示：此為擴充，主遊戲「{parent_name}」已被借出", 
                           {'parent': parent, 'parent_borrowed': True})
                else:
                    return (True, f"提示：此為擴充，需要主遊戲「{parent_name}」", 
                           {'parent': parent, 'parent_borrowed': False})
            else:
                # 合併收納：不應單獨借出
                return (False, f"此擴充為合併收納模式，請借出主遊戲「{parent_name}」", 
                       {'parent': parent})
        else:
            # 如果是主遊戲，檢查是否有合併收納的擴充
            merged_expansions = self.get_merged_expansions(game_name, all_games)
            
            if merged_expansions:
                exp_names = [exp.get(FIELD_NAME) for exp in merged_expansions]
                exp_names_filtered = [name for name in exp_names if name]
                return (True, f"將同時借出合併收納的擴充：{', '.join(exp_names_filtered)}", 
                       {'merged_expansions': merged_expansions})
            else:
                return (True, "", None)
    
    def auto_link_expansions(self, parent_game_name: str, expansion_names: List[str], 
                            all_games: List[Dict]) -> List[str]:
        """
        自動連結主遊戲與擴充（根據名稱模糊匹配）
        
        Args:
            parent_game_name: 主遊戲名稱
            expansion_names: 可能的擴充名稱列表
            all_games: 所有遊戲列表
            
        Returns:
            成功連結的擴充名稱列表
        """
        linked = []
        
        for exp_name in expansion_names:
            # 檢查擴充名稱是否包含主遊戲名稱
            if parent_game_name in exp_name and exp_name != parent_game_name:
                # 檢查遊戲是否存在
                for game in all_games:
                    if game.get(FIELD_NAME) == exp_name:
                        linked.append(exp_name)
                        break
        
        return linked
