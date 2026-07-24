# Golden Dataset V1.4.1

路径：`backend/app/ziwei/debug/classical_reference_charts/`

## 结构

每个 `SC-Cxx.json`：

- `verification_level`: `pending` | `verified_manual` | `verified_professional`
- `source`: `{ name, type }`
- `birth`: `{ solar_date, time, gender, location, true_solar_time }`
- `expected`: `{ calendar, meta, palaces, four_transform, fortune }`

宫位字段：`main_stars` / `lucky_stars` / `sha_stars` / `za_stars`

## 策略

- **仅** `verified_professional` 进入自动测试
- SC-C02…C20 当前为 `pending`：含引擎快照仅供 **coverage** 多样性分析，**不是**专业验证
- 导入文墨截图后：填满 `expected`，改 `verification_level`

## 数量

SC-C01 … SC-C20（共 20）
