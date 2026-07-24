# Classical / Professional Golden Reference Charts

Ziwei Core Engine **V1.3.1** 专业黄金验证数据集。

## 原则

1. **不修改排盘算法**以迎合测试。
2. 仅当**多个** `verified_professional` 案例证明公式错误时，才允许改算法。
3. 只有 `verification_level == verified_professional` 进入自动测试。
4. `pending` 禁止入测；`verified_manual` 可用于人工审计，不进 CI 门禁。

## 验证等级

| Level | 含义 | 自动测试 |
|-------|------|----------|
| `pending` | 尚无完整 reference | 否 |
| `verified_manual` | 人工/内部交叉核对 | 否 |
| `verified_professional` | 专业软件截图或权威专业盘确认 | **是** |

## 标准 JSON 格式

```json
{
  "id": "SC-Cxx",
  "source": "文墨天机专业版截图 / …",
  "verified_by": "姓名或来源说明",
  "verification_level": "pending | verified_manual | verified_professional",
  "gender": "male | female",
  "true_solar_time": false,
  "location": "深圳",
  "birth": {
    "solar": "YYYY-MM-DD",
    "time": "HH:MM",
    "location": "深圳",
    "longitude": null,
    "shichen": "未时"
  },
  "calendar": {
    "type": "solar",
    "lunar": "YYYY-M-D",
    "ganzhi": {
      "year": "",
      "month": "",
      "day": "",
      "hour": ""
    }
  },
  "meta": {
    "minggong": "",
    "shengong": "",
    "wuxingju": "",
    "mingzhu": "",
    "shenzhu": "",
    "ziwei_position": "",
    "tianfu_position": ""
  },
  "palaces": [
    {
      "name": "命宫",
      "branch": "戌",
      "main_stars": [],
      "transformations": []
    }
  ]
}
```

可选扩展（便于精确对比，可由 `palaces` 推导）：

- `fourteen_stars`: 十四主星 → `{branch, palace}`
- `four_transform`: 生年四化 `lu/quan/ke/ji`

## 工具

```python
from app.ziwei.debug.reference_manager import (
    add_reference_chart,
    validate_reference,
    compare_chart,
    export_report,
    list_auto_test_charts,
)
```

差异项 `ChartReferenceDiff.impact`：

- **critical**：命宫/身宫/五行局/紫微/十四主星
- **major**：四化
- **minor**：命主/身主等辅助字段

## 导入专业案例流程

1. 用文墨天机（或等价专业软件）按同一出生资料排盘；注明是否真太阳时与地点。
2. 填满 `meta` + 12 `palaces`（十四主星完整）。
3. 设 `verification_level: verified_professional`，填写 `verified_by` / `source`。
4. `validate_reference()` 通过后写入；跑 `tests/test_professional_reference.py`。
