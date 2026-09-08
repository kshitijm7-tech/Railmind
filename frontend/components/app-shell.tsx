import type { ReactNode } from "react";
import { Sidebar } from "./sidebar";

type AppShellProps = { eyebrow: string; title: string; actions?: ReactNode; children: ReactNode };

export function AppShell({ eyebrow, title, actions, children }: AppShellProps) {
  return (
    <div className="app-shell">
      <Sidebar />
      <main className="main-content">
        <header className="top-bar">
          <div>
            <p className="eyebrow">{eyebrow}</p>
            <h1>{title}</h1>
          </div>
          {actions}
        </header>
        <div className="workspace">{children}</div>
      </main>
    </div>
  );
}
