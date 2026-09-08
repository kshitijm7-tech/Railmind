'use client';

import React from 'react';
import Link from 'next/link';
import { useGlobalSearch } from '../../hooks/useGlobalSearch';

export function GlobalSearchModal() {
  const { query, setQuery, results, isSearching, isOpen, closeSearch } = useGlobalSearch();

  if (!isOpen) return null;

  return (
    <div className="modal-overlay" onClick={closeSearch}>
      <div className="command-palette" onClick={(e) => e.stopPropagation()}>
        <div style={{ display: 'flex', alignItems: 'center', padding: '0.75rem 1rem', borderBottom: '1px solid var(--surface-border)', background: 'var(--surface-elevated)' }}>
          <span style={{ marginRight: '0.5rem', color: 'var(--text-muted)' }}>🔍</span>
          <input
            type="text"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            placeholder="Search trains, maintenance tasks, assets, sections, incidents... (Esc to exit)"
            style={{
              flex: 1,
              background: 'transparent',
              border: 'none',
              color: 'var(--text-primary)',
              fontSize: '0.9rem',
              outline: 'none'
            }}
            autoFocus
          />
          {isSearching && <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>Searching...</span>}
        </div>

        <div style={{ maxHeight: '22rem', overflowY: 'auto', padding: '0.5rem' }}>
          {results.length === 0 ? (
            <div style={{ padding: '1.5rem', textAlign: 'center', color: 'var(--text-muted)', fontSize: '0.8rem' }}>
              {query.trim() === '' ? 'Type to search across the entire railway state model...' : 'No matching entities found in current corridor state.'}
            </div>
          ) : (
            <ul style={{ listStyle: 'none', margin: 0, padding: 0, display: 'flex', flexDirection: 'column', gap: '0.25rem' }}>
              {results.map((item) => (
                <li key={item.id}>
                  <Link
                    href={item.url}
                    onClick={closeSearch}
                    style={{
                      display: 'flex',
                      alignItems: 'center',
                      justifyContent: 'space-between',
                      padding: '0.6rem 0.8rem',
                      borderRadius: 'var(--radius-sm)',
                      background: 'var(--surface-panel)',
                      border: '1px solid var(--surface-border)',
                      transition: 'background 0.15s'
                    }}
                  >
                    <div>
                      <div style={{ fontWeight: 600, fontSize: '0.85rem', color: 'var(--text-primary)' }}>
                        {item.title}
                      </div>
                      <div style={{ fontSize: '0.75rem', color: 'var(--text-secondary)' }}>
                        {item.subtitle}
                      </div>
                    </div>
                    <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                      <span style={{ fontSize: '0.68rem', padding: '0.1rem 0.4rem', borderRadius: 'var(--radius-xs)', background: 'var(--surface-elevated)', color: 'var(--text-muted)', fontFamily: 'var(--font-mono)' }}>
                        {item.category}
                      </span>
                      {item.badge && (
                        <span style={{ fontSize: '0.68rem', fontWeight: 600, color: 'var(--text-accent)' }}>
                          {item.badge}
                        </span>
                      )}
                    </div>
                  </Link>
                </li>
              ))}
            </ul>
          )}
        </div>

        <div style={{ padding: '0.4rem 1rem', background: 'var(--surface-elevated)', borderTop: '1px solid var(--surface-border)', display: 'flex', justifyContent: 'space-between', fontSize: '0.7rem', color: 'var(--text-muted)' }}>
          <span>Navigation: Select to jump to operational view</span>
          <span>Shortcut: <kbd style={{ background: 'var(--surface-base)', padding: '0.1rem 0.3rem', borderRadius: '3px' }}>Ctrl + K</kbd></span>
        </div>
      </div>
    </div>
  );
}
