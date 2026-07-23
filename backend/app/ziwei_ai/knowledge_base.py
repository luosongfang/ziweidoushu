"""紫微知识库管理 — 读取 backend/app/knowledge 下 Markdown。"""

from __future__ import annotations

import re
from functools import lru_cache
from pathlib import Path

_KNOWLEDGE_ROOT = Path(__file__).resolve().parent.parent / "knowledge" / "markdown"

# 星曜名 → 文件
_STAR_FILES = {
    "紫微": "stars/ziwei.md",
    "天府": "stars/tianfu.md",
    "武曲": "stars/wuqu.md",
    "七杀": "stars/qisha.md",
}

# 宫位名 → 文件
_PALACE_FILES = {
    "命宫": "palaces/minggong.md",
    "官禄宫": "palaces/guanlu.md",
    "官禄": "palaces/guanlu.md",
    "财帛宫": "palaces/caibo.md",
    "财帛": "palaces/caibo.md",
    "夫妻宫": "palaces/fuqi.md",
    "夫妻": "palaces/fuqi.md",
}

_TRANSFORM_FILES = {
    "禄": "transformations/huilu.md",
    "化禄": "transformations/huilu.md",
    "权": "transformations/huiquan.md",
    "化权": "transformations/huiquan.md",
    "科": "transformations/huike.md",
    "化科": "transformations/huike.md",
    "忌": "transformations/huiji.md",
    "化忌": "transformations/huiji.md",
}

_PATTERN_FILES = {
    "紫府": "patterns/zifu.md",
    "紫微天府": "patterns/zifu.md",
    "杀破狼": "patterns/shapolang.md",
}

_LUCK_FILES = {
    "大限": "luck/dalimit.md",
    "流年": "luck/liunian.md",
}


def knowledge_root() -> Path:
    return _KNOWLEDGE_ROOT


@lru_cache(maxsize=128)
def _read_file(relative: str) -> str:
    path = _KNOWLEDGE_ROOT / relative
    if not path.exists():
        return ""
    return path.read_text(encoding="utf-8").strip()


def load_star(name: str) -> str:
    rel = _STAR_FILES.get(name)
    return _read_file(rel) if rel else ""


def load_palace(name: str) -> str:
    rel = _PALACE_FILES.get(name)
    return _read_file(rel) if rel else ""


def load_transform(name: str) -> str:
    rel = _TRANSFORM_FILES.get(name)
    return _read_file(rel) if rel else ""


def load_pattern(name: str) -> str:
    rel = _PATTERN_FILES.get(name)
    return _read_file(rel) if rel else ""


def load_luck(name: str) -> str:
    rel = _LUCK_FILES.get(name)
    return _read_file(rel) if rel else ""


def extract_keywords_section(markdown: str) -> list[str]:
    """从「## 性质关键词」段落提取关键词列表。"""
    if not markdown:
        return []
    match = re.search(
        r"##\s*性质关键词\s*\n(.*?)(?=\n##\s|\Z)",
        markdown,
        flags=re.S,
    )
    if not match:
        return []
    body = match.group(1)
    words: list[str] = []
    for line in body.splitlines():
        line = line.strip().lstrip("-*•").strip()
        if line:
            words.append(line)
    return words


def gather_context(
    stars: list[str],
    palaces: list[str],
    transforms: list[str] | None = None,
    patterns: list[str] | None = None,
    luck: list[str] | None = None,
    max_chars: int = 6000,
) -> list[str]:
    """按需收集知识片段，控制总长度。"""
    snippets: list[str] = []
    total = 0

    def _add(text: str) -> None:
        nonlocal total
        if not text:
            return
        if total + len(text) > max_chars:
            return
        snippets.append(text)
        total += len(text)

    for p in palaces:
        _add(load_palace(p))
    for s in stars:
        _add(load_star(s))
    for t in transforms or []:
        _add(load_transform(t))
    for pt in patterns or []:
        _add(load_pattern(pt))
    for lk in luck or []:
        _add(load_luck(lk))

    return snippets
