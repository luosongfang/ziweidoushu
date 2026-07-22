"""规则种子数据生成器 — 与 database/rules/*.sql 保持一致。"""

from __future__ import annotations

from app.ziwei.constants import EARTHLY_BRANCHES

RULES_VERSION = "2026.07.22"
SCHOOL = "sanhe"

# 六十甲子纳音全名
NAYIN_NAMES: dict[str, str] = {
    "甲子": "海中金", "乙丑": "海中金", "丙寅": "炉中火", "丁卯": "炉中火",
    "戊辰": "大林木", "己巳": "大林木", "庚午": "路旁土", "辛未": "路旁土",
    "壬申": "剑锋金", "癸酉": "剑锋金", "甲戌": "山头火", "乙亥": "山头火",
    "丙子": "涧下水", "丁丑": "涧下水", "戊寅": "城头土", "己卯": "城头土",
    "庚辰": "白蜡金", "辛巳": "白蜡金", "壬午": "杨柳木", "癸未": "杨柳木",
    "甲申": "泉中水", "乙酉": "泉中水", "丙戌": "屋上土", "丁亥": "屋上土",
    "戊子": "霹雳火", "己丑": "霹雳火", "庚寅": "松柏木", "辛卯": "松柏木",
    "壬辰": "长流水", "癸巳": "长流水", "甲午": "砂中金", "乙未": "砂中金",
    "丙申": "山下火", "丁酉": "山下火", "戊戌": "平地木", "己亥": "平地木",
    "庚子": "壁上土", "辛丑": "壁上土", "壬寅": "金箔金", "癸卯": "金箔金",
    "甲辰": "覆灯火", "乙巳": "覆灯火", "丙午": "天河水", "丁未": "天河水",
    "戊申": "大驿土", "己酉": "大驿土", "庚戌": "钗钏金", "辛亥": "钗钏金",
    "壬子": "桑柘木", "癸丑": "桑柘木", "甲寅": "大溪水", "乙卯": "大溪水",
    "丙辰": "沙中土", "丁巳": "沙中土", "戊午": "天上火", "己未": "天上火",
    "庚申": "石榴木", "辛酉": "石榴木", "壬戌": "大海水", "癸亥": "大海水",
}

NAYIN_ELEMENT_BUREAU: dict[str, tuple[str, int]] = {
    "甲子": ("金", 4), "乙丑": ("金", 4), "丙寅": ("火", 6), "丁卯": ("火", 6),
    "戊辰": ("木", 3), "己巳": ("木", 3), "庚午": ("土", 5), "辛未": ("土", 5),
    "壬申": ("金", 4), "癸酉": ("金", 4), "甲戌": ("火", 6), "乙亥": ("火", 6),
    "丙子": ("水", 2), "丁丑": ("水", 2), "戊寅": ("土", 5), "己卯": ("土", 5),
    "庚辰": ("金", 4), "辛巳": ("金", 4), "壬午": ("木", 3), "癸未": ("木", 3),
    "甲申": ("水", 2), "乙酉": ("水", 2), "丙戌": ("土", 5), "丁亥": ("土", 5),
    "戊子": ("火", 6), "己丑": ("火", 6), "庚寅": ("木", 3), "辛卯": ("木", 3),
    "壬辰": ("水", 2), "癸巳": ("水", 2), "甲午": ("金", 4), "乙未": ("金", 4),
    "丙申": ("火", 6), "丁酉": ("火", 6), "戊戌": ("木", 3), "己亥": ("木", 3),
    "庚子": ("土", 5), "辛丑": ("土", 5), "壬寅": ("金", 4), "癸卯": ("金", 4),
    "甲辰": ("火", 6), "乙巳": ("火", 6), "丙午": ("水", 2), "丁未": ("水", 2),
    "戊申": ("土", 5), "己酉": ("土", 5), "庚戌": ("金", 4), "辛亥": ("金", 4),
    "壬子": ("木", 3), "癸丑": ("木", 3), "甲寅": ("水", 2), "乙卯": ("水", 2),
    "丙辰": ("土", 5), "丁巳": ("土", 5), "戊午": ("火", 6), "己未": ("火", 6),
    "庚申": ("木", 3), "辛酉": ("木", 3), "壬戌": ("水", 2), "癸亥": ("水", 2),
}

