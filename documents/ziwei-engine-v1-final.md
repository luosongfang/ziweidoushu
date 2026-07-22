# 紫微AI 排盘引擎 V1.0 Final Architecture

> **状态**：已确认 · Sprint 0 执行中  
> **版本**：1.0-final  
> **流派**：三合派（sanhe）

---

## 1. 总体架构

```
Input → Calendar → Palace → Bureau → Star Placement → Brightness
     → Four Transform → Fortune → Combination → Chart Generator → Chart JSON → AI
```

**三层架构**：

| 层 | 职责 |
|----|------|
| 规则层 | 9 张 rules 表 + seeds，禁止 Python 硬编码 |
| 计算层 | 9 个 Engine 模块化编排 |
| 输出层 | Chart JSON Final + Verification + 持久化 |

---

## 2. 引擎模块

| 引擎 | 文件 | Sprint |
|------|------|--------|
| Calendar Engine | `engines/calendar_engine.py` | S2 |
| Palace Engine | `engines/palace_engine.py` | S3 |
| Bureau Engine | `engines/bureau_engine.py` | S3 |
| Star Placement Engine | `engines/star_placement_engine.py` | S4–5 |
| Brightness Engine | `engines/brightness_engine.py` | S5 |
| Four Transform Engine | `engines/four_transform_engine.py` | S5 |
| Fortune Engine | `engines/fortune_engine.py` | S6 |
| Combination Engine | `engines/combination_engine.py` | S6–7 |
| AI Analysis | `ai/analysis_service.py` | S7 |
| Chart Generator | `chart_generator.py` | S0 |

---

## 3. 规则数据库（database/rules/）

| 表 | 用途 |
|----|------|
| ziwei_position_rules | 紫微定位 |
| star_placement_rules | 安星规则 |
| nayin_rules | 纳音五行局 |
| daxian_rules | 大限顺逆 |
| four_transform_rules | 生年四化 |
| brightness_rules | 亮度 |
| star_combination_rules | 星曜组合（AI） |
| palace_meaning_rules | 十二宫语义（AI） |
| stars | 星曜元数据 + AI tags |

---

## 4. Chart JSON V1.0 Final

```json
{
  "version": "1.0-final",
  "school": "sanhe",
  "rulesVersion": "2026.07.22",
  "meta": { "mingGong", "shenGong", "wuxingJu", ... },
  "birth": { "solar", "lunar", "ganzhi", "shichen", "location" },
  "palaces": [{ "name", "branch", "position", "opposite", "sanhe", "analysis_tags", ... }],
  "fourTransformSummary": {},
  "combinations": { "patterns": [] },
  "fortune": { "daxianDirection" },
  "feixing": { "enabled": false },
  "trace": { "traceId", "steps" }
}
```

---

## 5. 目录结构

见 `backend/app/ziwei/` 及 `database/rules/`、`tests/fixtures/`。

---

## 6. 测试体系

- 单元测试：`tests/test_*.py`
- 标准命盘：`tests/fixtures/reference_charts.json`（≥12 组）
- 验证系统：`app/ziwei/verification/`
- CI：`docker-compose.yml` → `backend-test` 服务

---

## 7. Sprint 计划

| Sprint | 内容 |
|--------|------|
| S0 | 架构整理 ✅ |
| S1 | 数据库规则层 |
| S2 | 历法系统 |
| S3 | 宫位 + 五行局 |
| S4 | 十四主星 |
| S5 | 辅星 + 四化 + 亮度 |
| S6 | 大限 + 组合 + 验证 |
| S7 | AI 分析接口 ✅ |
| S8 | 商业化 ✅ |

---

## 8. 设计红线

1. 不允许随机生成命盘  
2. 不允许 mock 作为 API 最终结果  
3. 四化/安星/纳音必须 DB 驱动  
4. 规则变更必须跑完全部标准盘  
5. V1.0 仅 sanhe，策略模式预留  

---

详细算法见 `backend/app/ziwei/ALGORITHM.md`。
