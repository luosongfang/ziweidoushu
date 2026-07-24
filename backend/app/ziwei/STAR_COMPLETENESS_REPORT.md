# STAR_COMPLETENESS_REPORT.md

> Ziwei Core Engine V1.3 Phase 1 审计  
> 范围：`backend/app/ziwei` + `backend/app/ziwei_engine`  
> 日期：2026-07-24  
> 原则：只审计、标记状态；本文件阶段不补代码。

## 状态图例

| 标记 | 含义 |
|------|------|
| `implemented` | 规则存在且进入 ChartBuilder / V2.5 生产路径 |
| `wrong` | 实现存在但与经典三合规则冲突（已知） |
| `missing` | 无安置规则或未接入生产路径 |
| `partial` | 有实现但不完整 / 仅旧入口 |

---

## 1. 十四主星

| 星曜 | 状态 | 规则来源 | 备注 |
|------|------|----------|------|
| 紫微 | implemented | `seed_generator.calc_ziwei` + placement | 三合安紫微 |
| 天机 | implemented | 紫微逆 1 | |
| 太阳 | implemented | 紫微逆 3 | |
| 武曲 | implemented | 紫微逆 4 | |
| 天同 | implemented | 紫微逆 5 | |
| 廉贞 | implemented | 紫微逆 8 | |
| 天府 | implemented | 寅申镜像 `mirror` | V1.2 已修对宫错误 |
| 太阴 | implemented | 天府顺 1 | |
| 贪狼 | implemented | 天府顺 2 | |
| 巨门 | implemented | 天府顺 3 | |
| 天相 | implemented | 天府顺 4 | |
| 天梁 | implemented | 天府顺 5 | |
| 七杀 | implemented | 天府顺 6 | |
| 破军 | implemented | 天府顺 10 | |

**小结：14/14 implemented**

---

## 2. 六吉星

| 星曜 | 状态 | 规则来源 |
|------|------|----------|
| 左辅 | implemented | 月系，辰起顺 |
| 右弼 | implemented | 月系，戌起逆 |
| 文昌 | implemented | 时系，戌起顺 |
| 文曲 | implemented | 时系，辰起逆 |
| 天魁 | implemented | 年干查表 |
| 天钺 | implemented | 年干查表 |

**小结：6/6 implemented**

---

## 3. 六煞星

| 星曜 | 状态 | 规则来源 |
|------|------|----------|
| 擎羊 | implemented | 禄存顺 1 |
| 陀罗 | implemented | 禄存逆 1 |
| 火星 | implemented | 年支三合 + 时 |
| 铃星 | implemented | 年支三合 + 时 |
| 地空 | implemented | 时系 |
| 地劫 | implemented | 时系 |

**小结：6/6 implemented**

---

## 4. 禄存 / 天马

| 星曜 | 状态 | 备注 |
|------|------|------|
| 禄存 | implemented | 年干查表，V2 单独桶 `lu_cun` |
| 天马 | implemented | 年支查表，`za_star` |

---

## 5. 桃花星

| 星曜 | 状态 | 引擎 |
|------|------|------|
| 红鸾 | implemented | `AuxiliaryStarEngine` |
| 天喜 | implemented | 红鸾对宫 |
| 天姚 | implemented | 月系 |
| 咸池 | **missing** | 无规则 |

---

## 6. 孤寡星

| 星曜 | 状态 |
|------|------|
| 孤辰 | implemented |
| 寡宿 | implemented |

---

## 7. 杂曜

| 星曜 | 状态 | 备注 |
|------|------|------|
| 华盖 | implemented | 年支三合组 |
| 天刑 | implemented | 年支偏移 |
| 天哭 | implemented | 年支偏移 |
| 天虚 | implemented | 年支偏移 |
| 天官 | **missing** | 仅有知识库文案 |
| 天福 | **missing** | 仅有知识库文案 |
| 天寿 | **missing** | |
| 天才 | **missing** | |
| 天月 | **missing** | 仅有知识库文案 |

---

## 8. 四化

| 类型 | 状态 | 路径 |
|------|------|------|
| 生年四化 | implemented | `FourHuaCalculator` / `FourTransformEngine` |
| 大限四化 | implemented | `DaxianTransformCalculator`（仅 Builder） |
| 流年四化 | implemented | `LiunianTransformCalculator`（仅 Builder） |
| 自化/宫干飞化 | **missing** | Generator 仅占位 `feixing.enabled=False` |
| 流月/流日/流时四化 | **missing** | |

---

## 9. 运限

| 类型 | 状态 | 备注 |
|------|------|------|
| 大限 | implemented | |
| 小限 | implemented | ChartBuilder；虚岁 |
| 流年 | implemented | 太岁落宫 |
| 流月 | partial | 仅 ChartGenerator，简化算法 |
| 流日 | **missing** | |
| 流时 | **missing** | |

---

## 10. 亮度 / 格局

| 模块 | 状态 |
|------|------|
| 十四主星亮度 | implemented（庙旺得利平陷） |
| 辅煞杂曜亮度 | **missing** |
| 格局组合规则 | implemented（约 20 条，在 `CombinationEngine`） |
| 格局接入 V2 API | **missing**（仅 ChartGenerator） |

---

## 11. 双入口差异

| 能力 | ChartBuilder→V2.5 | ChartGenerator→v1 |
|------|-------------------|-------------------|
| 十四主星+六吉六煞 | ✓ | ✓ |
| 辅助 9 星 | ✓ | ✗ |
| 小限 | ✓ | ✗ |
| 大限/流年四化 | ✓ | ✗ |
| 格局组合 | ✗ | ✓ |
| 流月 | ✗ | partial |

---

## 12. Phase 2+ 优先补齐清单

1. **missing 星曜（6）**：咸池、天官、天福、天寿、天才、天月  
2. **自化/飞化**  
3. **格局接入生产路径**  
4. **辅煞亮度表（可扩展）**  
5. **流月/流日/流时**（可先骨架 + enabled=false，禁止假数据）  
6. **统一 ChartGenerator → ProfessionalChartSchema V3**

---

## 统计

| 类别 | implemented | missing | partial/wrong |
|------|-------------|---------|---------------|
| 十四主星 | 14 | 0 | 0 |
| 六吉 | 6 | 0 | 0 |
| 六煞 | 6 | 0 | 0 |
| 禄存天马 | 2 | 0 | 0 |
| 桃花 | 3 | 1 | 0 |
| 孤寡 | 2 | 0 | 0 |
| 杂曜(9) | 4 | 5 | 0 |
| **星曜合计** | **37** | **6** | **0** |
