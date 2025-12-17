"""
新增 update_game_playtime 方法到 SheetsClient
用於將 BGG 遊戲時間寫回 Google Sheets
"""

def update_game_playtime(self, game_name: str, min_playtime: int, max_playtime: int) -> bool:
    """更新遊戲的遊玩時間到 Google Sheets
    
    Args:
        game_name: 遊戲名稱
        min_playtime: 最小遊玩時間（分鐘）
        max_playtime: 最大遊玩時間（分鐘）
    
    Returns:
        bool: 更新成功返回 True，失敗返回 False
    """
    try:
        ws = self.get_games_worksheet()
        if not ws:
            return False
        
        # 取得所有資料
        all_data = ws.get_all_values()
        if not all_data:
            return False
        
        headers = all_data[0]
        
        # 找到欄位索引
        def get_or_create_col(col_name: str) -> int:
            if col_name in headers:
                return headers.index(col_name)
            else:
                # 新增欄位到最後
                headers.append(col_name)
                ws.update_cell(1, len(headers), col_name)
                return len(headers) - 1
        
        name_idx = headers.index('name') if 'name' in headers else 0
        minplaytime_idx = get_or_create_col('minplaytime')
        maxplaytime_idx = get_or_create_col('maxplaytime')
        
        # 找到遊戲所在的行
        for row_idx, row in enumerate(all_data[1:], start=2):
            if len(row) > name_idx and row[name_idx] == game_name:
                # 更新遊玩時間
                ws.update_cell(row_idx, minplaytime_idx + 1, min_playtime)
                ws.update_cell(row_idx, maxplaytime_idx + 1, max_playtime)
                logger.info(f"已更新 '{game_name}' 的遊玩時間: {min_playtime}-{max_playtime}分鐘")
                return True
        
        logger.warning(f"找不到遊戲: {game_name}")
        return False
        
    except Exception as e:
        logger.error(f"更新遊戲時間失敗: {e}", exc_info=True)
        return False
