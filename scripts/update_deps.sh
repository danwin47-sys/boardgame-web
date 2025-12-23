#!/bin/bash
# 依賴套件更新檢查腳本
# 用途：檢查過期套件和安全性問題

set -e

# 顏色輸出
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

echo -e "${GREEN}🔍 開始檢查依賴套件...${NC}"

# 啟動虛擬環境
if [ -d "venv" ]; then
    source venv/bin/activate
else
    echo -e "${RED}❌ 錯誤: 找不到虛擬環境${NC}"
    exit 1
fi

# 檢查過期套件
echo -e "${YELLOW}📦 檢查過期套件...${NC}"
pip list --outdated

# 安裝 safety（如果未安裝）
if ! command -v safety &> /dev/null; then
    echo -e "${YELLOW}📥 安裝 safety...${NC}"
    pip install safety
fi

# 執行安全性檢查
echo -e "${YELLOW}🔒 執行安全性檢查...${NC}"
safety check || echo -e "${RED}⚠️  發現安全性問題${NC}"

# 顯示當前版本
echo -e "${YELLOW}📋 當前依賴版本:${NC}"
pip freeze

echo -e "${GREEN}✅ 檢查完成!${NC}"
echo -e "${YELLOW}💡 提示: 使用 'pip install --upgrade <package>' 更新套件${NC}"
