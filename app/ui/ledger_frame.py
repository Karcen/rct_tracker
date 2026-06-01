# -*- coding: utf-8 -*-
"""数据台账选项卡：多条件检索 / 导出 Excel / 编辑 / 重打条码 / 删除。"""

import re
import tkinter as tk
from tkinter import ttk, messagebox

from app import config, db, i18n, logger, barcode_util, excel_export

PHONE_RE = re.compile(r"^\d{11}$")


class LedgerFrame(ttk.Frame):
    def __init__(self, master, app):
        super().__init__(master)
        self.app = app
        self._build()
        self.refresh()

    # ------------------------------------------------------------------
    def _build(self):
        # ---- 检索条件 ----
        bar = ttk.Frame(self, padding=(10, 8))
        bar.pack(fill="x")

        ttk.Label(bar, text=i18n.T("search_label")).pack(side="left")
        self.kw_var = tk.StringVar()
        ent = ttk.Entry(bar, textvariable=self.kw_var, width=18)
        ent.pack(side="left", padx=(2, 8))
        ent.bind("<Return>", lambda e: self.refresh())

        # 检索字段
        self.field_codes = ["all", "subject_id", "barcode", "name", "phone"]
        self.field_combo = ttk.Combobox(bar, width=10, state="readonly", values=[
            i18n.T("field_all"), i18n.T("field_subject_id"), i18n.T("field_barcode"),
            i18n.T("field_name"), i18n.T("field_phone")])
        self.field_combo.current(0)
        self.field_combo.pack(side="left", padx=(0, 8))

        # 分组
        ttk.Label(bar, text=i18n.T("group_filter_label")).pack(side="left")
        self.group_codes = ["__all__", "A", "B"]
        self.group_combo = ttk.Combobox(bar, width=8, state="readonly", values=[
            i18n.T("group_all"), i18n.T("group_a"), i18n.T("group_b")])
        self.group_combo.current(0)
        self.group_combo.pack(side="left", padx=(2, 8))

        # 轮次
        ttk.Label(bar, text=i18n.T("round_filter_label")).pack(side="left")
        self.round_codes = [0, 1, 2, 3]
        self.round_combo = ttk.Combobox(bar, width=8, state="readonly", values=[
            i18n.T("round_all"), i18n.T("round_n", n=1),
            i18n.T("round_n", n=2), i18n.T("round_n", n=3)])
        self.round_combo.current(0)
        self.round_combo.pack(side="left", padx=(2, 8))

        # 状态
        ttk.Label(bar, text=i18n.T("status_filter_label")).pack(side="left")
        self.status_codes = [None, "", "valid", "void", "mismatch", "damaged", "lost"]
        self.status_combo = ttk.Combobox(bar, width=10, state="readonly", values=[
            i18n.T("status_all")] + [i18n.status_label(c) for c in self.status_codes[1:]])
        self.status_combo.current(0)
        self.status_combo.pack(side="left", padx=(2, 8))

        ttk.Button(bar, text=i18n.T("btn_search"), command=self.refresh).pack(side="left", padx=3)
        ttk.Button(bar, text=i18n.T("btn_reset"), command=self.reset).pack(side="left", padx=3)

        # ---- 操作按钮 ----
        ab = ttk.Frame(self, padding=(10, 0))
        ab.pack(fill="x")
        ttk.Button(ab, text=i18n.T("btn_refresh"), command=self.refresh).pack(side="left", padx=3)
        ttk.Button(ab, text=i18n.T("btn_export_excel"), command=self.export).pack(side="left", padx=3)
        ttk.Button(ab, text=i18n.T("btn_edit"), command=self.edit_selected).pack(side="left", padx=3)
        ttk.Button(ab, text=i18n.T("btn_reprint"), command=self.reprint_selected).pack(side="left", padx=3)
        ttk.Button(ab, text=i18n.T("btn_delete"), command=self.delete_selected).pack(side="left", padx=3)
        self.count_var = tk.StringVar(value="")
        ttk.Label(ab, textvariable=self.count_var, foreground="#666").pack(side="right")

        # ---- 表格 ----
        wrap = ttk.Frame(self, padding=(10, 8))
        wrap.pack(fill="both", expand=True)
        cols = ("subject_id", "barcode", "name", "phone", "gender", "group",
                "register_time", "round1", "round2", "round3", "note")
        self.tree = ttk.Treeview(wrap, columns=cols, show="headings", selectmode="extended")
        widths = {"subject_id": 80, "barcode": 80, "name": 90, "phone": 110,
                  "gender": 50, "group": 80, "register_time": 140,
                  "round1": 80, "round2": 80, "round3": 80, "note": 120}
        for c in cols:
            self.tree.heading(c, text=i18n.T("col_" + c))
            self.tree.column(c, width=widths[c], anchor="center")
        vsb = ttk.Scrollbar(wrap, orient="vertical", command=self.tree.yview)
        hsb = ttk.Scrollbar(wrap, orient="horizontal", command=self.tree.xview)
        self.tree.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)
        self.tree.grid(row=0, column=0, sticky="nsew")
        vsb.grid(row=0, column=1, sticky="ns")
        hsb.grid(row=1, column=0, sticky="ew")
        wrap.rowconfigure(0, weight=1)
        wrap.columnconfigure(0, weight=1)
        self.tree.bind("<Double-1>", lambda e: self.edit_selected())

    # ------------------------------------------------------------------
    def reset(self):
        self.kw_var.set("")
        self.field_combo.current(0)
        self.group_combo.current(0)
        self.round_combo.current(0)
        self.status_combo.current(0)
        self.refresh()

    def refresh(self):
        field = self.field_codes[self.field_combo.current()]
        group_code = self.group_codes[self.group_combo.current()]
        group = group_code if group_code in ("A", "B") else ""
        round_no = self.round_codes[self.round_combo.current()]
        status = self.status_codes[self.status_combo.current()]
        rows = db.search(self.kw_var.get(), field, group, round_no, status)

        for iid in self.tree.get_children():
            self.tree.delete(iid)
        for r in rows:
            self.tree.insert("", "end", iid=str(r["id"]), values=(
                r["subject_id"], r["barcode"], r["name"], r["phone"],
                i18n.gender_label(r["gender"]), i18n.group_label(r["group_type"]),
                r["register_time"], i18n.status_label(r["round1_status"]),
                i18n.status_label(r["round2_status"]),
                i18n.status_label(r["round3_status"]), r["note"]))
        self.count_var.set("%d" % len(rows))

    def _selected_ids(self):
        return [int(iid) for iid in self.tree.selection()]

    def _selected_subjects(self):
        return [s for s in (db.get_by_id(i) for i in self._selected_ids()) if s]

    # ------------------------------------------------------------------
    def export(self):
        try:
            path = excel_export.export_ledger()
        except Exception as e:
            messagebox.showerror(i18n.T("error_title"), str(e))
            return
        logger.log("EXPORT", path)
        self.app.set_status(i18n.T("export_success", path=path))
        if messagebox.askyesno(i18n.T("info_title"),
                               i18n.T("export_success", path=path) + "\n\n"
                               + i18n.T("export_open_q")):
            config.open_path(config.EXPORT_DIR)

    def reprint_selected(self):
        subjects = self._selected_subjects()
        if not subjects:
            messagebox.showinfo(i18n.T("info_title"), i18n.T("nothing_selected"))
            return
        try:
            barcode_util.print_subjects(subjects)
            logger.log("PRINT", "reprint %d barcodes" % len(subjects))
        except Exception as e:
            messagebox.showwarning(i18n.T("warn_title"), str(e))

    def delete_selected(self):
        ids = self._selected_ids()
        if not ids:
            messagebox.showinfo(i18n.T("info_title"), i18n.T("nothing_selected"))
            return
        if not messagebox.askyesno(i18n.T("confirm_title"),
                                   i18n.T("delete_confirm", n=len(ids))):
            return
        for i in ids:
            db.delete_subject(i)
        logger.log("DELETE", "ids=%s" % ids)
        self.refresh()
        self.app.refresh_all()

    def edit_selected(self):
        ids = self._selected_ids()
        if not ids:
            messagebox.showinfo(i18n.T("info_title"), i18n.T("nothing_selected"))
            return
        if len(ids) > 1:
            messagebox.showinfo(i18n.T("info_title"), i18n.T("select_one_only"))
            return
        subject = db.get_by_id(ids[0])
        if subject:
            EditDialog(self, subject)


