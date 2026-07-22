# Phase 1 排盘引擎算法说明

> 模块位置：`backend/app/ziwei/`  
> 版本：V1.0 Final Sprint 0 | 架构文档：`documents/ziwei-engine-v1-final.md`

**Sprint 0 重构**：代码已迁移至 `engines/` 子目录，入口改为 `chart_generator.py`。

---

## 1. 模块结构

```
backend/app/ziwei/
├── constants.py    # 天干地支、纳音、命主身主常量
├── calendar.py     # 公历转农历、四柱、时辰
├── palace.py       # 命宫、身宫、十二宫布局
├── wuxing.py       # 五行局
├── daxian.py       # 大限（基础）
├── engine.py       # 排盘入口 ChartEngine.generate()
└── models.py       # 请求/响应 Pydantic 模型
```

---

## 2. 公历转农历与真太阳时（Sprint 2）

**依赖**：`lunar_python`（基于寿星天文历，商业级精度）

**输入**：
- `datetime` — 出生地钟面时间（地方平太阳时）
- `longitude` — 出生地经度（东经，可选）
- `timezone` — IANA 时区，默认 `Asia/Shanghai`（标准经度 120°E）

**输出**：农历年月日、闰月标记、四柱干支、真太阳时、节气信息

**规则**：
- **年柱**：以立春为界（非正月初一）
- **月柱**：以节气为界（非农历初一）
- **日柱**：按日递推六十甲子
- **时柱**：按出生时辰，含早/晚子时处理
- **真太阳时**：提供经度时启用，公式为  
  `真太阳时 = 钟面时间 + (经度 - 标准经度) × 4分钟 + 均时差`

**模块**：
- `engines/calendar_engine.py` — 历法主引擎
- `engines/true_solar.py` — 经度修正 + 均时差

```python
from app.ziwei.engines.calendar_engine import CalendarEngine
from datetime import datetime

# 无经度：钟面时间即排盘时间
CalendarEngine.convert(datetime(1990, 5, 15, 14, 30))

# 深圳经度：启用真太阳时
CalendarEngine.convert(datetime(1990, 5, 15, 14, 30), longitude=114.0579)
# → 庚午年 辛巳月 庚辰日 癸未时（真太阳时约 14:06，仍属未时）
```

**Chart JSON 字段**：
- `birth.solar` — 输入钟面时间
- `birth.trueSolarTime` — 排盘所用真太阳时（无经度时与 solar 相同）

---

## 3. 十二时辰转换

| 索引 | 时辰 | 时间范围 |
|------|------|----------|
| 0 | 子时 | 23:00–01:00 |
| 1 | 丑时 | 01:00–03:00 |
| 2 | 寅时 | 03:00–05:00 |
| 3 | 卯时 | 05:00–07:00 |
| 4 | 辰时 | 07:00–09:00 |
| 5 | 巳时 | 09:00–11:00 |
| 6 | 午时 | 11:00–13:00 |
| 7 | 未时 | 13:00–15:00 |
| 8 | 申时 | 15:00–17:00 |
| 9 | 酉时 | 17:00–19:00 |
| 10 | 戌时 | 19:00–21:00 |
| 11 | 亥时 | 21:00–23:00 |

**算法**：
```
if hour >= 23 or hour < 1:  → 子时(0)
else:                       → index = (hour - 1) // 2 + 1
```

实际排盘以 `lunar_python` 时柱地支为准（含子时跨日）。

---

## 4. 安命宫

**口诀**：寅起正月，顺数至生月，逆数至生时

**步骤**：

1. 正月建寅（地支索引 2）
2. 生月宫位 = `(2 + lunar_month - 1) % 12`
3. 命宫地支 = `(生月宫位 - 时辰索引 + 12) % 12`

**示例**：农历四月，未时(7)

```
生月宫位 = (2 + 4 - 1) % 12 = 5  → 巳
命宫     = (5 - 7 + 12) % 12 = 10 → 戌
```

---

## 5. 安身宫

**口诀**：寅起正月，顺数至生月，顺数至生时

**步骤**：

1. 生月宫位（同上）
2. 身宫地支 = `(生月宫位 + 时辰索引) % 12`

**示例**：农历四月，未时(7)

```
身宫 = (5 + 7) % 12 = 0 → 子
```

---

## 6. 布十二宫（Sprint 3）

以命宫地支为起点，**逆时针**排列：

