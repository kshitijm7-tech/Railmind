type DecisionCardProps = {
  action: string;
  reason: string;
  impact: string;
  risk: string;
  alternatives: string;
};

export function DecisionCard({ action, reason, impact, risk, alternatives }: DecisionCardProps) {
  return (
    <article className="decision-card">
      <div className="decision-card-header">
        <div>
          <p className="eyebrow">RECOMMENDATION</p>
          <h3>{action}</h3>
        </div>
        <span className="evidence-label">Structured evidence required</span>
      </div>
      <dl className="decision-evidence">
        <Evidence term="Why" description={reason} />
        <Evidence term="Impact" description={impact} />
        <Evidence term="Risk" description={risk} />
        <Evidence term="Alternatives" description={alternatives} />
      </dl>
      <div className="decision-actions" aria-label="Decision actions unavailable until backend integration">
        <button type="button" disabled>Approve</button>
        <button type="button" disabled>Modify</button>
        <button type="button" disabled>Reject</button>
      </div>
    </article>
  );
}

function Evidence({ term, description }: { term: string; description: string }) {
  return <div><dt>{term}</dt><dd>{description}</dd></div>;
}
