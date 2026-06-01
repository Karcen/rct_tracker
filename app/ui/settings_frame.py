# -*- coding: utf-8 -*-
"""系统设置选项卡：语言、条码规则、备份/恢复、数据目录、关于。"""

import os
import tkinter as tk
from tkinter import ttk, messagebox, filedialog

from app import config, db, i18n, logger


class SettingsFrame(ttk.Frame):
    def __init__(self, master, app):
        super().__init__(master)
        self.app = app
        self.settings = config.load_settings()
        self._build()

    def _build(self):
        wrap = ttk.Frame(self, padding=14)
        wrap.pack(fill="both", expand=True)

        # ---- 语言 ----
        lang_box = ttk.LabelFrame(wrap, text=i18n.T("set_language"), padding=12)
        lang_box.pack(fill="x", pady=6)
        self.lang_codes = ["zh", "en"]
        self.lang_combo = ttk.Combobox(lang_box, width=14, state="readonly",
                                       values=[i18n.T("lang_zh"), i18n.T("lang_en")])
        self.lang_combo.current(self.lang_codes.index(i18n.get_language()))
        self.lang_combo.pack(side="left")
        ttk.Button(lang_box, text=i18n.T("btn_save_settings"),
                   command=self._apply_language).pack(side="left", padx=10)

        # ---- 条码规则 ----
        rule = ttk.LabelFrame(wrap, text=i18n.T("set_barcode_rule_title"), padding=12)
        rule.pack(fill="x", pady=6)
        self.var_a = tk.StringVar(value=self.settings["group_a_prefix"])
        self.var_b = tk.StringVar(value=self.settings["group_b_prefix"])
        self.var_pad = tk.StringVar(value=str(self.settings["id_padding"]))
        self.var_sprefix = tk.StringVar(value=self.settings["subject_id_prefix"])
        self.var_spad = tk.StringVar(value=str(self.settings["subject_id_padding"]))
        grid = [
            (i18n.T("set_group_a_prefix"), self.var_a),
            (i18n.T("set_group_b_prefix"), self.var_b),
            (i18n.T("set_id_padding"), self.var_pad),
            (i18n.T("set_subject_prefix"), self.var_sprefix),
            (i18n.T("set_subject_padding"), self.var_spad),
        ]
        for i, (cap, var) in enumerate(grid):
            ttk.Label(rule, text=cap + "：").grid(row=i // 2, column=(i % 2) * 2,
                                                 sticky="e", padx=6, pady=5)
            ttk.Entry(rule, textvariable=var, width=12).grid(
                row=i // 2, column=(i % 2) * 2 + 1, sticky="w", padx=6, pady=5)
        ttk.Button(rule, text=i18n.T("btn_save_settings"),
                   command=self._save_barcode_rule).grid(row=3, column=0, columnspan=4, pady=(8, 0))

        # ---- 备份 / 恢复 ----
        bk = ttk.LabelFrame(wrap, text=i18n.T("backup_title"), padding=12)
        bk.pack(fill="x", pady=6)
        ttk.Button(bk, text=i18n.T("btn_backup_now"), command=self.backup_now).pack(side="left", padx=4)
        ttk.Button(bk, text=i18n.T("btn_restore"), command=self.restore).pack(side="left", padx=4)
        ttk.Button(bk, text=i18n.T("btn_open_data_dir"),
                   command=lambda: config.open_path(config.DATA_DIR)).pack(side="left", padx=4)

        # ---- 路径信息 ----
        info = ttk.Frame(wrap, padding=(0, 6))
        info.pack(fill="x")
        ttk.Label(info, text="%s：%s" % (i18n.T("db_path_label"), config.DB_PATH),
                  foreground="#666").pack(anchor="w")
        ttk.Label(info, text="%s：%s" % (i18n.T("backup_dir_label"), config.BACKUP_DIR),
                  foreground="#666").pack(anchor="w")

        # ---- 关于 ----
        about = ttk.LabelFrame(wrap, text=i18n.T("about_title"), padding=12)
        about.pack(fill="x", pady=6)
        ttk.Label(about, text=i18n.T("about_text", ver=config.APP_VERSION),
                  justify="left").pack(anchor="w")

    # ------------------------------------------------------------------
    def _apply_language(self):
        lang = self.lang_codes[self.lang_combo.current()]
        self.app.switch_language(lang)

    def _save_barcode_rule(self):
        try:
            pad = int(self.var_pad.get())
            spad = int(self.var_spad.get())
        except ValueError:
            messagebox.showerror(i18n.T("error_title"), i18n.T("settings_invalid_padding"))
            return
        if not (3 <= pad <= 10 and 3 <= spad <= 10):
            messagebox.showerror(i18n.T("error_title"), i18n.T("settings_invalid_padding"))
            return
        self.settings["group_a_prefix"] = self.var_a.get().strip() or "A"
        self.settings["group_b_prefix"] = self.var_b.get().strip() or "B"
        self.settings["id_padding"] = pad
        self.settings["subject_id_prefix"] = self.var_sprefix.get().strip() or "S"
        self.settings["subject_id_padding"] = spad
        config.save_settings(self.settings)
        self.app.settings = self.settings
        logger.log("SETTINGS", "barcode rule updated")
        messagebox.showinfo(i18n.T("info_title"), i18n.T("settings_saved"))

    def backup_now(self):
        try:
            path = db.backup_db("manual")
        except Exception as e:
            messagebox.showerror(i18n.T("error_title"), str(e))
            return
        logger.log("BACKUP", path)
        messagebox.showinfo(i18n.T("info_title"), i18n.T("backup_done", path=path))

    def restore(self):
        path = filedialog.askopenfilename(
            title=i18n.T("restore_select_title"),
            initialdir=config.BACKUP_DIR,
            filetypes=[("SQLite DB", "*.db"), ("All files", "*.*")])
        if not path or not os.path.exists(path):
            return
        if not messagebox.askyesno(i18n.T("confirm_title"), i18n.T("restore_confirm")):
            return
        try:
            db.restore_db(path)
        except Exception as e:
            messagebox.showerror(i18n.T("error_title"), str(e))
            return
        logger.log("RESTORE", path)
        messagebox.showinfo(i18n.T("info_title"), i18n.T("restore_done"))
        self.app.rebuild()  # 重建界面以加载恢复后的数据
