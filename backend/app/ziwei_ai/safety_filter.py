"""安全表达过滤 — 避免绝对化、恐吓与不当诊断表述。"""

from __future__ import annotations

import re

# 直接禁止出现的片段（命中则整句倾向替换）
_BANNED_PHRASES: list[tuple[re.Pattern[str], str]] = [
    (re.compile(r"一定会发财"), "可能具备财富管理优势，需要结合现实行动。"),
    (re.compile(r"必然发财"), "可能具备财富管理优势，需要结合现实行动。"),
    (re.compile(r"注定发财"), "可能具备财富管理优势，需要结合现实行动。"),
    (re.compile(r"今年有灾"), "这个阶段建议提高风险意识，做好规划。"),
    (re.compile(r"必有灾难"), "这个阶段建议提高风险意识，做好规划。"),
    (re.compile(r"一定会"), "比较可能"),
    (re.compile(r"必然"), "较可能"),
    (re.compile(r"注定"), "倾向于"),
    (re.compile(r"百分百"), "在一定程度上"),
    (re.compile(r"死亡预测|必死|将死|寿命将尽"), "关于健康与寿命，请以专业医疗建议为准，此处仅作生活节奏提醒。"),
    (re.compile(r"疾病诊断|确诊为|患有癌症|绝症"), "健康议题请咨询专业医疗机构，这里只提供生活与压力管理建议。"),
    (re.compile(r"财富保证|保证致富|稳赚不赔"), "财务结果存在不确定性，建议理性规划并控制风险。"),
    (re.compile(r"灾难"), "挑战"),
]


def apply_safety_filter(text: str) -> str:
    """对模型或规则文本做安全替换。"""
    if not text:
        return text
    out = text
    for pattern, repl in _BANNED_PHRASES:
        out = pattern.sub(repl, out)
    return out


def contains_unsafe_language(text: str) -> bool:
    probes = ["一定会", "必然", "注定", "死亡预测", "疾病诊断", "财富保证", "灾难"]
    return any(p in (text or "") for p in probes)
