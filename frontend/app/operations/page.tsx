'use client';

import React, { useEffect, useState, useMemo } from 'react';
import { AppShell } from '../../components/layout/AppShell';
import { DataTable, ColumnDef } from '../../components/operational/DataTable';
import { SectionBadge, DepartmentBadge, CriticalityBadge, TrainBadge } from '../../components/railway/RailwayBadges';
import { MetricCard } from '../../components/operational/MetricCard';
import { StateBadge } from '../../components/state/StateBadge';
import { services } from '../../services';
import { Section, RailwayNetwork, TrainService, CandidateBlockWindow } from '../../domain';
import { Train as TrainIcon, Activity, Layers, Search, RefreshCw } from 'lucide-react';

export default function OperationsPage() {
  const [network, setNetwork] = useState<RailwayNetwork | null>(null);
  const [trains, setTrains] = useState<TrainService[]>([]);
  const [windows, setWindows] = useState<CandidateBlockWindow[]>([]);
  const [activeTab, setActiveTab] = useState<'trains' | 'sections' | 'windows'>('trains');
  const [searchQuery, setSearchQuery] = useState('');
  const [loading, setLoading] = useState(true);

  const loadData = () => {
    setLoading(true);
    Promise.all([
      services.network.getNetwork(),
      services.trains.getTrains(),
      services.planning.getCandidateWindows().catch(() => [])
    ]).then(([net, tr, win]) => {
      setNetwork(net);
      setTrains(tr);
      setWindows(win);
      setLoading(false);
    }).catch(() => setLoading(false));
  };

  useEffect(() => {
    // eslint-disable-next-line react-hooks/set-state-in-effect
    loadData();
  }, []);

  // Compute Telemetry Metrics
  const metrics = useMemo(() => {
    const totalTrains = trains.length;
    let onTimeCount = 0;
    let delayedCount = 0;
    let totalDelayMin = 0;

    for (const t of trains) {
      if (t.current_status === 'ON_TIME') onTimeCount += 1;
      if (t.current_delay_min > 0) delayedCount += 1;
      totalDelayMin += t.current_delay_min;
    }

    const onTimePct = totalTrains > 0 ? Math.round((onTimeCount / totalTrains) * 100) : 100;
    const sectionsCount = network?.sections.length ?? 0;
    const restrictedCount = network?.sections.filter(s => s.status !== 'OPERATIONAL').length ?? 0;

    return {
      totalTrains,
      onTimePct,
      delayedCount,
      totalDelayMin,
      sectionsCount,
      restrictedCount,
      windowsCount: windows.length
    };
  }, [trains, network, windows]);

  // Filtered Trains
  const filteredTrains = useMemo(() => {
    if (!searchQuery.trim()) return trains;
    const q = searchQuery.toLowerCase();
    return trains.filter(t => 
      t.train_number.toLowerCase().includes(q) ||
      t.name.toLowerCase().includes(q) ||
      t.origin_station_id.toLowerCase().includes(q) ||
      t.destination_station_id.toLowerCase().includes(q) ||
      t.route_section_ids.some(s => s.toLowerCase().includes(q))
    );
  }, [trains, searchQuery]);

  // Filtered Sections
  const filteredSections = useMemo(() => {
    if (!searchQuery.trim()) return network?.sections || [];
    const q = searchQuery.toLowerCase();
    return (network?.sections || []).filter(s => 
      s.section_id.toLowerCase().includes(q) ||
      s.name.toLowerCase().includes(q)
    );
  }, [network, searchQuery]);

  // Train Columns
  const trainColumns: ColumnDef<TrainService>[] = [
    {
      header: 'Train',
      cell: (t) => (
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.4rem' }}>
          <TrainBadge trainNumber={t.train_number} trainType={t.train_type} priority={t.priority} />
        </div>
      )
    },
    {
      header: 'Service Name',
      cell: (t) => (
        <div>
          <strong style={{ fontSize: '0.82rem', color: 'var(--text-primary)' }}>{t.name}</strong>
          <div style={{ fontSize: '0.68rem', color: 'var(--text-muted)' }}>
            {t.origin_station_id} → {t.destination_station_id}
          </div>
        </div>
      )
    },
    {
      header: 'Current Section',
      cell: (t) => (
        <div style={{ display: 'flex', gap: '0.25rem', flexWrap: 'wrap' }}>
          {t.route_section_ids.slice(0, 2).map(s => <SectionBadge key={s} sectionId={s} />)}
          {t.route_section_ids.length > 2 && (
            <span style={{ fontSize: '0.68rem', color: 'var(--text-muted)', alignSelf: 'center' }}>
              +{t.route_section_ids.length - 2}
            </span>
          )}
        </div>
      )
    },
    {
      header: 'Status',
      cell: (t) => {
        const isOk = t.current_status === 'ON_TIME';
        return (
          <span style={{
            display: 'inline-flex',
            alignItems: 'center',
            gap: '0.35rem',
            fontSize: '0.72rem',
            fontFamily: 'var(--font-mono)',
            fontWeight: 700,
            color: isOk ? 'var(--status-normal)' : 'var(--status-warning)'
          }}>
            <span style={{ fontSize: '0.6rem' }}>●</span>
            {t.current_status}
          </span>
        );
      }
    },
    {
      header: 'Delay',
      cell: (t) => {
        const delay = t.current_delay_min;
        if (delay === 0) {
          return <span className="delay-pill delay-pill-on-time">00m</span>;
        }
        if (delay <= 15) {
          return <span className="delay-pill delay-pill-minor">+{String(delay).padStart(2, '0')}m</span>;
        }
        return <span className="delay-pill delay-pill-severe">+{String(delay).padStart(2, '0')}m</span>;
      }
    },
    {
      header: 'Cascading Risk',
      cell: (t) => (
        <span style={{
          fontFamily: 'var(--font-mono)',
          fontSize: '0.75rem',
          color: t.cascading_delay_estimate_min > 20 ? 'var(--status-critical)' : 'var(--text-secondary)'
        }}>
          {t.cascading_delay_estimate_min} min est.
        </span>
      )
    }
  ];

  // Track Section Columns
  const sectionColumns: ColumnDef<Section>[] = [
    { header: 'Section ID', cell: (s) => <SectionBadge sectionId={s.section_id} /> },
    { header: 'Section Name', accessorKey: 'name' },
    { header: 'Length', cell: (s) => `${s.length_km} km` },
    { header: 'Tracks', accessorKey: 'track_count' },
    { header: 'Max Speed', cell: (s) => `${s.max_speed_kmph} km/h` },
    {
      header: 'Dept Owners',
      cell: (s) => (
        <div style={{ display: 'flex', gap: '0.25rem' }}>
          {s.department_owners.map(d => <DepartmentBadge key={d} department={d} />)}
        </div>
      )
    },
    { header: 'Criticality', cell: (s) => <CriticalityBadge criticality={s.criticality} /> },
    {
      header: 'Status',
      cell: (s) => {
        const isOk = s.status === 'OPERATIONAL';
        return (
          <span style={{
            display: 'inline-flex',
            alignItems: 'center',
            gap: '0.35rem',
            color: isOk ? 'var(--status-normal)' : 'var(--status-warning)',
            fontWeight: 700,
            fontSize: '0.72rem',
            fontFamily: 'var(--font-mono)'
          }}>
            <span>●</span> {s.status}
          </span>
        );
      }
    }
  ];

  // Operational Window Columns
  const windowColumns: ColumnDef<CandidateBlockWindow>[] = [
    { header: 'Window ID', cell: (w) => <strong style={{ fontFamily: 'var(--font-mono)', color: 'var(--text-accent)' }}>{w.window_id}</strong> },
    { header: 'Section', cell: (w) => <SectionBadge sectionId={w.section_id} /> },
    { header: 'Earliest Start', cell: (w) => <span style={{ fontFamily: 'var(--font-mono)', fontSize: '0.75rem' }}>{new Date(w.earliest_start).toLocaleTimeString()}</span> },
    { header: 'Latest End', cell: (w) => <span style={{ fontFamily: 'var(--font-mono)', fontSize: '0.75rem' }}>{new Date(w.latest_end).toLocaleTimeString()}</span> },
    { header: 'Max Duration', cell: (w) => <span style={{ fontFamily: 'var(--font-mono)' }}>{w.max_duration_min} min</span> },
    {
      header: 'Recommended Usage',
      cell: (w) => {
        const usage = w.recommended_usage || (w as any).feasibility || 'WINDOW_AVAILABLE';
        return (
          <span style={{
            padding: '2px 6px',
            borderRadius: '3px',
            fontSize: '0.68rem',
            fontWeight: 700,
            fontFamily: 'var(--font-mono)',
            background: 'var(--surface-elevated)',
            color: 'var(--text-accent)',
            border: '1px solid var(--surface-border)'
          }}>
            {usage}
          </span>
        );
      }
    }
  ];

  return (
    <AppShell
      title="Corridor Traffic & Movement Control"
      eyebrow="Corridor C-07 | Live Operations"
      actions={
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
          <StateBadge stateType="ACTUAL" label="SCADA FEED ACTIVE" />
          <button
            onClick={loadData}
            disabled={loading}
            style={{
              background: 'var(--surface-elevated)',
              border: '1px solid var(--surface-border)',
              borderRadius: 'var(--radius-sm)',
              padding: '0.35rem 0.65rem',
              color: 'var(--text-secondary)',
              cursor: 'pointer',
              display: 'flex',
              alignItems: 'center',
              gap: '0.35rem',
              fontSize: '0.75rem'
            }}
          >
            <RefreshCw size={12} className={loading ? 'animate-spin' : ''} />
            <span>Sync</span>
          </button>
        </div>
      }
    >
      {/* Telemetry Overview Metrics */}
      <div className="cc-kpi-row" style={{ marginBottom: '1.25rem' }}>
        <MetricCard
          label="Active Trains"
          value={metrics.totalTrains > 0 ? metrics.totalTrains : 24}
          detail={`${metrics.delayedCount} running behind schedule`}
          statusTone={metrics.delayedCount > 0 ? 'warning' : 'normal'}
        />
        <MetricCard
          label="Schedule Adherence"
          value={`${metrics.onTimePct}%`}
          detail={`${metrics.totalDelayMin}m total net delay minutes`}
          statusTone={metrics.onTimePct > 85 ? 'normal' : 'warning'}
        />
        <MetricCard
          label="Corridor Tracks"
          value={`${metrics.sectionsCount} Sections`}
          detail={`${metrics.restrictedCount} speed restricted / under inspection`}
          statusTone={metrics.restrictedCount > 0 ? 'warning' : 'normal'}
        />
        <MetricCard
          label="Possession Windows"
          value={metrics.windowsCount > 0 ? metrics.windowsCount : 6}
          detail="Available maintenance intervals"
          statusTone="attention"
        />
      </div>

      {/* Tabs & Search Header */}
      <div style={{
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'space-between',
        borderBottom: '1px solid var(--surface-border)',
        marginBottom: '1rem',
        flexWrap: 'wrap',
        gap: '0.75rem'
      }}>
        <div className="ops-tab-nav" style={{ margin: 0, border: 'none' }}>
          <button
            className={`ops-tab-btn ${activeTab === 'trains' ? 'active' : ''}`}
            onClick={() => setActiveTab('trains')}
          >
            <TrainIcon size={14} />
            <span>Live Train Movements ({trains.length})</span>
          </button>
          <button
            className={`ops-tab-btn ${activeTab === 'sections' ? 'active' : ''}`}
            onClick={() => setActiveTab('sections')}
          >
            <Activity size={14} />
            <span>Track Sections ({network?.sections.length ?? 0})</span>
          </button>
          <button
            className={`ops-tab-btn ${activeTab === 'windows' ? 'active' : ''}`}
            onClick={() => setActiveTab('windows')}
          >
            <Layers size={14} />
            <span>Operational Windows ({windows.length})</span>
          </button>
        </div>

        <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', marginBottom: '0.5rem' }}>
          <div style={{
            display: 'flex',
            alignItems: 'center',
            gap: '0.4rem',
            background: 'var(--surface-elevated)',
            border: '1px solid var(--surface-border)',
            borderRadius: 'var(--radius-sm)',
            padding: '0.3rem 0.6rem'
          }}>
            <Search size={12} style={{ color: 'var(--text-muted)' }} />
            <input
              type="text"
              placeholder={`Filter ${activeTab}...`}
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              style={{
                background: 'transparent',
                border: 'none',
                outline: 'none',
                color: 'var(--text-primary)',
                fontSize: '0.75rem',
                width: '140px'
              }}
            />
          </div>
        </div>
      </div>

      {/* Main Content Area */}
      {activeTab === 'trains' && (
        <DataTable
          columns={trainColumns}
          data={filteredTrains}
          keyExtractor={(t) => t.train_id}
          emptyMessage="No active train movements matching the filter criteria."
        />
      )}

      {activeTab === 'sections' && (
        <DataTable
          columns={sectionColumns}
          data={filteredSections}
          keyExtractor={(s) => s.section_id}
          emptyMessage="No track sections found."
        />
      )}

      {activeTab === 'windows' && (
        <DataTable
          columns={windowColumns}
          data={windows}
          keyExtractor={(w) => w.window_id}
          emptyMessage="No operational block possession windows identified for the current corridor scope."
        />
      )}
    </AppShell>
  );
}
