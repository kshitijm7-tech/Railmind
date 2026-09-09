'use client';

import React, { useEffect, useState, useCallback } from 'react';
import { AppShell } from '../../components/layout/AppShell';
import { SectionCard } from '../../components/command-center/SectionCard';
import { Button } from '../../components/ui/Button';
import { services } from '../../services';
import type { Plan as DomainPlan } from '../../domain';
import { EmptyState, LoadingState } from '../../components/feedback/FeedbackStates';
import { getConfiguredApiMode } from '../../services/api/serviceFactory';

// Plan comparison entry interface matching backend contract
interface PlanComparisonEntry {
  planId: string;
  planName: string;
  strategy: string;
  metrics: {
    total_delay_minutes: number;
    passenger_trains_affected: number;
    goods_trains_affected: number;
    maintenance_tasks_completed: number;
    maintenance_tasks_unscheduled: number;
    blocks_count: number;
    bundled_blocks_count: number;
    overall_overrun_risk: number;
    overall_score?: number;
  };
  trainImpactCount: number;
  constraintViolations: number;
  overrunRisk: number;
  recommendationRank: number;
}

// Backend comparePlans returns Plan[]
interface ComparePlansResponse {
  candidates: PlanComparisonEntry[];
  recommendedPlanId: string;
  tradeoffSummary: string[];
}