```
命宫 → 兄弟 → 夫妻 → 子女 → 财帛 → 疾厄 →
迁移 → 交友 → 官禄 → 田宅 → 福德 → 父母
```

**公式**：
```
palace[i].branch_index = (ming_gong_index - i + 12) % 12
```

**Sprint 3 扩展**：
- 每宫 **干支**：五虎遁（年干定寅月干，顺布至各宫地支）
- **对宫**：命宫↔迁移、兄弟↔交友 …（固定映射）
- **三合**：地支三合组对应的另两宫名称
- **语义标签**：从 `palace_meaning_rules` 读取 keyword / meaning → Chart JSON `analysis_tags`

---

## 7. 定五行局（Sprint 3）

**步骤**：

1. **五虎遁**求命宫天干（年干定寅月干，顺布至命宫地支）：

   | 年干 | 寅月天干 |
   |------|----------|
   | 甲、己 | 丙 |
   | 乙、庚 | 戊 |
   | 丙、辛 | 庚 |
   | 丁、壬 | 壬 |
   | 戊、癸 | 甲 |

2. 命宫干支 → 查六十甲子**纳音五行**
3. 纳音五行 → 局数：

   | 五行 | 局名 | 起运年龄 |
   |------|------|----------|
   | 水 | 水二局 | 2 |
   | 木 | 木三局 | 3 |
   | 金 | 金四局 | 4 |
   | 土 | 土五局 | 5 |
   | 火 | 火六局 | 6 |

**示例**：庚年，命宫在戌

```
寅月干 = 戊（乙庚之岁戊为头）
戌宫干 = 戊 + 8 = 丙 → 丙戌
丙戌纳音 = 屋上土 → 土五局
```

---

## 8. 十四主星安放（Sprint 4）

**规则来源**：`ziwei_position_rules` + `star_placement_rules`（禁止 Python 硬编码口诀）

### 8.1 安紫微

1. 查 `ziwei_position_rules`：`bureau` + `lunar_day` → `ziwei_branch`
2. 该地支所在宫位即为紫微星落宫

### 8.2 紫微星系（相对紫微逆布）

| 星曜 | 方向 | 偏移 |
|------|------|------|
| 紫微 | — | 0 |
| 天机 | backward | 1 |
| 太阳 | backward | 3 |
| 武曲 | backward | 4 |
| 天同 | backward | 5 |
| 廉贞 | backward | 8 |

### 8.3 天府星系（天府在紫微对宫，顺布）

| 星曜 | 方向 | 偏移 |
|------|------|------|
| 天府 | opposite | 0 |
| 太阴 | forward | 1 |
| 贪狼 | forward | 2 |
| 巨门 | forward | 3 |
| 天相 | forward | 4 |
| 天梁 | forward | 5 |
| 七杀 | forward | 6 |
| 破军 | forward | 10 |

**方向语义**（地支环）：
- `forward`：顺行 +offset
- `backward`：逆行 −offset
- `opposite`：对宫（+6）

**模块**：`engines/star_placement_engine.py`

**示例**（1990-05-15 14:30 男，土五局，农历廿一）：
- 紫微在巳（疾厄宫）
- 同宫：紫微、七杀；官禄：太阳、巨门；福德：天同、太阴

---

## 9. 辅煞杂曜与四化（Sprint 5）

**规则来源**：`star_placement_rules` + `star_lookup_rules` + `four_transform_rules` + `brightness_rules`

### 9.1 辅星 / 煞星 / 杂曜

| 类型 | 星曜 | 规则 |
|------|------|------|
| 辅星 | 左辅/右弼 | 辰/戌起正月，顺/逆数至生月 |
| 辅星 | 文昌/文曲 | 戌/辰起子时，顺/逆数至生时 |
| 辅星 | 天魁/天钺/禄存 | 年干查 `star_lookup_rules` |
| 煞星 | 擎羊/陀罗 | 禄存顺/逆一位 |
| 煞星 | 火星/铃星 | 年支三合组起宫，顺数至生时 |
| 煞星 | 地空/地劫 | 亥起子时，顺/逆至生时 |
| 杂曜 | 天马 | 年支查 `star_lookup_rules` |

### 9.2 生年四化

年干查 `four_transform_rules` → 禄权科忌 → 星曜 `sihua` 字段 + `fourTransformSummary`。

### 9.3 亮度

