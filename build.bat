@echo off
chcp 65001 >nul
REM ============================================================
REM  打包脚本（Windows）：用 PyInstaller 生成单文件 exe
REM  Packaging script: build a single-file exe with PyInstaller
REM ============================================================
cd /d %~dp0

echo 安装打包依赖 / Installing build dependencies ...
python -m pip install -r requirements.txt
python -m pip install pyinstaller

echo 开始打包 / Building ...
REM --windowed     不弹出黑色控制台窗口 / no console window
REM --onefile      打包为单个 exe / single exe
REM --collect-all  确保 python-barcode 自带字体一起打包 / bundle barcode font data
python -m PyInstaller --noconfirm --clean --onefile --windowed ^
    --name RCT_Tracker ^
    --collect-all barcode ^
    main.py

echo.
echo 打包完成！可执行文件位于 dist\RCT_Tracker.exe
echo Done! The executable is at dist\RCT_Tracker.exe
echo 双击运行后会在同级目录自动生成 data\ 文件夹用于存放数据。
echo Running it creates a data\ folder next to the exe for all data.
pause
