'use client';

import React, { useState, useEffect } from 'react';
import { useGlobalSearch } from '../../hooks/useGlobalSearch';
import { Bell, Search, Radio, Cpu, Database } from 'lucide-react';

interface TopBarProps {
  title: string;
  eyebrow?: string;
  actions?: React.ReactNode;
}

export function TopBar({ title, eyebrow, actions }: TopBarProps) {
  const { openSearch } = useGlobalSearch();
  const [timeString, setTimeString] = useState<string>('');

  useEffect(() => {
    const updateTime = () => {
      const now = new Date();
      setTimeString(now.toTimeString().split(' ')[0] + ' UTC');
    };
    updateTime();
    const timer = setInterval(updateTime, 1000);
    return () => clearInterval(timer);
  }, []);

  return (
    <header className="top-bar-container">
      <div>
        {eyebrow && (
          <div style={{
            fontSize: '0.68rem',
            fontWeight: 700,
            color: 'var(--text-accent)',
            letterSpacing: '0.1em',
            textTransform: 'uppercase',
            display: 'flex',
            alignItems: 'center',
            gap: '0.4rem'
          }}>
            <span className="radar-live-dot" />
            {eyebrow}
          </div>
        )}
        <h1 style={{ margin: 0, fontSize: '1.25rem', fontWeight: 800, color: 'var(--text-primary)', letterSpacing: '0.02em' }}>
          {title}
        </h1>
      </div>

      {/* Center / Operational Telemetry Pills */}
      <div style={{ display: 'flex', alignItems: 'center', gap: '0.6rem' }}>
        <div style={{
          display: 'flex',
          alignItems: 'center',
          gap: '0.35rem',
          background: 'rgba(16, 185, 129, 0.08)',
          border: '1px solid rgba(16, 185, 129, 0.3)',
          borderRadius: 'var(--radius-xs)',
          padding: '0.2rem 0.55rem',
          fontSize: '0.68rem',
          fontFamily: 'var(--font-mono)',
          color: '#34d399',
          fontWeight: 700
        }} title="Operational status: System is actively monitoring live railway telemetry">
          <Radio size={12} className="text-emerald-400" />
          <span>OPS: ACTIVE</span>
        </div>

        <div style={{
          display: 'flex',
          alignItems: 'center',
          gap: '0.35rem',
          background: 'rgba(2, 132, 199, 0.08)',
          border: '1px solid rgba(56, 189, 248, 0.3)',
          borderRadius: 'var(--radius-xs)',
          padding: '0.2rem 0.55rem',
          fontSize: '0.68rem',
          fontFamily: 'var(--font-mono)',
          color: '#38bdf8',
          fontWeight: 700
        }} title="Engine status: E09 CP-SAT solver ready for possession scheduling">
          <Cpu size={12} />
          <span>E09 CP-SAT</span>
        </div>

        <div style={{
          display: 'flex',
          alignItems: 'center',
          gap: '0.35rem',
          background: 'var(--surface-elevated)',
          border: '1px solid var(--surface-border)',
          borderRadius: 'var(--radius-xs)',
          padding: '0.2rem 0.55rem',
          fontSize: '0.68rem',
          fontFamily: 'var(--font-mono)',
          color: 'var(--text-secondary)'
        }}>
          <Database size={12} style={{ color: 'var(--text-muted)' }} />
          <span>PORT 8000</span>
        </div>

        {timeString && (
          <div style={{
            fontSize: '0.72rem',
            fontFamily: 'var(--font-mono)',
            color: 'var(--text-primary)',
            padding: '0.2rem 0.5rem',
            background: 'var(--surface-elevated)',
            borderRadius: 'var(--radius-xs)',
            border: '1px solid var(--surface-border)'
          }}>
            {timeString}
          </div>
        )}
      </div>

      {/* Right Controls */}
      <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
        <button
          onClick={openSearch}
          style={{
            display: 'flex',
            alignItems: 'center',
            gap: '0.5rem',
            background: 'var(--surface-elevated)',
            border: '1px solid var(--surface-border)',
            borderRadius: 'var(--radius-sm)',
            padding: '0.35rem 0.75rem',
            color: 'var(--text-muted)',
            fontSize: '0.75rem',
            cursor: 'pointer',
            transition: 'border-color 0.15s ease'
          }}
          title="Search entities across corridor (Ctrl+K)"
        >
          <Search size={13} style={{ color: 'var(--text-muted)' }} />
          <span>Corridor Search...</span>
          <kbd style={{
            background: 'var(--surface-base)',
            padding: '0.1rem 0.35rem',
            borderRadius: '3px',
            fontSize: '0.65rem',
            border: '1px solid var(--surface-border)',
            color: 'var(--text-secondary)'
          }}>
            Ctrl+K
          </kbd>
        </button>

        {actions}

        <div style={{ width: '1px', height: '18px', background: 'var(--surface-border-strong)', margin: '0 0.2rem' }} />

        <button 
          style={{ 
            background: 'var(--surface-elevated)', 
            border: '1px solid var(--surface-border)', 
            color: 'var(--text-secondary)', 
            cursor: 'pointer',
            position: 'relative',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            width: '2rem',
            height: '2rem',
            borderRadius: 'var(--radius-sm)'
          }}
          title="Active Operational Notifications"
        >
          <Bell size={15} />
          <span style={{ 
            position: 'absolute', 
            top: '4px', 
            right: '4px', 
            width: '6px', 
            height: '6px', 
            background: 'var(--status-critical)', 
            borderRadius: '50%',
            border: '1px solid var(--surface-base)'
          }} />
        </button>

        <div style={{
          display: 'flex',
          alignItems: 'center',
          gap: '0.5rem',
          padding: '0.25rem 0.5rem',
          borderRadius: 'var(--radius-sm)',
          background: 'var(--surface-elevated)',
          border: '1px solid var(--surface-border)'
        }}>
          <div style={{
            width: '26px',
            height: '26px',
            borderRadius: 'var(--radius-xs)',
            background: 'linear-gradient(135deg, #0284c7 0%, #0369a1 100%)',
            display: 'grid',
            placeItems: 'center',
            fontSize: '0.72rem',
            fontWeight: 800,
            color: '#fff'
          }}>
            OC
          </div>
          <div style={{ display: 'flex', flexDirection: 'column' }}>
            <span style={{ fontSize: '0.72rem', fontWeight: 700, color: 'var(--text-primary)', lineHeight: 1.2 }}>
              Controller
            </span>
            <span style={{ fontSize: '0.62rem', color: 'var(--text-muted)', lineHeight: 1.1 }}>
              Central Div
            </span>
          </div>
        </div>
      </div>
    </header>
  );
}
