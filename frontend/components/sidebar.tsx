const navigation = [
  ["Command Center", "/"],
  ["Operations", "/operations"],
  ["Maintenance", "/maintenance/queue"],
  ["Planning", "/planning/blocks"],
  ["Simulation", "/simulation/scenarios"],
  ["Disruptions", "/disruptions/active"],
  ["Decisions", "/decisions/queue"],
  ["Audit", "/audit"],
];

export function Sidebar() {
  return (
    <aside className="sidebar" aria-label="Primary navigation">
      <Link className="brand" href="/" aria-label="RailMind Command Center">
        <span className="brand-mark" aria-hidden="true">RM</span>
        <span>RAILMIND</span>
      </Link>
      <nav>
        <p className="nav-label">WORKSPACES</p>
        <ul>
          {navigation.map(([label, href]) => (
            <li key={href}>
              <Link className={href === "/" ? "nav-link active" : "nav-link"} href={href}>
                {label}
              </Link>
            </li>
          ))}
        </ul>
      </nav>
      <footer className="sidebar-footer">Tier 1 · bounded corridor</footer>
    </aside>
  );
}
import Link from "next/link";
