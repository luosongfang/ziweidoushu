# Ziwei Core Engine V1.4.1 Report

> Golden Dataset 强校准系统  
> 日期：2026-07-24  
> **本阶段未修改任何排盘算法 / Knowledge Core / AI / 前端**

## 1. 交付物

| 模块 | 路径 |
|------|------|
| 黄金盘 SC-C01…C20 | `app/ziwei/debug/classical_reference_charts/` |
| Coverage Report | `app/ziwei/accuracy/coverage_report.py` |
| Root Cause Analyzer | `app/ziwei/accuracy/root_cause_analyzer.py` |
| Chart Conflict Detector | `app/ziwei/debug/chart_conflict_detector.py` |
| Tests | `tests/test_accuracy_center_v141.py` |

## 2. 黄金盘数量

| 指标 | 值 |
|------|------|
| 总案例 | **20**（SC-C01…SC-C20） |
| verified_professional | **1**（SC-C01） |
| pending | **19**（含引擎快照，仅供覆盖分析，**禁止当作专业真值**） |
| verified_manual | 0 |

> 策略：未经验证的专业截图不得标为 `verified_professional`；禁止为过测试硬编码假专业盘。

## 3. 覆盖范围（含 pending 快照，用于防同质化）

| 维度 | 状态 |
|------|------|
| male_yang | ok（7） |
| male_yin | ok（4） |
| female_yang | thin（1） |
| female_yin | ok（8） |
| 五行局 water/wood/metal/fire/earth | 3 / 3 / 2 / 3 / 9 |
| 时辰分布 | 十二时辰均有样本（pending 槽位） |
| homogeneous_risk | false |
| gaps | 无（结构性）；专业真值仍缺口 |

目的：避免全部案例落在同一性别/局数/时辰。当前 20 槽位已在出生资料层面拉开差异；**专业真值仍仅 1 例**。土五局偏多、female_yang 偏薄，导入文墨盘时应优先补这两类。

## 4. 当前准确率

| 范围 | 结果 |
|------|------|
| SC-C01 vs 引擎 | **100%** matched |
| verified_professional 平均 | **100%**（1/1） |
| 全库 20 例专业准确率 | **不可宣称**（19 pending） |

## 5. 最大风险模块

| 风险 | 说明 |
|------|------|
| **专业样本不足** | 仅 SC-C01 可测，无法证明与文墨天机全面一致 |
| **辅星/煞星/杂曜/运限** | 黄金盘字段已预留，但 expected 多为空 → Diff 跳过，覆盖盲区 |
| **真太阳时 / 地点** | 双盘冲突检测标为 `true_solar_time` 高发可能原因 |
| **流派差** | 命宫一致而主星不同 → `school_difference` / `star_position_engine` |

根因规则（`root_cause_analyzer`）：

1. 命宫不同 → `calendar_or_palace_engine`  
2. 命宫同、十四主星不同 → `star_position_engine`  
3. 主星同、四化不同 → `four_transform_engine`  
4. 主星同、辅煞杂不同 → `minor_star_engine`  
5. 大限/流年不同 → `fortune_engine`  

## 6. 下一步修复建议

1. 用**文墨天机**截图把 SC-C02…C20 升为 `verified_professional`（填满 `expected.palaces` 辅煞杂与四化）。  
2. 优先补齐覆盖缺口：女盘、五局各至少 2 个专业盘、子午卯酉等关键时辰。  
3. 出现 critical diff 时：先跑 `analyze_root_cause` + `detect_chart_conflict`，**多案例一致**后再改对应引擎（仍禁止单例硬编码）。  
4. 在专业盘到位前：不开发杂曜增强、小限、飞星、PDF、AI。

## 7. 测试

```bash
cd backend
python -m pytest tests/test_accuracy_center_v141.py -q
```

覆盖：empty palace strict compare / root cause / golden loading / coverage / conflict detection。  
与 Accuracy Center / Professional Reference / Classical Calibration 合计：**36 passed**（本机回归）。
