#!/bin/bash

# 獲取腳本所在目錄的絕對路徑
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PROJECT_ROOT="$( dirname "$SCRIPT_DIR" )"

cd "$PROJECT_ROOT"

echo "正在產生存放路徑清單 (Digest Manifest)..."

# 確保 FLASK_APP 已設定
export FLASK_APP="app:create_app"

# 執行 flask static digest
python3 -m flask digest compile

if [ $? -eq 0 ]; then
    echo "成功！清單已建立於 static/cache_manifest.json"
else
    echo "失敗：無法產生成清單。"
    exit 1
fi
