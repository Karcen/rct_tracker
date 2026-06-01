# -*- coding: utf-8 -*-
"""可复用的小部件：超链接标签、启动界面(splash)。"""

import webbrowser
import tkinter as tk
import tkinter.font as tkfont
from tkinter import ttk

from app import config, i18n


def make_hyperlink(parent, text, url=None, font=None):
    """生成可点击的超链接样式标签（蓝色、下划线、手型光标，点击打开浏览器）。"""
    target = url or config.AUTHOR_URL
    lbl = ttk.Label(parent, text=text, foreground="#1a73e8", cursor="hand2")
    f = tkfont.Font(font=font or lbl.cget("font"))
    f.configure(underline=True)
    lbl.configure(font=f)
    lbl.bind("<Button-1>", lambda e: webbrowser.open(target))
    lbl.bind("<Enter>", lambda e: lbl.configure(foreground="#0b57d0"))
    lbl.bind("<Leave>", lambda e: lbl.configure(foreground="#1a73e8"))
    return lbl


def show_splash(root, family=None, on_close=None, duration=1800):
    """启动界面：展示应用名、作者署名与联系链接，短暂停留后进入主界面。

    root      主窗口（启动时通常先 withdraw 隐藏）
    family    中文字体名
    on_close  关闭后回调（一般用于 deiconify 主窗口）
    duration  停留毫秒数
    """
    family = family or "TkDefaultFont"
    sp = tk.Toplevel(root)
    try:
        sp.overrideredirect(True)  # 去掉标题栏，做出 splash 效果
    except Exception:
        pass
    w, h = 480, 290
    sw, sh = root.winfo_screenwidth(), root.winfo_screenheight()
    sp.geometry("%dx%d+%d+%d" % (w, h, (sw - w) // 2, (sh - h) // 2))
    try:
        sp.attributes("-topmost", True)
    except Exception:
        pass

    frame = tk.Frame(sp, bg="#ffffff", highlightbackground="#1a73e8",
                     highlightthickness=2)
    frame.pack(fill="both", expand=True)

    tk.Label(frame, text=i18n.T("app_title"), bg="#ffffff", fg="#202124",
             font=(family, 18, "bold")).pack(pady=(46, 4))
    tk.Label(frame, text="RCT Field Tracking Manager", bg="#ffffff",
             fg="#5f6368", font=(family, 11)).pack()
    tk.Label(frame, text=i18n.T("made_by_full", name=config.AUTHOR_NAME),
             bg="#ffffff", fg="#202124", font=(family, 13)).pack(pady=(28, 2))
    link = tk.Label(frame, text=config.AUTHOR_URL, bg="#ffffff", fg="#1a73e8",
                    cursor="hand2", font=(family, 11, "underline"))
    link.pack()
    link.bind("<Button-1>", lambda e: webbrowser.open(config.AUTHOR_URL))
    tk.Label(frame, text="v" + config.APP_VERSION, bg="#ffffff", fg="#9aa0a6",
             font=(family, 9)).pack(side="bottom", pady=12)

    def _close():
        try:
            if sp.winfo_exists():
                sp.destroy()
        finally:
            if on_close:
                on_close()

    root.after(duration, _close)
    return sp
