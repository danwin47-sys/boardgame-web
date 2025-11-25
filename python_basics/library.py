import tkinter as tk
from tkinter import ttk, messagebox
import json
import os

class LibraryManager:
    def __init__(self, filename="library_data.json"):
        self.filename = filename
        self.books = self.load_data()

    def load_data(self):
        if not os.path.exists(self.filename):
            return [
                {"isbn": "001", "title": "哈利波特", "is_borrowed": False, "borrower": ""},
                {"isbn": "002", "title": "Python入門", "is_borrowed": False, "borrower": ""},
                {"isbn": "003", "title": "原子習慣", "is_borrowed": False, "borrower": ""},
            ]
        try:
            with open(self.filename, 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            return []

    def save_data(self):
        try:
            with open(self.filename, 'w', encoding='utf-8') as f:
                json.dump(self.books, f, ensure_ascii=False, indent=4)
        except Exception as e:
            messagebox.showerror("錯誤", f"存檔失敗: {e}")

    def add_book(self, isbn, title):
        for book in self.books:
            if book['isbn'] == isbn:
                return False, "ID 已存在！"
        self.books.append({"isbn": isbn, "title": title, "is_borrowed": False, "borrower": ""})
        self.save_data()
        return True, f"成功新增：《{title}》"

    def borrow_book(self, isbn, user):
        for book in self.books:
            if book['isbn'] == isbn:
                if book['is_borrowed']:
                    return False, f"已被 {book['borrower']} 借出。"
                book['is_borrowed'] = True
                book['borrower'] = user
                self.save_data()
                return True, f"成功借閱：《{book['title']}》"
        return False, "找不到此 ID。"

    def return_book(self, isbn):
        for book in self.books:
            if book['isbn'] == isbn:
                if not book['is_borrowed']:
                    return False, "此書未被借出。"
                book['is_borrowed'] = False
                book['borrower'] = ""
                self.save_data()
                return True, f"成功歸還：《{book['title']}》"
        return False, "找不到此 ID。"

class LibraryApp:
    def __init__(self, root):
        self.root = root
        self.root.title("圖書借還系統")
        self.root.geometry("600x450")
        self.manager = LibraryManager()
        self.create_widgets()
        self.refresh_list()

    def create_widgets(self):
        # 操作區
        frame_input = tk.LabelFrame(self.root, text="操作區", padx=10, pady=10)
        frame_input.pack(fill="x", padx=10, pady=5)

        tk.Label(frame_input, text="編號(ID):").grid(row=0, column=0, sticky="e")
        self.ent_isbn = tk.Entry(frame_input, width=15)
        self.ent_isbn.grid(row=0, column=1, padx=5)

        tk.Label(frame_input, text="書名:").grid(row=0, column=2, sticky="e")
        self.ent_title = tk.Entry(frame_input, width=15)
        self.ent_title.grid(row=0, column=3, padx=5)

        tk.Label(frame_input, text="借閱人:").grid(row=1, column=0, sticky="e")
        self.ent_user = tk.Entry(frame_input, width=15)
        self.ent_user.grid(row=1, column=1, padx=5)

        # 按鈕
        frame_btn = tk.Frame(frame_input)
        frame_btn.grid(row=2, column=0, columnspan=4, pady=10)
        tk.Button(frame_btn, text="新增", command=self.add, bg="#def").pack(side="left", padx=5)
        tk.Button(frame_btn, text="借書", command=self.borrow, bg="#dfd").pack(side="left", padx=5)
        tk.Button(frame_btn, text="還書", command=self.ret, bg="#fdd").pack(side="left", padx=5)

        # 列表區
        self.tree = ttk.Treeview(self.root, columns=("id", "title", "status", "user"), show="headings")
        self.tree.heading("id", text="ID"); self.tree.column("id", width=60, anchor="center")
        self.tree.heading("title", text="書名"); self.tree.column("title", width=200)
        self.tree.heading("status", text="狀態"); self.tree.column("status", width=80, anchor="center")
        self.tree.heading("user", text="借閱人"); self.tree.column("user", width=100, anchor="center")
        self.tree.pack(fill="both", expand=True, padx=10, pady=5)
        self.tree.bind("<<TreeviewSelect>>", self.on_select)

    def refresh_list(self):
        for row in self.tree.get_children(): self.tree.delete(row)
        for b in self.manager.books:
            status = "已借出" if b['is_borrowed'] else "可借閱"
            self.tree.insert("", "end", values=(b['isbn'], b['title'], status, b['borrower']))

    def on_select(self, e):
        sel = self.tree.selection()
        if sel:
            val = self.tree.item(sel)['values']
            self.ent_isbn.delete(0, tk.END); self.ent_isbn.insert(0, val[0])

    def add(self):
        if self.manager.add_book(self.ent_isbn.get(), self.ent_title.get())[0]:
            self.refresh_list(); self.ent_title.delete(0, tk.END)
        else: messagebox.showwarning("提示", "ID重複或欄位為空")

    def borrow(self):
        res, msg = self.manager.borrow_book(self.ent_isbn.get(), self.ent_user.get())
        if res: self.refresh_list(); self.ent_user.delete(0, tk.END); messagebox.showinfo("成功", msg)
        else: messagebox.showwarning("失敗", msg)

    def ret(self):
        res, msg = self.manager.return_book(self.ent_isbn.get())
        if res: self.refresh_list(); messagebox.showinfo("成功", msg)
        else: messagebox.showwarning("失敗", msg)

if __name__ == "__main__":
    root = tk.Tk()
    LibraryApp(root)
    root.mainloop()