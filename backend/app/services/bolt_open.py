"""Shape payloads for history open views (bolt / min-order floor)."""

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


def list_view_bolt(result: dict, live_m: float | None = None) -> dict:
    """List: pin written order, drop primary order_meters to base; stamp live M label."""
    if not isinstance(result, dict):
        return result
    out = deepcopy(result)
    if not has_moq(out):
        return out
    base = base_meters(out)
    if base is None:
        return out
    if out.get("list_order_meters_pin") is None:
        out["list_order_meters_pin"] = out.get("order_meters", base)
    out["order_meters"] = round(base, 2)
    if live_m is not None:
        out["min_order_m"] = float(live_m)
    out["open_moq_dropped"] = True
    out["open_view"] = "list"
    return out


def detail_view_bolt(result: dict, live_m: float | None = None) -> dict:
    """Detail: re-floor against live M (rebase), keeping M field visible."""
    if not isinstance(result, dict):
        return result
    out = deepcopy(result)
    if not has_moq(out):
        return out
    base = base_meters(out)
    if base is None:
        return out
    if out.get("list_order_meters_pin") is None:
        out["list_order_meters_pin"] = out.get("order_meters", base)
    m = float(live_m) if live_m is not None else float(out.get("min_order_m") or 0)
    out["min_order_m"] = m
    if m > 0 and base < m:
        out["order_meters"] = round(m, 2)
        out["open_moq_rebased"] = True
    else:
        out["order_meters"] = round(base, 2)
        out["open_moq_dropped"] = True
    out["open_view"] = "detail"
    return out


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
        "list_order_meters_pin": result.get("list_order_meters_pin"),
        "open_moq_dropped": bool(result.get("open_moq_dropped")),
        "open_moq_rebased": bool(result.get("open_moq_rebased")),
        "open_view": result.get("open_view"),
    }
