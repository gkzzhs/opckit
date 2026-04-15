#!/usr/bin/env python3
"""OPCKit 共享数据库 CLI — 所有 Skill 通过此脚本读写 ~/.opckit/data/opckit.db"""

import argparse, json, os, sqlite3, sys
from datetime import datetime, date, timedelta
from pathlib import Path

DB_PATH = Path(os.environ.get("OPCKIT_DB_PATH", Path.home() / ".opckit" / "data" / "opckit.db"))
CONFIG_DIR = Path.home() / ".opckit" / "config"
MAX_LIMIT = 50
DEFAULT_LIMIT = 10

SCHEMA = """
CREATE TABLE IF NOT EXISTS clients (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    industry TEXT,
    needs TEXT,
    budget TEXT,
    status TEXT DEFAULT 'potential',
    tags TEXT,
    notes TEXT,
    last_contact DATE DEFAULT CURRENT_DATE,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);
CREATE TABLE IF NOT EXISTS ledger (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    type TEXT NOT NULL,
    amount REAL NOT NULL,
    client_name TEXT,
    category TEXT,
    note TEXT,
    date DATE DEFAULT CURRENT_DATE,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);
CREATE TABLE IF NOT EXISTS content_log (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL,
    platform TEXT,
    content_type TEXT,
    status TEXT DEFAULT 'draft',
    publish_date DATE,
    performance TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);
"""

def log(msg): print(msg, file=sys.stderr)
def out(data): print(json.dumps(data, ensure_ascii=False, default=str))

def get_db():
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    conn.executescript(SCHEMA)
    return conn

def clamp_limit(val):
    return min(max(1, val), MAX_LIMIT)

# ── client ──────────────────────────────────────────────
def client_add(args):
    data = json.loads(args.data)
    db = get_db()
    fields = {k: data.get(k) for k in ("name","industry","needs","budget","status","tags","notes")}
    if not fields.get("name"):
        log("错误: name 字段必填"); sys.exit(1)
    if fields.get("tags") and isinstance(fields["tags"], list):
        fields["tags"] = json.dumps(fields["tags"], ensure_ascii=False)
    cols = [k for k,v in fields.items() if v is not None]
    vals = [fields[k] for k in cols]
    db.execute(f"INSERT INTO clients ({','.join(cols)}) VALUES ({','.join('?'*len(cols))})", vals)
    db.commit()
    rid = db.execute("SELECT last_insert_rowid()").fetchone()[0]
    log(f"✅ 客户「{fields['name']}」已录入 (ID: {rid})")
    out({"ok": True, "id": rid, "name": fields["name"]})

def client_list(args):
    db = get_db()
    limit = clamp_limit(args.limit)
    where_clauses, params = [], []
    if args.status:
        where_clauses.append("status=?"); params.append(args.status)
    if args.search:
        where_clauses.append("(name LIKE ? OR needs LIKE ?)"); params += [f"%{args.search}%"]*2
    where_sql = f" WHERE {' AND '.join(where_clauses)}" if where_clauses else ""
    q = f"SELECT * FROM clients{where_sql}"
    q += f" ORDER BY last_contact DESC LIMIT ? OFFSET ?"
    params += [limit, args.offset]
    rows = [dict(r) for r in db.execute(q, params).fetchall()]
    total = db.execute(f"SELECT COUNT(*) FROM clients{where_sql}", params[:-2]).fetchone()[0]
    log(f"📋 客户列表: 返回 {len(rows)} 条 (共 {total} 条)")
    out({"total": total, "returned": len(rows), "offset": args.offset, "clients": rows})

def client_stale(args):
    db = get_db()
    limit = clamp_limit(args.limit)
    cutoff = (date.today() - timedelta(days=args.days)).isoformat()
    rows = [dict(r) for r in db.execute(
        "SELECT * FROM clients WHERE last_contact<=? AND status IN ('potential','active') ORDER BY last_contact LIMIT ?",
        (cutoff, limit)).fetchall()]
    log(f"⏰ {len(rows)} 个客户超过 {args.days} 天未跟进")
    out({"stale_days": args.days, "count": len(rows), "clients": rows})