class EditDialog(tk.Toplevel):
    """编辑受试者信息弹窗（分组与条码锁定，保证一人一码全程复用）。"""

    def __init__(self, parent, subject):
        super().__init__(parent)
        self.parent = parent
        self.subject = subject
        self.title(i18n.T("edit_title"))
        self.transient(parent)
        self.grab_set()
        self.resizable(False, False)
        self._build()

    def _build(self):
        f = ttk.Frame(self, padding=14)
        f.pack(fill="both", expand=True)

        # 只读：受试者ID + 条码 + 分组
        ttk.Label(f, text=i18n.T("col_subject_id") + "：").grid(row=0, column=0, sticky="e", pady=5)
        ttk.Label(f, text="%s   |   %s：%s   |   %s：%s" % (
            self.subject["subject_id"], i18n.T("col_barcode"), self.subject["barcode"],
            i18n.T("col_group"), i18n.group_label(self.subject["group_type"])),
            font=(self.parent.app.font_family, 11, "bold")) \
            .grid(row=0, column=1, columnspan=3, sticky="w", pady=5)

        self.name_var = tk.StringVar(value=self.subject["name"])
        self.phone_var = tk.StringVar(value=self.subject["phone"])
        self.gender_var = tk.StringVar(value=self.subject["gender"] or "M")
        self.note_var = tk.StringVar(value=self.subject["note"] or "")

        ttk.Label(f, text=i18n.T("field_name") + "：").grid(row=1, column=0, sticky="e", pady=5)
        ttk.Entry(f, textvariable=self.name_var, width=22).grid(row=1, column=1, sticky="w", pady=5)
        ttk.Label(f, text=i18n.T("field_phone") + "：").grid(row=1, column=2, sticky="e", pady=5)
        ttk.Entry(f, textvariable=self.phone_var, width=18).grid(row=1, column=3, sticky="w", pady=5)

        ttk.Label(f, text=i18n.T("field_gender") + "：").grid(row=2, column=0, sticky="e", pady=5)
        gbox = ttk.Frame(f)
        gbox.grid(row=2, column=1, sticky="w", pady=5)
        for code, label in i18n.gender_options():
            ttk.Radiobutton(gbox, text=label, value=code,
                            variable=self.gender_var).pack(side="left", padx=(0, 6))
        ttk.Label(f, text=i18n.T("field_note") + "：").grid(row=2, column=2, sticky="e", pady=5)
        ttk.Entry(f, textvariable=self.note_var, width=18).grid(row=2, column=3, sticky="w", pady=5)

        # 三轮随访状态
        self.round_vars = {}
        status_display = [i18n.status_label(c) for c in i18n.STATUS_ORDER]
        for idx, rnd in enumerate((1, 2, 3)):
            ttk.Label(f, text=i18n.T("col_round%d" % rnd) + "：") \
                .grid(row=3 + idx, column=0, sticky="e", pady=5)
            cur = self.subject["round%d_status" % rnd]
            combo = ttk.Combobox(f, width=14, state="readonly", values=status_display)
            combo.current(i18n.STATUS_ORDER.index(cur) if cur in i18n.STATUS_ORDER else 0)
            combo.grid(row=3 + idx, column=1, sticky="w", pady=5)
            self.round_vars[rnd] = combo

        btns = ttk.Frame(f)
        btns.grid(row=6, column=0, columnspan=4, pady=(14, 0))
        ttk.Button(btns, text=i18n.T("ok"), command=self.save).pack(side="left", padx=6)
        ttk.Button(btns, text=i18n.T("cancel"), command=self.destroy).pack(side="left", padx=6)

    def save(self):
        name = self.name_var.get().strip()
        phone = self.phone_var.get().strip()
        if not name:
            messagebox.showerror(i18n.T("error_title"), i18n.T("msg_name_required"))
            return
        if not PHONE_RE.match(phone):
            messagebox.showerror(i18n.T("error_title"), i18n.T("msg_phone_invalid"))
            return
        r1 = i18n.STATUS_ORDER[self.round_vars[1].current()]
        r2 = i18n.STATUS_ORDER[self.round_vars[2].current()]
        r3 = i18n.STATUS_ORDER[self.round_vars[3].current()]
        db.update_subject(self.subject["id"], name, phone, self.gender_var.get(),
                          self.note_var.get().strip(), r1, r2, r3)
        logger.log("EDIT", "%s %s" % (self.subject["subject_id"], self.subject["barcode"]))
        self.parent.refresh()
        self.parent.app.refresh_all()
        self.destroy()
        messagebox.showinfo(i18n.T("info_title"), i18n.T("saved_ok"))
