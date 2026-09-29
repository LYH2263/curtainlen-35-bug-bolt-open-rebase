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
    from app.repositories import fabrics as fabrics_repo

    c = connect()
    try:
        row = c.execute(
            """SELECT r.*, w.name window_name, f.name fabric_name, f.min_order_m fabric_min_order
            FROM calc_runs r
            LEFT JOIN windows w ON w.id=r.window_id LEFT JOIN fabrics f ON f.id=r.fabric_id
            WHERE r.id=?""", (run_id,)).fetchone()
        if not row:
            return None
        d = dict(row)
        raw = json.loads(d.pop("result_json"))
        live_m = d.get("fabric_min_order")
        if live_m is None:
            fab = fabrics_repo.get_fabric(d.get("fabric_id")) if d.get("fabric_id") else None
            live_m = (fab or {}).get("min_order_m")
        d["result"] = detail_view_bolt(raw, live_m)
        return d
    finally:
        c.close()

def list_runs(limit=50):

    c = connect()
    try:
        rows = c.execute(
            """SELECT r.*, w.name window_name, f.name fabric_name FROM calc_runs r
            LEFT JOIN windows w ON w.id=r.window_id LEFT JOIN fabrics f ON f.id=r.fabric_id
            ORDER BY r.id DESC LIMIT ?""", (limit,)).fetchall()
        from app.services.bolt_open import list_view_bolt
        from app.repositories import fabrics as fabrics_repo

        out = []
        for row in rows:
            d = dict(row)
            raw = json.loads(d.pop("result_json"))
            fab = fabrics_repo.get_fabric(d.get("fabric_id")) if d.get("fabric_id") else None
            live_m = (fab or {}).get("min_order_m")
            d["result"] = list_view_bolt(raw, live_m)
            out.append(d)
        return out
    finally:
        c.close()
