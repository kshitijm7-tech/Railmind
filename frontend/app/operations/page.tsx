'use client';

import React, { useEffect, useState } from 'react';
import { AppShell } from '../../components/layout/AppShell';
import { DataTable, ColumnDef } from '../../components/operational/DataTable';
import { SectionBadge, DepartmentBadge, CriticalityBadge } from '../../components/railway/RailwayBadges';
import { services } from '../../services';
import { Section, RailwayNetwork } from '../../domain';

export default function OperationsPage() {
  const [network, setNetwork] = useState<RailwayNetwork | null>(null);

  useEffect(() => {
    services.network.getNetwork().then(setNetwork);
  }, []);

  const columns: ColumnDef<Section>[] = [
    { header: 'Section ID', cell: (s) => <SectionBadge sectionId={s.section_id} /> },
    { header: 'Section Name', accessorKey: 'name' },
    { header: 'Length', cell: (s) => `${s.length_km} km` },
    { header: 'Tracks', accessorKey: 'track_count' },
    { header: 'Max Speed', cell: (s) => `${s.max_speed_kmph} km/h` },
    { header: 'Dept Owners', cell: (s) => (
      <div style={{ display: 'flex', gap: '0.25rem' }}>
        {s.department_owners.map(d => <DepartmentBadge key={d} department={d} />)}
      </div>
    )},
    { header: 'Criticality', cell: (s) => <CriticalityBadge criticality={s.criticality} /> },
    { header: 'Status', cell: (s) => (
      <span style={{ color: s.status === 'OPERATIONAL' ? 'var(--status-normal)' : 'var(--status-warning)', fontWeight: 600, fontSize: '0.75rem' }}>
        ● {s.status}
      </span>
    )}
  ];

  return (
    <AppShell title="Corridor Operations & Track Infrastructure" eyebrow="Live Telemetry & Topology">
      <div style={{ marginBottom: '1rem', color: 'var(--text-secondary)', fontSize: '0.85rem' }}>
        Physical and operational status of all 9 track sections across Corridor C-07.
      </div>
      <DataTable
        columns={columns}
        data={network?.sections || []}
        keyExtractor={(s) => s.section_id}
      />
    </AppShell>
  );
}
