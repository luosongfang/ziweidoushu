"""StandardChartSchema V2 — 生产命盘统一输出结构。"""

from __future__ import annotations

from typing import Any, Literal, Optional

from pydantic import BaseModel, Field

MAIN_STAR_NAMES: tuple[str, ...] = (
    "紫微", "天机", "太阳", "武曲", "天同", "廉贞",
    "天府", "太阴", "贪狼", "巨门", "天相", "天梁", "七杀", "破军",
)
LUCKY_STAR_NAMES: tuple[str, ...] = (
    "左辅", "右弼", "文昌", "文曲", "天魁", "天钺",
)
LU_CUN_STAR_NAME = "禄存"
SHA_STAR_NAMES: tuple[str, ...] = (
    "擎羊", "陀罗", "火星", "铃星", "地空", "地劫",
)
ZA_STAR_NAMES: tuple[str, ...] = ("天马",)
AUXILIARY_STAR_NAMES: tuple[str, ...] = (
    "天刑", "天姚", "红鸾", "天喜", "孤辰", "寡宿", "华盖", "天哭", "天虚",
)
BRIGHTNESS_LEVELS: tuple[str, ...] = ("庙", "旺", "得", "利", "平", "陷", "不得")

StarCategory = Literal["main", "lucky", "sha", "za", "auxiliary"]
StarType = Literal["main", "lucky", "lu_cun", "sha", "za", "auxiliary"]
SiHuaType = Literal["禄", "权", "科", "忌"]
SchemaVersion = Literal["2.0", "2.5"]


class LunarDetailV2(BaseModel):
    lunar_year: int
    lunar_month: int
    lunar_day: int
    is_leap: bool


class GanzhiV2(BaseModel):
    year: str
    month: str
    day: str
    hour: str


class ShichenV2(BaseModel):
    name: str
    branch: str = ""


class BirthSchemaV2(BaseModel):
    solar: str
    lunar: str
    lunar_detail: LunarDetailV2
    year_gan: str
    year_zhi: str
    ganzhi: dict[str, str]
    shichen: ShichenV2 | str = ""


class MetaSchemaV2(BaseModel):
    name: str
    gender: Literal["male", "female"]
    mingGong: str
    shenGong: str
    mingGongGanZhi: str = ""
    wuxingJu: str
    bureauNumber: int = 0
    mingZhu: str = ""
    shenZhu: str = ""
    nayinElement: str = ""
    ziweiBranch: str = ""
    tianfuBranch: str = ""


class StarSchemaV2(BaseModel):
    name: str
    palace: str
    branch: str
    category: StarCategory
    type: StarType
    brightness: str = ""
    sihua: Optional[SiHuaType] = None
    isMain: bool = False
    source: str = ""
    trace: dict[str, Any] = Field(default_factory=dict)


class AuxiliaryStarSchemaV2(BaseModel):
    name: str
    palace: str
    branch: str = ""
    category: str = "auxiliary"
    source: str = "auxiliary_star_rules"
    trace: dict[str, Any] = Field(default_factory=dict)


class PalaceTransformV2(BaseModel):
    star: str
    type: SiHuaType


class DaXianRangeV2(BaseModel):
    palace: str
    startAge: int
    endAge: int


class PalaceSchemaV2(BaseModel):
    name: str
    branch: str
    ganzhi: str = ""
    position: int = Field(ge=1, le=12)
    opposite: str = ""
    sanhe: list[str] = Field(default_factory=list)
    is_ming_gong: bool = False
    is_shen_gong: bool = False
    main_stars: list[StarSchemaV2] = Field(default_factory=list)
    lucky_stars: list[StarSchemaV2] = Field(default_factory=list)
    sha_stars: list[StarSchemaV2] = Field(default_factory=list)
    za_stars: list[StarSchemaV2] = Field(default_factory=list)
    auxiliary_stars: list[AuxiliaryStarSchemaV2] = Field(default_factory=list)
    transformations: list[PalaceTransformV2] = Field(default_factory=list)
    daxian: DaXianRangeV2 | None = None