def client_update(args):
    data = json.loads(args.data)
    db = get_db()
    sets, vals = [], []
    for k in ("name","industry","needs","budget","status","tags","notes"):
        if k in data:
            v = data[k]
            if k == "tags" and isinstance(v, list): v = json.dumps(v, ensure_ascii=False)
            sets.append(f"{k}=?"); vals.append(v)
    sets.append("last_contact=?"); vals.append(date.today().isoformat())
    vals.append(args.id)
    cur = db.execute(f"UPDATE clients SET {','.join(sets)} WHERE id=?", vals)
    if cur.rowcount == 0:
        db.rollback()
        log(f"❌ 客户 ID:{args.id} 不存在")
        out({"ok": False, "error": f"client {args.id} not found"})
        sys.exit(1)
    db.commit()
    log(f"✅ 客户 ID:{args.id} 已更新")
    out({"ok": True, "id": args.id})

def client_count(args):
    db = get_db()
    total = db.execute("SELECT COUNT(*) FROM clients").fetchone()[0]
    by_status = {r[0]: r[1] for r in db.execute("SELECT status, COUNT(*) FROM clients GROUP BY status").fetchall()}
    log(f"📊 客户总数: {total}")
    out({"total": total, "by_status": by_status})

# ── ledger ──────────────────────────────────────────────
def ledger_income(args):
    if args.amount <= 0:
        log("❌ amount 必须大于 0")
        out({"ok": False, "error": "amount must be greater than 0"})
        sys.exit(1)
    db = get_db()
    db.execute("INSERT INTO ledger (type,amount,client_name,note) VALUES ('income',?,?,?)",
               (args.amount, args.from_client, args.note))
    db.commit()
    log(f"✅ 收入 ¥{args.amount} 已记录")
    out({"ok": True, "type": "income", "amount": args.amount})

def ledger_expense(args):
    if args.amount <= 0:
        log("❌ amount 必须大于 0")
        out({"ok": False, "error": "amount must be greater than 0"})
        sys.exit(1)
    db = get_db()
    db.execute("INSERT INTO ledger (type,amount,category,note) VALUES ('expense',?,?,?)",
               (args.amount, args.category, args.note))
    db.commit()
    log(f"✅ 支出 ¥{args.amount} 已记录")
    out({"ok": True, "type": "expense", "amount": args.amount})

def ledger_report(args):
    db = get_db()
    month = args.month or date.today().strftime("%Y-%m")
    inc = db.execute("SELECT COALESCE(SUM(amount),0) FROM ledger WHERE type='income' AND strftime('%Y-%m',date)=?", (month,)).fetchone()[0]
    exp = db.execute("SELECT COALESCE(SUM(amount),0) FROM ledger WHERE type='expense' AND strftime('%Y-%m',date)=?", (month,)).fetchone()[0]
    cat = {r[0]: r[1] for r in db.execute(
        "SELECT category, SUM(amount) FROM ledger WHERE type='expense' AND strftime('%Y-%m',date)=? GROUP BY category", (month,)).fetchall()}
    log(f"📊 {month} 报告: 收入 ¥{inc} 支出 ¥{exp} 净利润 ¥{inc-exp}")
    out({"month": month, "income": inc, "expense": exp, "net": inc-exp, "expense_by_category": cat})

def ledger_list(args):
    db = get_db()
    limit = clamp_limit(args.limit)
    rows = [dict(r) for r in db.execute(
        "SELECT * FROM ledger ORDER BY date DESC LIMIT ? OFFSET ?", (limit, args.offset)).fetchall()]
    total = db.execute("SELECT COUNT(*) FROM ledger").fetchone()[0]
    log(f"📋 收支记录: 返回 {len(rows)} 条 (共 {total} 条)")
    out({"total": total, "returned": len(rows), "records": rows})

# ── content ─────────────────────────────────────────────
def content_add(args):
    db = get_db()
    db.execute("INSERT INTO content_log (title,platform,content_type,status,publish_date) VALUES (?,?,?,?,?)",
               (args.title, args.platform, args.type, args.status or "draft", args.date))
    db.commit()
    rid = db.execute("SELECT last_insert_rowid()").fetchone()[0]
    log(f"✅ 内容「{args.title}」已记录 (ID: {rid})")
    out({"ok": True, "id": rid, "title": args.title})

