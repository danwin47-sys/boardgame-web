---
description: 提交變更並推送到 GitHub
---

# 部署流程

1. 檢查 Git 狀態

```bash
git status
```

2. 如果有未提交的變更，詢問用戶是否要提交

3. 暫存所有變更

```bash
git add .
```

4. 請用戶提供 commit 訊息，或根據變更內容自動生成適當的中文 commit 訊息

5. 提交變更

```bash
git commit -m "<commit訊息>"
```

6. 推送到遠端

```bash
git push
```

7. 確認推送成功並報告結果