FOUR_TRANSFORM: dict[str, dict[str, str]] = {
    "甲": {"lu": "廉贞", "quan": "破军", "ke": "武曲", "ji": "太阳"},
    "乙": {"lu": "天机", "quan": "天梁", "ke": "紫微", "ji": "太阴"},
    "丙": {"lu": "天同", "quan": "天机", "ke": "文昌", "ji": "廉贞"},
    "丁": {"lu": "太阴", "quan": "天同", "ke": "天机", "ji": "巨门"},
    "戊": {"lu": "贪狼", "quan": "太阴", "ke": "右弼", "ji": "天机"},
    "己": {"lu": "武曲", "quan": "贪狼", "ke": "天梁", "ji": "文曲"},
    "庚": {"lu": "太阳", "quan": "武曲", "ke": "太阴", "ji": "天同"},
    "辛": {"lu": "巨门", "quan": "太阳", "ke": "文曲", "ji": "文昌"},
    "壬": {"lu": "天梁", "quan": "紫微", "ke": "左辅", "ji": "武曲"},
    "癸": {"lu": "破军", "quan": "巨门", "ke": "太阴", "ji": "贪狼"},
}

DAXIAN_RULES = [
    {"gender": "male", "year_yinyang": "yang", "direction": "forward", "start_age_formula": "bureau_number"},
    {"gender": "male", "year_yinyang": "yin", "direction": "backward", "start_age_formula": "bureau_number"},
    {"gender": "female", "year_yinyang": "yang", "direction": "backward", "start_age_formula": "bureau_number"},
    {"gender": "female", "year_yinyang": "yin", "direction": "forward", "start_age_formula": "bureau_number"},
]

# 安星查表（Sprint 5）— 写入 star_lookup_rules 缓存
STAR_BRANCH_LOOKUPS: dict[str, dict[str, str]] = {
    "天魁": {
        "甲": "丑", "戊": "丑", "庚": "丑",
        "乙": "子", "己": "子",
        "丙": "亥", "丁": "亥",
        "壬": "卯", "癸": "卯",
        "辛": "午",
    },
    "天钺": {
        "甲": "未", "戊": "未", "庚": "未",
        "乙": "申", "己": "申",
        "丙": "酉", "丁": "酉",
        "壬": "巳", "癸": "巳",
        "辛": "寅",
    },
    "禄存": {
        "甲": "寅", "乙": "卯", "丙": "巳", "丁": "午", "戊": "巳",
        "己": "午", "庚": "申", "辛": "酉", "壬": "亥", "癸": "子",
    },
    "天马": {
        "寅": "申", "午": "申", "戌": "申",
        "申": "寅", "子": "寅", "辰": "寅",
        "巳": "亥", "酉": "亥", "丑": "亥",
        "亥": "巳", "卯": "巳", "未": "巳",
    },
}

# 火星/铃星：年支三合组 → 起宫地支
HUOLING_GROUP_BASES: dict[str, dict[str, str]] = {
    "火星": {"寅午戌": "丑", "申子辰": "寅", "巳酉丑": "卯", "亥卯未": "酉"},
    "铃星": {"寅午戌": "卯", "申子辰": "戌", "巳酉丑": "戌", "亥卯未": "戌"},
}

