"""对宫。"""

from __future__ import annotations

from app.ziwei.constants import EARTHLY_BRANCHES


def opposite_branch(branch: str) -> str:
    idx = EARTHLY_BRANCHES.index(branch)
    return EARTHLY_BRANCHES[(idx + 6) % 12]
