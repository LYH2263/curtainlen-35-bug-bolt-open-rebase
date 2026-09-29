from fastapi import APIRouter, HTTPException
from app.repositories import history as repo

router = APIRouter()


@router.get("/runs")
def runs(limit: int = 50):
    # 列表摘要直接展示写入时固化的订货米快照，不做任何重塑。
    return {"items": repo.list_runs(limit)}


@router.get("/runs/{run_id}")
def run(run_id: int):
    r = repo.get_run(run_id)
    if not r:
        raise HTTPException(404, "not found")
    return r
