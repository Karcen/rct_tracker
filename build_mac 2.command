#!/bin/bash
# ============================================================
#  RCT 线下追踪调研管理系统 —— macOS 打包脚本（生成 .app）
#  双击本文件即可用 PyInstaller 打包为 macOS 应用程序。
#  Build a macOS .app with PyInstaller.
# ============================================================
cd "$(dirname "$0")" || exit 1
echo "=== 打包为 macOS 应用 (.app) ==="

if ! command -v python3 >/dev/null 2>&1; then
  echo "[错误] 未检测到 python3，请先安装 Python 3.8+"
  read -r -p "回车退出" _; exit 1
fi

if [ ! -d ".venv" ]; then
  python3 -m venv .venv || { echo "创建虚拟环境失败"; read -r -p "回车退出" _; exit 1; }
fi
# shellcheck disable=SC1091
source .venv/bin/activate

echo "安装依赖与打包工具..."
python -m pip install --upgrade pip >/dev/null 2>&1
python -m pip install -r requirements.txt pyinstaller || { echo "依赖安装失败"; read -r -p "回车退出" _; exit 1; }

echo "开始打包（macOS 用 --windowed 生成 .app，不用 --onefile）..."
# --collect-all barcode 确保 python-barcode 自带字体被一并打包，不可省略
python -m PyInstaller --noconfirm --clean --windowed \
  --name RCT_Tracker \
  --collect-all barcode \
  main.py

echo ""
echo "打包完成！应用位于： dist/RCT_Tracker.app"
echo "首次打开若提示“无法验证开发者”，请右键点按 App → 打开 → 再点“打开”。"
read -r -p "按回车键退出..." _
