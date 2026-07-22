"""星曜数据模型。"""

from __future__ import annotations

from typing import Literal, Optional

from pydantic import BaseModel, Field


class StarOutput(BaseModel):
    name: str
    brightness: str = ""
    sihua: Optional[Literal["禄", "权", "科", "忌"]] = None
    isMain: bool = False


class FourTransformDetail(BaseModel):
    star: str
    palace: str


class FourTransformSummary(BaseModel):
    yearStem: str
    lu: FourTransformDetail
    quan: FourTransformDetail
    ke: FourTransformDetail
    ji: FourTransformDetail
