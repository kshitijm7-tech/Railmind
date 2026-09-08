'use client';

import React from 'react';
import { useGlobalSearch } from '../../hooks/useGlobalSearch';
import { Bell } from 'lucide-react';

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

      <div style={{ display: 'flex', alignItems: 'center', gap: '1rem' }}>
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

        <div style={{ width: '1px', height: '20px', background: 'var(--surface-border-strong)', margin: '0 0.25rem' }} />

        <button 
          style={{ 
            background: 'transparent', 
            border: 'none', 
            color: 'var(--text-secondary)', 
            cursor: 'pointer',
            position: 'relative',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            padding: '0.25rem'
          }}
        >
          <Bell size={18} />
          <span style={{ 
            position: 'absolute', 
            top: 0, 
            right: 0, 
            width: '8px', 
            height: '8px', 
            background: 'var(--status-critical)', 
            borderRadius: '50%',
            border: '2px solid var(--surface-base)'
          }} />
        </button>

        <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', marginLeft: '0.5rem' }}>
          <div style={{ width: '32px', height: '32px', borderRadius: '50%', background: 'var(--surface-elevated)', display: 'grid', placeItems: 'center', fontSize: '0.8rem', fontWeight: 600, border: '1px solid var(--surface-border-strong)' }}>
            OC
          </div>
          <div style={{ display: 'flex', flexDirection: 'column' }}>
            <span style={{ fontSize: '0.75rem', fontWeight: 600, color: 'var(--text-primary)' }}>Operations Controller</span>
            <span style={{ fontSize: '0.65rem', color: 'var(--text-muted)' }}>Central Division</span>
          </div>
        </div>
      </div>
    </header>
  );
}
