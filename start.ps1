# 桌遊館藏系統啟動腳本（修正版）
# 設定所有必要的環境變數並啟動應用程式

Write-Host "正在啟動桌遊館藏系統..." -ForegroundColor Cyan

# 自動清理舊的伺服器程序 (Zombie Processes)
Write-Host "檢查並清理舊的伺服器程序..." -ForegroundColor Yellow
Get-CimInstance Win32_Process | Where-Object { 
    ($_.Name -eq "python.exe" -or $_.Name -eq "pythonw.exe") -and 
    ($_.CommandLine -like "*serve.py*" -or $_.CommandLine -like "*flask_app.py*") 
} | ForEach-Object { 
    Write-Host "  - 停止程序 ID: $($_.ProcessId)" -ForegroundColor Red
    Stop-Process -Id $_.ProcessId -Force -ErrorAction SilentlyContinue 
}
Write-Host "清理完成。" -ForegroundColor Green

# Google Sheets 設定
# 注意：不設定 GOOGLE_CREDENTIALS，讓程式自動使用本地憑證檔案
$env:SHEET_URL = "https://docs.google.com/spreadsheets/d/1n2cCI1glkErCq835kNJD5hXyk1iR7IptPlnKKPm0_0Y/edit?gid=0#gid=0"

# BGG API 設定
$env:BGG_API_TOKEN = "cfebcba0-a1a7-4792-a6a6-d8514ecdc8c7"
$env:DEMO_MODE = "False"

# 管理員密碼
$env:ADMIN_PASSWORD = "admin123"

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
