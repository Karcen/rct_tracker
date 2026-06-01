# -*- coding: utf-8 -*-
"""扫码配对选项卡。

工作原理：USB 有线扫码枪在系统中等同于「键盘」，扫码后会自动把条码字符
「敲入」当前焦点输入框并回车。因此本页保持扫码输入框聚焦，监听回车事件
即可完成识别 -> 弹出受试者信息 -> 手动标记问卷状态。
条码损坏时，可手动输入条码/受试者ID检索（兜底方案）。
"""

import time
import tkinter as tk
from tkinter import ttk, messagebox

from app import db, i18n, logger


class ScanFrame(ttk.Frame):
    def __init__(self, master, app):
        super().__init__(master)
        self.app = app
        self.current_subject = None
        self.last_change = None  # (barcode, round_no, old_status) 供撤销
        self._build()

    # ------------------------------------------------------------------
    def _build(self):
        # 第一行：当前随访轮次
        top = ttk.Frame(self, padding=(10, 8))
        top.pack(fill="x")
        ttk.Label(top, text=i18n.T("current_round_label"),
                  font=(self.app.font_family, 12, "bold")).pack(side="left")
        self.round_var = tk.IntVar(value=1)
        for r in (1, 2, 3):
            ttk.Radiobutton(top, text=i18n.T("round_n", n=r), value=r,
                            variable=self.round_var).pack(side="left", padx=6)

        # 第二行：扫码 / 手动输入
        scanbar = ttk.Frame(self, padding=(10, 0))
        scanbar.pack(fill="x")
        ttk.Label(scanbar, text=i18n.T("scan_prompt"),
                  font=(self.app.font_family, 12, "bold")).pack(side="left")
        self.scan_var = tk.StringVar()
        self.scan_entry = ttk.Entry(scanbar, textvariable=self.scan_var,
                                    font=(self.app.font_family, 18), width=28)
        self.scan_entry.pack(side="left", fill="x", expand=True, padx=8, pady=8)
        self.scan_entry.bind("<Return>", self.on_scan)
        ttk.Button(scanbar, text=i18n.T("btn_lookup"), command=self.on_scan).pack(side="left")
        ttk.Label(self, text=i18n.T("scan_focus_hint"), foreground="#888",
                  padding=(10, 0)).pack(fill="x")

        # 受试者信息卡片
        card = ttk.LabelFrame(self, text=i18n.T("person_card_title"), padding=12)
        card.pack(fill="x", padx=10, pady=8)
        self.card_vars = {}
        fields = [
            ("subject_id", "col_subject_id"), ("barcode", "col_barcode"),
            ("name", "col_name"), ("phone", "col_phone"),
            ("gender", "col_gender"), ("group", "col_group"),
            ("round1", "col_round1"), ("round2", "col_round2"),
            ("round3", "col_round3"), ("note", "col_note"),
        ]
        for idx, (key, label_key) in enumerate(fields):
            row, col = divmod(idx, 2)
            ttk.Label(card, text=i18n.T(label_key) + "：",
                      foreground="#555").grid(row=row, column=col * 2, sticky="e", padx=6, pady=5)
            var = tk.StringVar(value="—")
            self.card_vars[key] = var
            ttk.Label(card, textvariable=var, font=(self.app.font_family, 12, "bold")) \
                .grid(row=row, column=col * 2 + 1, sticky="w", padx=6, pady=5)
        card.columnconfigure(1, weight=1)
        card.columnconfigure(3, weight=1)

        # 状态标记按钮区
        btns = ttk.LabelFrame(self, text=i18n.T("status_filter_label"), padding=10)
        btns.pack(fill="x", padx=10, pady=(0, 8))
        actions = [("valid", "btn_valid"), ("void", "btn_void"),
                   ("mismatch", "btn_mismatch"), ("damaged", "btn_damaged"),
                   ("lost", "btn_lost"), ("", "btn_pending")]
        for code, label_key in actions:
            ttk.Button(btns, text=i18n.T(label_key), width=12,
                       command=lambda c=code: self.mark(c)).pack(side="left", padx=4, pady=4)
        ttk.Button(btns, text=i18n.T("btn_undo"),
                   command=self.undo).pack(side="right", padx=4)

        # 本次扫码操作记录
        hist = ttk.LabelFrame(self, text=i18n.T("scan_history_title"), padding=8)
        hist.pack(fill="both", expand=True, padx=10, pady=(0, 8))
        cols = ("time", "barcode", "name", "round", "status")
        self.history = ttk.Treeview(hist, columns=cols, show="headings", height=6)
        heads = {"time": "col_time", "barcode": "col_barcode", "name": "col_name",
                 "round": "col_round", "status": "col_status"}
        for c in cols:
            self.history.heading(c, text=i18n.T(heads[c]))
            self.history.column(c, width=120, anchor="center")
        self.history.pack(side="left", fill="both", expand=True)
        vsb = ttk.Scrollbar(hist, orient="vertical", command=self.history.yview)
        self.history.configure(yscrollcommand=vsb.set)
        vsb.pack(side="right", fill="y")

        self.after(200, self.focus_scan)

    # ------------------------------------------------------------------
    def focus_scan(self):
        try:
            self.scan_entry.focus_set()
        except Exception:
            pass

    def on_scan(self, event=None):
        code = self.scan_var.get().strip()
        self.scan_var.set("")
        if not code:
            return
        subject = db.get_by_barcode(code) or db.get_by_subject_id(code)
        if not subject:
            self._show_card(None)
            self.app.set_status(i18n.T("no_record_found") + "：" + code)
            messagebox.showwarning(i18n.T("warn_title"),
                                   i18n.T("no_record_found") + "：" + code)
        else:
            self.current_subject = subject
            self._show_card(subject)
            logger.log("SCAN", "%s %s" % (subject["barcode"], subject["name"]))
            self.app.set_status("%s | %s" % (subject["barcode"], subject["name"]))
        self.focus_scan()

    def _show_card(self, subject):
        if not subject:
            for v in self.card_vars.values():
                v.set("—")
            self.current_subject = None
            return
        self.card_vars["subject_id"].set(subject["subject_id"])
        self.card_vars["barcode"].set(subject["barcode"])
        self.card_vars["name"].set(subject["name"])
        self.card_vars["phone"].set(subject["phone"])
        self.card_vars["gender"].set(i18n.gender_label(subject["gender"]))
        self.card_vars["group"].set(i18n.group_label(subject["group_type"]))
        self.card_vars["round1"].set(i18n.status_label(subject["round1_status"]))
        self.card_vars["round2"].set(i18n.status_label(subject["round2_status"]))
        self.card_vars["round3"].set(i18n.status_label(subject["round3_status"]))
        self.card_vars["note"].set(subject["note"] or "—")

    def mark(self, status):
        if not self.current_subject:
            messagebox.showwarning(i18n.T("warn_title"), i18n.T("no_subject_selected"))
            return
        r = self.round_var.get()
        bc = self.current_subject["barcode"]
        old = db.update_round_status(bc, r, status)
        self.last_change = (bc, r, old)
        logger.log("STATUS", "%s round%d %s -> %s" % (
            bc, r, old or "pending", status or "pending"))
        # 刷新卡片与历史
        self.current_subject = db.get_by_barcode(bc)
        self._show_card(self.current_subject)
        self.history.insert("", 0, values=(
            time.strftime("%H:%M:%S"), bc, self.current_subject["name"],
            i18n.T("round_n", n=r), i18n.status_label(status)))
        self.app.set_status(i18n.T("status_marked", round=r, status=i18n.status_label(status)))
        self.app.refresh_all()
        self.focus_scan()

    def undo(self):
        if not self.last_change:
            messagebox.showinfo(i18n.T("info_title"), i18n.T("undo_none"))
            return
        bc, r, old = self.last_change
        db.update_round_status(bc, r, old or "")
        logger.log("STATUS", "UNDO %s round%d -> %s" % (bc, r, old or "pending"))
        self.last_change = None
        if self.current_subject and self.current_subject["barcode"] == bc:
            self.current_subject = db.get_by_barcode(bc)
            self._show_card(self.current_subject)
        self.app.set_status(i18n.T("undo_done"))
        self.app.refresh_all()
        self.focus_scan()
