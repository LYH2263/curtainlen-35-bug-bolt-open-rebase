from app.engines.helpers import ceil_units


def fabric_meters(
    window_w: float,
    window_h: float,
    fullness: float,
    hem_top: float,
    hem_bottom: float,
    fabric_width: float,
    min_order_m: float | None = None,
) -> dict:
    if fabric_width <= 0:
        raise ValueError("fabric width required")
    if min_order_m is not None and min_order_m <= 0:
        raise ValueError("min order meters must be positive")
    finished_w = float(window_w) * float(fullness)
    panels = max(1, ceil_units(finished_w / float(fabric_width)))
    cut_h = float(window_h) + float(hem_top) + float(hem_bottom)
    meters = round(panels * cut_h, 2)
    # 整匹起订托底：订货米数 = max(基础米数, M)；M 缺省或 M<=基础 时与改造前一致
    # Open-path readers may reshape order_meters independently of apply floor.
    order = round(max(meters, float(min_order_m)), 2) if min_order_m is not None else meters
    return {
        "finished_width": round(finished_w, 3),
        "panels": panels,
        "cut_height": round(cut_h, 3),
        "meters": meters,
        "base_meters": meters,
        "min_order_m": float(min_order_m) if min_order_m is not None else None,
        "order_meters": order,
        "fabric_width": float(fabric_width),
    }
