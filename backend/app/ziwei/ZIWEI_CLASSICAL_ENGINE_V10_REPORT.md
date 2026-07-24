# Ziwei Classical Rule Engine V1.0 Report

> 日期：2026-07-24  
> 范围：**仅计算内核**（未改 frontend / Knowledge Core / AI prompt / membership）

## 1. 当前规则覆盖率

| 模块 | 覆盖 | 说明 |
|------|------|------|
| 历法（农历/四柱/节气） | ✅ | `calendar/lunar.py` trace |
| 命宫/身宫/十二宫 | ✅ | 寅起正月；命逆时、身顺时 |
| 五行局 | ✅ | 纳音 → 水二…火六 |
| 紫微定位 | ✅ | **`ziwei_position_table.json` 查表 150 格**（禁止运行时动态替代） |
| 天府 | ✅ | `tianfu_rule=traditional\|yin_shen_mirror\|opposite` |
| 十四主星 | ✅ | 紫微系逆布 + 天府系顺布，逐步 trace |
| 甲级辅星 | ✅ | 左辅右弼文昌文曲天魁天钺 |
| 乙级 | ✅ | 禄存、天马 |
| 煞星 | ✅ | 羊陀火铃空劫 |
| 丙级杂曜 | ✅ | 刑姚鸾喜孤寡华盖哭虚官福寿才月解巫等 |
| 生年四化 | ✅ | |
| 大限/流年/自化/小限 | 骨架 | 待专业盘批量校验后深化 |
| 岁前/将前/长生/博士 | ❌ | 仍受十四主星专业门禁约束，本版未实现 |

**SC-C01**：Classical ↔ Current dual compare **100% PASS**；与黄金盘十四主星一致。

## 2. 16册规则映射率（粗估）

| 资料类型 | 映射状态 |
|----------|----------|
| 安星口诀（紫微五局表、命身宫、十四主星） | 已代码化 + 可 trace |
| 辅煞杂曜常用表 | 部分代码化（丙级部分用通行表，需文墨交叉） |
| 四化 | 生年已映射；大限/流年/自化待深化 |
| 运限细盘 | 骨架 |
| 格局/杂曜进阶/飞星 | **未映射**（本阶段禁止扩 AI） |

粗估：**核心安星链 ~55–65%**；全书规则 **~25–35%**（缺岁前将前长生博士与运限细表）。

## 3. 与旧引擎（CurrentEngine）差异

| 项 | 结果 |
|----|------|
| DualEngineCompare（SC-C01） | calendar/palace/bureau/ziwei/tianfu/fourteen **全部 PASS** |
| 紫微 | Classical **查表**；Current 公式生成表 — 当前表源一致 |
| 天府 | 默认 traditional=寅申镜像，与 Current 一致；可切 opposite |
| 辅杂 | Classical 独立模块显式规则；Current 走 RulesLoader — 可能细节差，需专业盘比对 |

**与文墨仍可能大规模差主星**：根因不在「Classical vs Current」分裂，而在 **专业样本不足 + 真太阳时/流派**。禁止单盘硬改。

## 4. 下一阶段修复计划

1. 导入文墨截图填满 `references/golden` SC-C02…C50 的 `expected`（≥30 升 `verified_professional`）。  
2. 对每盘跑 ClassicalEngine + DualEngineCompare + `rule_trace`，聚合 `first_offset_step`。  
3. 多案例一致后再改**表数据或流派配置**（仍禁止单例硬编码）。  
4. 十四主星专业宣称通过后：岁前/将前/长生/博士。  
5. 运限/大限四化细表对齐。

## 5. ClassicalAccuracyGate

- 阈值：**98%**  
- 失败文案：**「命盘校准中，请勿生成解释」**  
- 已接入 `report_generator`（读 `chart_data.classical_accuracy`，**未改 AI prompt 正文**）

## 6. 测试

```bash
python -m pytest tests/test_classical_engine_v10.py -q
# 17 passed
```

覆盖：SC-C01 100%、紫微表、十四主星、五行局、空宫、辅助星、门禁。

## 7. 包结构

`backend/app/ziwei_classical/` 已按 Phase 0 目录落地；权威紫微表：

`references/ziwei_position_table.json`
