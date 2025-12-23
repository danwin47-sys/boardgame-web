#!/bin/bash
# 健康檢查腳本
# 用途：檢查服務是否正常運行

set -e

# 配置
HOST="localhost"
PORT="5001"
BASE_URL="http://$HOST:$PORT"

# 顏色輸出
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

echo -e "${GREEN}🏥 開始健康檢查...${NC}"

# 檢查服務是否運行
echo -e "${YELLOW}🔍 檢查服務狀態...${NC}"
if curl -f -s "$BASE_URL/health" > /dev/null; then
    echo -e "${GREEN}✅ 健康檢查端點正常${NC}"
else
    echo -e "${RED}❌ 健康檢查端點失敗${NC}"
    exit 1
fi

# 檢查主要 API
echo -e "${YELLOW}🔍 檢查 API 端點...${NC}"
if curl -f -s "$BASE_URL/api/games" > /dev/null; then
    echo -e "${GREEN}✅ Games API 正常${NC}"
else
    echo -e "${RED}❌ Games API 失敗${NC}"
    exit 1
fi

# 檢查系統資訊
echo -e "${YELLOW}🔍 檢查系統資訊...${NC}"
if curl -f -s "$BASE_URL/api/sys_info" > /dev/null; then
    echo -e "${GREEN}✅ System Info API 正常${NC}"
else
    echo -e "${RED}❌ System Info API 失敗${NC}"
    exit 1
fi

# 檢查 Metrics
echo -e "${YELLOW}🔍 檢查 Metrics...${NC}"
if curl -f -s "$BASE_URL/api/metrics/summary" > /dev/null; then
    echo -e "${GREEN}✅ Metrics API 正常${NC}"
else
    echo -e "${YELLOW}⚠️  Metrics API 無回應（可能正常）${NC}"
fi

echo -e "${GREEN}🎉 所有檢查通過!${NC}"
