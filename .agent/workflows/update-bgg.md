---
description: 更新 BGG 排名資料庫和快取
---

# 更新 BGG 資料流程

// turbo-all

1. 進入專案目錄 `c:\python-training\boardgame-web`

2. 更新 BGG 排名資料庫

```bash
python scripts/update/update_bgg_ranks.py
```

3. 更新推薦遊戲資料

```bash
python scripts/update/update_recommendations.py
```

4. 清除過期快取

```bash
python scripts/update/clear_cache.py
```

5. 報告更新結果，包含：
   - 更新的遊戲數量
   - 是否有錯誤發生
   - 建議的下次更新時間
