"""星曜模块。"""

from app.ziwei_engine.stars.evil_stars import EvilStarsCalculator
from app.ziwei_engine.stars.fourteen_stars import FourteenStarsCalculator
from app.ziwei_engine.stars.lucky_stars import LuckyStarsCalculator
from app.ziwei_engine.stars.tianfu import TianfuStarCalculator
from app.ziwei_engine.stars.ziwei import ZiweiStarCalculator

__all__ = [
    "ZiweiStarCalculator",
    "TianfuStarCalculator",
    "FourteenStarsCalculator",
    "LuckyStarsCalculator",
    "EvilStarsCalculator",
]
