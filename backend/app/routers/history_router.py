from fastapi import APIRouter, HTTPException
from app.repositories import history as repo
from app.services.bolt_open import summarize_bolt

router = APIRouter()


@router.get("/runs")
def runs(limit: int = 50):
    # repository 已按固化快照整形；这里只挂摘要，绝不再掺入布料现行 M
    items = repo.list_runs(limit)
    for it in items:
        it["bolt_summary"] = summarize_bolt(it.get("result") or {})
    return {"items": items}


@router.get("/runs/{run_id}")
def run(run_id: int):
    r = repo.get_run(run_id)
    if not r:
        raise HTTPException(404, "not found")
    r["bolt_summary"] = summarize_bolt(r.get("result") or {})
    return r
