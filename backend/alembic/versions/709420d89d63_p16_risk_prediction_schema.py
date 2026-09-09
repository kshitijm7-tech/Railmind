"""P16 risk prediction schema

Revision ID: 709420d89d63
Revises: 59b6f50ae003
Create Date: 2026-09-09 04:03:25.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision: str = '709420d89d63'
down_revision: Union[str, None] = '59b6f50ae003'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Risk Predictions
    op.create_table('risk_predictions',
    sa.Column('risk_id', sa.String(), nullable=False),
    sa.Column('request_id', sa.String(), nullable=False),
    sa.Column('target_type', sa.String(), nullable=False),
    sa.Column('target_id', sa.String(), nullable=False),
    sa.Column('risk_level', sa.String(), nullable=False),
    sa.Column('risk_score', sa.Float(), nullable=False),
    sa.Column('model_name', sa.String(), nullable=False),
    sa.Column('model_version', sa.String(), nullable=False),
    sa.Column('generated_at', sa.DateTime(timezone=True), nullable=False),
    sa.Column('factors', postgresql.JSONB(astext_type=sa.Text()), nullable=False),
    sa.Column('quality', postgresql.JSONB(astext_type=sa.Text()), nullable=False),
    sa.Column('provenance', postgresql.JSONB(astext_type=sa.Text()), nullable=False),
    sa.PrimaryKeyConstraint('risk_id')
    )


def downgrade() -> None:
    op.drop_table('risk_predictions')