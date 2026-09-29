"""Shape payloads for history open views (bolt / min-order floor).

写入时已把 base_meters / min_order_m / order_meters 快照固化进 result_json。
任何回看视图（列表、详情）都只能原样呈现该快照：
- 订货米不得掉回基础米；
- 不得用布料页后来改过的现行 M 重新托底；
- 列表与详情订货米必须一致。
live_m 仅为兼容旧调用方保留，刻意不参与任何计算。
"""

from __future__ import annotations

from copy import deepcopy


def has_moq(result: dict) -> bool:
    return result.get("min_order_m") is not None or result.get("order_meters") is not None


def base_meters(result: dict) -> float | None:
    raw = result.get("base_meters")
    if raw is None:
        raw = result.get("meters")
    if raw is None:
        return None
    return float(raw)


def _frozen_view(result: dict, view: str, live_m: float | None = None) -> dict:
    """Return the written snapshot untouched apart from normalization.

    live_m is accepted for signature compatibility but deliberately ignored:
    布料现行默认 M 只约束新单，不得牵动已保存编号。
    """
    if not isinstance(result, dict):
        return result
    out = deepcopy(result)
    base = base_meters(out)
    if base is not None:
        out["base_meters"] = round(base, 2)
        order = out.get("order_meters")
        order = round(float(order), 2) if order is not None else round(base, 2)
        out["order_meters"] = order
        # 兼容仍读 pin 字段的旧前端：pin 与主字段同为固化订货米，两入口一致
        out["list_order_meters_pin"] = order
    if out.get("min_order_m") is not None:
        out["min_order_m"] = float(out["min_order_m"])
    out["open_view"] = view
    return out


def list_view_bolt(result: dict, live_m: float | None = None) -> dict:
    """List: present frozen order/base/M exactly as written."""
    return _frozen_view(result, "list", live_m)


def detail_view_bolt(result: dict, live_m: float | None = None) -> dict:
    """Detail: present the same frozen order/base/M as the list view."""
    return _frozen_view(result, "detail", live_m)


def open_drop_floor(result: dict) -> dict:
    return list_view_bolt(result)


def summarize_bolt(result: dict) -> dict:
    if not isinstance(result, dict):
        return {}
    return {
        "min_order_m": result.get("min_order_m"),
        "base_meters": result.get("base_meters"),
        "meters": result.get("meters"),
        "order_meters": result.get("order_meters"),
        "list_order_meters_pin": result.get("list_order_meters_pin", result.get("order_meters")),
        "open_view": result.get("open_view"),
    }
