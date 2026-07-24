# Ziwei Core Engine V1.2.6 Classical Calibration Report

> 经典校准阶段报告  
> 日期：2026-07-24  
> 范围：历法 / 命身宫 / 五行局 / 紫微 / 十四主星 / 生年四化  
> **未做**：杂曜、小限、飞星、PDF、AI 增强文案

## 1. 发现的问题

| 问题 | 结论 |
|------|------|
| 用户反馈与文墨天机命宫/主星不一致 | 需 **文墨截图** 才能建立 SC-C02…C10 黄金盘；当前仅 SC-C01 可测 |
| 双入口 ChartBuilder / ChartGenerator | 已统一生产 API → `ChartPipeline` |
| 准确率未门禁 AI | 已加 `ChartAccuracyValidator`（score&lt;95 禁止 AI） |
| 命身宫公式 | 与经典一致，**无需改码**（见公式审计） |

## 2. 错误来源（当前已核实）

相对 **SC-C01（REF-01）**：

- 历法四柱：一致  
- 命宫戌 / 身宫子：一致  
- 土五局 / 紫微巳 / 天府亥：一致  
- 十四主星落宫：一致  
- 生年四化（庚）：一致  

相对 **文墨天机**：

- **尚未导入可验证 reference**（SC-C02…C10 均为 `pending_reference`）  
- 常见外部偏差源：真太阳时、农历/公历混用、节气月安命、天府对宫 vs 寅申镜像流派差  

## 3. 修复 / 新增文件

| 文件 | 说明 |
|------|------|
| `app/ziwei/debug/classical_audit.py` | ClassicalAuditReport + difference_report |
| `app/ziwei/debug/MING_SHEN_FORMULA_AUDIT.md` | 命身宫公式对比 |
| `app/ziwei/chart_pipeline.py` | 统一生产入口 |
| `app/ziwei/core/chart_accuracy_validator.py` | accuracy_score 门槛 |
| `app/api/chart_api.py` | 改走 ChartPipeline，默认 V2.5 |
| `tests/fixtures/classical_reference_charts/*` | SC-C01…C10 |
| `tests/test_classical_calibration.py` | 回归 |
| `tests/test_ming_shen_palace.py` | 命身宫 |
| `tests/test_ziwei_position.py` | 紫微定位 |
| `app/ziwei_ai/report_generator.py` | AI 准确率门禁 |

**本阶段未改**：Knowledge Core、排盘主公式（命身宫）、前端 UI。

## 4. 公式变化

| 模块 | 变化 |
|------|------|
| 命宫/身宫 | **无变化**（确认正确） |
| 五行局（命宫干支纳音） | **无变化** |
| 紫微 `calc_ziwei_branch_index` | **无变化** |
| 天府寅申镜像 | 沿用既有正确实现（巳↔亥与对宫重合） |
| 生年四化表 | **无变化** |

## 5. Reference 对比

| ID | 状态 | 来源 | 测试 |
|----|------|------|------|
| SC-C01 | **verified** | REF-01 / lunar_python 交叉核对 | 进入回归 |
| SC-C02…C10 | **pending_reference** | 待文墨天机截图 | **禁止入测** |

请提供文墨天机截图后，将对应 JSON 的 `status` 改为 `verified` 并填满 `reference_data`。

## 6. 测试结果

```bash
cd backend
python -m pytest tests/test_classical_calibration.py tests/test_ming_shen_palace.py tests/test_ziwei_position.py -q
```

预期：仅 SC-C01 参数化用例全部通过；pending 不参与。

## 7. 当前准确率

| 指标 | 值 |
|------|----|
| 对 SC-C01 核心盘 | **100%**（十四主星 + 命身宫 + 局 + 四化） |
| 对文墨天机多案例 | **未知**（缺 reference） |
| AI 准入阈值 | accuracy_score ≥ **95** |

## 下一步（需你提供）

1. 文墨天机专业版：至少 3 张完整盘截图（含出生时间、命宫、十四主星）  
2. 确认是否使用真太阳时 / 出生地  
3. 确认流派：天府是否「对宫」还是「寅申镜像」  

在完成文墨黄金盘入库前，**停止**杂曜 / 小限 / 飞星 / PDF / AI 增强开发。
