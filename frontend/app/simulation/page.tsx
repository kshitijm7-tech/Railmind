'use client';

import React, { useEffect, useState } from 'react';
import { AppShell } from '../../components/layout/AppShell';
import { StateBadge } from '../../components/state/StateBadge';
import { Button } from '../../components/ui/Button';
import { services } from '../../services';
import { Scenario } from '../../domain';
import { useOperationalContext } from '../../context/OperationalContext';

export default function SimulationPage() {
  const [scenarios, setScenarios] = useState<Scenario[]>([]);
  const { enterScenario, activeScenario } = useOperationalContext();

  useEffect(() => {
    services.simulation.getScenarios().then(setScenarios);
  }, []);

  return (
    <AppShell
      title="Simulation & What-If Digital Twin"
      eyebrow="Hypothetical Operational Branching"
      actions={<StateBadge stateType="SCENARIO" label="COPY-ON-WRITE BRANCHING" />}
    >
      <div style={{ marginBottom: '1.5rem', color: 'var(--text-secondary)', fontSize: '0.85rem' }}>
        Evaluate impact propagation, duration overruns, and unexpected track closures without mutating live operational state.
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(320px, 1fr))', gap: '1.25rem' }}>
        {scenarios.map(sc => {
          const isCurrentActive = activeScenario?.scenario_id === sc.scenario_id;
          return (
            <div
              key={sc.scenario_id}
              style={{
                background: 'var(--surface-panel)',
                border: isCurrentActive ? '1px solid var(--state-scenario)' : '1px solid var(--surface-border)',
                borderRadius: 'var(--radius-md)',
                padding: '1.25rem',
                display: 'flex',
                flexDirection: 'column',
                justifyContent: 'space-between'
              }}
            >
              <div>
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '0.5rem' }}>
                  <StateBadge stateType="SCENARIO" label={sc.scenario_type} />
                  <span style={{ fontSize: '0.7rem', color: 'var(--text-muted)' }}>Base: {sc.base_state_version}</span>
                </div>
                <h3 style={{ margin: '0.5rem 0', fontSize: '1.05rem', color: 'var(--text-primary)' }}>
                  {sc.name}
                </h3>
                <p style={{ margin: '0 0 1rem 0', color: 'var(--text-secondary)', fontSize: '0.82rem', lineHeight: 1.4 }}>
                  {sc.description}
                </p>
              </div>

              <div style={{ display: 'flex', justifyContent: 'flex-end' }}>
                <Button
                  variant={isCurrentActive ? 'outline' : 'primary'}
                  size="sm"
                  onClick={() => enterScenario(sc)}
                >
                  {isCurrentActive ? '✓ Currently Active Branch' : '⚡ Enter What-If Scenario'}
                </Button>
              </div>
            </div>
          );
        })}
      </div>
    </AppShell>
  );
}
