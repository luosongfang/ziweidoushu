# ZIWEI Golden Dataset Report

> Ziwei Core Engine **V1.3.1** Professional Golden Dataset Expansion  
> 日期：2026-07-24  
> **本阶段未修改任何排盘算法**

## 当前验证数量

| 等级 | 数量 |
|------|------|
| **verified_professional** | 1（SC-C01） |
| **verified_manual** | 0 |
| **pending** | 9（SC-C02…SC-C10） |
| **verified（合计）** | 1 |
| **total** | 10 |

## Accuracy

| 指标 | 值 |
|------|------|
| professional_match_rate | **100.0%**（1/1） |
| matched / tested | 1 / 1 |
| critical diffs | 0 |

> 说明：准确率仅针对 `verified_professional`。单一案例不足以证明排盘全面正确；需导入更多文墨天机等专业盘。

## Missing

- SC-C02 … SC-C10：`verification_level=pending`，缺少完整 `meta` / `palaces`，**禁止入测**

## 本阶段交付

| 项 | 路径 |
|----|------|
| Schema + README | `tests/fixtures/classical_reference_charts/README.md` |
| Reference Manager | `app/ziwei/debug/reference_manager.py` |
| ChartReferenceDiff | `compare_chart()` → critical / major / minor |
| 专业回归测试 | `tests/test_professional_reference.py` |
| 数据集索引 | `tests/fixtures/classical_reference_charts/index.json`（v1.3.1） |

## 验证等级策略

- 仅 **`verified_professional`** 进入自动测试
- `pending` / `verified_manual` 不进 CI 门禁
- **禁止**为通过测试修改公式；仅当多个专业案例证明公式错误时才允许改算法

## 下一步

1. 提供文墨天机截图（出生 + 命身局 + 十四主星 + 是否真太阳时）
2. 填入 SC-C02…C10，设为 `verified_professional`
3. 用 `compare_chart()` 收集 critical diffs；多案例一致后再改算法

## 工具用法

```python
from app.ziwei.debug.reference_manager import (
    add_reference_chart,
    validate_reference,
    compare_chart,
    export_report,
)
```