def content_update(args):
    db = get_db()
    sets, vals = [], []
    if args.title: sets.append("title=?"); vals.append(args.title)
    if args.platform: sets.append("platform=?"); vals.append(args.platform)
    if args.type: sets.append("content_type=?"); vals.append(args.type)
    if args.status: sets.append("status=?"); vals.append(args.status)
    if args.date: sets.append("publish_date=?"); vals.append(args.date)
    if args.performance: sets.append("performance=?"); vals.append(args.performance)
    if not sets:
        log("❌ 至少需要一个更新字段"); sys.exit(1)
    vals.append(args.id)
    cur = db.execute(f"UPDATE content_log SET {','.join(sets)} WHERE id=?", vals)
    if cur.rowcount == 0:
        db.rollback()
        log(f"❌ 内容 ID:{args.id} 不存在")
        out({"ok": False, "error": f"content {args.id} not found"})
        sys.exit(1)
    db.commit()
    log(f"✅ 内容 ID:{args.id} 已更新")
    out({"ok": True, "id": args.id})

def content_list(args):
    db = get_db()
    limit = clamp_limit(args.limit)
    where_clauses, params = [], []
    if args.status:
        where_clauses.append("status=?"); params.append(args.status)
    if args.platform:
        where_clauses.append("platform=?"); params.append(args.platform)
    where_sql = f" WHERE {' AND '.join(where_clauses)}" if where_clauses else ""
    q = f"SELECT * FROM content_log{where_sql}"
    q += f" ORDER BY created_at DESC LIMIT ? OFFSET ?"
    params += [limit, args.offset]
    rows = [dict(r) for r in db.execute(q, params).fetchall()]
    total = db.execute(f"SELECT COUNT(*) FROM content_log{where_sql}", params[:-2]).fetchone()[0]
    log(f"📋 内容列表: 返回 {len(rows)} 条 (共 {total} 条)")
    out({"total": total, "returned": len(rows), "content": rows})

# ── dashboard ───────────────────────────────────────────
def dashboard(args):
    db = get_db()
    month = date.today().strftime("%Y-%m")
    cutoff = (date.today() - timedelta(days=3)).isoformat()
    clients_total = db.execute("SELECT COUNT(*) FROM clients").fetchone()[0]
    clients_active = db.execute("SELECT COUNT(*) FROM clients WHERE status='active'").fetchone()[0]
    stale = [dict(r) for r in db.execute(
        "SELECT id,name,last_contact,needs FROM clients WHERE last_contact<=? AND status IN ('potential','active') ORDER BY last_contact LIMIT 5",
        (cutoff,)).fetchall()]
    inc = db.execute("SELECT COALESCE(SUM(amount),0) FROM ledger WHERE type='income' AND strftime('%Y-%m',date)=?", (month,)).fetchone()[0]
    exp = db.execute("SELECT COALESCE(SUM(amount),0) FROM ledger WHERE type='expense' AND strftime('%Y-%m',date)=?", (month,)).fetchone()[0]
    content_total = db.execute("SELECT COUNT(*) FROM content_log").fetchone()[0]
    content_month = db.execute(
        "SELECT COUNT(*) FROM content_log WHERE status='published' AND publish_date IS NOT NULL AND strftime('%Y-%m',publish_date)=?",
        (month,),
    ).fetchone()[0]
    log(f"📊 仪表盘: 客户 {clients_total} | 收入 ¥{inc} 支出 ¥{exp} | 内容 {content_total}")
    out({
        "clients": {"total": clients_total, "active": clients_active, "stale_3d": len(stale)},
        "finance": {"month": month, "income": inc, "expense": exp, "net": round(inc-exp, 2)},
        "content": {"total": content_total, "this_month": content_month},
        "stale_clients": stale
    })

