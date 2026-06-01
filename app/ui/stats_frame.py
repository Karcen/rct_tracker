# -*- coding: utf-8 -*-
"""统计分析选项卡：总人数、各组人数、各轮各状态样本数量。"""

import tkinter as tk
from tkinter import ttk

from app import db, i18n


class StatsFrame(ttk.Frame):
    def __init__(self, master, app):
        super().__init__(master)
        self.app = app
        self._build()
        self.refresh()

    def _build(self):
        top = ttk.Frame(self, padding=(10, 10))
        top.pack(fill="x")
        ttk.Label(top, text=i18n.T("stats_title"),
                  font=(self.app.font_family, 14, "bold")).pack(side="left")
        ttk.Button(top, text=i18n.T("btn_refresh"), command=self.refresh).pack(side="right")

        # 概览卡片
        summary = ttk.Frame(self, padding=(10, 0))
        summary.pack(fill="x")
        self.total_var = tk.StringVar()
        self.ga_var = tk.StringVar()
        self.gb_var = tk.StringVar()
        for i, (cap, var) in enumerate([
            (i18n.T("stat_total"), self.total_var),
            (i18n.T("stat_group_a"), self.ga_var),
            (i18n.T("stat_group_b"), self.gb_var)]):
            box = ttk.LabelFrame(summary, text=cap, padding=12)
            box.grid(row=0, column=i, padx=8, pady=8, sticky="ew")
            ttk.Label(box, textvariable=var,
                      font=(self.app.font_family, 22, "bold")).pack()
            summary.columnconfigure(i, weight=1)

        # 各轮 x 各状态 表格
        table = ttk.LabelFrame(self, text=i18n.T("stat_round_col"), padding=10)
        table.pack(fill="both", expand=True, padx=10, pady=8)
        cols = ("round", "valid", "void", "mismatch", "damaged", "lost", "pending")
        heads = {"round": "stat_round_col", "valid": "stat_valid", "void": "stat_void",
                 "mismatch": "stat_mismatch", "damaged": "stat_damaged",
                 "lost": "stat_lost", "pending": "stat_pending"}
        self.tree = ttk.Treeview(table, columns=cols, show="headings", height=5)
        for c in cols:
            self.tree.heading(c, text=i18n.T(heads[c]))
            self.tree.column(c, width=110, anchor="center")
        self.tree.pack(fill="both", expand=True)

    def refresh(self):
        s = db.get_stats()
        self.total_var.set(str(s["total"]))
        self.ga_var.set(str(s["group_a"]))
        self.gb_var.set(str(s["group_b"]))
        for iid in self.tree.get_children():
            self.tree.delete(iid)
        for rnd in (1, 2, 3):
            cc = s["rounds"][rnd]
            self.tree.insert("", "end", values=(
                i18n.T("round_n", n=rnd), cc["valid"], cc["void"],
                cc["mismatch"], cc["damaged"], cc["lost"], cc[""]))
