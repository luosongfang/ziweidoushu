"""紫微排盘引擎异常体系。"""


class ZiweiEngineError(Exception):
    """排盘引擎基础异常。"""


class CalendarError(ZiweiEngineError):
    """历法转换异常。"""


class RuleNotFoundError(ZiweiEngineError):
    """规则未找到（数据库驱动阶段使用）。"""


class UnsupportedSchoolError(ZiweiEngineError):
    """不支持的流派。"""


class UnsupportedCalendarError(ZiweiEngineError):
    """不支持的历法输入。"""
