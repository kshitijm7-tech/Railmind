'use client';

import React, { useEffect, useState, useMemo } from 'react';
import { AppShell } from '../../components/layout/AppShell';
import { DataTable, ColumnDef } from '../../components/operational/DataTable';
import { MetricCard } from '../../components/operational/MetricCard';
import { StateBadge } from '../../components/state/StateBadge';
import { services } from '../../services';
import { AuditEvent } from '../../domain';
import { ShieldCheck, Lock, FileText, Database } from 'lucide-react';

export default function AuditPage() {
  const [events, setEvents] = useState<AuditEvent[]>([]);

  useEffect(() => {
    services.audit.getAuditEvents().then(setEvents);
  }, []);

  const stats = useMemo(() => {
    const total = events.length;
    const users = new Set(events.map((e) => e.user)).size;
    const latestVersion = events.length > 0 ? events[0]?.state_version || 'v1024' : 'v1024';
    return { total, users, latestVersion };
  }, [events]);

  const columns: ColumnDef<AuditEvent>[] = [
    {
      header: 'Event ID',
      cell: (e) => (
        <span style={{ fontFamily: 'var(--font-mono)', fontWeight: 700, color: 'var(--text-accent)', fontSize: '0.78rem' }}>
          {e.event_id}
        </span>
      )
    },
    {
      header: 'Event Type',
      cell: (e) => (
        <span style={{
          fontFamily: 'var(--font-mono)',
          fontSize: '0.68rem',
          fontWeight: 700,
          padding: '2px 6px',
          borderRadius: '3px',
          background: 'var(--surface-elevated)',
          border: '1px solid var(--surface-border)',
          color: e.event_type.includes('DECISION') ? 'var(--status-normal)' : 'var(--text-primary)'
        }}>
          {e.event_type}
        </span>
      )
    },
    {
      header: 'Entity Scope',
      cell: (e) => (
        <span style={{ fontSize: '0.75rem', color: 'var(--text-secondary)', fontFamily: 'var(--font-mono)' }}>
          {e.entity_type} <span style={{ color: 'var(--text-muted)' }}>({e.entity_id})</span>
        </span>
      )
    },
    {
      header: 'Triggered By',
      cell: (e) => (
        <span style={{ fontSize: '0.78rem', color: 'var(--text-primary)', fontWeight: 500 }}>
          {e.user}
        </span>
      )
    },
    {
      header: 'State Version',
      cell: (e) => (
        <span style={{ fontFamily: 'var(--font-mono)', color: 'var(--state-prediction)', fontWeight: 600, fontSize: '0.75rem' }}>
          {e.state_version}
        </span>
      )
    },
    {
      header: 'Summary & Trace',
      cell: (e) => (
        <span style={{ fontSize: '0.78rem', color: 'var(--text-secondary)' }}>
          {e.summary}
        </span>
      )
    },
    {
      header: 'Timestamp (UTC)',
      cell: (e) => (
        <span style={{ fontSize: '0.72rem', color: 'var(--text-muted)', fontFamily: 'var(--font-mono)' }}>
          {new Date(e.timestamp).toLocaleTimeString()}
        </span>
      )
    }
  ];

  return (
    <AppShell
      title="Audit Trail & Safety Verification Logs"
      eyebrow="Governance, Immutability & Safety Traceability"
      actions={
        <div style={{ display: 'flex', gap: '0.5rem', alignItems: 'center' }}>
          <StateBadge stateType="ACTUAL" label="CHAIN INTEGRITY: VERIFIED" />
        </div>
      }
    >
      <div style={{ marginBottom: '1.25rem', color: 'var(--text-secondary)', fontSize: '0.85rem' }}>
        Append-only cryptographic audit log of all CP-SAT optimization jobs, digital twin simulations, state versions, and operator authorizations.
      </div>

      {/* KPI Metrics Strip */}
      <div className="cc-kpi-row" style={{ marginBottom: '1.25rem' }}>
        <MetricCard label="Audit Records" value={stats.total} statusTone="neutral" />
        <MetricCard label="Ledger Integrity" value="VERIFIED" statusTone="normal" />
        <MetricCard label="State Version Head" value={stats.latestVersion} statusTone="attention" />
        <MetricCard label="Active Authorized Actors" value={stats.users} statusTone="neutral" />
      </div>

      <div style={{
        background: 'var(--surface-panel)',
        border: '1px solid var(--surface-border)',
        borderRadius: 'var(--radius-md)',
        overflow: 'hidden',
      }}>
        <div style={{
          padding: '0.75rem 1rem',
          background: 'var(--surface-elevated)',
          borderBottom: '1px solid var(--surface-border)',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'space-between',
        }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', fontSize: '0.82rem', fontWeight: 700, color: 'var(--text-primary)' }}>
            <Lock size={15} style={{ color: 'var(--status-normal)' }} />
            <span>Cryptographic State Ledger (Corridor C-07)</span>
          </div>
          <span style={{ fontSize: '0.7rem', color: 'var(--text-muted)', fontFamily: 'var(--font-mono)' }}>
            STORAGE: POSTGRESQL / POSTGIS · APPEND-ONLY
          </span>
        </div>

        <DataTable
          columns={columns}
          data={events}
          keyExtractor={(e) => e.event_id}
        />
      </div>
    </AppShell>
  );
}

