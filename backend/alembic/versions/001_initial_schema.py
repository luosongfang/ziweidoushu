"""initial schema — Phase 2.5 Supabase PostgreSQL

Revision ID: 001_initial
Revises:
Create Date: 2026-07-23

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "001_initial"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "users",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("email", sa.String(length=255), nullable=True),
        sa.Column("username", sa.String(length=64), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_users_email", "users", ["email"], unique=True)
    op.create_index("ix_users_username", "users", ["username"], unique=False)

    op.create_table(
        "birth_profiles",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("user_id", sa.String(length=36), nullable=True),
        sa.Column("solar_date", sa.String(length=10), nullable=False),
        sa.Column("lunar_date", sa.String(length=32), nullable=True),
        sa.Column("birth_time", sa.String(length=5), nullable=False),
        sa.Column("location", sa.String(length=128), nullable=True),
        sa.Column("gender", sa.String(length=8), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_birth_profiles_user_id", "birth_profiles", ["user_id"], unique=False)

    op.create_table(
        "ziwei_charts",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("user_id", sa.String(length=36), nullable=True),
        sa.Column("birth_profile_id", sa.String(length=36), nullable=True),
        sa.Column("ming_gong", sa.String(length=8), nullable=False),
        sa.Column("shen_gong", sa.String(length=8), nullable=False),
        sa.Column("five_element", sa.String(length=16), nullable=False),
        sa.Column("chart_json", sa.JSON(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["birth_profile_id"], ["birth_profiles.id"]),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_ziwei_charts_user_id", "ziwei_charts", ["user_id"], unique=False)

    op.create_table(
        "chart_palaces",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("chart_id", sa.String(length=36), nullable=False),
        sa.Column("palace_name", sa.String(length=16), nullable=False),
        sa.Column("position", sa.String(length=8), nullable=False),
        sa.Column("stars", sa.JSON(), nullable=False),
        sa.Column("transformations", sa.JSON(), nullable=False),
        sa.ForeignKeyConstraint(["chart_id"], ["ziwei_charts.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_chart_palaces_chart_id", "chart_palaces", ["chart_id"], unique=False)

    op.create_table(
        "star_rules",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("star_name", sa.String(length=16), nullable=False),
        sa.Column("category", sa.String(length=16), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("rule_json", sa.JSON(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_star_rules_star_name", "star_rules", ["star_name"], unique=False)

    op.create_table(
        "four_hua_rules",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("year_gan", sa.String(length=2), nullable=False),
        sa.Column("hua_lu", sa.String(length=8), nullable=False),
        sa.Column("hua_quan", sa.String(length=8), nullable=False),
        sa.Column("hua_ke", sa.String(length=8), nullable=False),
        sa.Column("hua_ji", sa.String(length=8), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_four_hua_rules_year_gan", "four_hua_rules", ["year_gan"], unique=True)

    op.create_table(
        "ai_reports",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("chart_id", sa.String(length=36), nullable=False),
        sa.Column("report_type", sa.String(length=32), nullable=False),
        sa.Column("content", sa.Text(), nullable=False),
        sa.Column("model", sa.String(length=64), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["chart_id"], ["ziwei_charts.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_ai_reports_chart_id", "ai_reports", ["chart_id"], unique=False)

    op.create_table(
        "memberships",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("user_id", sa.String(length=36), nullable=False),
        sa.Column("level", sa.String(length=16), nullable=False),
        sa.Column("expire_time", sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_memberships_user_id", "memberships", ["user_id"], unique=False)

    op.create_table(
        "orders",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("user_id", sa.String(length=36), nullable=False),
        sa.Column("amount", sa.Numeric(precision=10, scale=2), nullable=False),
        sa.Column("status", sa.String(length=16), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_orders_user_id", "orders", ["user_id"], unique=False)


def downgrade() -> None:
    op.drop_index("ix_orders_user_id", table_name="orders")
    op.drop_table("orders")
    op.drop_index("ix_memberships_user_id", table_name="memberships")
    op.drop_table("memberships")
    op.drop_index("ix_ai_reports_chart_id", table_name="ai_reports")
    op.drop_table("ai_reports")
    op.drop_index("ix_four_hua_rules_year_gan", table_name="four_hua_rules")
    op.drop_table("four_hua_rules")
    op.drop_index("ix_star_rules_star_name", table_name="star_rules")
    op.drop_table("star_rules")
    op.drop_index("ix_chart_palaces_chart_id", table_name="chart_palaces")
    op.drop_table("chart_palaces")
    op.drop_index("ix_ziwei_charts_user_id", table_name="ziwei_charts")
    op.drop_table("ziwei_charts")
    op.drop_index("ix_birth_profiles_user_id", table_name="birth_profiles")
    op.drop_table("birth_profiles")
    op.drop_index("ix_users_username", table_name="users")
    op.drop_index("ix_users_email", table_name="users")
    op.drop_table("users")
