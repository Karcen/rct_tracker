# -*- coding: utf-8 -*-
"""中英文国际化（i18n）模块。

使用方式：
    from app import i18n
    i18n.set_language("zh")
    i18n.T("app_title")
    i18n.T("round_n", n=1)   # 支持 str.format 占位符
"""

# 当前语言（模块级全局变量）
_current = "zh"

# 受试者随访状态内部编码顺序：空字符串表示「未随访」
STATUS_ORDER = ["", "valid", "void", "mismatch", "damaged", "lost"]


TRANSLATIONS = {
    "zh": {
        # ===== 通用 / 应用框架 =====
        "app_title": "RCT 线下追踪调研管理系统",
        "menu_register": "信息登记",
        "menu_scan": "扫码配对",
        "menu_ledger": "数据台账",
        "menu_stats": "统计分析",
        "menu_settings": "系统设置",
        "menu_logs": "操作日志",
        "language_label": "语言",
        "lang_zh": "简体中文",
        "lang_en": "English",
        "made_by_full": "{name} 制作",
        "contact_author": "联系作者",
        "status_ready": "就绪。请连接 USB 扫码枪，开始登记或扫码。",
        "info_title": "提示",
        "warn_title": "警告",
        "error_title": "错误",
        "confirm_title": "确认",
        "btn_refresh": "刷新",
        "ok": "确定",
        "cancel": "取消",

        # ===== 信息登记 =====
        "reg_title": "受试者信息登记",
        "field_name": "姓名",
        "field_phone": "手机号",
        "field_gender": "性别",
        "field_group": "RCT 分组",
        "field_note": "备注",
        "gender_male": "男",
        "gender_female": "女",
        "gender_other": "其他",
        "group_a": "干预组",
        "group_b": "对照组",
        "btn_save_register": "保存登记并生成条码",
        "btn_preview_barcode": "预览条码",
        "btn_print_barcode": "打印条码",
        "btn_clear": "清空",
        "reg_recent_title": "最近登记记录（点击选中可预览/打印其条码）",
        # 台账列名（登记/台账/导出共用）
        "col_subject_id": "受试者ID",
        "col_barcode": "条码编号",
        "col_name": "姓名",
        "col_phone": "手机号",
        "col_gender": "性别",
        "col_group": "分组",
        "col_register_time": "登记时间",
        "col_round1": "第1轮状态",
        "col_round2": "第2轮状态",
        "col_round3": "第3轮状态",
        "col_note": "备注",
        "no_preview": "（暂无条码预览）",
        "preview_hint": "条码预览",
        "msg_name_required": "请填写姓名。",
        "msg_phone_invalid": "手机号必须为 11 位数字，请检查后重新输入。",
        "msg_duplicate_phone": "该手机号已登记：{name}（条码 {barcode}）。",
        "msg_duplicate_continue": "是否仍要作为新记录继续登记？",
        "msg_register_success": "登记成功！条码：{barcode}",
        "ask_print_now": "是否立即打印该受试者的条码？",
        "barcode_dep_missing": "未安装条码依赖库（python-barcode / Pillow），无法生成条码。\n请先执行：pip install python-barcode pillow",

        # ===== 扫码配对 =====
        "current_round_label": "当前随访轮次：",
        "round_n": "第 {n} 轮",
        "scan_prompt": "扫码 / 输入条码：",
        "btn_lookup": "查询",
        "person_card_title": "受试者信息",
        "no_record_found": "未找到对应受试者记录",
        "btn_valid": "正常有效",
        "btn_void": "空白作废",
        "btn_mismatch": "信息不符",
        "btn_damaged": "条码损坏",
        "btn_lost": "失访",
        "btn_pending": "清除状态",
        "btn_undo": "撤销上一步",
        "status_marked": "已标记：第 {round} 轮 -> {status}",
        "undo_none": "没有可撤销的操作。",
        "undo_done": "已撤销上一步状态修改。",
        "scan_history_title": "本次扫码操作记录",
        "col_time": "时间",
        "col_round": "轮次",
        "col_status": "状态",
        "no_subject_selected": "请先扫码或查询出受试者，再标记状态。",
        "scan_focus_hint": "提示：光标需停留在输入框，扫码枪即可自动录入。",

        # ===== 随访状态标签 =====
        "st_pending": "未随访",
        "st_valid": "正常有效",
        "st_void": "空白作废",
        "st_mismatch": "信息不符",
        "st_damaged": "条码损坏",
        "st_lost": "失访",

        # ===== 数据台账 =====
        "search_label": "检索关键字：",
        "field_all": "全部字段",
        "field_subject_id": "受试者ID",
        "field_barcode": "条码编号",
        "group_all": "全部分组",
        "round_all": "全部轮次",
        "status_all": "全部状态",
        "round_filter_label": "随访轮次：",
        "status_filter_label": "状态：",
        "group_filter_label": "分组：",
        "btn_search": "查询",
        "btn_reset": "重置",
        "btn_export_excel": "导出 Excel",
        "btn_edit": "编辑选中",
        "btn_reprint": "重新打印条码",
        "btn_delete": "删除选中",
        "export_success": "已导出到：\n{path}",
        "export_open_q": "是否立即打开导出文件所在目录？",
        "delete_confirm": "确认删除选中的 {n} 条记录？此操作不可撤销（建议先备份）。",
        "edit_title": "编辑受试者信息",
        "nothing_selected": "请先在台账中选中记录。",
        "select_one_only": "编辑功能每次仅支持选中一条记录。",
        "saved_ok": "保存成功。",

        # ===== 统计分析 =====
        "stats_title": "样本统计",
        "stat_total": "总人数",
        "stat_group_a": "干预组人数",
        "stat_group_b": "对照组人数",
        "stat_round_col": "轮次",
        "stat_valid": "有效",
        "stat_void": "作废",
        "stat_mismatch": "信息不符",
        "stat_damaged": "条码损坏",
        "stat_lost": "失访",
        "stat_pending": "未随访",

        # ===== 系统设置 =====
        "settings_title": "系统设置",
        "set_language": "界面语言",
        "set_barcode_rule_title": "条码编码规则（仅影响新登记记录）",
        "set_group_a_prefix": "干预组前缀",
        "set_group_b_prefix": "对照组前缀",
        "set_id_padding": "条码序号位数",
        "set_subject_prefix": "受试者ID前缀",
        "set_subject_padding": "受试者ID位数",
        "btn_save_settings": "保存设置",
        "settings_saved": "设置已保存。",
        "settings_invalid_padding": "位数必须为 3 到 10 之间的整数。",
        "backup_title": "数据备份与恢复",
        "btn_backup_now": "立即备份数据库",
        "backup_done": "备份完成：\n{path}",
        "btn_restore": "从备份恢复",
        "restore_confirm": "恢复将覆盖当前全部数据，确认继续？\n（当前数据会自动先备份一次）",
        "restore_done": "恢复完成，界面已刷新。",
        "restore_select_title": "选择要恢复的备份文件",
        "btn_open_data_dir": "打开数据目录",
        "db_path_label": "数据库文件",
        "backup_dir_label": "备份目录",
        "about_title": "关于",
        "about_text": "RCT 线下追踪调研管理系统 v{ver}\n本地文件存储 · 纸质问卷 + 条码 + 扫码枪全流程管理\n数据均保存在 data 目录，可整体拷贝备份。",

        # ===== 操作日志 =====
        "logs_title": "操作日志（登记 / 扫码 / 状态修改 / 导出 / 备份）",
        "log_col_time": "时间",
        "log_col_action": "操作类型",
        "log_col_detail": "详情",
        "btn_export_logs": "导出日志",
        "logs_exported": "日志已导出：\n{path}",
    },

    "en": {
        # ===== Common / framework =====
        "app_title": "RCT Field Tracking Manager",
        "menu_register": "Register",
        "menu_scan": "Scan & Match",
        "menu_ledger": "Ledger",
        "menu_stats": "Statistics",
        "menu_settings": "Settings",
        "menu_logs": "Logs",
        "language_label": "Language",
        "lang_zh": "简体中文",
        "lang_en": "English",
        "made_by_full": "Made by {name}",
        "contact_author": "Contact",
        "status_ready": "Ready. Connect the USB scanner to start registering or scanning.",
        "info_title": "Info",
        "warn_title": "Warning",
        "error_title": "Error",
        "confirm_title": "Confirm",
        "btn_refresh": "Refresh",
        "ok": "OK",
        "cancel": "Cancel",

        # ===== Registration =====
        "reg_title": "Subject Registration",
        "field_name": "Name",
        "field_phone": "Mobile No.",
        "field_gender": "Gender",
        "field_group": "RCT Group",
        "field_note": "Note",
        "gender_male": "Male",
        "gender_female": "Female",
        "gender_other": "Other",
        "group_a": "Intervention",
        "group_b": "Control",
        "btn_save_register": "Save & Generate Barcode",
        "btn_preview_barcode": "Preview Barcode",
        "btn_print_barcode": "Print Barcode",
        "btn_clear": "Clear",
        "reg_recent_title": "Recent registrations (click a row to preview/print its barcode)",
        # Ledger column headers (shared by register/ledger/export)
        "col_subject_id": "Subject ID",
        "col_barcode": "Barcode",
        "col_name": "Name",
        "col_phone": "Mobile",
        "col_gender": "Gender",
        "col_group": "Group",
        "col_register_time": "Registered at",
        "col_round1": "Round 1",
        "col_round2": "Round 2",
        "col_round3": "Round 3",
        "col_note": "Note",
        "no_preview": "(no barcode preview)",
        "preview_hint": "Barcode preview",
        "msg_name_required": "Please enter the name.",
        "msg_phone_invalid": "Mobile number must be exactly 11 digits. Please re-enter.",
        "msg_duplicate_phone": "This mobile number already exists: {name} (barcode {barcode}).",
        "msg_duplicate_continue": "Continue registering as a new record anyway?",
        "msg_register_success": "Registered! Barcode: {barcode}",
        "ask_print_now": "Print this subject's barcode now?",
        "barcode_dep_missing": "Barcode libraries (python-barcode / Pillow) are not installed.\nRun: pip install python-barcode pillow",

        # ===== Scan =====
        "current_round_label": "Current follow-up round:",
        "round_n": "Round {n}",
        "scan_prompt": "Scan / type barcode:",
        "btn_lookup": "Look up",
        "person_card_title": "Subject Information",
        "no_record_found": "No matching subject found",
        "btn_valid": "Valid",
        "btn_void": "Void/Blank",
        "btn_mismatch": "Mismatch",
        "btn_damaged": "Damaged",
        "btn_lost": "Lost",
        "btn_pending": "Clear status",
        "btn_undo": "Undo last",
        "status_marked": "Marked: round {round} -> {status}",
        "undo_none": "Nothing to undo.",
        "undo_done": "Last status change has been undone.",
        "scan_history_title": "Scan actions in this session",
        "col_time": "Time",
        "col_round": "Round",
        "col_status": "Status",
        "no_subject_selected": "Scan or look up a subject first, then mark the status.",
        "scan_focus_hint": "Tip: keep the cursor in the input box so the scanner can type automatically.",

        # ===== Status labels =====
        "st_pending": "Not yet",
        "st_valid": "Valid",
        "st_void": "Void/Blank",
        "st_mismatch": "Mismatch",
        "st_damaged": "Damaged",
        "st_lost": "Lost",

        # ===== Ledger =====
        "search_label": "Keyword:",
        "field_all": "All fields",
        "field_subject_id": "Subject ID",
        "field_barcode": "Barcode",
        "group_all": "All groups",
        "round_all": "All rounds",
        "status_all": "All status",
        "round_filter_label": "Round:",
        "status_filter_label": "Status:",
        "group_filter_label": "Group:",
        "btn_search": "Search",
        "btn_reset": "Reset",
        "btn_export_excel": "Export Excel",
        "btn_edit": "Edit selected",
        "btn_reprint": "Reprint barcode",
        "btn_delete": "Delete selected",
        "export_success": "Exported to:\n{path}",
        "export_open_q": "Open the export folder now?",
        "delete_confirm": "Delete the selected {n} record(s)? This cannot be undone (back up first).",
        "edit_title": "Edit Subject",
        "nothing_selected": "Please select a record in the ledger first.",
        "select_one_only": "Editing supports only one selected record at a time.",
        "saved_ok": "Saved.",

        # ===== Statistics =====
        "stats_title": "Sample Statistics",
        "stat_total": "Total subjects",
        "stat_group_a": "Intervention",
        "stat_group_b": "Control",
        "stat_round_col": "Round",
        "stat_valid": "Valid",
        "stat_void": "Void",
        "stat_mismatch": "Mismatch",
        "stat_damaged": "Damaged",
        "stat_lost": "Lost",
        "stat_pending": "Not yet",

        # ===== Settings =====
        "settings_title": "Settings",
        "set_language": "Interface language",
        "set_barcode_rule_title": "Barcode rule (affects new records only)",
        "set_group_a_prefix": "Intervention prefix",
        "set_group_b_prefix": "Control prefix",
        "set_id_padding": "Barcode digit count",
        "set_subject_prefix": "Subject ID prefix",
        "set_subject_padding": "Subject ID digit count",
        "btn_save_settings": "Save settings",
        "settings_saved": "Settings saved.",
        "settings_invalid_padding": "Digit count must be an integer between 3 and 10.",
        "backup_title": "Backup & Restore",
        "btn_backup_now": "Back up database now",
        "backup_done": "Backup done:\n{path}",
        "btn_restore": "Restore from backup",
        "restore_confirm": "Restoring overwrites all current data. Continue?\n(Current data is auto-backed-up first.)",
        "restore_done": "Restore complete, UI refreshed.",
        "restore_select_title": "Choose a backup file to restore",
        "btn_open_data_dir": "Open data folder",
        "db_path_label": "Database file",
        "backup_dir_label": "Backup folder",
        "about_title": "About",
        "about_text": "RCT Field Tracking Manager v{ver}\nLocal file storage · paper questionnaire + barcode + scanner workflow\nAll data lives in the data folder and can be copied as a whole.",

        # ===== Logs =====
        "logs_title": "Operation logs (register / scan / status / export / backup)",
        "log_col_time": "Time",
        "log_col_action": "Action",
        "log_col_detail": "Detail",
        "btn_export_logs": "Export logs",
        "logs_exported": "Logs exported:\n{path}",
    },
}


