"""Sprint 8 — 商业化：认证、持久化、会员、配额测试。"""

from __future__ import annotations

from uuid import UUID

import pytest

from app.db.memory_store import MemoryStore
from app.db.repository import Repository
from app.models.birth import BirthInput
from app.models.chart_record import ChartSaveRequest, PersistAnalysisRequest
from app.models.commerce import CreateOrderRequest
from app.models.user import AuthUser, ProfileUpdateRequest
from app.services.analysis_persistence_service import AnalysisPersistenceService
from app.services.chart_service import ChartPersistenceService
from app.services.commerce_service import CommerceService
from app.services.profile_service import ProfileService
from app.ziwei.rules.cache import clear_rules_cache


DEV_USER = AuthUser(id=UUID("11111111-1111-1111-1111-111111111111"), email="test@ziwei.ai")


@pytest.fixture(autouse=True)
def fresh_state():
    clear_rules_cache()
    MemoryStore.reset()
    yield
    MemoryStore.reset()
    clear_rules_cache()


def _birth_input() -> BirthInput:
    return BirthInput(
        name="基准男盘",
        gender="male",
        date="1990-05-15",
        time="14:30",
        location={"country": "China", "city": "深圳", "longitude": 114.0579},
    )


class TestProfileService:
    def test_auto_create_profile(self):
        profile = ProfileService.get_me(DEV_USER)
        assert profile.membership == "free"
        assert profile.ai_quota == 3
        assert profile.display_name == "test@ziwei.ai"

    def test_update_profile(self):
        ProfileService.get_me(DEV_USER)
        updated = ProfileService.update_me(
            DEV_USER,
            ProfileUpdateRequest(display_name="测试用户"),
        )
        assert updated.display_name == "测试用户"


class TestChartPersistence:
    def test_save_and_list(self):
        saved = ChartPersistenceService.save(
            DEV_USER,
            ChartSaveRequest(birth=_birth_input(), reference_date="2026-07-22"),
        )
        assert saved.chart_data.meta.mingGong == "戌"
        summaries = ChartPersistenceService.list_charts(DEV_USER)
        assert len(summaries) == 1
        assert summaries[0].id == saved.id

    def test_get_and_delete(self):
        saved = ChartPersistenceService.save(
            DEV_USER,
            ChartSaveRequest(birth=_birth_input()),
        )
        fetched = ChartPersistenceService.get_chart(DEV_USER, saved.id)
        assert fetched.name == "基准男盘"
        ChartPersistenceService.delete_chart(DEV_USER, saved.id)
        with pytest.raises(ValueError):
            ChartPersistenceService.get_chart(DEV_USER, saved.id)


class TestAnalysisPersistence:
    @pytest.mark.asyncio
    async def test_persist_analysis_deducts_quota(self):
        saved = ChartPersistenceService.save(
            DEV_USER,
            ChartSaveRequest(birth=_birth_input(), reference_date="2026-07-22"),
        )
        result, record = await AnalysisPersistenceService.generate_and_persist(
            DEV_USER,
            PersistAnalysisRequest(chart_id=saved.id, mode="rules"),
        )
        assert result.mode == "rules"
        assert "命盘概览" in record.result_text
        profile = ProfileService.get_me(DEV_USER)
        assert profile.ai_quota == 2

    @pytest.mark.asyncio
    async def test_quota_exceeded(self):
        repo = Repository()
        repo.ensure_profile(DEV_USER.id)
        repo._store.profiles[DEV_USER.id].ai_quota = 0
        saved = ChartPersistenceService.save(
            DEV_USER,
            ChartSaveRequest(birth=_birth_input()),
            repo=repo,
        )
        with pytest.raises(ValueError, match="次数不足"):
            await AnalysisPersistenceService.generate_and_persist(
                DEV_USER,
                PersistAnalysisRequest(chart_id=saved.id, mode="rules"),
                repo=repo,
            )


class TestCommerce:
    def test_list_plans(self):
        plans = CommerceService.list_plans()
        assert len(plans) == 2
        assert plans[0].price_cents > 0

    def test_create_and_confirm_order(self):
        ProfileService.get_me(DEV_USER)
        order = CommerceService.create_order(
            DEV_USER,
            CreateOrderRequest(plan_id="basic"),
        )
        assert order.status == "pending"
        result = CommerceService.confirm_order(DEV_USER, order.id)
        assert result.order.status == "paid"
        assert result.profile_membership == "basic"
        assert result.ai_quota == 33  # 3 free + 30 basic
