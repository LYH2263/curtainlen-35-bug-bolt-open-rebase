import pytest
from fastapi import HTTPException
from app import seed
from app.repositories import fabrics, history
from app.services import estimate_service

@pytest.fixture()
def fresh_db(tmp_path, monkeypatch):
    monkeypatch.setattr("app.db.DB_PATH", tmp_path / "t.db")
    seed.init_db()

def test_save_persists_base_min_and_order(fresh_db):
    # 卧室窗基础 7.0m，布料默认起订 10m → 保存固化三个数
    r = estimate_service.run_estimate(2, 1, True, "")
    assert r["run_id"]
    saved = history.list_runs()[0]["result"]
    assert saved["base_meters"] == 7.0
    assert saved["min_order_m"] == 10.0
    assert saved["order_meters"] == 10.0

def test_preview_only_writes_nothing(fresh_db):
    r = estimate_service.run_estimate(1, 1, False, "", 20.0)
    assert r["run_id"] is None
    assert r["order_meters"] == 20.0
    assert history.list_runs() == []

def test_non_positive_min_fails_and_skips_history(fresh_db):
    with pytest.raises(HTTPException) as e:
        estimate_service.run_estimate(2, 1, True, "", 0)
    assert e.value.status_code == 422
    with pytest.raises(HTTPException):
        estimate_service.run_estimate(2, 1, True, "", -1.5)
    assert history.list_runs() == []

def test_override_beats_fabric_default(fresh_db):
    r = estimate_service.run_estimate(2, 1, False, "", 8.0)
    assert r["min_order_m"] == 8.0
    assert r["order_meters"] == 8.0
    # 覆盖值 <= 基础时订货等于改造前 meters
    r2 = estimate_service.run_estimate(1, 1, False, "", 10.0)
    assert r2["order_meters"] == r2["base_meters"] == 14.25

def test_fabric_default_change_does_not_rewrite_old_runs(fresh_db):
    estimate_service.run_estimate(2, 1, True, "")
    fabrics.update_min_order(1, 99.0)
    old = history.list_runs()[0]["result"]
    assert old["min_order_m"] == 10.0
    assert old["order_meters"] == 10.0
    # 新单才用新默认
    r = estimate_service.run_estimate(2, 1, False, "")
    assert r["min_order_m"] == 99.0
    assert r["order_meters"] == 99.0

def test_list_and_detail_keep_floor_after_default_changes(fresh_db):
    # 基础 7.0、布料默认 M=10 保存一单 → 订货固化 10
    saved = estimate_service.run_estimate(2, 1, True, "")
    rid = saved["run_id"]
    fabrics.update_min_order(1, 99.0)   # 事后改布料页默认 M
    # 列表摘要打开：M 字段保留旧值，订货不掉回基础、不按 99 重托
    lst = history.list_runs()[0]["result"]
    assert lst["min_order_m"] == 10.0
    assert lst["base_meters"] == 7.0
    assert lst["order_meters"] == 10.0
    assert lst["list_order_meters_pin"] == 10.0
    # 详情打开：与列表完全一致
    det = history.get_run(rid)["result"]
    assert det["min_order_m"] == 10.0
    assert det["base_meters"] == 7.0
    assert det["order_meters"] == 10.0
    assert det["order_meters"] == lst["order_meters"]
    # 连默认 M 被清除也不影响旧单
    fabrics.update_min_order(1, None)
    assert history.get_run(rid)["result"]["order_meters"] == 10.0

def test_bench_recompute_with_write_time_params_matches_review(fresh_db):
    saved = estimate_service.run_estimate(2, 1, True, "")
    rid = saved["run_id"]
    fabrics.update_min_order(1, 99.0)   # 布料页现行默认已变
    review = history.get_run(rid)["result"]["order_meters"]
    # 算料台用写入时同参（window/fabric + 当时 M=10，非现行 99）再算 → 等于该编号回看订货米
    again = estimate_service.run_estimate(2, 1, False, "", 10.0)
    assert again["order_meters"] == review == 10.0
    assert again["base_meters"] == 7.0
