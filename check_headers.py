#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
檢查 Google Sheets 欄位名稱
"""
from core.sheets_client import SheetsClient

def check_headers():
    """檢查欄位"""
    client = SheetsClient()
    
    if not client.valid:
        print("❌ Google Sheets 連線失敗")
        return
    
    try:
        ws = client.get_games_worksheet()
        all_values = ws.get_all_values()
        
        if not all_values:
            print("❌ 無法讀取遊戲列表")
            return
        
        header = all_values[0]
        
        print("📋 Google Sheets 欄位名稱：")
        for i, col in enumerate(header):
            print(f"  [{i}] {repr(col)}")
    
    except Exception as e:
        print(f"❌ 錯誤：{e}")

if __name__ == "__main__":
    check_headers()
