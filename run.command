#!/bin/bash
# ============================================================
#  RCT 线下追踪调研管理系统 —— macOS 双击运行脚本
#  双击本文件即可自动创建虚拟环境、安装依赖并启动程序。
#  Run from source on macOS: create venv, install deps, launch.
# ============================================================
cd "$(dirname "$0")" || exit 1

echo "==============================================="
echo "  RCT 线下追踪调研管理系统 (macOS)"
echo "==============================================="

# 1) 检查 python3
if ! command -v python3 >/dev/null 2>&1; then
  echo "[错误] 未检测到 python3。请先安装 Python 3.8+："
  echo "       https://www.python.org/downloads/macos/"
  echo "       （推荐 python.org 官方版，自带 Tkinter 图形库）"
  read -r -p "按回车键退出..." _
  exit 1
fi

# 2) 检查 Tkinter（图形界面依赖，随 Python 提供，不是 pip 包）
if ! python3 -c "import tkinter" >/dev/null 2>&1; then
  echo "[错误] 当前 Python 缺少 Tkinter 图形库。"
  echo "       Homebrew 用户请执行：  brew install python-tk"
  echo "       或改用 python.org 官方版 Python（自带 Tkinter）。"
  read -r -p "按回车键退出..." _
  exit 1
fi

# 3) 创建/复用虚拟环境（隔离依赖，避免污染系统 Python，并绕过 PEP 668 限制）
if [ ! -d ".venv" ]; then
  echo "首次运行：正在创建虚拟环境 .venv ..."
  python3 -m venv .venv || { echo "创建虚拟环境失败"; read -r -p "回车退出" _; exit 1; }
fi
# shellcheck disable=SC1091
source .venv/bin/activate

# 4) 安装依赖
echo "正在检查/安装依赖（首次较慢，请稍候）..."
python -m pip install --upgrade pip >/dev/null 2>&1
python -m pip install -r requirements.txt || { echo "依赖安装失败"; read -r -p "回车退出" _; exit 1; }

# 5) 启动
echo "启动程序..."
python main.py
