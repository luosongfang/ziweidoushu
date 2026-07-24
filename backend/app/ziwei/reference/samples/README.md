# Professional Reference Samples (V1.6)

路径：`backend/app/ziwei/reference/samples/`

- `SC-P001`：`verified_professional`（由 SC-C01 映射，待补文墨原图）
- `SC-P002`…`SC-P050`：`pending` 覆盖槽（25男/25女，时辰/年干分散）

导入：

```python
from app.ziwei.reference import ReferenceImporter
ReferenceImporter().import_dict({...})
```

仅 `verified_professional` 进入校准统计与 Accuracy Gate V1.6。
