# Ziwei Core Engine V1.5 Report

> Professional Placement Verification  
> 日期：2026-07-24  
> **未改排盘算法 / Knowledge Core / AI / UI**  
> **未实现**岁前/将前/长生/博士（十四主星专业门禁未过）

## 1. 当前偏差来源（审计结论）

| 层级 | 状态 | 说明 |
|------|------|------|
| 引擎内部自洽 | 通过 | 紫微公式 ↔ 规则表 150/150；天府镜像与天府系顺布一致 |
| SC-C01 专业盘 | 通过 | 十四主星与引擎一致 |
| vs 文墨大规模差异 | **未闭合** | 仅 **1** 个 `verified_professional`；禁止单例定论 |
| 最可能外部偏移点 | 待证 | ①真太阳时/地点 ②历法日界/节气月 ③命宫起法 ④天府对宫派 vs 寅申镜像派 |

`star_trace.py` 逐步输出：`calendar → ming_gong → wuxing_ju → ziwei → tianfu → fourteen → palace_mapping`，用于定位「哪一步开始偏移」。

若文墨与引擎命宫已不同 → 先查 Calendar/Palace；命宫同而紫微不同 → 查局数或紫微口诀流派；紫微同而天府/主星不同 → 查镜像 vs 对宫及顺逆布。

## 2. 紫微定位准确率

| 指标 | 值 |
|------|------|
| 矩阵覆盖 | **5 局 × 30 日 = 150** |
| 公式 ↔ RulesLoader | **150/150 通过** |
| 相对文墨专业盘 | **样本不足，不可宣称** |

测试：`tests/test_ziwei_position_matrix.py`

## 3. 天府定位准确率

| 指标 | 值 |
|------|------|
| 寅申轴镜像公式 `(4-z)%12` | 12/12 地支自洽 |
| 天府系顺布（府阴贪巨相梁杀破） | 多局多日抽样通过 |
| 反例：紫微子→天府辰（非对宫午） | 通过 |
| 相对文墨 | **样本不足，不可宣称** |

测试：`tests/test_tianfu_position.py`

## 4. 十四主星准确率

| 指标 | 值 |
|------|------|
| verified_professional | **1 / 30 要求** |
| 现有专业盘与引擎匹配 | 1/1（SC-C01） |
| **accuracy_claim_allowed** | **False** |
| status | `insufficient_samples` |

规则：**至少 30 个 verified_professional 全部匹配**，才允许宣称十四主星专业准确率。  
禁止「单案例通过即认为正确」。

测试：`tests/test_fourteen_star_golden.py`

## 5. 缺失星曜列表（Phase 5 未实现）

门禁：`can_expand_professional_aux_systems() → allowed=False`

| 分组 | 状态 |
|------|------|
| 岁前十二神 | 整组缺失（待实现） |
| 将前十二神 | 大部分缺失（华盖/咸池等或已有杂曜同名，清单见 gate） |
| 长生十二神 | 整组缺失 |
| 博士十二神 | 整组缺失 |

**前提未满足：十四主星专业 100% 宣称** → 本阶段不新增上述系统。

## 6. 交付文件

| 文件 | 作用 |
|------|------|
| `app/ziwei/debug/star_trace.py` | 安星逐步 Trace |
| `tests/test_ziwei_position_matrix.py` | 150 紫微矩阵 |
| `tests/test_tianfu_position.py` | 天府+天府系 |
| `tests/test_fourteen_star_golden.py` | 十四主星专业门禁 |
| `app/ziwei/accuracy/fourteen_star_gate.py` | Phase5 扩展门禁 |
| `tests/test_phase5_aux_gate.py` | 禁止过早扩展 |

## 7. 下一步（仍不改算法直至多案证明）

1. 导入 ≥30 份文墨天机截图 → `verified_professional`（填满十四主星）  
2. 对每盘跑 `run_star_trace` + `compare_trace_to_reference`，统计 `first_offset_step`  
3. 仅当**多个**专业案指向同一规则错误时，才修改对应公式  
4. 十四主星宣称通过后，再开 Phase 5（岁前/将前/长生/博士）

## 8. 测试摘要

```text
tests/test_ziwei_position_matrix.py
tests/test_tianfu_position.py
tests/test_fourteen_star_golden.py
tests/test_phase5_aux_gate.py
→ 197 passed, 1 skipped
```
