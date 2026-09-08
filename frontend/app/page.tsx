import { DecisionCard } from "../components/decision-card";
import { AppShell } from "../components/app-shell";
import { StatusBadge } from "../components/status-badge";

export default function CommandCenterPage() {
  return (
    <AppShell
      eyebrow="Corridor C-07 · next 72 hours"
      title="Command Center"
      actions={<StatusBadge label="OFFLINE FOUNDATION" tone="neutral" />}
    >
      <section className="workspace-intro" aria-labelledby="workspace-status">
        <p className="eyebrow">P01 FRONTEND FOUNDATION</p>
        <h2 id="workspace-status">The decision workspace is ready for its first contract.</h2>
        <p>
          Operational data, recommendations, scenarios, and approvals will be supplied by
          later backend phases. This UI intentionally does not simulate or calculate them.
        </p>
      </section>

      <section className="metric-grid" aria-label="Operational state placeholders">
        <Metric label="Active alerts" value="—" detail="Event contract pending" />
        <Metric label="Pending decisions" value="—" detail="Recommendation contract pending" />
        <Metric label="Network availability" value="—" detail="State contract pending" />
      </section>

      <section aria-labelledby="decision-heading">
        <div className="section-heading">
          <div>
            <p className="eyebrow">ATTENTION QUEUE</p>
            <h2 id="decision-heading">Decision workspace</h2>
          </div>
          <StatusBadge label="AWAITING API" tone="attention" />
        </div>
        <DecisionCard
          action="No recommendation is available yet"
          reason="The frontend is awaiting the canonical Recommendation API contract."
          impact="This component will expose the optimiser’s expected operational impact."
          risk="Risk and confidence will be rendered from backend evidence, not invented in the UI."
          alternatives="Alternative plans will be supplied as structured recommendation data."
        />
      </section>
    </AppShell>
  );
}

function Metric({ label, value, detail }: { label: string; value: string; detail: string }) {
  return (
    <article className="metric-card">
      <p>{label}</p>
      <strong>{value}</strong>
      <span>{detail}</span>
    </article>
  );
}
