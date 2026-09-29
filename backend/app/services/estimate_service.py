from fastapi import HTTPException
from app.engines.curtain_math import fabric_meters
from app.repositories import fabrics, history, settings_repo, windows

def run_estimate(window_id: int, fabric_id: int, save: bool, note: str, min_order_m: float | None = None):
    w = windows.get_window(window_id)
    f = fabrics.get_fabric(fabric_id)
    if not w or not f:
        raise HTTPException(404, "not found")
    if w.get("data_quality") == "dirty":
        raise HTTPException(422, "dirty window")
    # 生效 M：请求覆盖优先，否则取布料默认；非正即校验失败，不落历史
    effective_m = min_order_m if min_order_m is not None else f.get("min_order_m")
    if effective_m is not None and effective_m <= 0:
        raise HTTPException(422, "min order meters must be positive")
    settings = settings_repo.get_all()
    fullness = float(w.get("fullness") or settings.get("default_fullness", 2.0))
    calc = fabric_meters(w["width"], w["height"], fullness, f["hem_top"], f["hem_bottom"], f["fabric_width"], effective_m)
    # 保存即固化基础米 base_meters、起订 min_order_m、订货 order_meters 快照
    run_id = history.insert_run(window_id, fabric_id, calc, note) if save else None
    return {"window": w, "fabric": f, "run_id": run_id, **calc}
