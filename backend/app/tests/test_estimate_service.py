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

def test_list_and_detail_keep_snapshot_after_default_change(fresh_db):
    # 基础 7.0m 被 M=10 托底到 10.0m，保存后改布料默认 M 再分别从列表/详情打开
    saved = estimate_service.run_estimate(2, 1, True, "")
    rid = saved["run_id"]
    fabrics.update_min_order(1, 99.0)

    listed = history.list_runs()[0]["result"]
    detail = history.get_run(rid)["result"]
    # M 字段保留写入值，订货米不掉回基础、不按新默认 99 重托底
    for v in (listed, detail):
        assert v["min_order_m"] == 10.0
        assert v["base_meters"] == 7.0
        assert v["order_meters"] == 10.0
    # 列表摘要与详情订货米一致
    assert listed["order_meters"] == detail["order_meters"]

def test_bench_replay_with_write_time_params_matches_run(fresh_db):
    # 算料台用写入时同参（显式 M=10）再算，订货米须等于该编号回看值
    estimate_service.run_estimate(2, 1, True, "", 10.0)
    fabrics.update_min_order(1, 99.0)  # 现行默认只约束新单
    replay = estimate_service.run_estimate(2, 1, False, "", 10.0)
    back = history.list_runs()[0]["result"]
    assert replay["order_meters"] == back["order_meters"] == 10.0
    assert replay["base_meters"] == back["base_meters"] == 7.0