主星查 `brightness_rules`（星名 + 地支）→ `brightness` 字段。

---

## 10. 大限（Phase 1 基础）

**顺逆规则**：
- 阳男阴女 → 顺行
- 阴男阳女 → 逆行

**阳干**：甲、丙、戊、庚、壬

**起运**：五行局数为起运年龄，每宫 10 年。

---

## 11. API 用法

```http
POST /api/v1/charts/generate
Content-Type: application/json

{
  "birth_datetime": "1990-05-15T14:30:00",
  "gender": "male",
  "name": "我的命盘"
}
```

---

## 12. 运行测试

```bash
cd backend
pip install -r requirements.txt
pytest tests/test_ziwei_phase1.py -v
```

**参考案例**：1990-05-15 14:30 男

| 项目 | 期望值 |
|------|--------|
| 农历 | 四月廿一 |
| 四柱 | 庚午 辛巳 庚辰 癸未 |
| 命宫 | 戌（丙戌） |
| 身宫 | 子 |
| 五行局 | 土五局 |
| 命主 | 禄存 |
| 身主 | 火星 |

---

## 13. 后续 Sprint

- [x] 十四主星安放（Sprint 4）
- [x] 六吉六煞 + 四化 + 亮度（Sprint 5）
- [x] 大限 + 组合 + 验证（Sprint 6）
- [x] AI 分析接口（Sprint 7）

---

## 14. 大限与流年（Sprint 6）

**大限**：读 `daxian_rules`，顺/逆布十二宫，起运年龄 = 五行局数。

**当前大限**：以虚拟年龄（周岁）定位所在宫位。

**流年**：流年地支 = 太岁所在宫位（与命盘地支对应）。

**流月**：以流年命宫起正月，顺数至目标月份（简化算法）。

**模块**：`engines/fortune_engine.py`

---

## 15. 组合引擎（Sprint 6）

读 `star_combination_rules`，按 `match_type` 识别格局：

| match_type | 含义 |
|------------|------|
| same_palace | 诸星同宫 |
| chart_present | 诸星均在盘内 |
| both_present | 诸星均在盘内但不同宫 |
| flank_ming | 两星夹命宫（兄弟/父母） |
| sole_main_star | 紫微独坐 |
| sihua | 生年四化 |

输出 `combinations.patterns` 供 AI 分析引用。

---

## 16. 验证系统（Sprint 6）

- `verification/reference_runner.py` — 标准盘对比
- `verification/manager.py` — `VerificationManager.run_reference_suite()`
- API：`GET /api/v1/verification/reference`

---

## 17. AI 分析接口（Sprint 7）

**模块**：`app/ai/`

| 文件 | 职责 |
|------|------|
| `context_builder.py` | 从 Chart JSON 提取结构化上下文，注入规则库 ai_prompt |
| `rag_retriever.py` | 知识库检索（内存种子 + 关键词匹配） |
| `prompt_builder.py` | LLM 提示词构建 |
| `llm_client.py` | OpenAI 兼容 API 调用（可选） |
| `analysis_service.py` | 分析编排入口 |

**分析类型**：`overall` / `palace` / `daxian` / `liunian`

**运行模式**：
- `rules`（默认）：规则 DB 驱动结构化解读，无需 API Key
- `llm`：配置 `OPENAI_API_KEY` 后启用 LLM + RAG
- `auto`：有 Key 用 LLM，否则 rules

**API**：
- `POST /api/v1/analyses/generate` — 传入 chart 或 birth
- `POST /api/v1/analyses/generate/birth-input` — BirthInput 便捷入口

---

## 18. 商业化（Sprint 8）

**认证**：Supabase JWT；开发模式 `AUTH_DEV_MODE=true` + `X-Dev-User-Id` 头

**API**：
- `GET/PATCH /api/v1/me` — 用户 Profile（会员等级、AI 配额）
- `POST/GET/DELETE /api/v1/charts/saved` — 命盘持久化
- `POST /api/v1/analyses/persist` — 解读 + 扣配额 + 存历史
- `GET /api/v1/analyses/history` — 解读历史
- `GET /api/v1/membership/plans` — 会员计划
- `POST /api/v1/membership/orders` — 创建订单
- `POST /api/v1/membership/orders/{id}/confirm` — 确认支付（stub）

**存储**：Supabase 未配置时使用内存仓储（开发/测试）

---
