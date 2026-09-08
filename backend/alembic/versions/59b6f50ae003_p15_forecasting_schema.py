"""P15 forecasting schema

Revision ID: 59b6f50ae003
Revises: e512319aa0b4
Create Date: 2026-09-09 03:50:33.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision: str = '59b6f50ae003'
down_revision: Union[str, None] = 'e512319aa0b4'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Forecast Results
    op.create_table('forecast_results',
    sa.Column('forecast_id', sa.String(), nullable=False),
    sa.Column('request_id', sa.String(), nullable=False),
    sa.Column('target_type', sa.String(), nullable=False),
    sa.Column('scope', sa.String(), nullable=False),
    sa.Column('scope_id', sa.String(), nullable=True),
    sa.Column('model_name', sa.String(), nullable=False),
    sa.Column('model_version', sa.String(), nullable=False),
    sa.Column('quality_score', sa.Float(), nullable=False),
    sa.Column('quality_level', sa.String(), nullable=False),
    sa.Column('generated_at', sa.DateTime(timezone=True), nullable=False),
    sa.Column('predictions', postgresql.JSONB(astext_type=sa.Text()), nullable=False),
    sa.Column('provenance', postgresql.JSONB(astext_type=sa.Text()), nullable=False),
    sa.PrimaryKeyConstraint('forecast_id')
    )


def downgrade() -> None:
    op.drop_table('forecast_results')