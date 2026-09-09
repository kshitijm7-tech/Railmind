'use client';

import React from 'react';
import Link from 'next/link';
import { usePathname } from 'next/navigation';
import {
  LayoutDashboard,
  Activity,
  Train,
  AlertTriangle,
  Wrench,
  Calendar,
  GitCompare,
  Cpu,
  Scale,
  ShieldCheck,
  Settings,
} from 'lucide-react';

type WorkspaceGroup = {
  group: string;
  items: {
    label: string;
    href: string;
    icon: string;
    iconComponent: React.ComponentType<{ size?: number; className?: string; style?: React.CSSProperties }>;
    prominent?: boolean;
  }[];
};

export const WORKSPACE_GROUPS: WorkspaceGroup[] = [
  {
    group: 'COMMAND',
    items: [
      { label: 'Command Center', href: '/', icon: 'dashboard', iconComponent: LayoutDashboard, prominent: true },
    ]
  },
  {
    group: 'OPERATIONS',
    items: [
      { label: 'Operations', href: '/operations', icon: 'activity', iconComponent: Activity },
      { label: 'Trains & Paths', href: '/trains', icon: 'train', iconComponent: Train },
      { label: 'Disruptions & Recovery', href: '/disruptions', icon: 'disruption', iconComponent: AlertTriangle },
    ]
  },
  {
    group: 'PLANNING',
    items: [
      { label: 'Maintenance Backlog', href: '/maintenance', icon: 'maintenance', iconComponent: Wrench },
      { label: 'Block Planning (E09)', href: '/planning', icon: 'planning', iconComponent: Calendar },
      { label: 'Plan Comparison', href: '/comparison', icon: 'comparison', iconComponent: GitCompare },
      { label: 'Simulation / What-If', href: '/simulation', icon: 'simulation', iconComponent: Cpu },
    ]
  },
  {
    group: 'DECISIONS',
    items: [
      { label: 'Decisions & Approvals (P17)', href: '/decisions', icon: 'decisions', iconComponent: Scale },
    ]
  },
  {
    group: 'SYSTEM',
    items: [
      { label: 'Audit & Safety Logs', href: '/audit', icon: 'audit', iconComponent: ShieldCheck },
      { label: 'Optimization Weights', href: '/settings', icon: 'settings', iconComponent: Settings },
    ]
  }
];

