"""Initial schema and postgis

Revision ID: 010c3ee27d98
Revises: 
Create Date: 2026-09-09 03:18:59.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql
import geoalchemy2


# revision identifiers, used by Alembic.
revision: str = '010c3ee27d98'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Add PostGIS
    op.execute('CREATE EXTENSION IF NOT EXISTS postgis;')

    # Corridors
    op.create_table('corridors',
    sa.Column('corridor_id', sa.String(), nullable=False),
    sa.Column('name', sa.String(), nullable=False),
    sa.Column('description', sa.String(), nullable=True),
    sa.Column('length_km', sa.Float(), nullable=False),
    sa.Column('traffic_type', sa.String(), nullable=False),
    sa.Column('geometry', geoalchemy2.types.Geometry(geometry_type='LINESTRING', srid=4326, from_text='ST_GeomFromEWKT', name='geometry'), nullable=True),
    sa.PrimaryKeyConstraint('corridor_id')
    )
    
    # Track Sections
    op.create_table('track_sections',
    sa.Column('section_id', sa.String(), nullable=False),
    sa.Column('corridor_id', sa.String(), nullable=False),
    sa.Column('name', sa.String(), nullable=False),
    sa.Column('type', sa.String(), nullable=False),
    sa.Column('length_m', sa.Integer(), nullable=False),
    sa.Column('max_speed_kmh', sa.Integer(), nullable=False),
    sa.Column('status', sa.String(), nullable=False),
    sa.Column('geometry', geoalchemy2.types.Geometry(geometry_type='LINESTRING', srid=4326, from_text='ST_GeomFromEWKT', name='geometry'), nullable=True),
    sa.ForeignKeyConstraint(['corridor_id'], ['corridors.corridor_id'], ),
    sa.PrimaryKeyConstraint('section_id')
    )
    
    # Assets
    op.create_table('assets',
    sa.Column('asset_id', sa.String(), nullable=False),
    sa.Column('section_id', sa.String(), nullable=False),
    sa.Column('type', sa.String(), nullable=False),
    sa.Column('condition', sa.String(), nullable=False),
    sa.Column('last_maintained', sa.DateTime(timezone=True), nullable=True),
    sa.Column('location', geoalchemy2.types.Geometry(geometry_type='POINT', srid=4326, from_text='ST_GeomFromEWKT', name='geometry'), nullable=True),
    sa.ForeignKeyConstraint(['section_id'], ['track_sections.section_id'], ),
    sa.PrimaryKeyConstraint('asset_id')
    )
    
    # Maintenance Tasks
    op.create_table('maintenance_tasks',
    sa.Column('task_id', sa.String(), nullable=False),
    sa.Column('asset_id', sa.String(), nullable=False),
    sa.Column('section_id', sa.String(), nullable=False),
    sa.Column('type', sa.String(), nullable=False),
    sa.Column('status', sa.String(), nullable=False),
    sa.Column('criticality', sa.String(), nullable=False),
    sa.Column('department', sa.String(), nullable=False),
    sa.Column('description', sa.Text(), nullable=False),
    sa.Column('duration_expected', sa.Integer(), nullable=False),
    sa.Column('duration_minimum', sa.Integer(), nullable=False),
    sa.Column('duration_maximum', sa.Integer(), nullable=False),
    sa.Column('requires_power_block', sa.Boolean(), nullable=False),
    sa.Column('requires_traffic_block', sa.Boolean(), nullable=False),
    sa.Column('dependencies', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
    sa.Column('required_resources', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
    sa.Column('associated_defects', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
    sa.ForeignKeyConstraint(['asset_id'], ['assets.asset_id'], ),
    sa.ForeignKeyConstraint(['section_id'], ['track_sections.section_id'], ),
    sa.PrimaryKeyConstraint('task_id')
    )

    # Trains
    op.create_table('trains',
    sa.Column('train_id', sa.String(), nullable=False),
    sa.Column('name', sa.String(), nullable=False),
    sa.Column('train_number', sa.String(), nullable=False),
    sa.Column('type', sa.String(), nullable=False),
    sa.Column('origin_station_id', sa.String(), nullable=False),
    sa.Column('destination_station_id', sa.String(), nullable=False),
    sa.Column('max_speed_kmh', sa.Integer(), nullable=False),
    sa.Column('length_m', sa.Integer(), nullable=False),
    sa.Column('weight_t', sa.Integer(), nullable=False),
    sa.Column('priority', sa.Integer(), nullable=False),
    sa.Column('sections', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
    sa.PrimaryKeyConstraint('train_id')
    )

    # Train Paths
    op.create_table('train_paths',
    sa.Column('train_id', sa.String(), nullable=False),
    sa.Column('segments', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
    sa.Column('constraints', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
    sa.Column('is_valid', sa.Boolean(), nullable=False),
    sa.ForeignKeyConstraint(['train_id'], ['trains.train_id'], ),
    sa.PrimaryKeyConstraint('train_id')
    )

    # Plans
    op.create_table('plans',
    sa.Column('plan_id', sa.String(), nullable=False),
    sa.Column('name', sa.String(), nullable=False),
    sa.Column('start_time', sa.DateTime(timezone=True), nullable=False),
    sa.Column('end_time', sa.DateTime(timezone=True), nullable=False),
    sa.Column('status', sa.String(), nullable=False),
    sa.Column('strategy', sa.String(), nullable=False),
    sa.Column('metrics', postgresql.JSONB(astext_type=sa.Text()), nullable=False),
    sa.Column('version', postgresql.JSONB(astext_type=sa.Text()), nullable=False),
    sa.Column('provenance', postgresql.JSONB(astext_type=sa.Text()), nullable=False),
    sa.PrimaryKeyConstraint('plan_id')
    )

    # Blocks
    op.create_table('blocks',
    sa.Column('block_id', sa.String(), nullable=False),
    sa.Column('plan_id', sa.String(), nullable=False),
    sa.Column('section_id', sa.String(), nullable=False),
    sa.Column('start_time', sa.DateTime(timezone=True), nullable=False),
    sa.Column('end_time', sa.DateTime(timezone=True), nullable=False),
    sa.Column('status', sa.String(), nullable=False),
    sa.Column('required_power_off', sa.Boolean(), nullable=False),
    sa.Column('is_integrated', sa.Boolean(), nullable=False),
    sa.Column('tasks', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
    sa.ForeignKeyConstraint(['plan_id'], ['plans.plan_id'], ),
    sa.PrimaryKeyConstraint('block_id')
    )

    # Simulation Runs
    op.create_table('simulation_runs',
    sa.Column('simulation_run_id', sa.String(), nullable=False),
    sa.Column('scenario_id', sa.String(), nullable=False),
    sa.Column('plan_id', sa.String(), nullable=False),
    sa.Column('plan_version', sa.Integer(), nullable=False),
    sa.Column('status', sa.String(), nullable=False),
    sa.Column('engine_version', sa.String(), nullable=False),
    sa.Column('started_at', sa.DateTime(timezone=True), nullable=False),
    sa.Column('completed_at', sa.DateTime(timezone=True), nullable=True),
    sa.Column('configuration', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
    sa.Column('provenance', postgresql.JSONB(astext_type=sa.Text()), nullable=False),
    sa.Column('result', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
    sa.PrimaryKeyConstraint('simulation_run_id')
    )

    # Decisions
    op.create_table('decisions',
    sa.Column('decision_id', sa.String(), nullable=False),
    sa.Column('plan_id', sa.String(), nullable=False),
    sa.Column('plan_version', sa.Integer(), nullable=False),
    sa.Column('action', sa.String(), nullable=False),
    sa.Column('justification', sa.Text(), nullable=False),
    sa.Column('decided_at', sa.DateTime(timezone=True), nullable=False),
    sa.Column('decided_by', sa.String(), nullable=False),
    sa.Column('status', sa.String(), nullable=False),
    sa.Column('decision_metadata', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
    sa.PrimaryKeyConstraint('decision_id')
    )


def downgrade() -> None:
    op.drop_table('decisions')
    op.drop_table('simulation_runs')
    op.drop_table('blocks')
    op.drop_table('plans')
    op.drop_table('train_paths')
    op.drop_table('trains')
    op.drop_table('maintenance_tasks')
    op.drop_table('assets')
    op.drop_table('track_sections')
    op.drop_table('corridors')
