"""P17 decision intelligence schema

Revision ID: 35b5383a7ef0
Revises: 709420d89d63
Create Date: 2026-09-09 04:15:40.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision: str = '35b5383a7ef0'
down_revision: Union[str, None] = '709420d89d63'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Decision Intelligence Results
    op.create_table('decision_intelligence_results',
    sa.Column('decision_id', sa.String(), nullable=False),
    sa.Column('request_id', sa.String(), nullable=False),
    sa.Column('recommended_plan_id', sa.String(), nullable=True),
    sa.Column('quality_level', sa.String(), nullable=False),
    sa.Column('engine_name', sa.String(), nullable=False),
    sa.Column('engine_version', sa.String(), nullable=False),
    sa.Column('generated_at', sa.DateTime(timezone=True), nullable=False),
    sa.Column('candidates', postgresql.JSONB(astext_type=sa.Text()), nullable=False),
    sa.Column('evidence', postgresql.JSONB(astext_type=sa.Text()), nullable=False),
    sa.Column('provenance', postgresql.JSONB(astext_type=sa.Text()), nullable=False),
    sa.PrimaryKeyConstraint('decision_id')
    )


def downgrade() -> None:
    op.drop_table('decision_intelligence_results')