# 知识库目录

存放 RAG（检索增强生成）所需的原始资料与处理脚本。

## 目录说明

| 路径 | 作用 |
|------|------|
| `raw/` | 原始古籍文本、流派资料（PDF、TXT、Markdown） |
| `raw/sanhe/` | 三合派资料 |
| `raw/feixing/` | 飞星派资料 |
| `processed/` | 清洗、切片后的文本块，供向量化入库 |
| `scripts/` | 知识入库脚本（阶段 4 实现 `ingest.py`） |

## 使用流程（阶段 4）

1. 将古籍文本放入 `raw/` 对应子目录
2. 运行切片脚本生成 `processed/` 文件
3. 运行 `scripts/ingest.py` 写入 `database` 中的 `knowledge_chunks` 表

## 注意事项

- 注意古籍资料的版权与合规
- 大体积原始文件建议加入 `.gitignore`
