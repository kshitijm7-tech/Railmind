'use client';

import React, { useEffect, useState } from 'react';
import { AppShell } from '../../components/layout/AppShell';
import { DataTable, ColumnDef } from '../../components/operational/DataTable';
import { SectionBadge } from '../../components/railway/RailwayBadges';
import { Button } from '../../components/ui/Button';
import { services } from '../../services';
import { Plan, CandidateBlockWindow } from '../../domain';

export default function PlanningPage() {
  const [plans, setPlans] = useState<Plan[]>([]);
  const [windows, setWindows] = useState<CandidateBlockWindow[]>([]);

  useEffect(() => {
    Promise.all([
      services.planning.getPlans(),
      services.planning.getCandidateWindows()
    ]).then(([pList, wList]) => {
      setPlans(pList);
      setWindows(wList);
    });
  }, []);

  const planColumns: ColumnDef<Plan>[] = [
    { header: 'Plan ID', cell: (p) => <strong style={{ fontFamily: 'var(--font-mono)' }}>{p.plan_id}</strong> },
    { header: 'Plan Name', accessorKey: 'name' },
    { header: 'Strategy', accessorKey: 'strategy' },
    { header: 'Predicted Delay', cell: (p) => `${p.metrics.total_delay_minutes} min` },
    { header: 'Tasks Done', cell: (p) => `${p.metrics.maintenance_tasks_completed} tasks` },
    { header: 'Overrun Risk (P90)', cell: (p) => `${(p.metrics.overall_overrun_risk * 100).toFixed(0)}%` },
    { header: 'Solver Time', cell: (p) => `${p.solver_runtime_ms} ms` },
    { header: 'Status', cell: (p) => <span style={{ fontWeight: 600, color: p.status === 'Recommended' ? '#38bdf8' : '#a2b7c9' }}>{p.status}</span> }
  ];

  return (
    <AppShell
      title="Block Planning & Possession Optimization"
      eyebrow="CP-SAT Constraint Engine"
      actions={
        <Button variant="primary" size="sm" onClick={() => alert('CP-SAT Solver run triggered (Phase 3)')}>
          ⚡ Run CP-SAT Optimization
        </Button>
      }
    >
      <div style={{ marginBottom: '1.5rem', color: 'var(--text-secondary)', fontSize: '0.85rem' }}>
        Joint optimization of maintenance possessions and train paths under hard safety and resource constraints.
      </div>

      <div style={{ marginBottom: '2rem' }}>
        <h3 style={{ margin: '0 0 0.5rem 0', fontSize: '1rem' }}>Generated Candidate Plans</h3>
        <DataTable
          columns={planColumns}
          data={plans}
          keyExtractor={(p) => p.plan_id}
        />
      </div>

      <div>
        <h3 style={{ margin: '0 0 0.5rem 0', fontSize: '1rem' }}>Available Possession Windows</h3>
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(300px, 1fr))', gap: '1rem' }}>
          {windows.map(w => (
            <div key={w.window_id} style={{ background: 'var(--surface-panel)', border: '1px solid var(--surface-border)', borderRadius: 'var(--radius-md)', padding: '1rem' }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '0.5rem' }}>
                <SectionBadge sectionId={w.section_id} />
                <span style={{ fontSize: '0.72rem', color: 'var(--text-accent)', fontFamily: 'var(--font-mono)' }}>
                  {w.recommended_usage}
                </span>
              </div>
              <div style={{ fontSize: '0.82rem', color: 'var(--text-primary)', fontWeight: 600 }}>
                Window ID: {w.window_id}
              </div>
              <div style={{ fontSize: '0.75rem', color: 'var(--text-secondary)', marginTop: '0.25rem' }}>
                Window Duration: max {w.max_duration_min} min ({new Date(w.earliest_start).toLocaleTimeString()} - {new Date(w.latest_end).toLocaleTimeString()})
              </div>
            </div>
          ))}
        </div>
      </div>
    </AppShell>
  );
}
