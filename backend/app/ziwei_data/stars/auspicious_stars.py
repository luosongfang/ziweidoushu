"""六吉星知识库 — 辅助、协作与贵人象征（现代倾向解读）。"""

from __future__ import annotations

from typing import Any

AUSPICIOUS_STAR_DATABASE: dict[str, dict[str, Any]] = {
    "左辅": {
        "name": "左辅",
        "type": "辅星",
        "category": "六吉星",
        "traditional": "传统中常象征辅助、协作与侧翼支持，多与得人之助的气质相关。",
        "keywords": ["辅助", "协作", "支持", "团队"],
        "strengths": ["团队合作倾向", "补位与协调能力"],
        "challenges": ["过度依赖他人时需强化自主"],
        "meaning": "辅助、协作、资源支持",
        "modern": "团队合作能力和获得支持机会的倾向，宜主动经营互助关系。",
    },
    "右弼": {
        "name": "右弼",
        "type": "辅星",
        "category": "六吉星",
        "traditional": "传统中常与左辅并称，象征协助、圆融与人际润滑。",
        "keywords": ["圆融", "协助", "人脉", "调和"],
        "strengths": ["人际调和倾向", "侧面推动事务"],
        "challenges": ["迎合过多时需明确立场"],
        "meaning": "圆融协助、人际润滑",
        "modern": "可理解为通过关系和协商推进事情的能力倾向。",
    },
    "文昌": {
        "name": "文昌",
        "type": "辅星",
        "category": "六吉星",
        "traditional": "传统中常象征文采、考试与文书能力，多用来描述学习与表达气质。",
        "keywords": ["文采", "学习", "文书", "考试"],
        "strengths": ["书面表达与学习倾向", "规则与文字敏感"],
        "challenges": ["纸上谈兵时需补实践验证"],
        "meaning": "文采、文书、学业象征",
        "modern": "可理解为学习力、写作与专业认证相关的发展倾向。",
    },
    "文曲": {
        "name": "文曲",
        "type": "辅星",
        "category": "六吉星",
        "traditional": "传统中常象征才艺、巧思与艺术气质，多与感性表达相关。",
        "keywords": ["才艺", "巧思", "艺术", "表达"],
        "strengths": ["创意表达倾向", "细节审美"],
        "challenges": ["灵感多时需结构化产出"],
        "meaning": "才艺、巧思、艺术象征",
        "modern": "可理解为创意、表演或设计类表达倾向。",
    },
    "天魁": {
        "name": "天魁",
        "type": "辅星",
        "category": "六吉星",
        "traditional": "传统中常象征阳贵人，多用来描述公开场合获得提携与认可的象征。",
        "keywords": ["贵人", "提携", "公开认可", "机遇"],
        "strengths": ["易获公开支持的倾向", "关键节点被看见"],
        "challenges": ["机遇出现时需自身准备到位"],
        "meaning": "阳贵人、公开提携象征",
        "modern": "可理解为更容易在公开渠道获得引荐与机会的倾向。",
    },
    "天钺": {
        "name": "天钺",
        "type": "辅星",
        "category": "六吉星",
        "traditional": "传统中常象征阴贵人，多用来描述私下协助、幕后支持的象征。",
        "keywords": ["贵人", "幕后支持", "人脉", "机缘"],
        "strengths": ["私下协作与引荐倾向", "关系中的隐性资源"],
        "challenges": ["需维护信任，忌透支人情"],
        "meaning": "阴贵人、幕后支持象征",
        "modern": "可理解为通过私下关系获得协助与信息的倾向。",
    },
}
