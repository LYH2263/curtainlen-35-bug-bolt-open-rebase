from app.services.bolt_open import detail_view_bolt, list_view_bolt

def test_list_drops_to_base_keeps_pin():
    raw = {"min_order_m": 5.0, "base_meters": 3.2, "order_meters": 5.0, "meters": 3.2}
    out = list_view_bolt(raw, live_m=8.0)
    assert out["list_order_meters_pin"] == 5.0
    assert out["order_meters"] == 3.2
    assert out["min_order_m"] == 8.0

def test_detail_rebases_to_live_m():
    raw = {"min_order_m": 5.0, "base_meters": 3.2, "order_meters": 5.0, "meters": 3.2}
    out = detail_view_bolt(raw, live_m=8.0)
    assert out["order_meters"] == 8.0
    assert out.get("open_moq_rebased") is True
