"""数据访问层（Sprint 8）。"""

from __future__ import annotations

from datetime import datetime, timezone
from uuid import UUID, uuid4

from app.db.memory_store import MemoryStore, StoredAnalysis, StoredChart, StoredOrder, StoredProfile, get_memory_store
from app.models.chart import ChartOutput
from app.models.commerce import MembershipPlan, PlanId


MEMBERSHIP_PLANS: dict[PlanId, MembershipPlan] = {
    "basic": MembershipPlan(
        id="basic",
        name="基础会员",
        price_cents=2900,
        ai_quota=30,
        duration_days=30,
        features=["每月 30 次 AI 解读", "命盘云端保存", "大限流年分析"],
    ),
    "premium": MembershipPlan(
        id="premium",
        name="高级会员",
        price_cents=9900,
        ai_quota=100,
        duration_days=30,
        features=["每月 100 次 AI 解读", "命盘云端保存", "全类型 AI 解读", "优先 LLM 通道"],
    ),
}

PLAN_MEMBERSHIP: dict[PlanId, str] = {"basic": "basic", "premium": "premium"}


class Repository:
    """统一仓储 — Sprint 8 使用内存实现。"""

    def __init__(self, store: MemoryStore | None = None) -> None:
        self._store = store or get_memory_store()

    def ensure_profile(self, user_id: UUID, email: str | None = None) -> StoredProfile:
        profile = self._store.profiles.get(user_id)
        if profile:
            return profile
        profile = StoredProfile(
            id=user_id,
            display_name=email or "新用户",
            membership="free",
            ai_quota=3,
        )
        self._store.profiles[user_id] = profile
        return profile

    def get_profile(self, user_id: UUID) -> StoredProfile | None:
        return self._store.profiles.get(user_id)

    def update_profile(
        self,
        user_id: UUID,
        display_name: str | None = None,
        avatar_url: str | None = None,
    ) -> StoredProfile:
        profile = self.ensure_profile(user_id)
        if display_name is not None:
            profile.display_name = display_name
        if avatar_url is not None:
            profile.avatar_url = avatar_url
        profile.updated_at = datetime.now(timezone.utc)
        return profile

    def save_chart(
        self,
        user_id: UUID,
        chart: ChartOutput,
        birth_datetime: datetime,
        calendar_type: str,
        timezone: str,
    ) -> StoredChart:
        record = StoredChart(
            id=uuid4(),
            user_id=user_id,
            name=chart.meta.name,
            birth_datetime=birth_datetime,
            gender=chart.meta.gender,
            calendar_type=calendar_type,
            timezone=timezone,
            chart_data=chart.model_dump(mode="json"),
        )
        self._store.charts[record.id] = record
        return record

    def list_charts(self, user_id: UUID) -> list[StoredChart]:
        items = [c for c in self._store.charts.values() if c.user_id == user_id]
        return sorted(items, key=lambda c: c.created_at, reverse=True)

    def get_chart(self, chart_id: UUID, user_id: UUID) -> StoredChart | None:
        chart = self._store.charts.get(chart_id)
        if chart and chart.user_id == user_id:
            return chart
        return None

    def delete_chart(self, chart_id: UUID, user_id: UUID) -> bool:
        chart = self.get_chart(chart_id, user_id)
        if not chart:
            return False
        del self._store.charts[chart_id]
        return True

    def save_analysis(
        self,
        user_id: UUID,
        chart_id: UUID,
        analysis_type: str,
        palace_name: str | None,
        prompt_version: str,
        input_context: dict,
        result_text: str,
        tokens_used: int,
    ) -> StoredAnalysis:
        record = StoredAnalysis(
            id=uuid4(),
            user_id=user_id,
            chart_id=chart_id,
            analysis_type=analysis_type,
            palace_name=palace_name,
            prompt_version=prompt_version,
            input_context=input_context,
            result_text=result_text,
            tokens_used=tokens_used,
        )
        self._store.analyses[record.id] = record
        return record

    def list_analyses(self, user_id: UUID) -> list[StoredAnalysis]:
        items = [a for a in self._store.analyses.values() if a.user_id == user_id]
        return sorted(items, key=lambda a: a.created_at, reverse=True)

    def get_analysis(self, analysis_id: UUID, user_id: UUID) -> StoredAnalysis | None:
        record = self._store.analyses.get(analysis_id)
        if record and record.user_id == user_id:
            return record
        return None

    def deduct_ai_quota(self, user_id: UUID, amount: int = 1) -> StoredProfile:
        profile = self.ensure_profile(user_id)
        if profile.ai_quota < amount:
            raise ValueError("AI 解读次数不足")
        profile.ai_quota -= amount
        profile.updated_at = datetime.now(timezone.utc)
        return profile

    def create_order(
        self,
        user_id: UUID,
        plan_id: PlanId,
        payment_provider: str,
    ) -> StoredOrder:
        plan = MEMBERSHIP_PLANS[plan_id]
        order = StoredOrder(
            id=uuid4(),
            user_id=user_id,
            plan_id=plan_id,
            amount_cents=plan.price_cents,
            currency=plan.currency,
            status="pending",
            payment_provider=payment_provider,
            payment_ref=None,
        )
        self._store.orders[order.id] = order
        return order

    def get_order(self, order_id: UUID, user_id: UUID) -> StoredOrder | None:
        order = self._store.orders.get(order_id)
        if order and order.user_id == user_id:
            return order
        return None

    def confirm_order(self, order_id: UUID, user_id: UUID) -> tuple[StoredOrder, StoredProfile]:
        order = self.get_order(order_id, user_id)
        if not order:
            raise ValueError("订单不存在")
        if order.status == "paid":
            raise ValueError("订单已支付")
        if order.status != "pending":
            raise ValueError("订单状态不可支付")

        plan = MEMBERSHIP_PLANS[order.plan_id]  # type: ignore[index]
        profile = self.ensure_profile(user_id)
        order.status = "paid"
        order.paid_at = datetime.now(timezone.utc)
        order.payment_ref = f"stub-{order.id.hex[:8]}"
        profile.membership = PLAN_MEMBERSHIP[order.plan_id]  # type: ignore[index]
        profile.ai_quota += plan.ai_quota
        profile.updated_at = datetime.now(timezone.utc)
        return order, profile

    @staticmethod
    def list_plans() -> list[MembershipPlan]:
        return list(MEMBERSHIP_PLANS.values())


def get_repository() -> Repository:
    return Repository()
