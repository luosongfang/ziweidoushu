# Ziwei Classical Engine V1.6 Report

> Traditional 16 Books Rule Calibration  
> 日期：2026-07-24  
> **未改 AI / UI / 会员**  
> **未因单软件/单盘修改公式**

## 1. 16册规则映射率

| 层级 | 映射率（粗估） |
|------|----------------|
| 核心安星链（历法→命身→局→紫微表→天府配置→十四主星） | **~90%** 已规则化+可 trace |
| 六吉六煞+常用杂曜 | **~75–85%** |
| 长生/博士/岁前/将前 | **~60%**（框架+来源，待专业盘交叉） |
| 运限细盘/格局 | **~15–30%** |
| 全书赋文断事 | **未映射**（本阶段不做 AI） |

16 部来源已在 `rules/sources/` **编目**（非全文 OCR）。

## 2. 当前算法来源

| 步骤 | rule_id | 主要来源 |
|------|---------|----------|
| 历法 | CAL_LUNAR_001 | 万年历/节气；全书用法 |
| 命宫 | PALACE_MING_001 | 全书 / 骨髓赋 / 三合安星诀 |
| 身宫 | PALACE_SHEN_001 | 全书 / 三合安星诀 |
| 五行局 | BUREAU_NAYIN_001 | 纳音表 |
| 紫微 | ZIWEI_TABLE_xxx | 全书 / 星曜秘诀（**仅查表**） |
| 天府 | TIANFU_A/B | 配置显式选择 |
| 十四主星 | STAR_* | 全书紫微系逆、天府系顺 |
| 生年四化 | HUA_BIRTH_001 | 钦天四化 |

运行入口：`ClassicalRuleEngine` → 输出 `classical_trace[]`。

## 3. 存在流派差异（冲突，禁止自动选择）

| 规则 | 选项 | 处理 |
|------|------|------|
| 天府 | 寅申镜像 vs 对宫 | `classical_config.tianfu_rule` |
| 命宫措辞 | 通行「顺月逆时」vs 传抄「逆月顺时」 | 文档化冲突；**现行实现=通行安法**（与 SC-C01 一致），不因单软件改 |
| 学派 | 三合 / 飞星 / 北派 | `classical_config.school` |

检测：`rule_conflict_detector.detect_rule_conflicts()` → `auto_select=false`。

## 4. 未实现规则

- 格局完整库  
- 大限/小限/流年细表与飞星派全套  
- 16册赋文断语（明确不做 AI）  
- 岁前等十二神与文墨逐星标定  

## 5. 下一阶段计划

1. 继续导入文墨专业样本（SC-P*），用 `first_offset_step` 频率≥70% 才审计对应 **规则表/配置**。  
2. 文献核对命宫异文与天府两说，扩充 `sources/` 摘录（仍不单盘硬改）。  
3. 运限与格局规则编目。  
4. 无来源规则保持生产禁入。

## 6. 测试

```bash
python -m pytest tests/test_classical_rule_engine.py -q
# 10 passed
```

覆盖：规则目录、有来源门禁、命身宫、紫微表、SC-C01+trace、冲突检测、辅星目录。

## 7. 关键文件

- `app/ziwei_classical/rules/`（catalog / sources / palace / bureau / stars / …）  
- `app/ziwei_classical/rule_engine.py`  
- `app/ziwei_classical/CLASSICAL_RULE_COVERAGE.md`  
- `tests/test_classical_rule_engine.py`
