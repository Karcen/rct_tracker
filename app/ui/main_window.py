# -*- coding: utf-8 -*-
"""主窗口：顶部语言切换 + 选项卡（登记/扫码/台账/统计/设置/日志）+ 底部状态栏。"""

import sys
import tkinter as tk
from tkinter import ttk
import tkinter.font as tkfont

from app import config, i18n
from app.ui import widgets
from app.ui.register_frame import RegisterFrame
from app.ui.scan_frame import ScanFrame
from app.ui.ledger_frame import LedgerFrame
from app.ui.stats_frame import StatsFrame
from app.ui.settings_frame import SettingsFrame
from app.ui.logs_frame import LogsFrame


class MainWindow:
    def __init__(self, root, settings):
        self.root = root
        self.settings = settings
        self.font_family = self._setup_fonts()
        self._build()

    # ----- 字体：确保中文正常显示 -----
    def _pick_font(self):
        if sys.platform.startswith("win"):
            cands = ["Microsoft YaHei UI", "Microsoft YaHei", "SimHei", "SimSun"]
        elif sys.platform == "darwin":
            cands = ["PingFang SC", "Heiti SC", "STHeiti", "Arial Unicode MS"]
        else:
            cands = ["WenQuanYi Micro Hei", "Noto Sans CJK SC", "Droid Sans Fallback"]
        try:
            avail = set(tkfont.families())
        except Exception:
            avail = set()
        for c in cands:
            if c in avail:
                return c
        return "TkDefaultFont"

    def _setup_fonts(self):
        family = self._pick_font()
        for name in ("TkDefaultFont", "TkTextFont", "TkMenuFont",
                     "TkHeadingFont", "TkEntryFont"):
            try:
                f = tkfont.nametofont(name)
                f.configure(family=family, size=11)
            except Exception:
                pass
        self.root.option_add("*Font", ("%s" % family, 11))
        return family

    # ----- 构建界面 -----
    def _build(self):
        self.root.title(i18n.T("app_title"))
        self.root.geometry("1120x720")
        self.root.minsize(960, 640)

        # 顶部栏
        top = ttk.Frame(self.root, padding=(10, 6))
        top.pack(side="top", fill="x")
        ttk.Label(top, text=i18n.T("app_title"),
                  font=(self.font_family, 15, "bold")).pack(side="left")

        ttk.Label(top, text=i18n.T("language_label") + "：").pack(side="left", padx=(24, 2))
        self._lang_display = {"zh": i18n.T("lang_zh"), "en": i18n.T("lang_en")}
        self.lang_combo = ttk.Combobox(
            top, width=10, state="readonly",
            values=[self._lang_display["zh"], self._lang_display["en"]])
        self.lang_combo.set(self._lang_display[i18n.get_language()])
        self.lang_combo.bind("<<ComboboxSelected>>", self._on_lang_change)
        self.lang_combo.pack(side="left")

        # 右上角：作者署名 + 联系链接（点击打开作者主页）
        widgets.make_hyperlink(top, i18n.T("contact_author")).pack(side="right", padx=(0, 2))
        ttk.Label(top, text=i18n.T("made_by_full", name=config.AUTHOR_NAME) + "  ·",
                  foreground="#5f6368").pack(side="right", padx=(0, 4))

        # 选项卡
        self.nb = ttk.Notebook(self.root)
        self.nb.pack(fill="both", expand=True, padx=8, pady=6)

        self.register_frame = RegisterFrame(self.nb, self)
        self.scan_frame = ScanFrame(self.nb, self)
        self.ledger_frame = LedgerFrame(self.nb, self)
        self.stats_frame = StatsFrame(self.nb, self)
        self.settings_frame = SettingsFrame(self.nb, self)
        self.logs_frame = LogsFrame(self.nb, self)

        self.nb.add(self.register_frame, text="  " + i18n.T("menu_register") + "  ")
        self.nb.add(self.scan_frame, text="  " + i18n.T("menu_scan") + "  ")
        self.nb.add(self.ledger_frame, text="  " + i18n.T("menu_ledger") + "  ")
        self.nb.add(self.stats_frame, text="  " + i18n.T("menu_stats") + "  ")
        self.nb.add(self.settings_frame, text="  " + i18n.T("menu_settings") + "  ")
        self.nb.add(self.logs_frame, text="  " + i18n.T("menu_logs") + "  ")
        self.nb.bind("<<NotebookTabChanged>>", self._on_tab_change)

        # 底部状态栏
        self.status_var = tk.StringVar(value=i18n.T("status_ready"))
        ttk.Label(self.root, textvariable=self.status_var, relief="sunken",
                  anchor="w", padding=(8, 3)).pack(side="bottom", fill="x")

    def _on_tab_change(self, event=None):
        """切到不同选项卡时刷新数据 / 自动聚焦扫码框。"""
        try:
            current = self.nb.select()
            if current == str(self.scan_frame):
                self.scan_frame.focus_scan()
            elif current == str(self.ledger_frame):
                self.ledger_frame.refresh()
            elif current == str(self.stats_frame):
                self.stats_frame.refresh()
            elif current == str(self.logs_frame):
                self.logs_frame.refresh()
        except Exception:
            pass

    def _on_lang_change(self, event=None):
        sel = self.lang_combo.get()
        code = "zh" if sel == self._lang_display["zh"] else "en"
        if code != i18n.get_language():
            self.switch_language(code)

    # ----- 对外接口 -----
    def set_status(self, text):
        self.status_var.set(text)

    def switch_language(self, lang):
        """切换语言：保存设置并重建整个界面。"""
        i18n.set_language(lang)
        self.settings["language"] = lang
        config.save_settings(self.settings)
        self.rebuild()

    def rebuild(self):
        """销毁并重建界面（语言切换 / 数据恢复后调用）。"""
        for w in self.root.winfo_children():
            w.destroy()
        self._build()

    def refresh_all(self):
        """数据变更后刷新台账与统计。"""
        for fr in ("ledger_frame", "stats_frame"):
            try:
                getattr(self, fr).refresh()
            except Exception:
                pass
