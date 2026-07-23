"""Dual-path (stable / aggressive) life-choice simulator — no LLM, no success prophecy."""

from __future__ import annotations

from functools import lru_cache
from typing import Any

from sqlalchemy import text

from app.database.database import SessionLocal
from app.knowledge.decision.decision_risk_analyzer import DecisionRiskAnalyzer

# Fallback path models
_FALLBACK_PATHS: dict[str, dict[str, dict[str, Any]]] = {
    "entrepreneurship": {
        "stable": {
            "conditions": ["已有现金流安全垫", "可兼职验证", "核心客户可触达"],
            "advantages": ["资源积累更稳", "试错成本可控", "便于复盘迭代"],
            "risks": ["窗口把握偏慢", "可能错过短期扩张机会"],
            "recommended_actions": [
                "先做最小可行试点",
                "固定月度现金流复盘",
                "把资源整合优势落到可交付案例",
            ],
            "reflection_questions": [
                "安全垫能支撑多久的验证期？",
                "若试点失败，最小损失是什么？",
            ],
            "focus": ["现金流", "资源积累"],
        },
        "aggressive": {
            "conditions": ["愿意承担较高波动", "团队或渠道可快速铺开"],
            "advantages": ["市场扩张速度快", "机会窗口抓取更积极"],
            "risks": ["资源透支", "节奏失控时复盘不足"],
            "recommended_actions": [
                "设定明确止损线",
                "用周节奏跟踪关键指标",
                "扩张与现金周转并行监控",
            ],
            "reflection_questions": [
                "最大可承受回撤是多少？",
                "扩张是否有可验证需求支撑？",
            ],
            "focus": ["市场扩张", "机会窗口"],
        },
    },
    "career_change": {
        "stable": {
            "conditions": ["可边学边转", "保留基本收入"],
            "advantages": ["转型压力较低", "能力补齐更扎实"],
            "risks": ["周期较长", "惯性拖延"],
            "recommended_actions": ["能力地图补齐", "试岗/副业验证", "设定半年评估点"],
            "reflection_questions": ["已验证能力与假设能力如何区分？"],
            "focus": ["能力积累", "风险缓冲"],
        },
        "aggressive": {
            "conditions": ["可集中投入转型", "有明确目标岗位"],
            "advantages": ["变化适应与开创动能可被快速调用"],
            "risks": ["收入空窗", "信息不足导致误判"],
            "recommended_actions": ["密集信息访谈", "短期项目作品集", "明确退出标准"],
            "reflection_questions": ["若三个月未达标，下一步是调整还是退出？"],
            "focus": ["快速切换", "机会窗口"],
        },
    },
    "relationship_choice": {
        "stable": {
            "conditions": ["双方愿意持续沟通"],
            "advantages": ["关系经营更可预期", "边界逐步清晰"],
            "risks": ["回避关键冲突"],
            "recommended_actions": ["定期对齐期待", "练习清晰表达", "小步改善互动"],
            "reflection_questions": ["最需要被看见的需求是否已被听见？"],
            "focus": ["沟通质量", "边界经营"],
        },
        "aggressive": {
            "conditions": ["需要尽快澄清关系走向"],
            "advantages": ["减少长期消耗", "更快对齐价值观"],
            "risks": ["沟通过急造成误解"],
            "recommended_actions": ["设定真诚对话节点", "写下不可妥协项", "必要时寻求支持"],
            "reflection_questions": ["你更在意确定感，还是关系弹性？"],
            "focus": ["关系澄清", "价值对齐"],
        },
    },
    "relocation": {
        "stable": {
            "conditions": ["可先短期体验新环境"],
            "advantages": ["迁移成本可控", "信息更充分"],
            "risks": ["决策周期拉长"],
            "recommended_actions": ["短期驻留验证", "比较生活与事业约束", "列出不可逆成本"],
            "reflection_questions": ["迁移解决的是机会还是逃避？"],
            "focus": ["环境验证", "成本控制"],
        },
        "aggressive": {
            "conditions": ["目标城市有明确机会"],
            "advantages": ["更快进入新网络", "抓住窗口"],
            "risks": ["适应压力大", "支持系统断裂"],
            "recommended_actions": ["先建最小支持网络", "保留回退方案", "季度复盘适应度"],
            "reflection_questions": ["若不适应当地，90天内如何调整？"],
            "focus": ["机会窗口", "网络重建"],
        },
    },
    "investment_decision": {
        "stable": {
            "conditions": ["安全垫已建立"],
            "advantages": ["波动承受更稳", "纪律易执行"],
            "risks": ["收益预期偏低"],
            "recommended_actions": ["先定最大回撤", "分散与定期复盘", "区分生活金与学习仓"],
            "reflection_questions": ["这笔钱亏损后是否影响基本生活？"],
            "focus": ["安全垫", "纪律配置"],
        },
        "aggressive": {
            "conditions": ["可承受较高波动且有止损"],
            "advantages": ["更积极参与机会窗口"],
            "risks": ["集中度过高", "情绪化加仓"],
            "recommended_actions": ["强制止损规则", "仓位上限", "周度风险检查"],
            "reflection_questions": ["若回撤触发止损，你是否能执行？"],
            "focus": ["机会窗口", "风险敞口管理"],
        },
    },
}

