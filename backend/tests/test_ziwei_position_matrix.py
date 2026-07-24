"""紫微定位 5局×30日 = 150 规则矩阵测试。

验证：calc_ziwei_branch_index ↔ ziwei_position_rules ↔ RulesLoader 三者一致。
禁止为单个命例硬编码；矩阵由公式生成。
"""

from __future__ import annotations

import pytest

from app.ziwei.constants import EARTHLY_BRANCHES
from app.ziwei.rules.cache import clear_rules_cache
from app.ziwei.rules.loader import RulesLoader
from app.ziwei.rules.seed_generator import calc_ziwei_branch_index, generate_ziwei_position_rules


@pytest.fixture(autouse=True)
def _rules():
    clear_rules_cache()
    yield
    clear_rules_cache()


def _matrix() -> list[tuple[int, int, str]]:
    """(bureau, lunar_day, expected_branch) — 由公式生成，非人工表。"""
    rows = []
    for bureau in (2, 3, 4, 5, 6):
        for day in range(1, 31):
            idx = calc_ziwei_branch_index(day, bureau)
            rows.append((bureau, day, EARTHLY_BRANCHES[idx]))
    assert len(rows) == 150
    return rows


MATRIX = _matrix()


class TestZiweiPositionMatrixSize:
    def test_exactly_150_cells(self):
        assert len(MATRIX) == 150
        assert len(generate_ziwei_position_rules()) == 150


class TestZiweiPositionMatrix:
    @pytest.mark.parametrize(
        "bureau,lunar_day,expected_branch",
        MATRIX,
        ids=[f"ju{b}-d{d:02d}" for b, d, _ in MATRIX],
    )
    def test_formula_equals_rules_loader(self, bureau, lunar_day, expected_branch):
        formula = EARTHLY_BRANCHES[calc_ziwei_branch_index(lunar_day, bureau)]
        table = RulesLoader.get_ziwei_position(bureau, lunar_day)
        assert formula == expected_branch
        assert table == expected_branch
        assert formula == table

    def test_seed_rows_match_formula(self):
        for row in generate_ziwei_position_rules():
            exp = EARTHLY_BRANCHES[
                calc_ziwei_branch_index(row["lunar_day"], row["bureau"])
            ]
            assert row["ziwei_branch"] == exp
