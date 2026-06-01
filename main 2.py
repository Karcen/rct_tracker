# -*- coding: utf-8 -*-
"""程序入口（entry point）。

启动流程：
1. 读取设置并设定界面语言；
2. 初始化数据库（首次运行自动建表）；
3. 可选地在启动时自动备份数据库（数据安全）；
4. 创建 Tk 主窗口并进入事件循环。
"""

import tkinter as tk
from tkinter import messagebox

from app import config, db, i18n
from app.ui.main_window import MainWindow


def main():
    settings = config.load_settings()
    i18n.set_language(settings.get("language", "zh"))

    db.init_db()

    # 启动时自动备份，降低误操作/异常退出导致的数据损失风险
    if settings.get("auto_backup_on_start", True):
        try:
            db.backup_db(reason="startup")
        except Exception:
            pass

    root = tk.Tk()
    try:
        MainWindow(root, settings)
    except Exception as e:
        messagebox.showerror("Error", str(e))
        raise
    root.mainloop()


if __name__ == "__main__":
    main()
