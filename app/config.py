# -*- coding: utf-8 -*-
"""全局配置与设置持久化模块。

设计要点：
1. 所有数据均存放在程序根目录下的 data/ 子目录，方便整体拷贝备份；
2. 兼容 PyInstaller 打包：打包后数据放在 exe 同级目录，源码运行时放在项目根目录；
3. 设置以 JSON 形式保存，易于人工查看与修改。
"""

import os
import sys
import json
import subprocess


APP_NAME = "RCT 线下追踪调研管理系统"
APP_NAME_EN = "RCT Field Tracking Manager"
APP_VERSION = "1.0.0"


def get_base_dir():
    """获取程序运行根目录（兼容 PyInstaller onefile/onedir 打包）。"""
    if getattr(sys, "frozen", False):
        # 已打包：数据放在可执行文件同级目录，便于现场拷贝备份
        return os.path.dirname(sys.executable)
    # 源码运行：项目根目录（本文件位于 <root>/app/config.py）
    return os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


BASE_DIR = get_base_dir()
DATA_DIR = os.path.join(BASE_DIR, "data")          # 数据库 + 设置
BACKUP_DIR = os.path.join(DATA_DIR, "backups")     # 数据库备份快照
BARCODE_DIR = os.path.join(DATA_DIR, "barcodes")   # 生成的条码图片
LOG_DIR = os.path.join(DATA_DIR, "logs")           # 文本操作日志
EXPORT_DIR = os.path.join(BASE_DIR, "exports")     # 导出的 Excel / 打印页

DB_PATH = os.path.join(DATA_DIR, "rct_data.db")
SETTINGS_PATH = os.path.join(DATA_DIR, "settings.json")


# 启动即确保各目录存在（幂等操作）
for _d in (DATA_DIR, BACKUP_DIR, BARCODE_DIR, LOG_DIR, EXPORT_DIR):
    os.makedirs(_d, exist_ok=True)


# 默认设置项（首次运行时写入）
DEFAULT_SETTINGS = {
    "language": "zh",            # 界面语言：zh / en
    "group_a_prefix": "A",       # 干预组条码前缀
    "group_b_prefix": "B",       # 对照组条码前缀
    "id_padding": 5,             # 条码序号补零位数，例如 5 -> A00001
    "subject_id_prefix": "S",    # 全局受试者ID前缀
    "subject_id_padding": 6,     # 全局受试者ID补零位数，例如 6 -> S000001
    "auto_backup_on_start": True,  # 启动时自动备份数据库
    "barcode_module_height": 12.0,  # 条码高度（毫米，影响清晰度）
    "barcode_font_size": 10,        # 条码下方文字字号
}


def load_settings():
    """读取设置；缺失项用默认值补全，保证向后兼容。"""
    data = dict(DEFAULT_SETTINGS)
    if os.path.exists(SETTINGS_PATH):
        try:
            with open(SETTINGS_PATH, "r", encoding="utf-8") as f:
                data.update(json.load(f))
        except Exception:
            # 设置文件损坏时回退到默认值，避免程序无法启动
            pass
    return data


def save_settings(settings):
    """保存设置到 JSON 文件。"""
    with open(SETTINGS_PATH, "w", encoding="utf-8") as f:
        json.dump(settings, f, ensure_ascii=False, indent=2)


def open_path(path):
    """在系统文件管理器中打开指定目录（跨平台）。"""
    try:
        if sys.platform.startswith("win"):
            os.startfile(path)  # type: ignore[attr-defined]
        elif sys.platform == "darwin":
            subprocess.Popen(["open", path])
        else:
            subprocess.Popen(["xdg-open", path])
        return True
    except Exception:
        return False
