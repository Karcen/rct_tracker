# -*- coding: utf-8 -*-
"""信息登记选项卡：录入受试者 -> 校验 -> 生成全局ID与条码 -> 预览/打印。"""

import os
import re
import tkinter as tk
from tkinter import ttk, messagebox

from app import db, i18n, logger, barcode_util

# 图片预览：优先使用 Pillow，缺失时回退到 Tk 自带 PNG 读取
try:
    from PIL import Image, ImageTk
    _HAS_PIL = True
except Exception:
    _HAS_PIL = False

PHONE_RE = re.compile(r"^\d{11}$")  # 手机号：11 位数字


class RegisterFrame(ttk.Frame):
    def __init__(self, master, app):
        super().__init__(master)
        self.app = app
        self._preview_img = None       # 保持图片引用，防止被回收
        self.selected_subject = None   # 当前选中的受试者（用于预览/打印）
        self._build()
        self._refresh_recent()

    # ------------------------------------------------------------------
    def _build(self):
        # 左侧表单 + 右侧条码预览
        body = ttk.Frame(self)
        body.pack(fill="both", expand=True, padx=10, pady=8)

        form = ttk.LabelFrame(body, text=i18n.T("reg_title"), padding=12)
        form.grid(row=0, column=0, sticky="nsew", padx=(0, 10))

        self.name_var = tk.StringVar()
        self.phone_var = tk.StringVar()
        self.gender_var = tk.StringVar(value="M")
        self.group_var = tk.StringVar(value="A")
        self.note_var = tk.StringVar()

        # 姓名
        ttk.Label(form, text=i18n.T("field_name") + "：").grid(row=0, column=0, sticky="e", pady=6)
        ttk.Entry(form, textvariable=self.name_var, width=24).grid(row=0, column=1, sticky="w", pady=6)

        # 手机号
        ttk.Label(form, text=i18n.T("field_phone") + "：").grid(row=1, column=0, sticky="e", pady=6)
        ttk.Entry(form, textvariable=self.phone_var, width=24).grid(row=1, column=1, sticky="w", pady=6)

        # 性别
        ttk.Label(form, text=i18n.T("field_gender") + "：").grid(row=2, column=0, sticky="e", pady=6)
        gender_box = ttk.Frame(form)
        gender_box.grid(row=2, column=1, sticky="w", pady=6)
        for code, label in i18n.gender_options():
            ttk.Radiobutton(gender_box, text=label, value=code,
                            variable=self.gender_var).pack(side="left", padx=(0, 8))

        # 分组
        ttk.Label(form, text=i18n.T("field_group") + "：").grid(row=3, column=0, sticky="e", pady=6)
        group_box = ttk.Frame(form)
        group_box.grid(row=3, column=1, sticky="w", pady=6)
        for code, label in i18n.group_options():
            ttk.Radiobutton(group_box, text="%s (%s)" % (label, code), value=code,
                            variable=self.group_var).pack(side="left", padx=(0, 8))

        # 备注
        ttk.Label(form, text=i18n.T("field_note") + "：").grid(row=4, column=0, sticky="e", pady=6)
        ttk.Entry(form, textvariable=self.note_var, width=24).grid(row=4, column=1, sticky="w", pady=6)

        # 按钮区
        btns = ttk.Frame(form)
        btns.grid(row=5, column=0, columnspan=2, pady=(14, 0))
        ttk.Button(btns, text=i18n.T("btn_save_register"), command=self.save).pack(side="left", padx=4)
        ttk.Button(btns, text=i18n.T("btn_clear"), command=lambda: self._clear_form()).pack(side="left", padx=4)

        # 右侧：条码预览
        preview = ttk.LabelFrame(body, text=i18n.T("preview_hint"), padding=12)
        preview.grid(row=0, column=1, sticky="nsew")
        self.preview_label = ttk.Label(preview, text=i18n.T("no_preview"), anchor="center")
        self.preview_label.pack(fill="both", expand=True)
        pbtns = ttk.Frame(preview)
        pbtns.pack(pady=(8, 0))
        ttk.Button(pbtns, text=i18n.T("btn_preview_barcode"), command=self.preview_barcode).pack(side="left", padx=4)
        ttk.Button(pbtns, text=i18n.T("btn_print_barcode"), command=self.print_barcode).pack(side="left", padx=4)

        body.columnconfigure(0, weight=1)
        body.columnconfigure(1, weight=1)
        body.rowconfigure(0, weight=1)

        # 最近登记列表
        recent = ttk.LabelFrame(self, text=i18n.T("reg_recent_title"), padding=8)
        recent.pack(fill="both", expand=True, padx=10, pady=(0, 8))
        cols = ("subject_id", "barcode", "name", "phone", "gender", "group", "register_time")
        self.tree = ttk.Treeview(recent, columns=cols, show="headings", height=8)
        widths = {"subject_id": 90, "barcode": 90, "name": 100, "phone": 120,
                  "gender": 60, "group": 90, "register_time": 150}
        for c in cols:
            self.tree.heading(c, text=i18n.T("col_" + c))
            self.tree.column(c, width=widths[c], anchor="center")
        vsb = ttk.Scrollbar(recent, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=vsb.set)
        self.tree.pack(side="left", fill="both", expand=True)
        vsb.pack(side="right", fill="y")
        self.tree.bind("<<TreeviewSelect>>", self._on_select_recent)

    # ------------------------------------------------------------------
    def save(self):
        name = self.name_var.get().strip()
        phone = self.phone_var.get().strip()
        # 1) 姓名校验
        if not name:
            messagebox.showerror(i18n.T("error_title"), i18n.T("msg_name_required"))
            return
        # 2) 手机号强制 11 位数字校验
        if not PHONE_RE.match(phone):
            messagebox.showerror(i18n.T("error_title"), i18n.T("msg_phone_invalid"))
            return
        # 3) 重复手机号预警
        dup = db.phone_exists(phone)
        if dup:
            msg = i18n.T("msg_duplicate_phone", name=dup["name"], barcode=dup["barcode"]) \
                + "\n" + i18n.T("msg_duplicate_continue")
            if not messagebox.askyesno(i18n.T("warn_title"), msg):
                return

        gender = self.gender_var.get()
        group = self.group_var.get()
        note = self.note_var.get().strip()
        try:
            subject = db.add_subject(name, phone, gender, group, note)
        except Exception as e:
            messagebox.showerror(i18n.T("error_title"), str(e))
            return

        logger.log("REGISTER", "%s %s %s %s %s" % (
            subject["subject_id"], subject["barcode"], name, phone, group))
        self.selected_subject = subject

        # 生成并预览条码
        ok = self._generate_and_preview(subject)
        self._refresh_recent()
        self.app.refresh_all()
        self.app.set_status(i18n.T("msg_register_success", barcode=subject["barcode"]))
        messagebox.showinfo(i18n.T("info_title"),
                            i18n.T("msg_register_success", barcode=subject["barcode"]))

        # 询问是否立即打印
        if ok and messagebox.askyesno(i18n.T("info_title"), i18n.T("ask_print_now")):
            self.print_barcode()

        self._clear_form(keep_group=True)

    def _generate_and_preview(self, subject):
        if not barcode_util.HAS_BARCODE:
            messagebox.showwarning(i18n.T("warn_title"), i18n.T("barcode_dep_missing"))
            return False
        try:
            path = barcode_util.generate_barcode_image(subject["barcode"])
            self._show_image(path)
            return True
        except Exception as e:
            messagebox.showwarning(i18n.T("warn_title"), str(e))
            return False

    def _show_image(self, path, target_w=380):
        """在预览区显示条码图片（PIL 优先，回退 Tk PhotoImage）。"""
        if not path or not os.path.exists(path):
            self.preview_label.config(image="", text=i18n.T("no_preview"))
            return
        try:
            if _HAS_PIL:
                img = Image.open(path)
                w, h = img.size
                scale = target_w / float(w)
                img = img.resize((target_w, max(1, int(h * scale))))
                self._preview_img = ImageTk.PhotoImage(img)
            else:
                photo = tk.PhotoImage(file=path)
                # 仅支持整数缩小
                factor = max(1, int(photo.width() / target_w))
                if factor > 1:
                    photo = photo.subsample(factor, factor)
                self._preview_img = photo
            self.preview_label.config(image=self._preview_img, text="")
        except Exception:
            self.preview_label.config(image="", text=i18n.T("no_preview"))

    def preview_barcode(self):
        if not self.selected_subject:
            messagebox.showinfo(i18n.T("info_title"), i18n.T("nothing_selected"))
            return
        self._generate_and_preview(self.selected_subject)

    def print_barcode(self):
        if not self.selected_subject:
            messagebox.showinfo(i18n.T("info_title"), i18n.T("nothing_selected"))
            return
        try:
            barcode_util.print_subjects([self.selected_subject])
            logger.log("PRINT", "barcode %s" % self.selected_subject["barcode"])
        except Exception as e:
            messagebox.showwarning(i18n.T("warn_title"), str(e))

    # ------------------------------------------------------------------
    def _clear_form(self, keep_group=False):
        self.name_var.set("")
        self.phone_var.set("")
        self.gender_var.set("M")
        self.note_var.set("")
        if not keep_group:
            self.group_var.set("A")

    def _refresh_recent(self, limit=50):
        for iid in self.tree.get_children():
            self.tree.delete(iid)
        rows = db.all_subjects()[-limit:][::-1]  # 最近 limit 条，倒序展示
        for r in rows:
            self.tree.insert("", "end", iid=str(r["id"]), values=(
                r["subject_id"], r["barcode"], r["name"], r["phone"],
                i18n.gender_label(r["gender"]), i18n.group_label(r["group_type"]),
                r["register_time"]))

    def _on_select_recent(self, event=None):
        sel = self.tree.selection()
        if not sel:
            return
        subject = db.get_by_id(int(sel[0]))
        if subject:
            self.selected_subject = subject
            # 选中即尝试预览其条码（若图片已存在或可生成）
            if barcode_util.HAS_BARCODE:
                try:
                    path = barcode_util.generate_barcode_image(subject["barcode"])
                    self._show_image(path)
                except Exception:
                    pass
