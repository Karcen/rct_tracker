# -*- coding: utf-8 -*-
"""操作日志模块：登记 / 扫码 / 状态修改 / 导出 / 备份等行为留痕。

日志同时写入两处：
1. 数据库 operation_logs 表（便于界面内查询）；
2. data/logs/YYYYMMDD.log 文本文件（便于离线/脱机查看）。
"""

import os
from datetime import datetime

from app import config, db


def log(action, detail=""):
    """记录一条操作日志。action 为操作类型（REGISTER/SCAN/STATUS/...）。"""
    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    try:
        conn = db.get_conn()
        conn.execute(
            "INSERT INTO operation_logs(timestamp, action, detail) VALUES(?,?,?)",
            (ts, action, detail),
        )
        conn.commit()
    except Exception:
        pass
    # 文本日志（失败不影响主流程）
    try:
        fn = os.path.join(config.LOG_DIR, datetime.now().strftime("%Y%m%d") + ".log")
        with open(fn, "a", encoding="utf-8") as f:
            f.write("%s\t%s\t%s\n" % (ts, action, detail))
    except Exception:
        pass


def get_logs(limit=1000):
    """读取最近的日志记录（倒序）。"""
    try:
        rows = db.get_conn().execute(
            "SELECT * FROM operation_logs ORDER BY id DESC LIMIT ?", (limit,)
        ).fetchall()
        return [dict(r) for r in rows]
    except Exception:
        return []