export function Sidebar() {
  const pathname = usePathname();

  return (
    <aside className="app-sidebar" aria-label="Primary navigation">
      {/* Brand Header */}
      <div style={{
        padding: '1.25rem 1.25rem 1rem',
        borderBottom: '1px solid var(--surface-border)',
        background: 'linear-gradient(180deg, rgba(225, 29, 72, 0.08) 0%, transparent 100%)'
      }}>
        <Link href="/" style={{ display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
          <div style={{
            width: '2.25rem',
            height: '2.25rem',
            background: 'linear-gradient(135deg, #e11d48 0%, #be123c 100%)',
            border: '1px solid rgba(244, 63, 94, 0.5)',
            borderRadius: 'var(--radius-sm)',
            display: 'grid',
            placeItems: 'center',
            fontWeight: 800,
            color: '#ffffff',
            fontSize: '0.9rem',
            letterSpacing: '0.05em',
            boxShadow: '0 0 12px rgba(225, 29, 72, 0.35)'
          }}>
            RM
          </div>
          <div>
            <div style={{ display: 'flex', alignItems: 'center', gap: '0.4rem' }}>
              <span style={{ fontSize: '0.9rem', fontWeight: 800, letterSpacing: '0.12em', color: 'var(--text-primary)' }}>
                RAILMIND
              </span>
              <span style={{
                fontSize: '0.55rem',
                fontWeight: 700,
                padding: '0.1rem 0.35rem',
                background: 'rgba(225, 29, 72, 0.15)',
                border: '1px solid rgba(225, 29, 72, 0.4)',
                color: '#f43f5e',
                borderRadius: '3px',
                letterSpacing: '0.05em'
              }}>
                OPS
              </span>
            </div>
            <div style={{ fontSize: '0.65rem', color: 'var(--text-muted)', letterSpacing: '0.05em', marginTop: '1px' }}>
              CONTROL PLATFORM · C-07
            </div>
          </div>
        </Link>
      </div>

      {/* Navigation Groups */}
      <nav style={{ flex: 1, padding: '1rem 0.6rem', overflowY: 'auto', display: 'flex', flexDirection: 'column', gap: '1.1rem' }}>
        {WORKSPACE_GROUPS.map((group) => (
          <div key={group.group}>
            <div style={{
              fontSize: '0.62rem',
              fontWeight: 700,
              color: 'var(--text-muted)',
              letterSpacing: '0.1em',
              padding: '0 0.65rem 0.35rem',
              textTransform: 'uppercase'
            }}>
              {group.group}
            </div>
            <ul style={{ listStyle: 'none', margin: 0, padding: 0, display: 'flex', flexDirection: 'column', gap: '0.2rem' }}>
              {group.items.map((item) => {
                const isActive = pathname === item.href;
                const Icon = item.iconComponent;
                return (
                  <li key={item.href}>
                    <Link
                      href={item.href}
                      style={{
                        display: 'flex',
                        alignItems: 'center',
                        gap: '0.65rem',
                        padding: item.prominent ? '0.6rem 0.75rem' : '0.5rem 0.75rem',
                        borderRadius: 'var(--radius-sm)',
                        fontSize: '0.8rem',
                        fontWeight: isActive || item.prominent ? 600 : 500,
                        color: isActive ? '#ffffff' : (item.prominent ? 'var(--text-accent)' : 'var(--text-secondary)'),
                        backgroundColor: isActive
                          ? 'var(--surface-elevated)'
                          : (item.prominent ? 'rgba(56, 189, 248, 0.08)' : 'transparent'),
                        borderLeft: isActive
                          ? '3px solid var(--text-accent)'
                          : (item.prominent ? '3px solid rgba(56, 189, 248, 0.4)' : '3px solid transparent'),
                        borderTop: isActive ? '1px solid var(--surface-border)' : '1px solid transparent',
                        borderRight: isActive ? '1px solid var(--surface-border)' : '1px solid transparent',
                        borderBottom: isActive ? '1px solid var(--surface-border)' : '1px solid transparent',
                        transition: 'all 0.15s ease'
                      }}
                    >
                      <Icon size={item.prominent ? 17 : 15} style={{
                        color: isActive ? 'var(--text-accent)' : (item.prominent ? 'var(--text-accent)' : 'var(--text-muted)'),
                        flexShrink: 0
                      }} />
                      <span style={{ whiteSpace: 'nowrap', overflow: 'hidden', textOverflow: 'ellipsis' }}>{item.label}</span>
                    </Link>
                  </li>
                );
              })}
            </ul>
          </div>
        ))}
      </nav>

      {/* Control Room Telemetry Footer */}
      <footer style={{
        padding: '0.75rem 1rem',
        borderTop: '1px solid var(--surface-border)',
        background: 'var(--surface-subtle)',
        display: 'flex',
        flexDirection: 'column',
        gap: '0.35rem'
      }}>
        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', fontSize: '0.68rem', fontFamily: 'var(--font-mono)' }}>
          <span style={{ color: 'var(--text-muted)' }}>SOLVER</span>
          <span style={{ color: 'var(--status-normal)', fontWeight: 700, display: 'inline-flex', alignItems: 'center', gap: '4px' }}>
            <span className="radar-live-dot" /> E09 CP-SAT
          </span>
        </div>
        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', fontSize: '0.68rem', fontFamily: 'var(--font-mono)' }}>
          <span style={{ color: 'var(--text-muted)' }}>CORRIDOR</span>
          <span style={{ color: 'var(--text-secondary)' }}>C-07 (9 SECTIONS)</span>
        </div>
        <div style={{ fontSize: '0.62rem', color: 'var(--text-dim)', marginTop: '2px' }}>
          SIH26027 · Bounded Production Slice
        </div>
      </footer>
    </aside>
  );
}
