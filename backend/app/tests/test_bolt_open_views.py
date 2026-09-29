from app.services.bolt_open import detail_view_bolt, list_view_bolt, summarize_bolt

RAW = {"min_order_m": 5.0, "base_meters": 3.2, "order_meters": 5.0, "meters": 3.2}


def test_list_keeps_written_order():
    # 列表订货米必须保持写入时的托底值，不得掉回基础米
    out = list_view_bolt(dict(RAW), live_m=8.0)
    assert out["base_meters"] == 3.2
    assert out["min_order_m"] == 5.0
    assert out["order_meters"] == 5.0
    assert out["list_order_meters_pin"] == 5.0


def test_detail_keeps_written_order_ignores_live_m():
    # 详情订货米保持写入值；布料页后来改的默认 M（8.0）不得重新托底
    out = detail_view_bolt(dict(RAW), live_m=8.0)
    assert out["base_meters"] == 3.2
    assert out["min_order_m"] == 5.0
    assert out["order_meters"] == 5.0


def test_list_and_detail_orders_match():
    lst = list_view_bolt(dict(RAW), live_m=8.0)
    det = detail_view_bolt(dict(RAW), live_m=8.0)
    assert lst["order_meters"] == det["order_meters"] == 5.0
    # 现行 M 被清成 None，旧单也不受影响
    det_none = detail_view_bolt(dict(RAW), live_m=None)
    assert det_none["order_meters"] == 5.0
    assert det_none["min_order_m"] == 5.0


def test_no_floor_run_unchanged():
    raw = {"base_meters": 14.25, "order_meters": 14.25, "meters": 14.25, "min_order_m": None}
    out = detail_view_bolt(dict(raw), live_m=99.0)
    assert out["order_meters"] == 14.25 == out["base_meters"]
    assert out["min_order_m"] is None


def test_summary_reflects_frozen_order():
    out = summarize_bolt(list_view_bolt(dict(RAW), live_m=8.0))
    assert out["order_meters"] == 5.0
    assert out["list_order_meters_pin"] == 5.0
