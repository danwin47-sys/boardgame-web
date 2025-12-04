# 桌遊館藏系統啟動腳本（修正版）
# 設定所有必要的環境變數並啟動應用程式
# Google Sheets 設定
# 注意：不設定 GOOGLE_CREDENTIALS，讓程式自動使用本地憑證檔案
$env:SHEET_URL = "https://docs.google.com/spreadsheets/d/1n2cCI1glkErCq835kNJD5hXyk1iR7IptPlnKKPm0_0Y/edit?gid=0#gid=0"

# 機密資訊：請從 .env 檔案讀取或手動設定
if (-not $env:BGG_API_TOKEN) {
    Write-Host "警告: BGG_API_TOKEN 未設定，BGG 功能可能無法使用" -ForegroundColor Yellow
}
if (-not $env:ADMIN_PASSWORD) {
    Write-Host "警告: ADMIN_PASSWORD 未設定，管理員登入將無法使用" -ForegroundColor Yellow
    Write-Host "請設定: `$env:ADMIN_PASSWORD = 'your_password'" -ForegroundColor Yellow
}

$env:DEMO_MODE = "False"

# 伺服器設定
$env:PORT = "5000"
$env:HOST = "0.0.0.0"

Write-Host "環境變數已設定：" -ForegroundColor Green
Write-Host "  - SHEET_URL: 已設定" -ForegroundColor Yellow
Write-Host "  - 憑證檔案: 使用本地 boardgame-bot-5f6751855184.json" -ForegroundColor Yellow
Write-Host "  - BGG_API_TOKEN: 已設定" -ForegroundColor Yellow
Write-Host "  - DEMO_MODE: $env:DEMO_MODE" -ForegroundColor Yellow
Write-Host ""

Write-Host "正在啟動 Flask 應用程式..." -ForegroundColor Cyan
Write-Host "訪問 http://localhost:5000 查看桌遊清單" -ForegroundColor Green
Write-Host ""

# 啟動 Flask
# 啟動 Waitress Server
python serve.py