# ── init ────────────────────────────────────────────────
def init(args):
    import shutil
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    tmpl_src = Path(__file__).resolve().parent.parent / "config" / "templates"
    # 也兼容安装后的位置
    if not tmpl_src.exists():
        tmpl_src = CONFIG_DIR / "templates"
    target = CONFIG_DIR / "industry.json"
    if args.template:
        src = tmpl_src / f"{args.template}.json"
        if not src.exists():
            avail = [f.stem for f in tmpl_src.glob("*.json")] if tmpl_src.exists() else []
            log(f"❌ 模板 '{args.template}' 不存在。可选: {', '.join(avail)}")
            out({"ok": False, "error": f"template '{args.template}' not found", "available": avail})
            sys.exit(1)
        shutil.copy2(str(src), str(target))
        log(f"✅ 行业配置已初始化: {args.template}")
        out({"ok": True, "template": args.template, "config_path": str(target)})
    else:
        avail = [f.stem for f in tmpl_src.glob("*.json")] if tmpl_src.exists() else []
        log(f"可选模板: {', '.join(avail)}")
        out({"available_templates": avail})
    get_db()  # 确保数据库已创建

# ── CLI 入口 ────────────────────────────────────────────
def main():
    p = argparse.ArgumentParser(prog="opckit-db", description="OPCKit 共享数据库 CLI")
    sub = p.add_subparsers(dest="module")

    # client
    c = sub.add_parser("client")
    cs = c.add_subparsers(dest="action")
    ca = cs.add_parser("add");    ca.add_argument("--data", required=True)
    cl = cs.add_parser("list");   cl.add_argument("--status"); cl.add_argument("--search"); cl.add_argument("--limit", type=int, default=DEFAULT_LIMIT); cl.add_argument("--offset", type=int, default=0)
    ct = cs.add_parser("stale");  ct.add_argument("--days", type=int, default=3); ct.add_argument("--limit", type=int, default=DEFAULT_LIMIT)
    cu = cs.add_parser("update"); cu.add_argument("--id", type=int, required=True); cu.add_argument("--data", required=True)
    cs.add_parser("count")

    # ledger
    l = sub.add_parser("ledger")
    ls = l.add_subparsers(dest="action")
    li = ls.add_parser("income");  li.add_argument("--amount", type=float, required=True); li.add_argument("--from", dest="from_client"); li.add_argument("--note", default="")
    le = ls.add_parser("expense"); le.add_argument("--amount", type=float, required=True); le.add_argument("--category", default="其他"); le.add_argument("--note", default="")
    lr = ls.add_parser("report");  lr.add_argument("--month")
    ll = ls.add_parser("list");    ll.add_argument("--limit", type=int, default=DEFAULT_LIMIT); ll.add_argument("--offset", type=int, default=0)

    # content
    t = sub.add_parser("content")
    ts = t.add_subparsers(dest="action")
    ta = ts.add_parser("add"); ta.add_argument("--title", required=True); ta.add_argument("--platform", default=""); ta.add_argument("--type", default=""); ta.add_argument("--status"); ta.add_argument("--date")
    tu = ts.add_parser("update"); tu.add_argument("--id", type=int, required=True); tu.add_argument("--title"); tu.add_argument("--platform"); tu.add_argument("--type"); tu.add_argument("--status"); tu.add_argument("--date"); tu.add_argument("--performance")
    tl = ts.add_parser("list"); tl.add_argument("--status"); tl.add_argument("--platform"); tl.add_argument("--limit", type=int, default=DEFAULT_LIMIT); tl.add_argument("--offset", type=int, default=0)

    # dashboard
    sub.add_parser("dashboard")

    # init
    ini = sub.add_parser("init"); ini.add_argument("--template", default="")

    args = p.parse_args()
    dispatch = {
        ("client","add"): client_add, ("client","list"): client_list,
        ("client","stale"): client_stale, ("client","update"): client_update,
        ("client","count"): client_count,
        ("ledger","income"): ledger_income, ("ledger","expense"): ledger_expense,
        ("ledger","report"): ledger_report, ("ledger","list"): ledger_list,
        ("content","add"): content_add, ("content","update"): content_update, ("content","list"): content_list,
        ("dashboard", None): dashboard, ("init", None): init,
    }
    key = (args.module, getattr(args, "action", None))
    if key in dispatch:
        dispatch[key](args)
    else:
        p.print_help()

if __name__ == "__main__":
    main()
