#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
同步 Google Sheets 狀態欄位
將「歸還」改為「在庫」
"""
from core.sheets_client import SheetsClient


def sync_status():
    """同步狀態欄位"""
    client = SheetsClient()

    if not client.valid:
        print("❌ Google Sheets 連線失敗")
        return

    print("🔄 開始同步 Google Sheets 狀態欄位...")
    print()

    try:
        ws = client.get_games_worksheet()
        all_values = ws.get_all_values()

        if not all_values:
            print("❌ 無法讀取遊戲列表")
            return

        header = all_values[0]
        games_data = all_values[1:]

        # 找到狀態欄位索引
        try:
            status_idx = header.index("status")
        except ValueError:
            print("❌ 找不到「status」欄位")
            return

        print(f"📋 找到狀態欄位在第 {status_idx + 1} 欄")
        print()

        # 統計
        total_games = len(games_data)
        updated_count = 0
        borrowed_count = 0
        batch_updates = []

        print("🔍 掃描遊戲狀態...")
        for i, row in enumerate(games_data, start=2):
            if len(row) <= status_idx:
                continue

            current_status = row[status_idx]

            # 將「歸還」改為「在庫」
            if current_status == "歸還":
                batch_updates.append(client.create_batch_update(i, status_idx, "在庫"))
                updated_count += 1
                if updated_count <= 5:  # 只顯示前5個
                    game_name = row[0] if len(row) > 0 else "(無名稱)"
                    print(f"  [{i-1}] {game_name}: 「歸還」→「在庫」")
            elif current_status == "借出":
                borrowed_count += 1

        if updated_count > 5:
            print(f"  ... 還有 {updated_count - 5} 個遊戲需要更新")

        print()
        print(f"📊 統計：")
        print(f"  - 總遊戲數: {total_games}")
        print(f"  - 需要更新: {updated_count} (歸還 → 在庫)")
        print(f"  - 借出狀態: {borrowed_count} (保持不變)")
        print(f"  - 已是在庫: {total_games - updated_count - borrowed_count}")
        print()

        if batch_updates:
            confirm = input(f"❓ 確定要更新 {updated_count} 筆資料嗎？(y/N): ")
            if confirm.lower() == "y":
                print("⏳ 正在更新...")
                ws.batch_update(batch_updates)
                client.invalidate_games_cache()
                print("✅ 更新完成！")
                print("💡 請重新整理網頁以查看最新狀態")
            else:
                print("❌ 已取消更新")
        else:
            print("✅ 所有狀態欄位已經是最新的，無需更新！")

    except Exception as e:
        print(f"❌ 錯誤：{e}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    sync_status()
