import tkinter as tk
from tkinter import ttk
import json
import os

class JsonSpreadsheet:
    def __init__(self, root, json_file="boardgames.json"):
        self.root = root
        self.root.title("桌遊資料庫檢視器 (仿試算表)")
        self.root.geometry("1100x600")
        self.json_file = json_file
        
        # 定義欄位對照 (JSON Key -> 中文標題)
        # 這裡決定了表格的順序與顯示名稱
        self.column_map = {
            "name": "桌遊名稱",
            "status": "狀態",
            "borrower": "借閱人",
            "ext": "分機",
            "email": "Email",
            "location": "位置",
            "difficulty": "難度"
        }
        
        self.load_data()
        self.create_widgets()
        self.populate_table()

    def load_data(self):
        """讀取 JSON 檔案"""
        if not os.path.exists(self.json_file):
            self.data = []
            print(f"錯誤：找不到 {self.json_file}")
            return

        try:
            with open(self.json_file, 'r', encoding='utf-8') as f:
                self.data = json.load(f)
        except Exception as e:
            print(f"讀取錯誤: {e}")
            self.data = []

    def create_widgets(self):
        """建立表格與捲軸"""
        # 建立外框容器
        frame = tk.Frame(self.root)
        frame.pack(fill="both", expand=True, padx=10, pady=10)

        # 設定 Treeview 的欄位 ID
        columns = list(self.column_map.keys())
        
        # 建立 Treeview
        self.tree = ttk.Treeview(frame, columns=columns, show="headings")
        
        # 設定垂直捲軸
        vsb = ttk.Scrollbar(frame, orient="vertical", command=self.tree.yview)
        vsb.pack(side="right", fill="y")
        
        # 設定水平捲軸
        hsb = ttk.Scrollbar(frame, orient="horizontal", command=self.tree.xview)
        hsb.pack(side="bottom", fill="x")
        
        self.tree.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)
        self.tree.pack(fill="both", expand=True)

        # 設定欄位標題與屬性
        for col_key, header_text in self.column_map.items():
            # 1. 設定標題文字，並綁定點擊排序功能
            self.tree.heading(col_key, text=header_text, 
                              command=lambda c=col_key: self.sort_column(c, False))
            
            # 2. 設定欄位寬度 (名稱欄寬一點，其他窄一點)
            width = 250 if col_key == "name" else 100
            anchor = "w" if col_key == "name" or col_key == "email" else "center"
            
            self.tree.column(col_key, width=width, anchor=anchor, minwidth=50)

        # 設定斑馬紋顏色 (奇數行灰色)
        self.tree.tag_configure('oddrow', background='#f0f0f0')
        self.tree.tag_configure('evenrow', background='white')

    def populate_table(self):
        """將資料填入表格"""
        # 清空表格
        for row in self.tree.get_children():
            self.tree.delete(row)
            
        if not self.data:
            return

        count = 0
        for item in self.data:
            # 根據 column_map 的順序抓取值
            values = [item.get(key, "") for key in self.column_map.keys()]
            
            # 判斷單雙行來給予顏色標籤
            tag = 'evenrow' if count % 2 == 0 else 'oddrow'
            
            self.tree.insert("", "end", values=values, tags=(tag,))
            count += 1

    def sort_column(self, col, reverse):
        """點擊標題時進行排序"""
        # 取得該欄所有資料 [(值, ID), (值, ID)...]
        l = [(self.tree.set(k, col), k) for k in self.tree.get_children('')]
        
        # 嘗試將數字字串轉為數字進行排序 (例如難度 3.8)
        try:
            l.sort(key=lambda t: float(t[0]) if t[0] else 0, reverse=reverse)
        except ValueError:
            l.sort(reverse=reverse)

        # 重新排列顯示順序
        for index, (val, k) in enumerate(l):
            self.tree.move(k, '', index)
            # 重新上色斑馬紋
            tag = 'evenrow' if index % 2 == 0 else 'oddrow'
            self.tree.item(k, tags=(tag,))

        # 下次點擊時反向排序
        self.tree.heading(col, command=lambda: self.sort_column(col, not reverse))

if __name__ == "__main__":
    root = tk.Tk()
    app = JsonSpreadsheet(root)
    root.mainloop()