#!/bin/bash
# 資料庫備份腳本
# 用途：定期備份 SQLite 資料庫

set -e  # 遇到錯誤立即退出

# 配置
DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_DIR="data/backups"
DB_PATH="data/bgg_ranks/bgg_ranks.db"
RETENTION_DAYS=30

# 顏色輸出
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${GREEN}🔄 開始資料庫備份...${NC}"

# 建立備份目錄
mkdir -p "$BACKUP_DIR"

# 檢查資料庫是否存在
if [ ! -f "$DB_PATH" ]; then
    echo -e "${RED}❌ 錯誤: 資料庫檔案不存在: $DB_PATH${NC}"
    exit 1
fi

# 執行備份
BACKUP_FILE="$BACKUP_DIR/bgg_ranks_$DATE.db"
echo -e "${YELLOW}📦 備份到: $BACKUP_FILE${NC}"

sqlite3 "$DB_PATH" ".backup '$BACKUP_FILE'"

# 檢查備份是否成功
if [ -f "$BACKUP_FILE" ]; then
    BACKUP_SIZE=$(du -h "$BACKUP_FILE" | cut -f1)
    echo -e "${GREEN}✅ 備份成功! 大小: $BACKUP_SIZE${NC}"
else
    echo -e "${RED}❌ 備份失敗!${NC}"
    exit 1
fi

# 清理舊備份（保留最近 30 天）
echo -e "${YELLOW}🧹 清理 $RETENTION_DAYS 天前的舊備份...${NC}"
DELETED_COUNT=$(find "$BACKUP_DIR" -name "bgg_ranks_*.db" -mtime +$RETENTION_DAYS -delete -print | wc -l)

if [ "$DELETED_COUNT" -gt 0 ]; then
    echo -e "${GREEN}✅ 已刪除 $DELETED_COUNT 個舊備份${NC}"
else
    echo -e "${YELLOW}ℹ️  沒有需要清理的舊備份${NC}"
fi

# 列出當前所有備份
echo -e "${YELLOW}📋 當前備份列表:${NC}"
ls -lh "$BACKUP_DIR"/bgg_ranks_*.db 2>/dev/null || echo "  (無備份檔案)"

echo -e "${GREEN}🎉 備份完成! 時間: $(date)${NC}"
