# -*- coding: utf-8 -*-
"""SQLite 本地数据访问层（data access layer）。

为什么用 SQLite：
- 它是 Python 标准库自带的「文件型数据库」，整个库就是一个 .db 文件，
  无需安装/部署任何数据库服务，直接拷贝该文件即可备份/迁移，满足
  「本地文件存储、无需独立数据库」的需求；
- 同时支持事务（ACID），保证「实时保存」与「可回滚」。

表结构：
- subjects        受试者主台账（一人一行，条码全程复用）
- counters        各类自增序号（按组序号、全局受试者序号）
- operation_logs  操作日志
"""

import os
import shutil
import sqlite3
from datetime import datetime

from app import config

_conn = None  # 模块级共享连接


def get_conn():
    """获取（惰性创建）数据库连接，行工厂设为 Row 以便按列名取值。"""
    global _conn
    if _conn is None:
        _conn = sqlite3.connect(config.DB_PATH, check_same_thread=False)
        _conn.row_factory = sqlite3.Row
        _conn.execute("PRAGMA foreign_keys = ON")
    return _conn


def _now():
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def init_db():
    """初始化表结构（幂等）。"""
    conn = get_conn()
    cur = conn.cursor()
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS subjects (
            id            INTEGER PRIMARY KEY AUTOINCREMENT,
            subject_id    TEXT UNIQUE NOT NULL,   -- 全局唯一受试者ID，如 S000001
            barcode       TEXT UNIQUE NOT NULL,   -- 条码编码，如 A00001，与ID一一绑定
            name          TEXT NOT NULL,
            phone         TEXT NOT NULL,
            gender        TEXT,                   -- M/F/O
            group_type    TEXT NOT NULL,          -- A=干预组 B=对照组
            register_time TEXT NOT NULL,
            round1_status TEXT DEFAULT '',        -- 随访状态编码，空=未随访
            round2_status TEXT DEFAULT '',
            round3_status TEXT DEFAULT '',
            note          TEXT DEFAULT ''
        )
        """
    )
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS counters (
            name  TEXT PRIMARY KEY,
            value INTEGER NOT NULL DEFAULT 0
        )
        """
    )
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS operation_logs (
            id        INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT NOT NULL,
            action    TEXT NOT NULL,
            detail    TEXT
        )
        """
    )
    # 常用索引，加速检索
    cur.execute("CREATE INDEX IF NOT EXISTS idx_phone ON subjects(phone)")
    cur.execute("CREATE INDEX IF NOT EXISTS idx_group ON subjects(group_type)")
    conn.commit()


# ----------------------------------------------------------------------
# 自增序号
# ----------------------------------------------------------------------

def next_counter(name):
    """原子地取下一个序号（counters 表）。"""
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("INSERT OR IGNORE INTO counters(name, value) VALUES(?, 0)", (name,))
    cur.execute("UPDATE counters SET value = value + 1 WHERE name = ?", (name,))
    conn.commit()
    return cur.execute("SELECT value FROM counters WHERE name = ?", (name,)).fetchone()[0]


# ----------------------------------------------------------------------
# 登记 / 查询
# ----------------------------------------------------------------------

def phone_exists(phone):
    """返回首个使用该手机号的记录（用于重复预警），无则返回 None。"""
    conn = get_conn()
    row = conn.execute(
        "SELECT * FROM subjects WHERE phone = ? ORDER BY id LIMIT 1", (phone,)
    ).fetchone()
    return dict(row) if row else None


def add_subject(name, phone, gender, group_type, note=""):
    """新增受试者，自动生成全局ID与条码，返回新记录 dict。

    条码规则：分组前缀 + 补零序号（按组独立计数），如 A00001 / B00001。
    受试者ID规则：全局前缀 + 全局补零序号，如 S000001。
    """
    settings = config.load_settings()
    # 1) 条码（按组序号）
    seq = next_counter("group_" + group_type)
    prefix = settings["group_a_prefix"] if group_type == "A" else settings["group_b_prefix"]
    barcode = "%s%s" % (prefix, str(seq).zfill(int(settings["id_padding"])))
    # 2) 全局受试者ID
    gseq = next_counter("subject")
    subject_id = "%s%s" % (
        settings["subject_id_prefix"],
        str(gseq).zfill(int(settings["subject_id_padding"])),
    )

    conn = get_conn()
    conn.execute(
        """
        INSERT INTO subjects
            (subject_id, barcode, name, phone, gender, group_type,
             register_time, round1_status, round2_status, round3_status, note)
        VALUES (?,?,?,?,?,?,?,?,?,?,?)
        """,
        (subject_id, barcode, name, phone, gender, group_type, _now(), "", "", "", note),
    )
    conn.commit()
    return get_by_barcode(barcode)


def get_by_barcode(barcode):
    row = get_conn().execute(
        "SELECT * FROM subjects WHERE barcode = ?", (barcode,)
    ).fetchone()
    return dict(row) if row else None


def get_by_subject_id(subject_id):
    row = get_conn().execute(
        "SELECT * FROM subjects WHERE subject_id = ?", (subject_id,)
    ).fetchone()
    return dict(row) if row else None


def get_by_id(row_id):
    row = get_conn().execute("SELECT * FROM subjects WHERE id = ?", (row_id,)).fetchone()
    return dict(row) if row else None


def all_subjects():
    rows = get_conn().execute("SELECT * FROM subjects ORDER BY id ASC").fetchall()
    return [dict(r) for r in rows]


def search(keyword="", field="all", group="", round_no=0, status=None):
    """多条件检索。

    keyword  关键字
    field    检索字段：all/subject_id/barcode/name/phone
    group    分组：A/B/空(全部)
    round_no 轮次：1/2/3/0(不限)
    status   该轮状态编码；None 表示不按状态过滤（""为未随访也是有效过滤值）
    """
    q = "SELECT * FROM subjects WHERE 1=1"
    params = []
    kw = (keyword or "").strip()
    if kw:
        like = "%" + kw + "%"
        if field == "subject_id":
            q += " AND subject_id LIKE ?"; params.append(like)
        elif field == "barcode":
            q += " AND barcode LIKE ?"; params.append(like)
        elif field == "name":
            q += " AND name LIKE ?"; params.append(like)
        elif field == "phone":
            q += " AND phone LIKE ?"; params.append(like)
        else:  # all
            q += " AND (subject_id LIKE ? OR barcode LIKE ? OR name LIKE ? OR phone LIKE ?)"
            params += [like, like, like, like]
    if group in ("A", "B"):
        q += " AND group_type = ?"; params.append(group)
    if round_no in (1, 2, 3) and status is not None:
        q += " AND round%d_status = ?" % round_no
        params.append(status)
    q += " ORDER BY id ASC"
    rows = get_conn().execute(q, params).fetchall()
    return [dict(r) for r in rows]


# ----------------------------------------------------------------------
# 状态修改 / 编辑 / 删除
# ----------------------------------------------------------------------

def update_round_status(barcode, round_no, status):
    """修改某轮随访状态，返回修改前的旧值（用于撤销）。"""
    if round_no not in (1, 2, 3):
        raise ValueError("round_no must be 1/2/3")
    conn = get_conn()
    row = conn.execute("SELECT * FROM subjects WHERE barcode = ?", (barcode,)).fetchone()
    if not row:
        return None
    old = row["round%d_status" % round_no]
    conn.execute(
        "UPDATE subjects SET round%d_status = ? WHERE barcode = ?" % round_no,
        (status, barcode),
    )
    conn.commit()
    return old


def update_subject(row_id, name, phone, gender, note,
                   round1=None, round2=None, round3=None):
    """编辑受试者可修改字段（分组与条码锁定，保证一人一码全程复用）。"""
    conn = get_conn()
    sets = ["name = ?", "phone = ?", "gender = ?", "note = ?"]
    params = [name, phone, gender, note]
    if round1 is not None:
        sets.append("round1_status = ?"); params.append(round1)
    if round2 is not None:
        sets.append("round2_status = ?"); params.append(round2)
    if round3 is not None:
        sets.append("round3_status = ?"); params.append(round3)
    params.append(row_id)
    conn.execute("UPDATE subjects SET %s WHERE id = ?" % ", ".join(sets), params)
    conn.commit()


def delete_subject(row_id):
    conn = get_conn()
    conn.execute("DELETE FROM subjects WHERE id = ?", (row_id,))
    conn.commit()


# ----------------------------------------------------------------------
# 统计
# ----------------------------------------------------------------------

def get_stats():
    """返回统计字典：总数、各组人数、各轮各状态计数。"""
    conn = get_conn()
    total = conn.execute("SELECT COUNT(*) FROM subjects").fetchone()[0]
    ga = conn.execute("SELECT COUNT(*) FROM subjects WHERE group_type='A'").fetchone()[0]
    gb = conn.execute("SELECT COUNT(*) FROM subjects WHERE group_type='B'").fetchone()[0]
    rounds = {}
    from app.i18n import STATUS_ORDER
    for r in (1, 2, 3):
        col = "round%d_status" % r
        counts = {}
        for code in STATUS_ORDER:
            counts[code] = conn.execute(
                "SELECT COUNT(*) FROM subjects WHERE %s = ?" % col, (code,)
            ).fetchone()[0]
        rounds[r] = counts
    return {"total": total, "group_a": ga, "group_b": gb, "rounds": rounds}


# ----------------------------------------------------------------------
# 备份 / 恢复（数据安全）
# ----------------------------------------------------------------------

def backup_db(reason="manual"):
    """使用 SQLite 在线备份 API 生成数据库快照，返回备份文件路径。"""
    init_db()  # 确保库存在
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    dst = os.path.join(config.BACKUP_DIR, "rct_data_%s_%s.db" % (ts, reason))
    bck = sqlite3.connect(dst)
    try:
        with bck:
            get_conn().backup(bck)
    finally:
        bck.close()
    return dst


def list_backups():
    """列出全部备份文件（按时间倒序）。"""
    if not os.path.isdir(config.BACKUP_DIR):
        return []
    files = [os.path.join(config.BACKUP_DIR, f)
             for f in os.listdir(config.BACKUP_DIR) if f.endswith(".db")]
    files.sort(key=lambda p: os.path.getmtime(p), reverse=True)
    return files


def restore_db(backup_path):
    """从备份恢复：先自动备份当前库，再覆盖，最后重新连接。"""
    backup_db(reason="before_restore")
    global _conn
    if _conn is not None:
        _conn.close()
        _conn = None
    shutil.copy2(backup_path, config.DB_PATH)
    get_conn()  # 重新建立连接
