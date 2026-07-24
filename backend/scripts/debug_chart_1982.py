# -*- coding: utf-8 -*-
"""Write debug JSON for 1982-02-22 未时 after algorithm fix."""
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from app.ziwei.rules.cache import clear_rules_cache
from app.ziwei_engine.chart_builder import ChartBuilder

clear_rules_cache()

OUT = ROOT / "scripts" / "debug_1982_out.json"


def main() -> None:
    chart = ChartBuilder.build(
        name="debug",
        gender="male",
        solar_date="1982-02-22",
        time="14:00",
        location=None,
    )
    debug = chart["algorithm_debug"]
    payload = {
        **debug,
        "mingGong": chart["chart"]["ming_gong"],
        "mingGongGanzhi": chart["chart"]["five_element_detail"]["ming_gong_ganzhi"],
        "nayin": chart["chart"]["five_element_detail"]["nayin"],
        "mingPalaceStars": [
            s["name"]
            for s in chart["chart"]["main_stars"]
            if s["palace"] == "命宫"
        ],
    }
    OUT.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"WROTE {OUT}")


if __name__ == "__main__":
    main()
