'use client';

import React, { useEffect, useState, useMemo } from 'react';
import { AppShell } from '../../components/layout/AppShell';
import { DataTable, ColumnDef } from '../../components/operational/DataTable';
import { TrainBadge, SectionBadge } from '../../components/railway/RailwayBadges';
import { MetricCard } from '../../components/operational/MetricCard';
import { StateBadge } from '../../components/state/StateBadge';
import { services } from '../../services';
import { TrainService } from '../../domain';
import { Search, Train } from 'lucide-react';

export default function TrainsPage() {
  const [trains, setTrains] = useState<TrainService[]>([]);
  const [filterQuery, setFilterQuery] = useState('');

  useEffect(() => {
    services.trains.getTrains().then(setTrains);
  }, []);

  const filteredTrains = useMemo(() => {
    if (!filterQuery) return trains;
    const q = filterQuery.toLowerCase();
    return trains.filter((t) =>
      t.train_number.toLowerCase().includes(q) ||
      t.name.toLowerCase().includes(q) ||
      t.origin_station_id.toLowerCase().includes(q) ||
      t.destination_station_id.toLowerCase().includes(q) ||
      t.current_status.toLowerCase().includes(q)
    );
  }, [trains, filterQuery]);

  const stats = useMemo(() => {
    const total = trains.length;
    const onTimeCount = trains.filter((t) => t.current_status === 'ON_TIME').length;
    const punctuality = total > 0 ? Math.round((onTimeCount / total) * 100) : 100;
    const totalDelay = trains.reduce((acc, t) => acc + (t.current_delay_min || 0), 0);
    const totalCascading = trains.reduce((acc, t) => acc + (t.cascading_delay_estimate_min || 0), 0);
    return { total, punctuality, totalDelay, totalCascading };
  }, [trains]);

  const columns: ColumnDef<TrainService>[] = [
    {
      header: 'Train',
      cell: (t) => <TrainBadge trainNumber={t.train_number} trainType={t.train_type} priority={t.priority} />
    },
    {
      header: 'Train Name',
      cell: (t) => (
        <div>
          <span style={{ fontWeight: 600, color: 'var(--text-primary)', fontSize: '0.82rem' }}>{t.name}</span>
          <div style={{ fontSize: '0.68rem', color: 'var(--text-muted)' }}>{t.train_type} · Priority {t.priority}</div>
        </div>
      )
    },
    {
      header: 'Origin → Dest',
      cell: (t) => (
        <span style={{ fontFamily: 'var(--font-mono)', fontSize: '0.75rem', color: 'var(--text-secondary)' }}>
          {t.origin_station_id} → {t.destination_station_id}
        </span>
      )
    },
    {
      header: 'Route Sections',
      cell: (t) => (
        <div style={{ display: 'flex', gap: '0.25rem', flexWrap: 'wrap' }}>
          {t.route_section_ids.map((s) => <SectionBadge key={s} sectionId={s} />)}
        </div>
      )
    },
    {
      header: 'Status',
      cell: (t) => {
        const isOnTime = t.current_status === 'ON_TIME';
        return (
          <span
            className="delay-pill"
            style={{
              background: isOnTime ? 'rgba(16, 185, 129, 0.15)' : 'rgba(245, 158, 11, 0.15)',
              color: isOnTime ? 'var(--status-normal)' : 'var(--status-warning)',
              border: `1px solid ${isOnTime ? 'rgba(16, 185, 129, 0.4)' : 'rgba(245, 158, 11, 0.4)'}`,
            }}
          >
            ● {t.current_status}
          </span>
        );
      }
    },
    {
      header: 'Current Delay',
      cell: (t) => {
        const delay = t.current_delay_min;
        return (
          <span style={{
            fontFamily: 'var(--font-mono)',
            fontWeight: 700,
            fontSize: '0.82rem',
            color: delay === 0 ? 'var(--status-normal)' : (delay > 15 ? 'var(--status-critical)' : 'var(--status-warning)')
          }}>
            {delay === 0 ? 'ON TIME' : `+${delay} min`}
          </span>
        );
      }
    },
    {
      header: 'Cascading Risk',
      cell: (t) => (
        <span style={{ fontFamily: 'var(--font-mono)', fontSize: '0.78rem', color: 'var(--text-secondary)' }}>
          +{t.cascading_delay_estimate_min} min
        </span>
      )
    }
  ];

  return (
    <AppShell
      title="Train Operations & Schedule Adherence"
      eyebrow="Corridor C-07 Timetable Coordination & Path Telemetry"
      actions={
        <div style={{ display: 'flex', gap: '0.5rem', alignItems: 'center' }}>
          <StateBadge stateType="ACTUAL" label="TMS RADAR: SYNCED" />
        </div>
      }
    >
      <div style={{ marginBottom: '1.25rem', color: 'var(--text-secondary)', fontSize: '0.85rem' }}>
        Live tracking of scheduled passenger express and freight rakes traversing the 9 sections of Corridor C-07.
      </div>

      {/* KPI Metrics Strip */}
      <div className="cc-kpi-row" style={{ marginBottom: '1.25rem' }}>
        <MetricCard label="Active Trains" value={stats.total} statusTone="neutral" />
        <MetricCard label="Punctuality Rate" value={`${stats.punctuality}%`} statusTone={stats.punctuality >= 85 ? 'normal' : 'warning'} />
        <MetricCard label="Accumulated Delay" value={`+${stats.totalDelay} min`} statusTone={stats.totalDelay <= 15 ? 'normal' : 'warning'} />
        <MetricCard label="Cascading Delay Risk" value={`+${stats.totalCascading} min`} statusTone="attention" />
      </div>

      {/* Search & Filter Bar */}
      <div style={{
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'space-between',
        padding: '0.6rem 0.8rem',
        background: 'var(--surface-panel)',
        border: '1px solid var(--surface-border)',
        borderRadius: 'var(--radius-md)',
        marginBottom: '1rem',
        flexWrap: 'wrap',
        gap: '0.75rem',
      }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', flex: '1 1 240px' }}>
          <Search size={15} style={{ color: 'var(--text-muted)' }} />
          <input
            type="text"
            placeholder="Search by train number, name, origin, or destination..."
            value={filterQuery}
            onChange={(e) => setFilterQuery(e.target.value)}
            style={{
              background: 'transparent',
              border: 'none',
              color: 'var(--text-primary)',
              fontSize: '0.82rem',
              width: '100%',
              outline: 'none',
            }}
          />
        </div>
        <div style={{ fontSize: '0.72rem', color: 'var(--text-muted)', fontFamily: 'var(--font-mono)' }}>
          Showing {filteredTrains.length} of {trains.length} services
        </div>
      </div>

      <DataTable
        columns={columns}
        data={filteredTrains}
        keyExtractor={(t) => t.train_id}
      />
    </AppShell>
  );
}

