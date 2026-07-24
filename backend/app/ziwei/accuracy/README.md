# Professional Accuracy Center (V1.4)

只做**检测**，不修改排盘算法。

## 模块

| 文件 | 职责 |
|------|------|
| `accuracy_manager.py` | 黄金盘管理；仅 `verified_professional` 入自动测试 |
| `reference_compare.py` | engine vs reference → critical/major/minor + score |
| `chart_diff_engine.py` | 基础信息 / 十二宫 / 星曜 / 四化 / 运限 字段级 diff |
| `accuracy_report.py` | 生成 `output/accuracy_report.json` |
| `validation_gate.py` | score&lt;95 或存在 critical → 阻断 |

## 用法

```python
from app.ziwei.accuracy import AccuracyManager, AccuracyReportBuilder, AccuracyValidationGate

mgr = AccuracyManager()
result = mgr.compare_with_engine("SC-C01")
gate = AccuracyValidationGate().evaluate(compare_result=result)
report = AccuracyReportBuilder().build_and_write()
```

## 影响等级

- **critical**：四柱 / 五行局 / 命身宫 / 十四主星 / 紫微天府
- **major**：辅星、煞星、四化、大限/流年
- **minor**：命主身主、杂曜、三合对宫、小限、农历文案
