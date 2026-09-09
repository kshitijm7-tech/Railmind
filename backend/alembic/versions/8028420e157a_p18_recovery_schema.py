"""P18 recovery schema

Revision ID: 8028420e157a
Revises: 35b5383a7ef0
Create Date: 2026-09-09 04:28:33.153723

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision: str = '8028420e157a'
down_revision: Union[str, None] = '35b5383a7ef0'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table('disruptions',
    sa.Column('disruption_id', sa.String(), nullable=False),
    sa.Column('type', sa.String(), nullable=False),
    sa.Column('severity', sa.String(), nullable=False),
    sa.Column('status', sa.String(), nullable=False),
    sa.Column('affected_resource', sa.String(), nullable=False),
    sa.Column('affected_resource_type', sa.String(), nullable=False),
    sa.Column('start_time', sa.DateTime(timezone=True), nullable=False),
    sa.Column('expected_end_time', sa.DateTime(timezone=True), nullable=False),
    sa.Column('actual_end_time', sa.DateTime(timezone=True), nullable=True),
    sa.Column('description', sa.Text(), nullable=False),
    sa.Column('state_mode', sa.String(), nullable=False),
    sa.Column('scenario_id', sa.String(), nullable=True),
    sa.Column('reported_at', sa.DateTime(timezone=True), nullable=False),
    sa.Column('source', sa.String(), nullable=False),
    sa.Column('provenance', postgresql.JSONB(astext_type=sa.Text()), nullable=False),
    sa.PrimaryKeyConstraint('disruption_id')
    )
    
    op.create_table('recovery_assessments',
    sa.Column('recovery_id', sa.String(), nullable=False),
    sa.Column('disruption_id', sa.String(), nullable=False),
    sa.Column('quality', sa.String(), nullable=False),
    sa.Column('engine_version', sa.String(), nullable=False),
    sa.Column('generated_at', sa.DateTime(timezone=True), nullable=False),
    sa.Column('impact_assessment', postgresql.JSONB(astext_type=sa.Text()), nullable=False),
    sa.Column('recovery_options', postgresql.JSONB(astext_type=sa.Text()), nullable=False),
    sa.Column('warnings', postgresql.JSONB(astext_type=sa.Text()), nullable=False),
    sa.Column('provenance', postgresql.JSONB(astext_type=sa.Text()), nullable=False),
    sa.ForeignKeyConstraint(['disruption_id'], ['disruptions.disruption_id'], ),
    sa.PrimaryKeyConstraint('recovery_id')
    )


def downgrade() -> None:
    op.drop_table('recovery_assessments')
    op.drop_table('disruptions')