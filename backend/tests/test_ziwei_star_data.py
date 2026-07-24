"""紫微星曜知识库 V1 测试 — 数据层 + API + AI 规则分析。"""

from __future__ import annotations

from fastapi.testclient import TestClient

from app.main import app
from app.ziwei_ai.analysis_engine import analyze_chart
from app.ziwei_ai.prompts import build_analyze_user_prompt
from app.ziwei_data import (
    FOUR_TRANSFORMATIONS,
    MAIN_STAR_DATABASE,
    build_star_analysis,
    get_star_public,
    knowledge_coverage,
)

client = TestClient(app)


class TestStarDatabase:
    def test_fourteen_main_stars_present(self):
        expected = {
            "紫微", "天机", "太阳", "武曲", "天同", "廉贞",
            "天府", "太阴", "贪狼", "巨门", "天相", "天梁", "七杀", "破军",
        }
        assert expected <= set(MAIN_STAR_DATABASE)

    def test_ziwei_fields_complete(self):
        z = MAIN_STAR_DATABASE["紫微"]
        assert z["type"] == "主星"
        assert z["traditional"]
        assert z["modern"]
        assert z["keywords"]
        assert z["strengths"]
        assert z["challenges"]
        assert "一定当官" not in z["traditional"]
        assert "一定当官" not in z["modern"]

    def test_evil_stars_no_scare_language(self):
        from app.ziwei_data.stars.evil_stars import EVIL_STAR_DATABASE

        blob = " ".join(
            str(v.get("traditional", "")) + str(v.get("modern", ""))
            for v in EVIL_STAR_DATABASE.values()
        )
        for banned in ("灾难", "必死", "注定死亡", "一定破财"):
            assert banned not in blob

    def test_four_transformations_ten_stems(self):
        stems = set("甲乙丙丁戊己庚辛壬癸")
        assert set(FOUR_TRANSFORMATIONS) == stems
        assert FOUR_TRANSFORMATIONS["壬"]["化禄"] == "天梁"
        assert FOUR_TRANSFORMATIONS["壬"]["化权"] == "紫微"
        assert FOUR_TRANSFORMATIONS["壬"]["化科"] == "左辅"
        assert FOUR_TRANSFORMATIONS["壬"]["化忌"] == "武曲"

    def test_build_star_analysis_ming_zifu(self):
        rows = build_star_analysis(["紫微", "天府"])
        assert [r["star"] for r in rows] == ["紫微", "天府"]
        assert "管理" in rows[0]["meaning"] or "组织" in rows[0]["meaning"]
        assert "资源" in rows[1]["meaning"] or "稳定" in rows[1]["meaning"]

    def test_coverage_snapshot(self):
        cov = knowledge_coverage()
        assert cov["main_stars"] == 14
        assert cov["auspicious_stars"] == 6
        assert cov["evil_stars"] == 6
        assert cov["minor_stars"] == 11
        assert cov["transformations_stems"] == 10


class TestStarInfoApi:
    def test_get_ziwei(self):
        res = client.get("/api/star/紫微")
        assert res.status_code == 200
        data = res.json()
        assert data["name"] == "紫微"
        assert data["type"] == "主星"
        assert data["traditional"]
        assert data["modern"]
        assert isinstance(data["keywords"], list)
        assert len(data["keywords"]) >= 1

    def test_get_tianfu(self):
        res = client.get("/api/star/天府")
        assert res.status_code == 200
        assert res.json()["name"] == "天府"

    def test_unknown_star_404(self):
        res = client.get("/api/star/不存在的星")
        assert res.status_code == 404

    def test_public_helper_matches_api(self):
        info = get_star_public("紫微")
        assert info is not None
        assert info["name"] == "紫微"


class TestAiStarAnalysisWiring:
    def test_analyze_chart_star_analysis_for_ming_zifu(self):
        chart = {
            "命宫": {"stars": ["紫微", "天府"]},
            "官禄宫": {"stars": ["武曲"]},
        }
        analysis = analyze_chart(chart, ["命宫"])
        stars = [x["star"] for x in analysis.star_analysis]
        assert "紫微" in stars
        assert "天府" in stars
        assert any("紫微" in s for s in analysis.knowledge_snippets)
        assert "知识库提示" in analysis.traditional_analysis or analysis.star_analysis

    def test_prompt_includes_star_knowledge(self):
        star_analysis = build_star_analysis(["紫微", "天府"])
        prompt = build_analyze_user_prompt(
            question="我的命宫有什么特点？",
            category="personality",
            related_palaces=["命宫"],
            traditional_analysis="测试传统",
            modern_interpretation="测试现代",
            strengths=["规划"],
            knowledge_text="摘录",
            chart_digest="命宫：紫微、天府",
            star_analysis=star_analysis,
        )
        assert "紫微" in prompt
        assert "天府" in prompt
        assert "星曜知识库" in prompt
        assert "我的命宫有什么特点？" in prompt