class StarsSchemaV2(BaseModel):
    """结构化星曜索引 — 十四主星 / 六吉 / 六煞 / 禄存 / 天马。"""

    main: list[StarSchemaV2] = Field(default_factory=list)
    lucky: list[StarSchemaV2] = Field(default_factory=list)
    lu_cun: list[StarSchemaV2] = Field(default_factory=list)
    sha: list[StarSchemaV2] = Field(default_factory=list)
    za: list[StarSchemaV2] = Field(default_factory=list)
    auxiliary: list[AuxiliaryStarSchemaV2] = Field(default_factory=list)
    all: list[StarSchemaV2] = Field(default_factory=list)


class FourTransformDetailV2(BaseModel):
    star: str
    palace: str
    type: SiHuaType


class FourTransformSchemaV2(BaseModel):
    yearStem: str
    lu: FourTransformDetailV2
    quan: FourTransformDetailV2
    ke: FourTransformDetailV2
    ji: FourTransformDetailV2


class DaXianSchemaV2(BaseModel):
    direction: Literal["forward", "backward"]
    ranges: list[DaXianRangeV2] = Field(default_factory=list)


class PeriodTransformSchemaV2(BaseModel):
    period: str = ""
    stem: str = ""
    palace: str = ""
    year: int = 0
    branch: str = ""
    lu: FourTransformDetailV2
    quan: FourTransformDetailV2
    ke: FourTransformDetailV2
    ji: FourTransformDetailV2
    source: str = "four_transform_rules"
    trace: dict[str, Any] = Field(default_factory=dict)


class LiuNianSchemaV2(BaseModel):
    year: int = 0
    branch: str = ""
    palace: str = ""
    annual_transform: Optional[PeriodTransformSchemaV2] = None


class XiaoxianCycleV2(BaseModel):
    age: int
    palace: str
    branch: str = ""


class XiaoxianSchemaV2(BaseModel):
    enabled: bool = False
    current_age: int = 0
    current_palace: str = ""
    current_branch: str = ""
    direction: str = "forward"
    yearly_cycle: list[XiaoxianCycleV2] = Field(default_factory=list)
    ranges: list[XiaoxianCycleV2] = Field(default_factory=list)
    trace: dict[str, Any] = Field(default_factory=dict)


class TraceSchemaV2(BaseModel):
    traceId: str = ""
    steps: list[dict[str, Any]] = Field(default_factory=list)
    rulesVersion: str = "2026.07.22"
    source: str = "chart_builder"


class StandardChartSchemaV2(BaseModel):
    """StandardChartSchema V2 / V2.5 — 生产命盘标准结构。"""

    schema_version: SchemaVersion = "2.5"
    name: str
    gender: Literal["male", "female"]
    birth: BirthSchemaV2
    meta: MetaSchemaV2
    palaces: list[PalaceSchemaV2]
    stars: StarsSchemaV2
    four_transform: FourTransformSchemaV2
    daxian_transform: Optional[PeriodTransformSchemaV2] = None
    brightness: dict[str, str] = Field(default_factory=dict)
    sanhe: dict[str, list[str]] = Field(default_factory=dict)
    opposite: dict[str, str] = Field(default_factory=dict)
    daxian: DaXianSchemaV2
    liunian: LiuNianSchemaV2
    xiaoxian: XiaoxianSchemaV2 = Field(default_factory=XiaoxianSchemaV2)
    trace: TraceSchemaV2 = Field(default_factory=TraceSchemaV2)
    warnings: list[str] = Field(default_factory=list)
    engine_version: str = "1.2"
    rules_version: str = "2026.07.23"
    school: str = "sanhe"


class ChartCreateApiResponse(StandardChartSchemaV2):
    """POST /api/chart/create 响应 — V2 标准 + API 元数据。"""

    chart_id: Optional[str] = None
    birth_profile_id: Optional[str] = None
    persisted: bool = False
