from app.db import connect

def list_fabrics():
    c = connect()
    try:
        return [dict(r) for r in c.execute("SELECT * FROM fabrics ORDER BY id").fetchall()]
    finally:
        c.close()

def get_fabric(fid: int):
    c = connect()
    try:
        r = c.execute("SELECT * FROM fabrics WHERE id=?", (fid,)).fetchone()
        return dict(r) if r else None
    finally:
        c.close()

def update_min_order(fid: int, min_order_m):
    """更新布料默认起订米数；只影响后续新单，不回写历史 calc_runs 快照。"""
    c = connect()
    try:
        cur = c.execute("UPDATE fabrics SET min_order_m=? WHERE id=?", (min_order_m, fid))
        c.commit()
        return cur.rowcount > 0
    finally:
        c.close()
