@echo off
chcp 65001 > nul
title Kausan IT-Ops Dashboard 啟動程式

echo ╔═══════════════════════════════════════════════════════════╗
echo ║       Kausan IT-Ops Dashboard 儀表板啟動程式              ║
echo ╚═══════════════════════════════════════════════════════════╝
echo.

REM 檢查 Python 是否已安裝
python --version > nul 2>&1
if errorlevel 1 (
    echo [錯誤] 未偵測到 Python，請先安裝 Python 3.8 或以上版本
    echo 下載連結：https://www.python.org/downloads/
    pause
    exit /b 1
)

echo [步驟 1/3] 檢查依賴套件...
python -c "import streamlit" > nul 2>&1
if errorlevel 1 (
    echo [安裝中] 偵測到缺少依賴套件，正在安裝...
    pip install -r requirements.txt
    if errorlevel 1 (
        echo [錯誤] 套件安裝失敗，請手動執行：pip install -r requirements.txt
        pause
        exit /b 1
    )
) else (
    echo [✓] 依賴套件已就緒
)

echo.
echo [步驟 2/3] 檢查環境變數設定...
if not exist ".env" (
    echo [提示] 未找到 .env 檔案，使用預設設定啟動
    echo [提示] 如需連接 Zabbix/AI API，請複製 .env.example 並重新命名為 .env
) else (
    echo [✓] 環境變數設定檔已載入
)

echo.
echo [步驟 3/3] 啟動 Streamlit 儀表板...
echo.
echo ════════════════════════════════════════════════════════════
echo    儀表板將在瀏覽器中自動開啟
echo    網址: http://localhost:8501
echo.
echo    按 Ctrl+C 可停止服務
echo ════════════════════════════════════════════════════════════
echo.

REM 啟動 Streamlit
streamlit run app.py

REM 如果意外退出
echo.
echo [程式已結束]
pause