# 十四主星亮度表（三合派标准）
MAIN_STAR_BRIGHTNESS: dict[str, dict[str, str]] = {
    "紫微": {"子": "平", "丑": "庙", "寅": "庙", "卯": "旺", "辰": "得", "巳": "旺", "午": "庙", "未": "庙", "申": "旺", "酉": "旺", "戌": "得", "亥": "旺"},
    "天机": {"子": "庙", "丑": "陷", "寅": "得", "卯": "旺", "辰": "利", "巳": "平", "午": "庙", "未": "陷", "申": "得", "酉": "旺", "戌": "利", "亥": "平"},
    "太阳": {"子": "陷", "丑": "不得", "寅": "旺", "卯": "庙", "辰": "旺", "巳": "旺", "午": "旺", "未": "得", "申": "得", "酉": "平", "戌": "不得", "亥": "陷"},
    "武曲": {"子": "旺", "丑": "庙", "寅": "得", "卯": "利", "辰": "庙", "巳": "平", "午": "旺", "未": "庙", "申": "得", "酉": "利", "戌": "庙", "亥": "平"},
    "天同": {"子": "旺", "丑": "不得", "寅": "利", "卯": "平", "辰": "平", "巳": "庙", "午": "陷", "未": "不得", "申": "旺", "酉": "平", "戌": "平", "亥": "庙"},
    "廉贞": {"子": "平", "丑": "利", "寅": "庙", "卯": "平", "辰": "利", "巳": "平", "午": "庙", "未": "利", "申": "庙", "酉": "平", "戌": "利", "亥": "平"},
    "天府": {"子": "庙", "丑": "庙", "寅": "庙", "卯": "得", "辰": "庙", "巳": "得", "午": "旺", "未": "庙", "申": "得", "酉": "旺", "戌": "庙", "亥": "得"},
    "太阴": {"子": "庙", "丑": "庙", "寅": "陷", "卯": "陷", "辰": "陷", "巳": "陷", "午": "陷", "未": "陷", "申": "得", "酉": "旺", "戌": "旺", "亥": "庙"},
    "贪狼": {"子": "旺", "丑": "庙", "寅": "平", "卯": "利", "辰": "庙", "巳": "平", "午": "旺", "未": "庙", "申": "平", "酉": "利", "戌": "庙", "亥": "平"},
    "巨门": {"子": "旺", "丑": "不得", "寅": "庙", "卯": "庙", "辰": "陷", "巳": "旺", "午": "旺", "未": "不得", "申": "庙", "酉": "庙", "戌": "陷", "亥": "旺"},
    "天相": {"子": "庙", "丑": "庙", "寅": "庙", "卯": "陷", "辰": "得", "巳": "得", "午": "庙", "未": "得", "申": "庙", "酉": "陷", "戌": "得", "亥": "得"},
    "天梁": {"子": "庙", "丑": "旺", "寅": "庙", "卯": "庙", "辰": "庙", "巳": "陷", "午": "庙", "未": "旺", "申": "陷", "酉": "得", "戌": "庙", "亥": "陷"},
    "七杀": {"子": "旺", "丑": "庙", "寅": "庙", "卯": "旺", "辰": "庙", "巳": "平", "午": "旺", "未": "庙", "申": "庙", "酉": "旺", "戌": "庙", "亥": "平"},
    "破军": {"子": "庙", "丑": "旺", "寅": "得", "卯": "陷", "辰": "旺", "巳": "平", "午": "庙", "未": "旺", "申": "得", "酉": "陷", "戌": "旺", "亥": "平"},
}


def calc_ziwei_branch_index(lunar_day: int, bureau: int) -> int:
    """
    安紫微星（三合派）。

    口诀：生日除局数，商数减一，余数不为零则再减一，以寅宫起顺数。
    """
    remainder = lunar_day % bureau
    quotient = lunar_day // bureau
    if remainder != 0:
        quotient += 1
    index = quotient - 1
    if remainder != 0:
        index -= 1
    return (2 + index) % 12  # 寅=2


def generate_nayin_rules() -> list[dict]:
    rows = []
    for gz, (element, bureau) in NAYIN_ELEMENT_BUREAU.items():
        rows.append({
            "heavenly_stem": gz[0],
            "earthly_branch": gz[1],
            "nayin": NAYIN_NAMES[gz],
            "element": element,
            "bureau_number": bureau,
            "school": SCHOOL,
            "version": RULES_VERSION,
        })
    return rows


def generate_ziwei_position_rules() -> list[dict]:
    rows = []
    for bureau in (2, 3, 4, 5, 6):
        for day in range(1, 31):
            idx = calc_ziwei_branch_index(day, bureau)
            rows.append({
                "bureau": bureau,
                "lunar_day": day,
                "ziwei_branch": EARTHLY_BRANCHES[idx],
                "school": SCHOOL,
                "version": RULES_VERSION,
            })
    return rows


def generate_brightness_rules() -> list[dict]:
    rows = []
    for star, branches in MAIN_STAR_BRIGHTNESS.items():
        for branch, brightness in branches.items():
            rows.append({
                "star_name": star,
                "branch": branch,
                "brightness": brightness,
                "school": SCHOOL,
                "version": RULES_VERSION,
            })
    return rows


