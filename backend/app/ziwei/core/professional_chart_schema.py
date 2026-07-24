"""ProfessionalChartSchema V3 — 专业排盘完整字段标准（Ziwei Core Engine V1.3）。

不替代 V2.5 运行时契约；由 ProfessionalNormalizer 产出。
排盘算法正确性优先；禁止为展示填充虚假数据。
"""

from __future__ import annotations

from typing import Any, Literal, Optional

from pydantic import BaseModel, Field

SchemaVersionV3 = Literal["3.0"]

MAIN_STAR_NAMES_V3: tuple[str, ...] = (
    "紫微", "天机", "太阳", "武曲", "天同", "廉贞",
    "天府", "太阴", "贪狼", "巨门", "天相", "天梁", "七杀", "破军",
)
SIX_LUCKY_NAMES: tuple[str, ...] = (
    "左辅", "右弼", "文昌", "文曲", "天魁", "天钺",
)
SIX_SHA_NAMES: tuple[str, ...] = (
    "擎羊", "陀罗", "火星", "铃星", "地空", "地劫",
)
OTHER_STAR_NAMES: tuple[str, ...] = (
    "禄存", "天马",
    "红鸾", "天喜", "天姚", "咸池",
    "孤辰", "寡宿", "华盖", "天刑", "天哭", "天虚",
    "天官", "天福", "天寿", "天才", "天月",
)


class BirthV3(BaseModel):
    solar_date: str = ""
    lunar_date: str = ""
    lunar_detail: dict[str, Any] = Field(default_factory=dict)
    ganzhi_year: str = ""
    ganzhi_month: str = ""
    ganzhi_day: str = ""
    ganzhi_hour: str = ""
    true_solar_time: str | None = None
    shichen: str | dict[str, Any] = ""


class BaziV3(BaseModel):
    year: str = ""
    month: str = ""
    day: str = ""
    hour: str = ""


class MetaV3(BaseModel):
    ming_gong: str = ""
    shen_gong: str = ""
    ming_zhu: str = ""
    shen_zhu: str = ""
    wuxing_ju: str = ""
    bureau_number: int = 0
    yin_yang: str = ""
    gender: Literal["male", "female"] = "male"
    name: str = ""
    ming_gong_ganzhi: str = ""
    ziwei_branch: str = ""
    tianfu_branch: str = ""


class StarPlacementV3(BaseModel):
    name: str
    branch: str = ""
    palace: str = ""
    brightness: str = ""
    sihua: str | None = None
    category: str = ""
    rule_source: str = ""
    trace: dict[str, Any] = Field(default_factory=dict)


class PalaceV3(BaseModel):
    palace_name: str
    branch: str
    ganzhi: str = ""
    position: int = 0
    opposite: str = ""
    sanhe: list[str] = Field(default_factory=list)
    is_ming_gong: bool = False
    is_shen_gong: bool = False
    main_stars: list[StarPlacementV3] = Field(default_factory=list)
    lucky_stars: list[StarPlacementV3] = Field(default_factory=list)
    evil_stars: list[StarPlacementV3] = Field(default_factory=list)
    minor_stars: list[StarPlacementV3] = Field(default_factory=list)
    brightness: dict[str, str] = Field(default_factory=dict)
    transformations: list[dict[str, str]] = Field(default_factory=list)
    daxian: dict[str, Any] | None = None
    liunian: dict[str, Any] | None = None
    xiaoxian: dict[str, Any] | None = None


class StarsIndexV3(BaseModel):
    main_stars: list[StarPlacementV3] = Field(default_factory=list)
    six_lucky: list[StarPlacementV3] = Field(default_factory=list)
    six_sha: list[StarPlacementV3] = Field(default_factory=list)
    others: list[StarPlacementV3] = Field(default_factory=list)
    all: list[StarPlacementV3] = Field(default_factory=list)


class SiHuaBlockV3(BaseModel):
    lu: str = ""
    quan: str = ""
    ke: str = ""
    ji: str = ""
    details: dict[str, Any] = Field(default_factory=dict)
    stem: str = ""
    source: str = ""
    trace: dict[str, Any] = Field(default_factory=dict)


class FourTransformV3(BaseModel):
    birth_transform: SiHuaBlockV3 = Field(default_factory=SiHuaBlockV3)
    daxian_transform: SiHuaBlockV3 = Field(default_factory=SiHuaBlockV3)
    liunian_transform: SiHuaBlockV3 = Field(default_factory=SiHuaBlockV3)
    self_transform: list[dict[str, Any]] = Field(default_factory=list)
    # 兼容简写
    year: SiHuaBlockV3 | None = None
    daxian: SiHuaBlockV3 | None = None
    liunian: SiHuaBlockV3 | None = None
    self: list[dict[str, Any]] = Field(default_factory=list)


class FortunePeriodV3(BaseModel):
    enabled: bool = True
    items: list[dict[str, Any]] = Field(default_factory=list)
    current: dict[str, Any] = Field(default_factory=dict)
    direction: str = ""
    trace: dict[str, Any] = Field(default_factory=dict)


class FortuneV3(BaseModel):
    daxian: FortunePeriodV3 = Field(default_factory=FortunePeriodV3)
    liuxian: FortunePeriodV3 = Field(default_factory=FortunePeriodV3)  # 流年
    xiaoxian: FortunePeriodV3 = Field(default_factory=FortunePeriodV3)
    liuyue: FortunePeriodV3 = Field(default_factory=FortunePeriodV3)
    liuri: FortunePeriodV3 = Field(default_factory=FortunePeriodV3)
    liushi: FortunePeriodV3 = Field(default_factory=FortunePeriodV3)


class CombinationV3(BaseModel):
    name: str
    palaces: list[str] = Field(default_factory=list)
    stars: list[str] = Field(default_factory=list)
    source: str = "traditional"
    match_type: str = ""
    confidence: float = 1.0


class QualityV3(BaseModel):
    quality_score: float = 0.0
    warnings: list[str] = Field(default_factory=list)
    checks: dict[str, bool] = Field(default_factory=dict)


class TraceV3(BaseModel):
    trace_id: str = ""
    steps: list[dict[str, Any]] = Field(default_factory=list)
    rules_version: str = ""
    engine_version: str = "1.3"
    source: str = "chart_generator"


class ProfessionalChartSchemaV3(BaseModel):
    """专业命盘完整结构 V3。"""

    schema_version: SchemaVersionV3 = "3.0"
    name: str = ""
    gender: Literal["male", "female"] = "male"
    birth: BirthV3 = Field(default_factory=BirthV3)
    bazi: BaziV3 = Field(default_factory=BaziV3)
    meta: MetaV3 = Field(default_factory=MetaV3)
    palaces: list[PalaceV3] = Field(default_factory=list)
    stars: StarsIndexV3 = Field(default_factory=StarsIndexV3)
    four_transform: FourTransformV3 = Field(default_factory=FourTransformV3)
    fortune: FortuneV3 = Field(default_factory=FortuneV3)
    brightness: dict[str, str] = Field(default_factory=dict)
    star_combination: list[CombinationV3] = Field(default_factory=list)
    sanhe_structure: dict[str, list[str]] = Field(default_factory=dict)
    feixing: dict[str, Any] = Field(default_factory=lambda: {"enabled": False, "items": []})
    quality: QualityV3 = Field(default_factory=QualityV3)
    trace: TraceV3 = Field(default_factory=TraceV3)
    engine_version: str = "1.3"
    rules_version: str = ""
    school: str = "sanhe"
    # V2.5 兼容快照（可选）
    legacy_v2: Optional[dict[str, Any]] = None
