'use client';

import React from 'react';
import Link from 'next/link';
import { usePathname } from 'next/navigation';

export const WORKSPACE_NAVIGATION = [
  { label: 'Command Center', href: '/', icon: '🎛️' },
  { label: 'Operations', href: '/operations', icon: '📡' },
  { label: 'Maintenance', href: '/maintenance', icon: '🔧' },
  { label: 'Block Planning', href: '/planning', icon: '📅' },
  { label: 'Trains & Paths', href: '/trains', icon: '🚆' },
  { label: 'Simulation / What-If', href: '/simulation', icon: '🧪' },
  { label: 'Disruptions & Recovery', href: '/disruptions', icon: '⚠️' },
  { label: 'Decisions & Approvals', href: '/decisions', icon: '⚖️' },
  { label: 'Audit & Safety Logs', href: '/audit', icon: '📜' },
  { label: 'Settings', href: '/settings', icon: '⚙️' },
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

      <nav style={{ flex: 1, padding: 'var(--spacing-3) var(--spacing-3)', overflowY: 'auto' }}>
        <div style={{ fontSize: '0.68rem', fontWeight: 700, color: 'var(--text-muted)', letterSpacing: '0.08em', padding: '0.5rem 0.6rem', textTransform: 'uppercase' }}>
          OPERATIONAL WORKSPACES
        </div>
        <ul style={{ listStyle: 'none', margin: 0, padding: 0, display: 'flex', flexDirection: 'column', gap: '0.15rem' }}>
          {WORKSPACE_NAVIGATION.map((item) => {
            const isActive = pathname === item.href;
            return (
              <li key={item.href}>
                <Link
                  href={item.href}
                  style={{
                    display: 'flex',
                    alignItems: 'center',
                    gap: '0.6rem',
                    padding: '0.55rem 0.75rem',
                    borderRadius: 'var(--radius-sm)',
                    fontSize: '0.82rem',
                    fontWeight: isActive ? 600 : 400,
                    color: isActive ? '#ffffff' : 'var(--text-secondary)',
                    backgroundColor: isActive ? 'var(--surface-elevated)' : 'transparent',
                    borderLeft: isActive ? '2px solid var(--text-accent)' : '2px solid transparent',
                    transition: 'all 0.15s ease'
                  }}
                >
                  <span style={{ fontSize: '0.9rem' }}>{item.icon}</span>
                  <span>{item.label}</span>
                </Link>
              </li>
            );
          })}
        </ul>
      </nav>

      <footer style={{ padding: 'var(--spacing-3) var(--spacing-4)', borderTop: '1px solid var(--surface-border)', fontSize: '0.72rem', color: 'var(--text-muted)' }}>
        <div>SIH26027 · Tier 1 Bounded Slice</div>
        <div style={{ fontSize: '0.65rem', opacity: 0.8 }}>CP-SAT Engine: Ready</div>
      </footer>
    </aside>
  );
}