def generate_star_placement_rules() -> list[dict]:
    """十四主星相对紫微/天府的安置规则。"""
    ziwei_group = [
        ("紫微", "self", "forward", 0),
        ("天机", "紫微", "backward", 1),
        ("太阳", "紫微", "backward", 3),
        ("武曲", "紫微", "backward", 4),
        ("天同", "紫微", "backward", 5),
        ("廉贞", "紫微", "backward", 8),
    ]
    tianfu_group = [
        ("天府", "紫微", "opposite", 0),
        ("太阴", "天府", "forward", 1),
        ("贪狼", "天府", "forward", 2),
        ("巨门", "天府", "forward", 3),
        ("天相", "天府", "forward", 4),
        ("天梁", "天府", "forward", 5),
        ("七杀", "天府", "forward", 6),
        ("破军", "天府", "forward", 10),
    ]
    rows = []
    for star, base, direction, offset in ziwei_group + tianfu_group:
        rows.append({
            "rule_type": "main_star",
            "star_name": star,
            "base_star": base,
            "direction": direction,
            "offset": offset,
            "condition": {},
            "school": SCHOOL,
            "version": RULES_VERSION,
        })
    # 辅煞杂曜规则（Sprint 5：条件写入 condition，查表写入 star_lookup_rules）
    aux_rules = [
        ("左辅", "aux_star", "", "forward", 0, {"by": "lunar_month", "base_branch": "辰"}),
        ("右弼", "aux_star", "", "backward", 0, {"by": "lunar_month", "base_branch": "戌"}),
        ("文昌", "aux_star", "", "forward", 0, {"by": "hour_branch", "base_branch": "戌"}),
        ("文曲", "aux_star", "", "backward", 0, {"by": "hour_branch", "base_branch": "辰"}),
        ("天魁", "aux_star", "", "lookup", 0, {"by": "year_stem", "lookup": "天魁"}),
        ("天钺", "aux_star", "", "lookup", 0, {"by": "year_stem", "lookup": "天钺"}),
        ("禄存", "aux_star", "", "lookup", 0, {"by": "year_stem", "lookup": "禄存"}),
        ("擎羊", "sha_star", "禄存", "forward", 1, {}),
        ("陀罗", "sha_star", "禄存", "backward", 1, {}),
        ("火星", "sha_star", "", "forward", 0, {"by": "year_branch_hour", "lookup": "火星"}),
        ("铃星", "sha_star", "", "forward", 0, {"by": "year_branch_hour", "lookup": "铃星"}),
        ("地空", "sha_star", "", "forward", 0, {"by": "hour_branch", "base_branch": "亥"}),
        ("地劫", "sha_star", "", "backward", 0, {"by": "hour_branch", "base_branch": "亥"}),
        ("天马", "za_star", "", "lookup", 0, {"by": "year_branch", "lookup": "天马"}),
    ]
    for star, rtype, base, direction, offset, condition in aux_rules:
        rows.append({
            "rule_type": rtype,
            "star_name": star,
            "base_star": base,
            "direction": direction,
            "offset": offset,
            "condition": condition,
            "school": SCHOOL,
            "version": RULES_VERSION,
        })
    return rows


def generate_star_lookup_rules() -> list[dict]:
    """星曜地支查表规则（辅煞杂曜）。"""
    rows = []
    for star_name, mapping in STAR_BRANCH_LOOKUPS.items():
        rows.append({
            "star_name": star_name,
            "lookup_by": "year_stem" if star_name != "天马" else "year_branch",
            "mapping": mapping,
            "school": SCHOOL,
            "version": RULES_VERSION,
        })
    for star_name, group_bases in HUOLING_GROUP_BASES.items():
        rows.append({
            "star_name": star_name,
            "lookup_by": "year_branch_hour",
            "group_bases": group_bases,
            "school": SCHOOL,
            "version": RULES_VERSION,
        })
    return rows


