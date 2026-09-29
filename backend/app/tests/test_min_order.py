import pytest
from app.engines.curtain_math import fabric_meters

def test_order_floored_to_min():
    # 基础 7.0m，起订 10m → 订货托底到 10m，基础米不变
    r = fabric_meters(2.2, 1.5, 2.0, 0.10, 0.15, 1.4, min_order_m=10.0)
    assert r["meters"] == 7.0
    assert r["base_meters"] == 7.0
    assert r["min_order_m"] == 10.0
    assert r["order_meters"] == 10.0

def test_min_below_base_keeps_legacy_meters():
    # M <= 基础 → 订货等于改造前 meters
    r = fabric_meters(3.0, 2.6, 2.0, 0.10, 0.15, 1.4, min_order_m=10.0)
    assert r["meters"] == 14.25
    assert r["order_meters"] == 14.25

def test_min_equal_base_keeps_legacy_meters():
    r = fabric_meters(2.2, 1.5, 2.0, 0.10, 0.15, 1.4, min_order_m=7.0)
    assert r["order_meters"] == r["meters"] == 7.0

def test_no_min_order():
    r = fabric_meters(3.0, 2.6, 2.0, 0.10, 0.15, 1.4)
    assert r["min_order_m"] is None
    assert r["order_meters"] == r["meters"]

def test_non_positive_min_rejected():
    with pytest.raises(ValueError):
        fabric_meters(3.0, 2.6, 2.0, 0.10, 0.15, 1.4, min_order_m=0)
    with pytest.raises(ValueError):
        fabric_meters(3.0, 2.6, 2.0, 0.10, 0.15, 1.4, min_order_m=-3)
