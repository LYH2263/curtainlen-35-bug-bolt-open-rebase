from fastapi import APIRouter, HTTPException
from app.repositories import fabrics as fabrics_repo
from app.repositories import history as repo
from app.services.bolt_open import detail_view_bolt, list_view_bolt, summarize_bolt

router = APIRouter()


@router.get("/runs")
def runs(limit: int = 50):
    items = repo.list_runs(limit)
    for it in items:
        fab = fabrics_repo.get_fabric(it.get("fabric_id")) if it.get("fabric_id") else None
        live_m = (fab or {}).get("min_order_m")
        it["result"] = list_view_bolt(it.get("result") or {}, live_m)
        it["bolt_summary"] = summarize_bolt(it["result"])
    return {"items": items}


@router.get("/runs/{run_id}")
def run(run_id: int):
    r = repo.get_run(run_id)
    if not r:
        raise HTTPException(404, "not found")
    fab = fabrics_repo.get_fabric(r.get("fabric_id")) if r.get("fabric_id") else None
    live_m = (fab or {}).get("min_order_m")
    r["result"] = detail_view_bolt(r.get("result") or {}, live_m)
    r["bolt_summary"] = summarize_bolt(r["result"])
    return r
