'use client';

import React, { useEffect, useState } from 'react';
import { AppShell } from '../../components/layout/AppShell';
import { DataTable, ColumnDef } from '../../components/operational/DataTable';
import { TrainBadge, SectionBadge } from '../../components/railway/RailwayBadges';
import { services } from '../../services';
import { TrainService } from '../../domain';

export default function TrainsPage() {
  const [trains, setTrains] = useState<TrainService[]>([]);

  useEffect(() => {
    services.trains.getTrains().then(setTrains);
  }, []);

  const columns: ColumnDef<TrainService>[] = [
    { header: 'Train', cell: (t) => <TrainBadge trainNumber={t.train_number} trainType={t.train_type} priority={t.priority} /> },
    { header: 'Train Name', accessorKey: 'name' },
    { header: 'Origin', accessorKey: 'origin_station_id' },
    { header: 'Destination', accessorKey: 'destination_station_id' },
    { header: 'Route Sections', cell: (t) => (
      <div style={{ display: 'flex', gap: '0.25rem', flexWrap: 'wrap' }}>
        {t.route_section_ids.map(s => <SectionBadge key={s} sectionId={s} />)}
      </div>
    )},
    { header: 'Status', cell: (t) => (
      <span style={{ color: t.current_status === 'ON_TIME' ? '#34d399' : '#f59e0b', fontWeight: 600, fontSize: '0.75rem' }}>
        ● {t.current_status}
      </span>
    )},
    { header: 'Current Delay', cell: (t) => `${t.current_delay_min} min` },
    { header: 'Cascading Risk', cell: (t) => `${t.cascading_delay_estimate_min} min` }
  ];

  return (
    <AppShell title="Train Operations & Schedule Adherence" eyebrow="Timetable Coordination">
      <div style={{ marginBottom: '1.25rem', color: 'var(--text-secondary)', fontSize: '0.85rem' }}>
        Scheduled and active passenger and freight train services navigating Corridor C-07.
      </div>
      <DataTable
        columns={columns}
        data={trains}
        keyExtractor={(t) => t.train_id}
      />
    </AppShell>
  );
}