def generate_stars_metadata() -> list[dict]:
    main_stars = [
        ("紫微", "土", "阴", ["领导", "权威", "尊贵"]),
        ("天机", "木", "阴", ["智慧", "谋略", "变动"]),
        ("太阳", "火", "阳", ["光明", "贵气", "发散"]),
        ("武曲", "金", "阴", ["财富", "刚毅", "执行"]),
        ("天同", "水", "阳", ["福德", "温和", "享受"]),
        ("廉贞", "火", "阴", ["政治", "血光", "桃花"]),
        ("天府", "土", "阳", ["库藏", "稳定", "管理"]),
        ("太阴", "水", "阴", ["财富", "母性", "内敛"]),
        ("贪狼", "木", "阳", ["欲望", "桃花", "社交"]),
        ("巨门", "水", "阴", ["口才", "暗蔽", "是非"]),
        ("天相", "水", "阳", ["印信", "辅助", "协调"]),
        ("天梁", "土", "阳", ["荫庇", "清高", "医疗"]),
        ("七杀", "金", "阳", ["将星", "冲动", "变革"]),
        ("破军", "水", "阴", ["破坏", "开创", "消耗"]),
    ]
    aux_stars = [
        ("左辅", "土", "阳", "辅助"), ("右弼", "水", "阴", "辅助"),
        ("文昌", "金", "阳", "文才"), ("文曲", "水", "阴", "文才"),
        ("天魁", "火", "阳", "贵人"), ("天钺", "火", "阴", "贵人"),
        ("禄存", "土", "阴", "财禄"), ("天马", "火", "阳", "变动"),
        ("擎羊", "金", "阳", "刑伤"), ("陀罗", "金", "阴", "拖延"),
        ("火星", "火", "阳", "爆发"), ("铃星", "火", "阴", "焦虑"),
        ("地空", "火", "阴", "空亡"), ("地劫", "火", "阳", "破耗"),
    ]
    rows = []
    for name, element, yinyang, keywords in main_stars:
        rows.append({
            "name": name, "element": element, "yin_yang": yinyang,
            "category": "main", "keywords": keywords,
            "personality_tags": keywords, "career_tags": keywords[:2],
            "wealth_tags": keywords[:1], "relationship_tags": keywords[:1],
            "description": f"{name}星主{keywords[0]}",
            "ai_prompt": f"解读{name}时重点分析{keywords[0]}特质",
            "school": SCHOOL, "is_active": True,
        })
    for name, element, yinyang, keyword in aux_stars:
        cat = "sha" if name in ("擎羊", "陀罗", "火星", "铃星", "地空", "地劫") else "aux"
        rows.append({
            "name": name, "element": element, "yin_yang": yinyang,
            "category": cat, "keywords": [keyword],
            "personality_tags": [keyword], "career_tags": [], "wealth_tags": [],
            "relationship_tags": [], "description": f"{name}主{keyword}",
            "ai_prompt": f"分析{name}对命盘的影响", "school": SCHOOL, "is_active": True,
        })
    return rows


def generate_star_combination_rules() -> list[dict]:
    # (名称, 星曜, 类别, tags, match_type, required_sihua?)
    combos = [
        ("紫府同宫", ["紫微", "天府"], "main_combo", ["管理能力", "资源整合", "领导型人格"], "same_palace", None),
        ("紫府朝垣", ["紫微", "天府"], "main_combo", ["格局清贵", "事业稳定", "管理天赋"], "both_present", None),
        ("杀破狼", ["七杀", "破军", "贪狼"], "main_combo", ["开创变革", "大起大落", "行动力强"], "chart_present", None),
        ("机月同梁", ["天机", "太阴", "天同", "天梁"], "main_combo", ["智慧型", "服务导向", "稳定发展"], "chart_present", None),
        ("日月并明", ["太阳", "太阴"], "main_combo", ["光明磊落", "贵气十足", "公众形象佳"], "same_palace", None),
        ("昌曲同宫", ["文昌", "文曲"], "aux_combo", ["才华横溢", "文笔出众", "学术优势"], "same_palace", None),
        ("魁钺夹命", ["天魁", "天钺"], "aux_combo", ["贵人相助", "机遇较多", "逢凶化吉"], "flank_ming", None),
        ("禄马交驰", ["禄存", "天马"], "aux_combo", ["动中求财", "事业奔波", "财富流动"], "same_palace", None),
        ("火铃同宫", ["火星", "铃星"], "aux_combo", ["性格急躁", "突发变动", "需注意情绪"], "same_palace", None),
        ("羊陀夹命", ["擎羊", "陀罗"], "aux_combo", ["波折较多", "需防刑伤", "坚韧考验"], "flank_ming", None),
        ("紫微独坐", ["紫微"], "main_combo", ["独立领导", "自我要求高", "权威气质"], "sole_main_star", None),
        ("廉贞七杀", ["廉贞", "七杀"], "main_combo", ["权力欲望", "竞争意识", "事业冲劲"], "same_palace", None),
        ("武曲贪狼", ["武曲", "贪狼"], "main_combo", ["财富追求", "社交能力", "多元发展"], "same_palace", None),
        ("天同太阴", ["天同", "太阴"], "main_combo", ["温和内敛", "感情细腻", "享受生活"], "same_palace", None),
        ("太阳化禄", ["太阳"], "sihua_combo", ["事业机遇", "名声提升", "贵人提拔"], "sihua", "禄"),
        ("太阴化科", ["太阴"], "sihua_combo", ["名声远播", "才学显现", "温和贵人"], "sihua", "科"),
        ("武曲化权", ["武曲"], "sihua_combo", ["掌财能力", "执行力强", "事业主导"], "sihua", "权"),
        ("天同化忌", ["天同"], "sihua_combo", ["情绪困扰", "福德有损", "需调节心态"], "sihua", "忌"),
        ("廉贞化禄", ["廉贞"], "sihua_combo", ["桃花财禄", "人际活跃", "创意变现"], "sihua", "禄"),
        ("破军化权", ["破军"], "sihua_combo", ["破旧立新", "变革领导", "突破困境"], "sihua", "权"),
    ]
    rows = []
    for name, stars, category, tags, match_type, required_sihua in combos:
        rows.append({
            "combination_name": name,
            "stars": stars,
            "category": category,
            "match_type": match_type,
            "required_sihua": required_sihua,
            "personality": tags[0] if tags else "",
            "career": tags[1] if len(tags) > 1 else "",
            "wealth": tags[2] if len(tags) > 2 else "",
            "relationship": "",
            "ai_prompt": f"分析{name}组合时，重点解读：{', '.join(tags)}",
            "school": SCHOOL,
            "version": RULES_VERSION,
        })
    return rows


