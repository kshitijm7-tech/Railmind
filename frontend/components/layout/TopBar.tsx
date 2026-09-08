'use client';

import React from 'react';
import { useGlobalSearch } from '../../hooks/useGlobalSearch';

interface TopBarProps {
  title: string;
  eyebrow?: string;
  actions?: React.ReactNode;
}

export function TopBar({ title, eyebrow, actions }: TopBarProps) {
  const { openSearch } = useGlobalSearch();

  return (
    <header className="top-bar-container">
      <div>
        {eyebrow && (
          <div style={{ fontSize: '0.72rem', fontWeight: 700, color: 'var(--text-muted)', letterSpacing: '0.08em', textTransform: 'uppercase' }}>
            {eyebrow}
          </div>
        )}
        <h1 style={{ margin: 0, fontSize: '1.4rem', fontWeight: 700, color: 'var(--text-primary)' }}>
          {title}
        </h1>
      </div>

      <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
        <button
          onClick={openSearch}
          style={{
            display: 'flex',
            alignItems: 'center',
            gap: '0.6rem',
            background: 'var(--surface-elevated)',
            border: '1px solid var(--surface-border)',
            borderRadius: 'var(--radius-sm)',
            padding: '0.4rem 0.8rem',
            color: 'var(--text-muted)',
            fontSize: '0.78rem',
            cursor: 'pointer'
          }}
          title="Search entities across corridor"
        >
          <span>🔍 Quick Search...</span>
          <kbd style={{ background: 'var(--surface-base)', padding: '0.1rem 0.35rem', borderRadius: '3px', fontSize: '0.68rem', border: '1px solid var(--surface-border)' }}>
            Ctrl+K
          </kbd>
        </button>

        {actions}
      </div>
    </header>
  );
}
