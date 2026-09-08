'use client';

import React, { useEffect, useState } from 'react';
import { AppShell } from '../../components/layout/AppShell';
import { DataTable, ColumnDef } from '../../components/operational/DataTable';
import { services } from '../../services';
import { AuditEvent } from '../../domain';

export default function AuditPage() {
  const [events, setEvents] = useState<AuditEvent[]>([]);

  useEffect(() => {
    services.audit.getAuditEvents().then(setEvents);
  }, []);

  const columns: ColumnDef<AuditEvent>[] = [
    { header: 'Event ID', cell: (e) => <span style={{ fontFamily: 'var(--font-mono)' }}>{e.event_id}</span> },
    { header: 'Event Type', accessorKey: 'event_type' },
    { header: 'Entity', cell: (e) => `${e.entity_type} (${e.entity_id})` },
    { header: 'Triggered By', accessorKey: 'user' },
    { header: 'State Version', cell: (e) => <span style={{ fontFamily: 'var(--font-mono)', color: 'var(--text-accent)' }}>{e.state_version}</span> },
    { header: 'Summary', accessorKey: 'summary' },
    { header: 'Timestamp', cell: (e) => new Date(e.timestamp).toLocaleTimeString() }
  ];

  return (
    <AppShell title="Audit Trail & Safety Verification Logs" eyebrow="Governance & Traceability">
      <div style={{ marginBottom: '1.25rem', color: 'var(--text-secondary)', fontSize: '0.85rem' }}>
        Append-only traceable log of all optimization jobs, plan simulations, state versions, and operator authorizations.
      </div>
      <DataTable
        columns={columns}
        data={events}
        keyExtractor={(e) => e.event_id}
      />
    </AppShell>
  );
}
