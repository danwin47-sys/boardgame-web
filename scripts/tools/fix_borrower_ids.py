#!/usr/bin/env python3
"""
借閱者 ID 公式設定腳本

功能：
1. 掃描所有桌遊記錄
2. 為 borrower_id 欄位設定 XLOOKUP 公式
3. 公式會自動根據 borrower 欄位查找對應的會員 ID
4. 實現類似 custodian_id 的自動連動功能
5. 輸出設定統計報告

使用方式：
    python scripts/tools/fix_borrower_ids.py [--dry-run]

參數：
    --dry-run: 僅顯示將要設定公式的資料，不實際更新
"""

import sys
import os
from pathlib import Path

# 設定專案根目錄路徑
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

import argparse
import logging
from typing import List, Dict, Tuple

from core.sheets_client import SheetsClient
from core.member_service import MemberService
from core.constants import (
    FIELD_NAME,
    FIELD_BORROWER,
    FIELD_BORROWER_ID,
    FIELD_STATUS,
    GAME_STATUS_BORROWED
)

# 設定日誌
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class BorrowerIdFixer:
    """為 borrower_id 設定 XLOOKUP 公式"""
    
    def __init__(self, dry_run: bool = False):
        self.dry_run = dry_run
        self.client = SheetsClient()
        self.member_service = MemberService(self.client)
        
        # 統計資訊
        self.total_games = 0
        self.borrowed_games = 0
        self.formula_set_count = 0
        self.errors: List[Dict] = []
        
    @staticmethod
    def col_index_to_letter(col_idx: int) -> str:
        """將欄位索引轉換為 Excel 列字母 (0-based -> A, 1 -> B, ...)"""
        letters = ''
        col_idx += 1  # Excel 列從 1 開始
        while col_idx > 0:
            col_idx -= 1
            letters = chr(col_idx % 26 + ord('A')) + letters
            col_idx //= 26
        return letters
    
    def create_formula(self, row: int, borrower_col_idx: int) -> str:
        """建立 XLOOKUP 公式"""
        col_letter = self.col_index_to_letter(borrower_col_idx)
        # 使用 IFERROR 包裹 XLOOKUP，避免找不到會員時顯示錯誤
        # members 工作表：A 欄 = 姓名，C 欄 = ID
        formula = f'=IFERROR(XLOOKUP({col_letter}{row},members!$A$2:$A$100,members!$C$2:$C$100),"")'
        return formula
    
    def scan_games(self) -> List[Tuple[int, Dict]]:
        """
        掃描所有桌遊，準備設定公式
        
        Returns:
            List of (row_number, game_data) tuples
        """
        logger.info("掃描桌遊資料...")
        
        ws = self.client.get_games_worksheet()
        all_values = ws.get_all_values()
        
        if not all_values:
            logger.error("無法讀取桌遊資料")
            return []
        
        header = all_values[0]
        games_data = all_values[1:]
        
        # 找出欄位索引
        try:
            name_idx = header.index(FIELD_NAME)
            status_idx = header.index(FIELD_STATUS)
            borrower_idx = header.index(FIELD_BORROWER)
            borrower_id_idx = header.index(FIELD_BORROWER_ID)
        except ValueError as e:
            logger.error(f"找不到必要欄位: {e}")
            return []
        
        to_process = []
        self.total_games = len(games_data)
        
        for i, row in enumerate(games_data):
            row_number = i + 2  # +2 because header is row 1, and index starts at 0
            
            # 確保 row 有足夠的欄位
            if len(row) <= max(name_idx, status_idx, borrower_idx, borrower_id_idx):
                continue
            
            game_name = row[name_idx] if len(row) > name_idx else ''
            status = row[status_idx] if len(row) > status_idx else ''
            
            # 統計借出的桌遊
            if status == GAME_STATUS_BORROWED:
                self.borrowed_games += 1
            
            # 處理所有桌遊（設定公式）
            to_process.append((row_number, {
                'name': game_name,
                'status': status,
                'borrower_idx': borrower_idx,
                'borrower_id_idx': borrower_id_idx
            }))
        
        logger.info(f"共掃描 {self.total_games} 款桌遊")
        logger.info(f"其中 {self.borrowed_games } 款處於借出狀態")
        logger.info(f"將為所有桌遊設定 borrower_id 公式")
        
        return to_process
    
    def set_formulas(self, to_process: List[Tuple[int, Dict]]):
        """為所有記錄設定公式"""
        
        if not to_process:
            logger.info("沒有需要處理的記錄")
            return
        
        if self.dry_run:
            logger.info("\n[DRY RUN 模式] 以下儲存格將設定公式：")
            logger.info("-" * 80)
        
        ws = self.client.get_games_worksheet()
        batch_updates = []
        
        for row_number, game_data in to_process:
            game_name = game_data['name']
            borrower_idx = game_data['borrower_idx']
            borrower_id_idx = game_data['borrower_id_idx']
            
            # 生成公式
            formula = self.create_formula(row_number, borrower_idx)
            
            if self.dry_run:
                logger.info(f"  第 {row_number} 行 | 桌遊: {game_name:30s} | 公式: {formula}")
            else:
                # 建立更新請求
                update_request = self.client.create_batch_update(
                    row_number,
                    borrower_id_idx,
                    formula
                )
                batch_updates.append(update_request)
            
            self.formula_set_count += 1
        
        # 執行批次更新
        if not self.dry_run and batch_updates:
            logger.info(f"\n正在設定 {len(batch_updates)} 個公式...")
            try:
                ws.batch_update(batch_updates)
                self.client.invalidate_games_cache()
                logger.info("✅ [成功] 公式設定完成！")
            except Exception as e:
                logger.error(f"❌ 更新失敗: {e}")
                raise
    
    def print_summary(self):
        """列印統計摘要"""
        logger.info("\n" + "=" * 80)
        logger.info("公式設定統計摘要" )
        logger.info("=" * 80)
        logger.info(f"掃描桌遊總數：      {self.total_games}")
        logger.info(f"借出狀態桌遊：      {self.borrowed_games}")
        logger.info(f"已設定公式數：      {self.formula_set_count}")
        
        if self.errors:
            logger.warning(f"\n處理失敗的記錄 ({len(self.errors)} 筆)：")
            for error in self.errors[:10]:  # 只顯示前 10 筆
                logger.warning(f"  - 第 {error['row']} 行: {error['game']} ({error['reason']})")
            
            if len(self.errors) > 10:
                logger.warning(f"  ... 還有 {len(self.errors) - 10} 筆")
        
        logger.info("=" * 80)
        
        if self.dry_run:
            logger.info("\n[提示] 這是 DRY RUN 模式，實際資料未被修改")
            logger.info("       若要執行設定，請移除 --dry-run 參數")
        else:
            logger.info("\n[完成] borrower_id 欄位現在會自動根據 borrower 欄位更新會員 ID")
    
    def run(self):
        """執行公式設定流程"""
        try:
            # 檢查連線
            if not self.client.valid:
                logger.error("[失敗] Google Sheets 連線失敗")
                return False
            
            logger.info("✅ [成功] Google Sheets 連線成功")
            
            # 掃描需要處理的記錄
            to_process = self.scan_games()
            
            # 設定公式
            self.set_formulas(to_process)
            
            # 列印摘要
            self.print_summary()
            
            return True
            
        except Exception as e:
            logger.error(f"[失敗] 執行失敗: {e}", exc_info=True)
            return False


def main():
    """主程式入口"""
    parser = argparse.ArgumentParser(
        description='為 Google Sheets 的 borrower_id 欄位設定 XLOOKUP 公式'
    )
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='僅顯示將要設定的公式，不實際更新'
    )
    
    args = parser.parse_args()
    
    logger.info("=" * 80)
    logger.info("借閱者 ID 公式設定腳本")
    logger.info("=" * 80)
    
    if args.dry_run:
        logger.info("模式：DRY RUN (不會修改資料)")
    else:
        logger.info("模式：執行公式設定")
        response = input("\n[警告] 即將為所有桌遊的 borrower_id 欄位設定 XLOOKUP 公式，是否繼續？ (y/n): ")
        if response.lower() != 'y':
            logger.info("已取消")
            return
    
    logger.info("")
    
    fixer = BorrowerIdFixer(dry_run=args.dry_run)
    success = fixer.run()
    
    sys.exit(0 if success else 1)


if __name__ == '__main__':
    main()
