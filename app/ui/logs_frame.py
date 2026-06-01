# -*- coding: utf-8 -*-
"""操作日志选项卡：查看 / 导出 登记、扫码、状态修改等行为记录。"""

import os
from datetime import datetime
import tkinter as tk
from tkinter import ttk, messagebox

from app import config, i18n, logger


class LogsFrame(ttk.Frame):
    def __init__(self, master, app):
        super().__init__(master)
        self.app = app
        self._build()
        self.refresh()

    def _build(self):
        top = ttk.Frame(self, padding=(10, 8))
        top.pack(fill="x")
        ttk.Label(top, text=i18n.T("logs_title"),
                  font=(self.app.font_family, 12, "bold")).pack(side="left")
        ttk.Button(top, text=i18n.T("btn_refresh"), command=self.refresh).pack(side="right")
        ttk.Button(top, text=i18n.T("btn_export_logs"),
                   command=self.export_logs).pack(side="right", padx=6)

        wrap = ttk.Frame(self, padding=(10, 0))
        wrap.pack(fill="both", expand=True)
        cols = ("time", "action", "detail")
        self.tree = ttk.Treeview(wrap, columns=cols, show="headings")
        self.tree.heading("time", text=i18n.T("log_col_time"))
        self.tree.heading("action", text=i18n.T("log_col_action"))
        self.tree.heading("detail", text=i18n.T("log_col_detail"))
        self.tree.column("time", width=160, anchor="center")
        self.tree.column("action", width=110, anchor="center")
        self.tree.column("detail", width=520, anchor="w")
        vsb = ttk.Scrollbar(wrap, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=vsb.set)
        self.tree.pack(side="left", fill="both", expand=True)
        vsb.pack(side="right", fill="y")

    def refresh(self):
        for iid in self.tree.get_children():
            self.tree.delete(iid)
        for r in logger.get_logs(2000):
            self.tree.insert("", "end", values=(r["timestamp"], r["action"], r["detail"]))

    def export_logs(self):
        rows = logger.get_logs(100000)
        fn = os.path.join(config.EXPORT_DIR,
                          "operation_logs_%s.csv" % datetime.now().strftime("%Y%m%d_%H%M%S"))
        try:
            with open(fn, "w", encoding="utf-8-sig") as f:  # utf-8-sig 便于 Excel 直接打开
                f.write("time,action,detail\n")
                for r in rows:
                    detail = (r["detail"] or "").replace('"', '""')
                    f.write('"%s","%s","%s"\n' % (r["timestamp"], r["action"], detail))
        except Exception as e:
            messagebox.showerror(i18n.T("error_title"), str(e))
            return
        messagebox.showinfo(i18n.T("info_title"), i18n.T("logs_exported", path=fn))
