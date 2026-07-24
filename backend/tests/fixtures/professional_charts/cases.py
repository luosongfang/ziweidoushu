"""Professional chart fixtures — 至少 20 个出生案例输入（期望由引擎计算，禁止手填假星）。"""

from __future__ import annotations

# (id, name, gender, solar_date, time, location)
PROFESSIONAL_CASES: list[dict] = [
    {"id": "PC-01", "name": "案例01", "gender": "male", "solar_date": "1982-02-22", "time": "14:00", "location": None},
    {"id": "PC-02", "name": "案例02", "gender": "female", "solar_date": "1990-05-15", "time": "14:30", "location": "深圳"},
    {"id": "PC-03", "name": "案例03", "gender": "male", "solar_date": "1988-11-08", "time": "09:20", "location": None},
    {"id": "PC-04", "name": "案例04", "gender": "female", "solar_date": "1975-03-12", "time": "23:40", "location": "北京"},
    {"id": "PC-05", "name": "案例05", "gender": "male", "solar_date": "2000-01-01", "time": "00:30", "location": None},
    {"id": "PC-06", "name": "案例06", "gender": "female", "solar_date": "1995-07-20", "time": "16:00", "location": "上海"},
    {"id": "PC-07", "name": "案例07", "gender": "male", "solar_date": "1968-09-09", "time": "06:15", "location": None},
    {"id": "PC-08", "name": "案例08", "gender": "female", "solar_date": "1985-12-25", "time": "12:00", "location": "广州"},
    {"id": "PC-09", "name": "案例09", "gender": "male", "solar_date": "1992-04-04", "time": "03:00", "location": None},
    {"id": "PC-10", "name": "案例10", "gender": "female", "solar_date": "1979-08-18", "time": "18:45", "location": "杭州"},
    {"id": "PC-11", "name": "案例11", "gender": "male", "solar_date": "2001-06-06", "time": "11:11", "location": None},
    {"id": "PC-12", "name": "案例12", "gender": "female", "solar_date": "1983-10-10", "time": "20:20", "location": "成都"},
    {"id": "PC-13", "name": "案例13", "gender": "male", "solar_date": "1998-02-14", "time": "08:00", "location": None},
    {"id": "PC-14", "name": "案例14", "gender": "female", "solar_date": "1972-05-05", "time": "15:30", "location": None},
    {"id": "PC-15", "name": "案例15", "gender": "male", "solar_date": "1986-01-28", "time": "04:00", "location": "北京"},
    {"id": "PC-16", "name": "案例16", "gender": "female", "solar_date": "1993-09-30", "time": "22:10", "location": None},
    {"id": "PC-17", "name": "案例17", "gender": "male", "solar_date": "1965-07-01", "time": "13:00", "location": None},
    {"id": "PC-18", "name": "案例18", "gender": "female", "solar_date": "2005-11-11", "time": "07:30", "location": "上海"},
    {"id": "PC-19", "name": "案例19", "gender": "male", "solar_date": "1991-03-21", "time": "17:00", "location": None},
    {"id": "PC-20", "name": "案例20", "gender": "female", "solar_date": "1980-06-15", "time": "10:45", "location": "深圳"},
]
