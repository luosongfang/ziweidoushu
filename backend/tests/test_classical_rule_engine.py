"""Classical Rule Engine V1.6 — 16册规则校准测试。"""

from __future__ import annotations

import pytest

from app.ziwei.rules.cache import clear_rules_cache
from app.ziwei_classical.rule_engine import ClassicalRuleEngine, lookup_ziwei_from_rules_table
from app.ziwei_classical.rules.loader import (
    assert_has_source,
    get_aux_catalog,
    get_ming_rule,
    get_ziwei_table,
    list_sourced_rules,
    load_catalog,
)
from app.ziwei_classical.rules.palace.ming_gong_rule import apply_ming_gong_rule
from app.ziwei_classical.rules.palace.shen_gong_rule import apply_shen_gong_rule
from app.ziwei_classical.rules.rule_conflict_detector import (
    detect_rule_conflicts,
    require_manual_config,
)
from app.ziwei_classical.validator.classical_trace import ClassicalTrace


@pytest.fixture(autouse=True)
def _rules():
    clear_rules_cache()
    yield
    clear_rules_cache()


SC01 = dict(birth_date="1990-05-15", birth_time="14:30", gender="male", location="深圳")


class TestCatalogAndSources:
    def test_sixteen_books_cataloged(self):
        cat = load_catalog()
        assert len(cat["books"]) == 16
        assert cat["policy"]["no_single_case_hardcode"] is True
        assert cat["policy"]["conflict_auto_select"] is False

    def test_sourced_rules_have_source(self):
        rules = list_sourced_rules()
        assert len(rules) >= 5
        for r in rules:
            if r.get("validation") == "required" or r.get("source"):
                assert r.get("source"), r.get("id")

    def test_unsourced_forbidden(self):
        with pytest.raises(PermissionError):
            assert_has_source({"id": "X", "source": []})


class TestPalaceRules:
    def test_ming_shen_sc01(self):
        tr = ClassicalTrace()
        ming = apply_ming_gong_rule(4, 7, "庚", trace=tr)  # 四月未时
        shen = apply_shen_gong_rule(4, 7, trace=tr)
        assert ming["branch"] == "戌"
        assert shen["branch"] == "子"
        assert ming["rule_id"] == "PALACE_MING_001"
        assert any(s.rule_id == "PALACE_MING_001" for s in tr.steps)


class TestZiweiTable:
    def test_150_entries(self):
        table = get_ziwei_table()
        assert len(table["entries"]) == 150
        assert table.get("source")

    def test_day21_earth5(self):
        br, rid = lookup_ziwei_from_rules_table(5, 21)
        assert br == "巳"
        assert rid.startswith("ZIWEI_TABLE_")


class TestRuleEngineCore:
    def test_sc01_core_and_trace(self):
        out = ClassicalRuleEngine().compute(**SC01)
        assert out["ming_gong"]["branch"] == "戌"
        assert out["bureau"]["bureau_name"] == "土五局"
        assert out["ziwei"]["branch"] == "巳"
        assert out["fourteen_stars"]["紫微"] == "巳"
        assert out["fourteen_stars"]["天府"] == "亥"
        assert len(out["fourteen_stars"]) == 14
        trace = out["classical_trace"]
        assert trace
        steps = {t["step"] for t in trace}
        assert "ziwei_position" in steps
        assert "ming_gong" in steps
        zw = next(t for t in trace if t["step"] == "ziwei_position")
        assert zw["rule_id"]
        assert zw["source"]
        assert zw["result"] == "巳"
        assert zw["input"]["day"] == 21

    def test_empty_ming_palace(self):
        out = ClassicalRuleEngine().compute(**SC01)
        ming_p = next(p for p in out["palaces"] if p["is_ming_gong"])
        assert ming_p["main_stars"] == []


class TestConflicts:
    def test_tianfu_conflict_no_autoselect(self):
        conflicts = detect_rule_conflicts()
        tf = next(c for c in conflicts if c["rule"] == "tianfu")
        assert tf["conflict"] is True
        assert tf["auto_select"] is False
        assert "yanshen_mirror" in tf["options"] or "opposite" in tf["options"]
        summary = require_manual_config(conflicts)
        assert summary["has_conflicts"] is True


class TestAuxCatalog:
    def test_aux_catalog_has_sources(self):
        cat = get_aux_catalog()
        assert "六吉" in cat["groups"]
        assert "六煞" in cat["groups"]
        for sr in cat["star_rules"]:
            assert sr.get("source"), sr["name"]
            assert sr.get("start") is not None or sr.get("direction")
