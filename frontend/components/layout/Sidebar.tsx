'use client';

import React from 'react';
import Link from 'next/link';
import { usePathname } from 'next/navigation';

type WorkspaceGroup = {
  group: string;
  items: {
    label: string;
    href: string;
    icon: string;
    prominent?: boolean;
  }[];
};

export const WORKSPACE_GROUPS: WorkspaceGroup[] = [
  {
    group: 'COMMAND',
    items: [
      { label: 'Command Center', href: '/', icon: '🎛️', prominent: true },
    ]
  },
  {
    group: 'OPERATIONS',
    items: [
      { label: 'Operations', href: '/operations', icon: '📡' },
      { label: 'Trains & Paths', href: '/trains', icon: '🚆' },
      { label: 'Disruptions & Recovery', href: '/disruptions', icon: '⚠️' },
    ]
  },
  {
    group: 'PLANNING',
    items: [
      { label: 'Maintenance', href: '/maintenance', icon: '🔧' },
      { label: 'Block Planning', href: '/planning', icon: '📅' },
      { label: 'Simulation / What-If', href: '/simulation', icon: '🧪' },
    ]
  },
  {
    group: 'DECISIONS',
    items: [
      { label: 'Decisions & Approvals', href: '/decisions', icon: '⚖️' },
    ]
  },
  {
    group: 'SYSTEM',
    items: [
      { label: 'Audit & Safety Logs', href: '/audit', icon: '📜' },
      { label: 'Settings', href: '/settings', icon: '⚙️' },
    ]
  }
];

export function Sidebar() {
  const pathname = usePathname();

  return (
    <aside className="app-sidebar" aria-label="Primary navigation">
      <div style={{ padding: 'var(--spacing-4) var(--spacing-5)', borderBottom: '1px solid var(--surface-border)' }}>
        <Link href="/" style={{ display: 'flex', alignItems: 'center', gap: '0.6rem' }}>
          <div style={{ width: '2rem', height: '2rem', background: '#0284c7', border: '1px solid #38bdf8', borderRadius: 'var(--radius-sm)', display: 'grid', placeItems: 'center', fontWeight: 800, color: 'white', fontSize: '0.85rem' }}>
            RM
          </div>
          <div>
            <div style={{ fontSize: '0.85rem', fontWeight: 700, letterSpacing: '0.1em', color: 'var(--text-primary)' }}>
              RAILMIND
            </div>
            <div style={{ fontSize: '0.65rem', color: 'var(--text-muted)', letterSpacing: '0.04em' }}>
              DECISION INTELLIGENCE
            </div>
          </div>
        </Link>
      </div>

      <nav style={{ flex: 1, padding: 'var(--spacing-4) var(--spacing-3)', overflowY: 'auto', display: 'flex', flexDirection: 'column', gap: '1rem' }}>
        {WORKSPACE_GROUPS.map((group) => (
          <div key={group.group}>
            <div style={{ fontSize: '0.65rem', fontWeight: 700, color: 'var(--text-muted)', letterSpacing: '0.08em', padding: '0 0.6rem 0.4rem', textTransform: 'uppercase' }}>
              {group.group}
            </div>
            <ul style={{ listStyle: 'none', margin: 0, padding: 0, display: 'flex', flexDirection: 'column', gap: '0.15rem' }}>
              {group.items.map((item) => {
                const isActive = pathname === item.href;
                return (
                  <li key={item.href}>
                    <Link
                      href={item.href}
                      style={{
                        display: 'flex',
                        alignItems: 'center',
                        gap: '0.6rem',
                        padding: item.prominent ? '0.65rem 0.75rem' : '0.55rem 0.75rem',
                        borderRadius: 'var(--radius-sm)',
                        fontSize: '0.82rem',
                        fontWeight: isActive || item.prominent ? 600 : 400,
                        color: isActive ? '#ffffff' : (item.prominent ? 'var(--text-accent)' : 'var(--text-secondary)'),
                        backgroundColor: isActive ? 'var(--surface-elevated)' : (item.prominent ? 'rgba(2, 132, 199, 0.1)' : 'transparent'),
                        borderLeft: isActive ? '2px solid var(--text-accent)' : (item.prominent ? '2px solid rgba(2, 132, 199, 0.4)' : '2px solid transparent'),
                        transition: 'all 0.15s ease'
                      }}
                    >
                      <span style={{ fontSize: item.prominent ? '1.1rem' : '0.9rem' }}>{item.icon}</span>
                      <span>{item.label}</span>
                    </Link>
                  </li>
                );
              })}
            </ul>
          </div>
        ))}
      </nav>

      <footer style={{ padding: 'var(--spacing-3) var(--spacing-4)', borderTop: '1px solid var(--surface-border)', fontSize: '0.72rem', color: 'var(--text-muted)' }}>
        <div>SIH26027 · Tier 1 Bounded Slice</div>
        <div style={{ fontSize: '0.65rem', opacity: 0.8 }}>CP-SAT Engine: Ready</div>
      </footer>
    </aside>
  );
}
