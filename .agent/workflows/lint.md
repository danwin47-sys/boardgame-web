---
description: 檢查並修復程式碼格式
---

# 程式碼品質檢查流程

// turbo-all

1. 進入專案目錄 `c:\python-training\boardgame-web`

2. 使用 autopep8 自動修復格式問題

```bash
autopep8 --in-place --recursive --aggressive app/ core/
```

3. 執行 flake8 檢查

```bash
flake8 app/ core/ --max-line-length=120
```

4. 執行 mypy 類型檢查

```bash
mypy app/ core/ --ignore-missing-imports
```

5. 報告檢查結果，如果有問題則提供修復建議
