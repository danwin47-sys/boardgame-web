#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
除錯腳本：檢查特定遊戲的資料
"""
import sys
from core.sheets_client import SheetsClient

def debug_game(search_name):
    """檢查遊戲資料"""
    client = SheetsClient()
    
    if not client.valid:
        print("❌ Google Sheets 連線失敗")
        return
    
    print(f"🔍 搜尋遊戲：{search_name}\n")
    
    # 獲取所有遊戲
    try:
        ws = client.get_games_worksheet()
        all_values = ws.get_all_values()
        
        if not all_values:
            print("❌ 無法讀取遊戲列表")
            return
        
        header = all_values[0]
        games_data = all_values[1:]
        
        print("📋 試算表欄位：")
        for i, col in enumerate(header):
            print(f"  [{i}] {col}")
        print()
        
        # 搜尋遊戲
        found_games = []
        for row_idx, row in enumerate(games_data, start=2):
            if len(row) > 0 and search_name.lower() in row[0].lower():
                found_games.append((row_idx, row))
        
        if not found_games:
            print(f"❌ 找不到包含「{search_name}」的遊戲")
            print("\n💡 建議：")
            print("  1. 檢查遊戲名稱拼寫")
            print("  2. 嘗試使用部分關鍵字搜尋")
            return
        
        print(f"✅ 找到 {len(found_games)} 個匹配的遊戲：\n")
        
        for row_idx, row in found_games:
            print(f"{'='*80}")
            print(f"遊戲名稱：{row[0] if len(row) > 0 else '(空)'}")
            print(f"工作表行號：{row_idx}")
            print(f"\n完整資料：")
            for i, (col_name, value) in enumerate(zip(header, row)):
                if value:  # 只顯示有值的欄位
                    print(f"  {col_name}: {repr(value)}")
            print()
            
            # 特別檢查狀態欄位
            status_idx = header.index('狀態') if '狀態' in header else None
            if status_idx is not None and len(row) > status_idx:
                status = row[status_idx]
                print(f"⚠️ 狀態欄位詳情：")
                print(f"  值: {repr(status)}")
                print(f"  類型: {type(status)}")
                print(f"  長度: {len(status)}")
                print(f"  是否為「借出」: {status == '借出'}")
                print(f"  是否為「在庫」: {status == '在庫'}")
                
                # 檢查是否有隱藏字元
                if status:
                    print(f"  字元碼: {[ord(c) for c in status]}")
    
    except Exception as e:
        print(f"❌ 錯誤：{e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    search = sys.argv[1] if len(sys.argv) > 1 else "工業革命"
    debug_game(search)