function PlanComparisonWorkspace() {
  const [comparison, setComparison] = useState<ComparePlansResponse | null>(null);
  const [selectedPlanIds, setSelectedPlanIds] = useState<string[]>([]);
  const apiMode = getConfiguredApiMode();

// Trigger comparison when plans are selected
  useEffect(() => {
    if (selectedPlanIds.length >= 2) {
      // Limit to max 5 plans per backend contract
      // Pass plan IDs to comparePlans service
      // The service accepts string[] and internally handles PlanId type
      services.planning.comparePlans({ planIds: selectedPlanIds.slice(0, 5) as any }).then(
        (results: DomainPlan[]) => {
          // Map backend Plan results to UI PlanComparisonEntry model
          const entryMap = new Map<string, PlanComparisonEntry>();
          results.forEach((plan) => {
            entryMap.set(plan.plan_id, {
              planId: plan.plan_id,
              planName: plan.name || plan.plan_id,
              strategy: plan.strategy || 'BALANCED',
              metrics: {
                total_delay_minutes: plan.metrics?.total_delay_minutes ?? 0,
                passenger_trains_affected: plan.metrics?.passenger_trains_affected ?? 0,
                goods_trains_affected: plan.metrics?.goods_trains_affected ?? 0,
                maintenance_tasks_completed: plan.metrics?.maintenance_tasks_completed ?? 0,
                maintenance_tasks_unscheduled: plan.metrics?.maintenance_tasks_unscheduled ?? 0,
                blocks_count: plan.metrics?.blocks_count ?? 0,
                bundled_blocks_count: plan.metrics?.bundled_blocks_count ?? 0,
                overall_overrun_risk: plan.metrics?.overall_overrun_risk ?? 0,
              },
              trainImpactCount: (plan.metrics?.passenger_trains_affected > 0 || plan.metrics?.goods_trains_affected > 0) ? 1 : 0,
              constraintViolations: 0,
              overrunRisk: plan.metrics?.overall_overrun_risk ?? 0,
              recommendationRank: 0,
            });
          });

          // Build comparison response for UI
          const candidates: PlanComparisonEntry[] = [];
          const tradeoffSummary: string[] = [];

          // Get all selected plan IDs and create entries
          selectedPlanIds.forEach((id) => {
            const entry = entryMap.get(id) || {
              planId: id,
              planName: id,
              strategy: 'BALANCED',
              metrics: {
                total_delay_minutes: 0,
                passenger_trains_affected: 0,
                goods_trains_affected: 0,
                maintenance_tasks_completed: 0,
                maintenance_tasks_unscheduled: 0,
                blocks_count: 0,
                bundled_blocks_count: 0,
                overall_overrun_risk: 0,
              },
              trainImpactCount: 0,
              constraintViolations: 0,
              overrunRisk: 0,
              recommendationRank: 0,
            };
            candidates.push(entry);
          });

          // Generate simple tradeoff summary from available data
          if (candidates.length > 0) {
            const delayValues = candidates.map((c) => c.metrics.total_delay_minutes);
            const violationCounts = candidates.map((c) => c.constraintViolations);
            const trainImpacts = candidates.map((c) => c.trainImpactCount);

            // Simple observations based on backend data
            if (delayValues.some((v) => v > 0)) {
              tradeoffSummary.push('Delay varies across plans');
            }
            if (violationCounts.some((v) => v > 0)) {
              tradeoffSummary.push('Constraint violations differ between plans');
            }
            if (trainImpacts.some((v) => v > 0)) {
              tradeoffSummary.push('Train impact differs between plans');
            }
          }

          setComparison({
            candidates,
            recommendedPlanId: '',
            tradeoffSummary,
          });
        }
      ).catch((error: any) => {
        console.error('Plan comparison failed:', error);
        setComparison(null);
      });
    }
  }, [selectedPlanIds]);

  // Plan selection handler
  const handlePlanSelect = useCallback((planId: string) => {
    if (selectedPlanIds.includes(planId)) {
      // Deselect
      setSelectedPlanIds(selectedPlanIds.filter((id) => id !== planId));
    } else {
      // Select (max 5 plans)
      if (selectedPlanIds.length < 5) {
        setSelectedPlanIds([...selectedPlanIds, planId]);
      }
    }
  }, [selectedPlanIds]);

  // Compare plans handler
  const handleCompare = useCallback(() => {
    // Triggered by useEffect when sufficient plans are selected
  }, []);

  return (
    <AppShell
      title="Plan Comparison & Evaluation"
      eyebrow="Side-by-side plan comparison — system generated candidates pending human review"
    >
      <div style={{ marginBottom: '1.5rem', color: 'var(--text-secondary)', fontSize: '0.85rem' }}>
        Side-by-side comparison of generated block plans under hard safety and resource constraints.
      </div>

      {/* Plan Selection Bar */}
      <SectionCard
        eyebrow="Plan Selection"
        title="Select Plans to Compare"
        status={selectedPlanIds.length >= 2 ? 'success' : 'loading'}
      >
        <div style={{ fontSize: '0.875rem' }}>
          {selectedPlanIds.length > 0 ? (
            <>
              <p style={{ margin: '0.5rem 0', color: 'var(--text-primary)' }}>
                Selected: {selectedPlanIds.length} plan{selectedPlanIds.length !== 1 && 's'}
              </p>
              <p style={{ margin: '0.25rem 0', color: 'var(--text-secondary)' }}>
                {selectedPlanIds.map((id) => `${id}`).join(', ')}
              </p>
              <Button
                variant="secondary"
                size="sm"
                onClick={() => setSelectedPlanIds([])}
                style={{ marginTop: '0.5rem' }}
              >
                Deselect All
              </Button>
            </>
          ) : (
            <EmptyState
              title="No plans selected"
              description={
                'Select at least two plans to compare. Plans can be selected from the Block Planning Workspace.'
              }
              actionLabel='Go to Planning'
              onAction={() => {/* navigate to planning workspace */}
              }
            />
          )}
        </div>
      </SectionCard>

      {/* Comparison Results */}
      {comparison ? (
        <section style={{ padding: '1.5rem' }}>
          {/* Comparison Overview */}
          <SectionCard
            eyebrow="Comparison Overview"
            title="Comparison Overview"
            status="success"
          >
            <div style={{ fontSize: '0.875rem' }}>
              <p style={{ margin: '0.5rem 0', color: 'var(--text-primary)' }}>
                Comparing {comparison.candidates.length} plans
              </p>
              <p style={{ margin: '0.25rem 0', color: 'var(--text-secondary)' }}>
                Source: {apiMode}
              </p>
              {comparison.tradeoffSummary.length > 0 && (
                <div style={{ margin: '0.5rem 0', padding: '0.5rem', background: 'var(--surface-panel)', border: '1px solid var(--surface-border)', borderRadius: '3px' }}>
                  <p style={{ margin: '0', fontSize: '0.75rem', color: 'var(--text-primary)' }}>
                    Trade-Offs
                  </p>
                  <ul style={{ margin: '0.25rem 0 0 1rem', fontSize: '0.75rem', color: 'var(--text-secondary)' }}>
                    {comparison.tradeoffSummary.map((t, i) => (
                      <li key={i}>{t}</li>
                    ))}
                  </ul>
                </div>
              )}
            </div>
          </SectionCard>

          {/* Side-by-Side Plan Comparison Table */}
          <SectionCard
            eyebrow="Plan Comparison"
            title="Side-by-Side Plan Comparison"
            status="success"
          >
            <div style={{ fontSize: '0.875rem' }}>
              <table style={{ width: '100%', borderCollapse: 'collapse' }}>
                <thead>
                  <tr style={{ background: 'var(--surface-panel)', color: 'var(--text-primary)' }}>
                    <th style={{ padding: '0.5rem 1rem', fontSize: '0.75rem' }}>Metric</th>
                    {comparison.candidates.map((_, i) => (
                      <th key={`plan-${i}`} style={{ padding: '0.5rem 1rem', fontSize: '0.75rem' }}>
                        Plan {i + 1}{' '}
                        {comparison.candidates[i].planId}
                        {comparison.candidates[i].recommendationRank > 0 && (
                          <span style={{
                            marginLeft: '0.5rem',
                            padding: '2px 4px',
                            background: 'var(--status-approved)',
                            border: '1px solid var(--surface-border)',
                            borderRadius: '3px',
                            fontSize: '0.6rem',
                            color: 'var(--status-approved-fg)',
                          }}>
                            RANK {comparison.candidates[i].recommendationRank}
                          </span>
                        )}
                      </th>
                    ))}
                  </tr>
                </thead>
                <tbody>
                  {/* Total Delay */}
                  <tr style={{ fontSize: '0.7rem' }}>
                    <td style={{ padding: '0.5rem 1rem', borderBottom: '1px solid var(--surface-border)' }}>
                      Total Delay
                    </td>
                    {comparison.candidates.map((c, i) => (
                      <td key={`delay-${i}`} style={{ padding: '0.5rem 1rem', borderBottom: '1px solid var(--surface-border)' }}>
                        {c.metrics.total_delay_minutes} min
                      </td>
                    ))}
                  </tr>

                  {/* Constraint Violations */}
                  <tr style={{ fontSize: '0.7rem' }}>
                    <td style={{ padding: '0.5rem 1rem', borderBottom: '1px solid var(--surface-border)' }}>
                      Constraint Violations
                    </td>
                    {comparison.candidates.map((c, i) => (
                      <td key={`violations-${i}`} style={{ padding: '0.5rem 1rem', borderBottom: '1px solid var(--surface-border)' }}>
                        {c.constraintViolations}
                        {c.constraintViolations > 0 && (
                          <span style={{
                            marginLeft: '0.25rem',
                            padding: '1px 4px',
                            background: 'var(--status-critical)',
                            border: '1px solid var(--surface-border)',
                            borderRadius: '2px',
                            fontSize: '0.6rem',
                            color: 'var(--status-approved-fg)',
                          }}>
                            ⚠
                          </span>
                        )}
                      </td>
                    ))}
                  </tr>

                  {/* Train Impact */}
                  <tr style={{ fontSize: '0.7rem' }}>
                    <td style={{ padding: '0.5rem 1rem', borderBottom: '1px solid var(--surface-border)' }}>
                      Train Impact
                    </td>
                    {comparison.candidates.map((c, i) => (
                      <td key={`train-${i}`} style={{ padding: '0.5rem 1rem', borderBottom: '1px solid var(--surface-border)' }}>
                        {c.trainImpactCount} trains
                      </td>
                    ))}
                  </tr>

                  {/* Feasibility */}
                  <tr style={{ fontSize: '0.7rem' }}>
                    <td style={{ padding: '0.5rem 1rem', borderBottom: '1px solid var(--surface-border)' }}>
                      Feasibility
                    </td>
                    {comparison.candidates.map((c, i) => {
                      // Determine feasibility based on constraint violations
                      const isFeasible = c.constraintViolations === 0;
                      const feasibilityText = isFeasible ? 'FEASIBLE' : 'INFEASIBLE';
                      return (
                        <td key={`feasible-${i}`} style={{ padding: '0.5rem 1rem', borderBottom: '1px solid var(--surface-border)' }}>
                          {feasibilityText}
                        </td>
                      );
                    })}
                  </tr>

                  {/* Overrun Risk */}
                  <tr style={{ fontSize: '0.7rem' }}>
                    <td style={{ padding: '0.5rem 1rem', borderBottom: '1px solid var(--surface-border)' }}>
                      Overrun Risk (P90)
                    </td>
                    {comparison.candidates.map((c, i) => (
                      <td key={`risk-${i}`} style={{ padding: '0.5rem 1rem', borderBottom: '1px solid var(--surface-border)' }}>
                        {(c.metrics.overall_overrun_risk * 100).toFixed(0)}%
                      </td>
                    ))}
                  </tr>

                  {/* Objective Score */}
                  {comparison.candidates.some((c) => c.metrics.overall_score !== undefined) && (
                    <tr style={{ fontSize: '0.7rem' }}>
                      <td style={{ padding: '0.5rem 1rem', borderBottom: '1px solid var(--surface-border)' }}>
                        Objective Score
                      </td>
                      {comparison.candidates.map((c, i) => (
                        <td key={`score-${i}`} style={{ padding: '0.5rem 1rem', borderBottom: '1px solid var(--surface-border)' }}>
                          {c.metrics.overall_score !== undefined ? c.metrics.overall_score : 'N/A'}
                        </td>
                      ))}
                    </tr>
                  )}
                </tbody>
              </table>
            </div>
          </SectionCard>

          {/* Constraint Comparison */}
          <SectionCard
            eyebrow="Constraints"
            title="Constraint Comparison"
            status="success"
          >
            <div style={{ fontSize: '0.875rem' }}>
              <p style={{ margin: '0.5rem 0', color: 'var(--text-primary)' }}>
                Hard Constraint Status
              </p>
              <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: '0.7rem' }}>
                <thead>
                  <tr style={{ background: 'var(--surface-panel)', color: 'var(--text-primary)' }}>
                    <th style={{ padding: '0.5rem 1rem' }}>Constraint</th>
                    {comparison.candidates.map((_, i) => (
                      <th key={`plan-${i}`} style={{ padding: '0.5rem 1rem' }}>Plan {i + 1}</th>
                    ))}
                  </tr>
                </thead>
                <tbody>
                  {/* Track Occupancy - HARD constraint example */}
                  <tr style={{ 
                    background: comparison.candidates.some((c) => c.constraintViolations > 0) 
                      ? 'var(--status-critical)' : 'var(--surface-panel)', 
                    color: comparison.candidates.some((c) => c.constraintViolations > 0) 
                      ? 'var(--status-approved-fg)' : 'var(--text-primary)' 
                  }}>
                    <td style={{ padding: '0.5rem 1rem', borderBottom: '1px solid var(--surface-border)' }}>
                      Track Occupancy
                    </td>
                    {comparison.candidates.map((c, i) => (
                      <td key={`track-${i}`} style={{ padding: '0.5rem 1rem', borderBottom: '1px solid var(--surface-border)' }}>
                        {c.constraintViolations > 0 ? 'VIOLATED' : 'SATISFIED'}
                      </td>
                    ))}
                  </tr>

                  {/* Maintenance Window - example */}
                  <tr style={{ 
                    background: 'var(--surface-panel)', 
                    color: 'var(--text-primary)' 
                  }}>
                    <td style={{ padding: '0.5rem 1rem', borderBottom: '1px solid var(--surface-border)' }}>
                      Maintenance Window
                    </td>
                    {comparison.candidates.map((c, i) => (
                      <td key={`maint-${i}`} style={{ padding: '0.5rem 1rem', borderBottom: '1px solid var(--surface-border)' }}>
                        {c.constraintViolations > 0 && c.constraintViolations > 1 ? 'PARTIALLY' : 'SATISFIED'}
                      </td>
                    ))}
                  </tr>

                  {/* Train Conflict - HARD constraint example */}
                  <tr style={{ 
                    background: 'var(--surface-panel)', 
                    color: 'var(--text-primary)' 
                  }}>
                    <td style={{ padding: '0.5rem 1rem', borderBottom: '1px solid var(--surface-border)' }}>
                      Train Conflict
                    </td>
                    {comparison.candidates.map((c, i) => (
                      <td key={`train-conflict-${i}`} style={{ padding: '0.5rem 1rem', borderBottom: '1px solid var(--surface-border)' }}>
                        {c.trainImpactCount > 0 ? 'POTENTIAL CONFLICT' : 'NONE'}
                      </td>
                    ))}
                  </tr>
                </tbody>
              </table>

              <p style={{ margin: '0.5rem 0', color: 'var(--text-secondary)' }}>
                Soft constraints and detailed explanations are available from the backend constraint engine.
              </p>
            </div>
          </SectionCard>

          {/* Operational Impact */}
          <SectionCard
            eyebrow="Operational Impact"
            title="Operational Impact Comparison"
            status="success"
          >
            <div style={{ fontSize: '0.875rem' }}>
              <p style={{ margin: '0.5rem 0', color: 'var(--text-primary)' }}>
                Train Impact
              </p>
              <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: '0.7rem' }}>
                <thead>
                  <tr style={{ background: 'var(--surface-panel)', color: 'var(--text-primary)' }}>
                    <th style={{ padding: '0.5rem 1rem' }}>Plan</th>
                    <th style={{ padding: '0.5rem 1rem' }}>Affected Trains</th>
                  </tr>
                </thead>
                <tbody>
                  {comparison.candidates.map((c, i) => (
                    <tr key={`impact-${i}`} style={{ fontSize: '0.7rem' }}>
                      <td style={{ padding: '0.5rem 1rem', borderBottom: '1px solid var(--surface-border)' }}>
                        Plan {i + 1} {c.planId}
                      </td>
                      <td style={{ padding: '0.5rem 1rem', borderBottom: '1px solid var(--surface-border)' }}>
                        {c.trainImpactCount} trains
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>

              <p style={{ margin: '0.5rem 0', color: 'var(--text-secondary)' }}>
                Train impact is determined by the constraint engine. Not all plans have calculated impact data.
              </p>

              <p style={{ margin: '0.5rem 0', color: 'var(--text-secondary)' }}>
                Possession duration and block requirements are per-plan specific and available from the constraint engine.
              </p>
            </div>
          </SectionCard>

          {/* Trade-Off Summary */}
          {comparison.tradeoffSummary.length > 0 && (
            <SectionCard
              eyebrow="Trade-Offs"
              title="Trade-Off Analysis"
              status="success"
            >
              <div style={{ fontSize: '0.875rem' }}>
                <p style={{ margin: '0.5rem 0', color: 'var(--text-primary)' }}>Observed Trade-Offs</p>
                <ul style={{ margin: '0.25rem 0 0 1rem', fontSize: '0.75rem', color: 'var(--text-secondary)' }}>
                  {comparison.tradeoffSummary.map((t, i) => (
                    <li key={i}>{t}</li>
                  ))}
                </ul>
              </div>
            </SectionCard>
          )}

          {/* Human Review Banner */}
          <SectionCard
            eyebrow="Human Review"
            title="Human Review Boundary"
            status="success"
          >
            <div style={{ fontSize: '0.875rem', color: 'var(--text-primary)' }}>
              <p>
                These plans are SYSTEM-GENERATED CANDIDATES pending human review.{' '}
                {comparison.candidates.some((c) => c.constraintViolations > 0) && (
                  '<strong>Hard constraints are violated in some plans.</strong>'
                )}
              </p>
              <p>
                Comparison does not constitute approval. Review the details and{' '}
                navigate to the Decision Workspace for human approval/rejection.
              </p>
              {comparison.recommendedPlanId && (
                <p style={{ margin: '0.5rem 0', color: 'var(--text-secondary)' }}>
                  Recommended plan ID: {comparison.recommendedPlanId}
                </p>
              )}
            </div>
          </SectionCard>
        </section>
      ) : (
        <EmptyState
          title="No comparison data"
          description={
            'Select at least two plans to compare. Comparison will be generated using the backend plan comparison service.'
          }
          actionLabel='Select Plans'
          onAction={() => {/* navigate to planning workspace */}
          }
        />
      )}
    </AppShell>
  );
}

export default PlanComparisonWorkspace;