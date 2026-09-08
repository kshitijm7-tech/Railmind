type Tone = "neutral" | "attention" | "warning" | "critical" | "approved";

export function StatusBadge({ label, tone }: { label: string; tone: Tone }) {
  return <span className={`status-badge status-${tone}`}>{label}</span>;
}
