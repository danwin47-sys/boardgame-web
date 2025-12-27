#!/bin/bash
# 本地 CI/CD 檢查腳本
# 在推送到 GitHub 前執行此腳本，確保通過所有檢查

set -e  # 遇到錯誤立即停止

echo "🚀 開始本地 CI/CD 檢查..."
echo ""

# 啟動虛擬環境
if [ -d "venv" ]; then
    source venv/bin/activate
    echo "✅ 虛擬環境已啟動"
else
    echo "⚠️  警告：找不到 venv 目錄，使用系統 Python"
fi
echo ""


# 顏色定義
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# 檢查結果追蹤
CHECKS_PASSED=0
CHECKS_FAILED=0

# 函數：執行檢查
run_check() {
    local check_name=$1
    local check_command=$2
    
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo "📋 檢查: $check_name"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    
    if eval "$check_command"; then
        echo -e "${GREEN}✅ $check_name - 通過${NC}"
        ((CHECKS_PASSED++))
    else
        echo -e "${RED}❌ $check_name - 失敗${NC}"
        ((CHECKS_FAILED++))
        return 1
    fi
    echo ""
}

# 1. Flake8 程式碼品質檢查
run_check "Flake8 程式碼品質" \
    "flake8 app/ core/ --count --select=E9,F63,F7,F82 --show-source --statistics" || true

# 2. Flake8 完整檢查（警告）
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "📋 檢查: Flake8 完整檢查（僅警告）"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
flake8 app/ core/ --count --statistics || echo -e "${YELLOW}⚠️  有一些程式碼風格警告，但不影響推送${NC}"
echo ""

# 3. Pytest 測試
run_check "Pytest 單元測試" \
    "pytest tests/ -v --tb=short -x" || true

# 4. 檢查是否有未追蹤的大檔案
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "📋 檢查: 大檔案檢查"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
LARGE_FILES=$(find . -type f -size +1M -not -path "*/\.*" -not -path "*/venv/*" -not -path "*/node_modules/*" 2>/dev/null || true)
if [ -z "$LARGE_FILES" ]; then
    echo -e "${GREEN}✅ 大檔案檢查 - 通過（無大於 1MB 的檔案）${NC}"
    ((CHECKS_PASSED++))
else
    echo -e "${YELLOW}⚠️  發現大檔案：${NC}"
    echo "$LARGE_FILES"
    echo -e "${YELLOW}請確認這些檔案是否需要加入 .gitignore${NC}"
fi
echo ""

# 5. 檢查敏感資料
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "📋 檢查: 敏感資料檢查"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
if git diff --cached --name-only | grep -q "\.env$"; then
    echo -e "${RED}❌ 警告：.env 檔案即將被提交！${NC}"
    echo -e "${RED}   .env 包含敏感資料，不應上傳到 GitHub${NC}"
    ((CHECKS_FAILED++))
else
    echo -e "${GREEN}✅ 敏感資料檢查 - 通過${NC}"
    ((CHECKS_PASSED++))
fi
echo ""

# 總結
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "📊 檢查總結"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo -e "${GREEN}✅ 通過: $CHECKS_PASSED${NC}"
echo -e "${RED}❌ 失敗: $CHECKS_FAILED${NC}"
echo ""

if [ $CHECKS_FAILED -eq 0 ]; then
    echo -e "${GREEN}🎉 所有檢查通過！可以安全推送到 GitHub${NC}"
    echo ""
    echo "執行以下指令推送："
    echo "  git push"
    exit 0
else
    echo -e "${RED}⚠️  有 $CHECKS_FAILED 項檢查失敗，請修復後再推送${NC}"
    exit 1
fi
