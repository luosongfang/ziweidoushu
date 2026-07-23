# Golden Regression — Ziwei Core Engine V1.2

本目录存放 `StandardChartSchema V2.5` 标准化输出，用于版本升级回归测试。

- 来源：`ChartBuilder.build()` → `ChartNormalizer.normalize()`
- 输入：`tests/fixtures/standard_charts/SC-*.json`
- 参考年：2026

运行回归：

```bash
pytest backend/tests/test_chart_completeness.py -v
```
