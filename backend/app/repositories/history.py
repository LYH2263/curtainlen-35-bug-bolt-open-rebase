import json
from datetime import datetime, timezone
from app.db import connect

def insert_run(window_id, fabric_id, result, note=""):
    c = connect()
    try:
        cur = c.execute(
            "INSERT INTO calc_runs(window_id,fabric_id,result_json,note,created_at) VALUES (?,?,?,?,?)",
            (window_id, fabric_id, json.dumps(result, ensure_ascii=False), note, datetime.now(timezone.utc).isoformat()),
        )
        c.commit()
        return int(cur.lastrowid)
    finally:
        c.close()

def get_run(run_id):
    from app.services.bolt_open import detail_view_bolt

    c = connect()
    try:
        row = c.execute(
            """SELECT r.*, w.name window_name, f.name fabric_name
            FROM calc_runs r
            LEFT JOIN windows w ON w.id=r.window_id LEFT JOIN fabrics f ON f.id=r.fabric_id
            WHERE r.id=?""", (run_id,)).fetchone()
        if not row:
            return None
        d = dict(row)
        raw = json.loads(d.pop("result_json"))
        # 只读写入时固化的快照；布料现行默认 M 不参与，绝不重新托底
        d["result"] = detail_view_bolt(raw)
        return d
    finally:
        c.close()

def list_runs(limit=50):
    from app.services.bolt_open import list_view_bolt

    c = connect()
    try:
        rows = c.execute(
            """SELECT r.*, w.name window_name, f.name fabric_name FROM calc_runs r
            LEFT JOIN windows w ON w.id=r.window_id LEFT JOIN fabrics f ON f.id=r.fabric_id
            ORDER BY r.id DESC LIMIT ?""", (limit,)).fetchall()
        out = []
        for row in rows:
            d = dict(row)
            raw = json.loads(d.pop("result_json"))
            # 列表与详情同参同快照：订货米保持写入值，不掉回基础、不按现行 M 重算
            d["result"] = list_view_bolt(raw)
            out.append(d)
        return out
    finally:
        c.close()
