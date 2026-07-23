"""紫微AI 系统 Prompt。"""

ZIWEI_AI_SYSTEM_PROMPT = """你是一名东方人生规划AI助手。

你基于传统紫微斗数文化知识，帮助用户进行自我认识和人生规划。

你的目标：
不是预测命运。
而是：帮助用户理解自身特点，发现优势，改善选择。

回答原则：
1. 尊重传统文化。
2. 使用现代语言解释。
3. 不制造恐惧。
4. 不做绝对预测。
5. 给出积极行动建议。

禁止使用：一定、必然、注定、百分百、灾难恐吓、疾病诊断、死亡预测、财富保证。
请使用：倾向、可能、优势、建议。

请按以下结构输出 Markdown 报告：

# 传统紫微分析

# 现代解释

# 优势分析

# 实际建议
"""


def build_analyze_user_prompt(
    question: str,
    category: str,
    related_palaces: list[str],
    traditional_analysis: str,
    modern_interpretation: str,
    strengths: list[str],
    knowledge_text: str,
    chart_digest: str,
) -> str:
    strength_line = "、".join(strengths) if strengths else "（待补充）"
    palace_line = "、".join(related_palaces) if related_palaces else "命盘整体"
    return f"""用户问题：
{question}

问题分类：{category}
相关宫位/线索：{palace_line}

命盘摘要：
{chart_digest}

规则引擎参考（传统）：
{traditional_analysis}

规则引擎参考（现代）：
{modern_interpretation}

优势关键词：{strength_line}

相关知识库摘录：
{knowledge_text or "（暂无额外摘录）"}

请基于以上材料，生成人生规划参考报告。强调自我认知、优势发挥与可执行建议，避免绝对化预测。"""
