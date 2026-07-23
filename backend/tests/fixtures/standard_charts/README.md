# 标准命盘测试库（Ziwei Core Engine Audit V1.0）

本目录存放 **10 个经典命盘回归用例**，用于防止排盘引擎升级破坏核心逻辑。

## 文件说明

| 文件 | 说明 |
|------|------|
| `index.json` | 用例索引与元数据 |
| `SC-01.json` … `SC-10.json` | 单个命盘用例（input + expected） |

## 用例分级

- **full**：含十四主星落宫 + 生年四化 + 辅煞（可全量回归）
- **partial**：含干支/命宫/五行局/十二宫地支（历法/宫位回归）
- **pending_stars**：结构字段已确认，星曜期望待引擎快照补全

## 运行验证

```bash
cd backend
pytest tests/test_verification.py tests/test_calendar.py -q
```

修复阶段完成后，应对所有 `full` 用例执行 `verify_reference_chart` 等价校验。