def set_language(lang):
    """切换当前语言（zh / en）。"""
    global _current
    if lang in TRANSLATIONS:
        _current = lang


def get_language():
    """返回当前语言代码。"""
    return _current


def T(key, **kwargs):
    """翻译查询；找不到时回退中文，再回退 key 本身。支持 format 占位符。"""
    text = TRANSLATIONS.get(_current, {}).get(key)
    if text is None:
        text = TRANSLATIONS["zh"].get(key, key)
    if kwargs:
        try:
            text = text.format(**kwargs)
        except Exception:
            pass
    return text


# ===== 编码 -> 显示标签 的便捷函数 =====

def status_label(code):
    """随访状态编码转可读标签。"""
    return T("st_" + (code if code else "pending"))


def status_options(include_all=False):
    """返回 [(编码, 标签)] 列表，供下拉框使用。"""
    opts = [(c, status_label(c)) for c in STATUS_ORDER]
    if include_all:
        opts = [("__all__", T("status_all"))] + opts
    return opts


def group_label(code):
    """分组编码转标签：A=干预组，B=对照组。"""
    if code == "A":
        return T("group_a")
    if code == "B":
        return T("group_b")
    return code


def group_options(include_all=False):
    opts = [("A", T("group_a")), ("B", T("group_b"))]
    if include_all:
        opts = [("__all__", T("group_all"))] + opts
    return opts


def gender_label(code):
    return {"M": T("gender_male"), "F": T("gender_female"),
            "O": T("gender_other")}.get(code, code)


def gender_options():
    return [("M", T("gender_male")), ("F", T("gender_female")),
            ("O", T("gender_other"))]
