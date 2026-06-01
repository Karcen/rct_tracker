@echo off
chcp 65001 >nul
REM ============================================================
REM  源码运行脚本（Windows）：自动安装依赖并启动程序
REM  Run from source on Windows: install deps and launch
REM ============================================================
cd /d %~dp0

where python >nul 2>nul
if errorlevel 1 (
    echo [错误] 未检测到 Python，请先安装 Python 3.8+ 并勾选 Add to PATH
    echo [ERROR] Python not found. Install Python 3.8+ and check "Add to PATH".
    pause
    exit /b 1
)

echo 正在检查/安装依赖 / Installing dependencies ...
python -m pip install -r requirements.txt

echo 启动程序 / Launching ...
python main.py
pause
