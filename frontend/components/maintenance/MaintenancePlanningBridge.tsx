'use client';

import React from 'react';
import { Button } from '../ui/Button';
import { StateBadge } from '../state/StateBadge';

interface MaintenancePlanningBridgeProps {
  onOpenPlanning?: () => void;
  disabled?: boolean;
}

export function MaintenancePlanningBridge({ onOpenPlanning, disabled = true }: MaintenancePlanningBridgeProps) {
  return (
    <section className="maintenance-planning-bridge" aria-labelledby="planning-bridge-heading">
      <h3 id="planning-bridge-heading" className="planning-bridge-title">Planning Bridge</h3>
      <p className="planning-bridge-description">
        Selected maintenance tasks can be forwarded to the Block Planning workspace for
        possession window generation, constraint evaluation, and optimization.
      </p>

      <div className="planning-bridge-status">
        <StateBadge stateType="PREDICTION" label="FUTURE INTEGRATION" />
        <span className="planning-bridge-note">
          Requires E01 (Constraint Engine) and E03 (Optimization Engine) — not yet implemented
        </span>
      </div>

      <div className="planning-bridge-capabilities">
        <h4>Planned capabilities:</h4>
        <ul>
          <li>Candidate possession window generation per section</li>
          <li>Hard constraint validation (safety, resource, possession)</li>
          <li>Train impact analysis per candidate block</li>
          <li>CP-SAT multi-objective optimization (delay, priority, bundling)</li>
          <li>Monte Carlo robustness evaluation</li>
          <li>Plan comparison and human approval</li>
        </ul>
      </div>

      <div className="planning-bridge-actions">
        <Button
          variant="primary"
          size="sm"
          onClick={onOpenPlanning}
          disabled={disabled}
          aria-disabled={disabled}
        >
          Open Block Planning Workspace →
        </Button>
        {disabled && (
          <span className="planning-bridge-disabled-note">
            Requires backend endpoints for candidate generation and plan creation (E01/E03)
          </span>
        )}
      </div>

      <details className="planning-bridge-contracts">
        <summary>Required backend contracts (not yet implemented)</summary>
        <ul style={{ fontSize: '0.75rem', color: 'var(--text-secondary)', marginTop: '0.5rem' }}>
          <li>POST /api/v1/planning/candidates → CandidateBlockWindow[]</li>
          <li>POST /api/v1/planning/generate → AsyncJob (plan generation)</li>
          <li>POST /api/v1/plans/compare → PlanComparison</li>
          <li>POST /api/v1/simulations → AsyncJob (simulation)</li>
          <li>GET /api/v1/recommendations → Recommendation[]</li>
        </ul>
      </details>
    </section>
  );
}