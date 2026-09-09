"""P14 data ingestion schema

Revision ID: e512319aa0b4
Revises: 010c3ee27d98
Create Date: 2026-09-09 03:36:43.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision: str = 'e512319aa0b4'
down_revision: Union[str, None] = '010c3ee27d98'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Ingestion Batches
    op.create_table('ingestion_batches',
    sa.Column('batch_id', sa.String(), nullable=False),
    sa.Column('source', sa.String(), nullable=False),
    sa.Column('status', sa.String(), nullable=False),
    sa.Column('requested_at', sa.DateTime(timezone=True), nullable=False),
    sa.Column('received_at', sa.DateTime(timezone=True), nullable=False),
    sa.Column('completed_at', sa.DateTime(timezone=True), nullable=True),
    sa.Column('schema_version', sa.String(), nullable=False),
    sa.Column('adapter_version', sa.String(), nullable=False),
    sa.Column('normalizer_version', sa.String(), nullable=False),
    sa.Column('record_count', sa.Integer(), nullable=False),
    sa.Column('accepted_count', sa.Integer(), nullable=False),
    sa.Column('rejected_count', sa.Integer(), nullable=False),
    sa.Column('duplicate_count', sa.Integer(), nullable=False),
    sa.Column('correlation_id', sa.String(), nullable=False),
    sa.PrimaryKeyConstraint('batch_id')
    )

    # Ingestion Records
    op.create_table('ingestion_records',
    sa.Column('record_id', sa.String(), nullable=False),
    sa.Column('batch_id', sa.String(), nullable=False),
    sa.Column('source', sa.String(), nullable=False),
    sa.Column('source_record_id', sa.String(), nullable=False),
    sa.Column('payload_hash', sa.String(), nullable=False),
    sa.Column('received_at', sa.DateTime(timezone=True), nullable=False),
    sa.Column('status', sa.String(), nullable=False),
    sa.Column('normalized_entity_type', sa.String(), nullable=True),
    sa.Column('normalized_entity_id', sa.String(), nullable=True),
    sa.Column('payload', postgresql.JSONB(astext_type=sa.Text()), nullable=False),
    sa.Column('quality_result', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
    sa.ForeignKeyConstraint(['batch_id'], ['ingestion_batches.batch_id'], ),
    sa.PrimaryKeyConstraint('record_id')
    )
    op.create_index(op.f('ix_ingestion_records_batch_id'), 'ingestion_records', ['batch_id'], unique=False)
    op.create_index(op.f('ix_ingestion_records_normalized_entity_id'), 'ingestion_records', ['normalized_entity_id'], unique=False)
    op.create_index(op.f('ix_ingestion_records_source'), 'ingestion_records', ['source'], unique=False)
    op.create_index(op.f('ix_ingestion_records_source_record_id'), 'ingestion_records', ['source_record_id'], unique=False)
    
    # Unique constraint for idempotency
    op.create_unique_constraint('uq_ingestion_records_source_source_id', 'ingestion_records', ['source', 'source_record_id'])

    # Quarantine Records
    op.create_table('quarantine_records',
    sa.Column('quarantine_id', sa.String(), nullable=False),
    sa.Column('batch_id', sa.String(), nullable=False),
    sa.Column('source', sa.String(), nullable=False),
    sa.Column('source_record_id', sa.String(), nullable=False),
    sa.Column('raw_payload', postgresql.JSONB(astext_type=sa.Text()), nullable=False),
    sa.Column('errors', postgresql.JSONB(astext_type=sa.Text()), nullable=False),
    sa.Column('warnings', postgresql.JSONB(astext_type=sa.Text()), nullable=False),
    sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
    sa.Column('status', sa.String(), nullable=False),
    sa.PrimaryKeyConstraint('quarantine_id')
    )
    op.create_index(op.f('ix_quarantine_records_batch_id'), 'quarantine_records', ['batch_id'], unique=False)


def downgrade() -> None:
    op.drop_table('quarantine_records')
    op.drop_table('ingestion_records')
    op.drop_table('ingestion_batches')