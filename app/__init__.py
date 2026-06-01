# -*- coding: utf-8 -*-
"""RCT 线下追踪调研管理系统 —— 应用包（application package）。

逻辑分层（layered architecture）：
    config        全局路径与设置持久化
    i18n          中英文国际化
    db            SQLite 本地数据访问层
    logger        操作日志
    barcode_util  Code128 一维码生成与打印
    excel_export  台账导出 Excel
    ui/*          Tkinter 图形界面
"""

__version__ = "1.0.0"