_SCENARIO_DISPLAY = {
    "entrepreneurship": "创业",
    "career_change": "职业转换",
    "relationship_choice": "感情选择",
    "relocation": "迁移选择",
    "investment_decision": "投资决策",
}

_PATH_DISPLAY = {"stable": "稳健路径", "aggressive": "进取路径"}


class PathSimulator:
    """Generate stable/aggressive decision paths without predicting winners."""

    @classmethod
    @lru_cache(maxsize=1)
    def _load_db(cls) -> tuple[dict[str, Any], ...]:
        db = SessionLocal()
        try:
            rows = db.execute(
                text(
                    """
                    SELECT scenario, path_type, conditions, advantages, risks,
                           recommended_actions, reflection_questions
                    FROM public.decision_path_models
                    """
                )
            ).mappings().all()
            if not rows:
                return tuple()
            import json

            out = []
            for r in rows:
                item = dict(r)
                for k in (
                    "conditions",
                    "advantages",
                    "risks",
                    "recommended_actions",
                    "reflection_questions",
                ):
                    v = item.get(k)
                    if isinstance(v, str):
                        item[k] = json.loads(v)
                    item[k] = list(item.get(k) or [])
                out.append(item)
            return tuple(out)
        except Exception:
            return tuple()
        finally:
            db.close()

    @classmethod
    def refresh(cls) -> None:
        cls._load_db.cache_clear()

    @classmethod
    def _path_data(cls, scenario: str, path_type: str) -> dict[str, Any]:
        for row in cls._load_db():
            if row.get("scenario") == scenario and row.get("path_type") == path_type:
                data = dict(row)
                fb = (_FALLBACK_PATHS.get(scenario) or {}).get(path_type) or {}
                if not data.get("focus"):
                    data["focus"] = list(fb.get("focus") or [])
                return data
        return dict((_FALLBACK_PATHS.get(scenario) or {}).get(path_type) or {})

    @classmethod
    def simulate(
        cls,
        decision_analysis: dict[str, Any] | None,
        *,
        scenario_code: str | None = None,
    ) -> dict[str, Any]:
        da = decision_analysis or {}
        code = scenario_code or da.get("scenario_code") or "entrepreneurship"
        if code not in _FALLBACK_PATHS:
            # map fuzzy
            desc = str(da.get("scenario") or "")
            for k, label in _SCENARIO_DISPLAY.items():
                if label in desc or k in desc:
                    code = k
                    break
            else:
                code = "entrepreneurship"

        paths: list[dict[str, Any]] = []
        for ptype in ("stable", "aggressive"):
            raw = cls._path_data(code, ptype)
            focus = list(raw.get("focus") or [])
            if not focus:
                focus = ["资源管理", "节奏复盘"] if ptype == "stable" else ["机会验证", "止损机制"]
            # merge lightly with decision strengths/challenges (not prophecy)
            advantages = DecisionRiskAnalyzer.sanitize_list(
                list(dict.fromkeys(list(raw.get("advantages") or []) + list(da.get("strengths") or [])[:2]))
            )[:6]
            risks = DecisionRiskAnalyzer.sanitize_list(
                list(dict.fromkeys(list(raw.get("risks") or []) + list(da.get("challenges") or [])[:2]))
            )[:6]
            actions = DecisionRiskAnalyzer.sanitize_list(
                list(
                    dict.fromkeys(
                        list(raw.get("recommended_actions") or [])
                        + list(da.get("action_suggestions") or [])[:2]
                    )
                )
            )[:6]
            paths.append(
                {
                    "type": _PATH_DISPLAY.get(ptype, ptype),
                    "path_type": ptype,
                    "focus": focus,
                    "advantages": advantages,
                    "risks": risks,
                    "actions": actions,
                    "reflection_questions": list(raw.get("reflection_questions") or [])[:4],
                    "conditions": list(raw.get("conditions") or [])[:4],
                }
            )

        final = DecisionRiskAnalyzer.sanitize(
            "两条路径提供不同节奏与风险偏好的对照框架，"
            "结合现实条件进行选择；不预测哪条路径必然胜出。"
        )
        return {
            "scenario": _SCENARIO_DISPLAY.get(code, da.get("scenario") or code),
            "scenario_code": code,
            "paths": paths,
            "final": final,
            "safety_notice": DecisionRiskAnalyzer.sanitize(
                "双路径模拟仅供人生规划辅助，不预测绝对结果，不输出宿命论。"
            ),
        }
