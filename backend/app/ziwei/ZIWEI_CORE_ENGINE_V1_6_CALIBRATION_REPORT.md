# Ziwei Core Engine V1.6 Calibration Report

> Professional Reference Calibration  
> 日期：2026-07-24  
> **未改 AI / UI / 会员 / 知识库**  
> **未因单盘修改公式**

## 1. 50 盘统计

| 指标 | 值 |
|------|------|
| 总样本 SC-P001…P050 | **50** |
| 男 / 女 | **25 / 25** |
| verified_professional | **1**（SC-P001） |
| pending | **49**（待文墨截图填 `chart_reference`） |
| 覆盖设计 | 十二时辰槽、十天干年槽、真太阳时默认 true |

## 2. 最大误差来源

当前专业可测样本仅 1 个，且与 Classical Engine **完全匹配** → **无误差节点可统计**。

与文墨「大规模十四主星差异」**尚未进入可证伪的多案统计**；在 49 个 pending 填满前，**禁止改公式**。

## 3. 首次偏移节点（first_offset_step_frequency）

| 节点 | 频率（专业样本） |
|------|------------------|
| matched | 100%（1/1） |
| calendar / ming_gong / five_element / ziwei / tianfu | 0% |

策略：同一 `first_offset_step` 占全部专业样本 **≥70%** 才允许启动规则审计（仍禁止单盘硬编码）。

当前：`formula_change_allowed = false`

## 4. 是否需要修改公式

**否。**

理由：未达 30 专业盘；无节点 ≥70% 失败频率；SC-P001 自洽。

## 5. 规则覆盖率

| 项 | 状态 |
|----|------|
| Reference Import / Validator | ✅ |
| Diff + first_offset | ✅ |
| classical_config.json 流派切换 | ✅ sanhe / feixing / beipai |
| 岁前/将前/长生/博士 | ✅ **框架 only**（rule_source + formula + trace，未接 AI） |
| Accuracy Gate V1.6 | ✅ claim=false（1/30） |

## 6. Accuracy Gate V1.6

需同时：

1. verified_professional ≥ 30  
2. 十四主星准确率 ≥ 98%  
3. 无 critical 节点残留  

→ 当前 `accuracy_claim_allowed=false`

## 7. 下一阶段计划

1. 导入文墨截图，将 SC-P002…P050 升为 `verified_professional`（覆盖五局与十二时辰）。  
2. 跑 `run_calibration_batch` → 输出 `first_offset_step_frequency`。  
3. 仅当某节点 ≥70% 时，审计该节点规则表/流派配置。  
4. 宣称通过后，再考虑把岁前等框架接入排盘输出（仍不接 AI）。

## 8. 测试

```bash
python -m pytest tests/test_professional_calibration_v16.py -q
```