def generate_palace_meaning_rules() -> list[dict]:
    palaces = [
        ("命宫", "自我", "代表先天性格、人生格局与整体运势"),
        ("兄弟", "手足", "代表兄弟姐妹、同事及平辈关系"),
        ("夫妻", "配偶", "代表婚姻感情、配偶特质与恋爱模式"),
        ("子女", "后代", "代表子女缘分、创造力与Investment"),
        ("财帛", "财富", "代表赚钱能力、理财模式与物质资源"),
        ("疾厄", "健康", "代表身体健康、灾厄与内在情绪"),
        ("迁移", "外出", "代表外出运、社会形象与外界评价"),
        ("交友", "人际", "代表朋友、下属与人际网络"),
        ("官禄", "事业", "代表事业发展、工作成就与社会地位"),
        ("田宅", "不动产", "代表家庭环境、房产与内在安全感"),
        ("福德", "精神", "代表精神世界、享受能力与福报"),
        ("父母", "长辈", "代表父母缘分、上司关系与遗传背景"),
    ]
    rows = []
    for name, keyword, meaning in palaces:
        rows.append({
            "palace_name": name, "keyword": keyword, "meaning": meaning,
            "career": f"{name}对事业的影响" if name in ("命宫", "官禄", "财帛") else "",
            "wealth": f"{name}对财富的影响" if name in ("财帛", "田宅") else "",
            "relationship": f"{name}对感情的影响" if name in ("夫妻", "福德") else "",
            "health": f"{name}对健康的影响" if name == "疾厄" else "",
            "ai_prompt": f"解读{name}时，{meaning}",
            "school": SCHOOL, "version": RULES_VERSION,
        })
    return rows


def build_all_rules() -> dict:
    """构建完整规则缓存（与 DB seeds 一致）。"""
    return {
        "version": RULES_VERSION,
        "school": SCHOOL,
        "nayin_rules": generate_nayin_rules(),
        "ziwei_position_rules": generate_ziwei_position_rules(),
        "star_placement_rules": generate_star_placement_rules(),
        "star_lookup_rules": generate_star_lookup_rules(),
        "four_transform_rules": [
            {"heavenly_stem": stem, **vals, "school": SCHOOL, "version": RULES_VERSION}
            for stem, vals in FOUR_TRANSFORM.items()
        ],
        "daxian_rules": [
            {**r, "school": SCHOOL, "version": RULES_VERSION} for r in DAXIAN_RULES
        ],
        "brightness_rules": generate_brightness_rules(),
        "stars": generate_stars_metadata(),
        "star_combination_rules": generate_star_combination_rules(),
        "palace_meaning_rules": generate_palace_meaning_rules(),
    }
