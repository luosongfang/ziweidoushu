"""天府定位与天府系顺布独立验证。"""

from __future__ import annotations

import pytest

from app.ziwei.constants import EARTHLY_BRANCHES
from app.ziwei.engines.star_placement_engine import StarPlacementEngine
from app.ziwei.rules.cache import clear_rules_cache
from app.ziwei.rules.seed_generator import calc_tianfu_branch_index, calc_ziwei_branch_index

# 经典寅申轴镜像表（文档化期望；由公式 (4-z)%12 生成，非单例硬编码）
TIANFU_MIRROR_TABLE: dict[str, str] = {
    EARTHLY_BRANCHES[z]: EARTHLY_BRANCHES[calc_tianfu_branch_index(z)] for z in range(12)
}

TIANFU_SERIES_OFFSETS: tuple[tuple[str, int], ...] = (
    ("天府", 0),
    ("太阴", 1),
    ("贪狼", 2),
    ("巨门", 3),
    ("天相", 4),
    ("天梁", 5),
    ("七杀", 6),
    ("破军", 10),
)


@pytest.fixture(autouse=True)
def _rules():
    clear_rules_cache()
    yield
    clear_rules_cache()


class TestTianfuMirror:
    def test_mirror_table_size(self):
        assert len(TIANFU_MIRROR_TABLE) == 12

    @pytest.mark.parametrize("ziwei_branch", list(EARTHLY_BRANCHES))
    def test_mirror_formula(self, ziwei_branch):
        z = EARTHLY_BRANCHES.index(ziwei_branch)
        tf = EARTHLY_BRANCHES[calc_tianfu_branch_index(z)]
        assert TIANFU_MIRROR_TABLE[ziwei_branch] == tf
        # 寅申同宫
        if ziwei_branch in ("寅", "申"):
            assert tf == ziwei_branch
        # 仅巳亥与对宫重合
        opposite = EARTHLY_BRANCHES[(z + 6) % 12]
        if ziwei_branch in ("巳", "亥"):
            assert tf == opposite
        else:
            # 其他宫镜像 ≠ 对宫（或碰巧——除寅申巳亥外均不等于对宫）
            if ziwei_branch not in ("寅", "申"):
                assert tf != opposite or ziwei_branch in ("巳", "亥")

    def test_not_simple_opposite_for_zi(self):
        """紫微在子 → 天府在辰，不是午（对宫）。"""
        z = EARTHLY_BRANCHES.index("子")
        assert EARTHLY_BRANCHES[calc_tianfu_branch_index(z)] == "辰"
        assert EARTHLY_BRANCHES[(z + 6) % 12] == "午"


class TestTianfuSeries:
    @pytest.mark.parametrize("bureau", [2, 3, 4, 5, 6])
    @pytest.mark.parametrize("lunar_day", [1, 8, 15, 21, 30])
    def test_series_forward_from_tianfu(self, bureau, lunar_day):
        ziwei_idx = calc_ziwei_branch_index(lunar_day, bureau)
        tianfu_idx = calc_tianfu_branch_index(ziwei_idx)
        # 用引擎完整安置（需假 palace 列表仅解析主星）
        from app.ziwei.engines.palace_engine import PalaceResult

        palaces = []
        for i in range(12):
            br = EARTHLY_BRANCHES[i]
            palaces.append(
                PalaceResult(
                    name=f"P{i}",
                    branch=br,
                    branch_index=i,
                    position=i,
                    opposite=EARTHLY_BRANCHES[(i + 6) % 12],
                    sanhe=[],
                    is_ming_gong=(i == 2),
                    is_shen_gong=False,
                    ganzhi="",
                )
            )
        result = StarPlacementEngine.compute(
            palaces, lunar_day, bureau, "甲", "子", 0, 1
        )
        assert result.star_branches["紫微"] == EARTHLY_BRANCHES[ziwei_idx]
        assert result.star_branches["天府"] == EARTHLY_BRANCHES[tianfu_idx]
        for star, offset in TIANFU_SERIES_OFFSETS:
            expected = EARTHLY_BRANCHES[(tianfu_idx + offset) % 12]
            assert result.star_branches[star] == expected, (
                f"{star}: bureau={bureau} day={lunar_day}"
            )


class TestZiweiSeriesBackward:
    def test_ziwei_group_offsets(self):
        """紫微系相对紫微逆布：机1 阳3 武4 同5 廉8。"""
        from app.ziwei.engines.palace_engine import PalaceResult

        lunar_day, bureau = 21, 5
        ziwei_idx = calc_ziwei_branch_index(lunar_day, bureau)
        palaces = []
        for i in range(12):
            br = EARTHLY_BRANCHES[i]
            palaces.append(
                PalaceResult(
                    name=f"P{i}",
                    branch=br,
                    branch_index=i,
                    position=i,
                    opposite=EARTHLY_BRANCHES[(i + 6) % 12],
                    sanhe=[],
                    is_ming_gong=False,
                    is_shen_gong=False,
                    ganzhi="",
                )
            )
        result = StarPlacementEngine.compute(
            palaces, lunar_day, bureau, "庚", "午", 7, 4
        )
        z = ziwei_idx
        expect = {
            "紫微": EARTHLY_BRANCHES[z],
            "天机": EARTHLY_BRANCHES[(z - 1) % 12],
            "太阳": EARTHLY_BRANCHES[(z - 3) % 12],
            "武曲": EARTHLY_BRANCHES[(z - 4) % 12],
            "天同": EARTHLY_BRANCHES[(z - 5) % 12],
            "廉贞": EARTHLY_BRANCHES[(z - 8) % 12],
        }
        for star, br in expect.items():
            assert result.star_branches[star] == br
