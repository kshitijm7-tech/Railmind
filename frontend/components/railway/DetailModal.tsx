'use client';

import React from 'react';
import { X, Train, Wrench, ShieldAlert, MapPin, Calendar, CheckCircle2, Clock, Layers } from 'lucide-react';
import { Button } from '../ui/Button';

export type DetailItemType = 'train' | 'station' | 'task' | 'block' | 'section';

export interface DetailModalProps {
  isOpen: boolean;
  onClose: () => void;
  type: DetailItemType;
  data: any;
  onAction?: (action: string, payload?: any) => void;
}

export function DetailModal({ isOpen, onClose, type, data, onAction }: DetailModalProps) {
  if (!isOpen || !data) return null;

  return (
    <div
      role="dialog"
      aria-modal="true"
      style={{
        position: 'fixed',
        inset: 0,
        backgroundColor: 'rgba(7, 10, 15, 0.85)',
        backdropFilter: 'blur(6px)',
        zIndex: 1000,
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        padding: '1rem',
      }}
      onClick={onClose}
    >
      <div
        style={{
          width: '100%',
          maxWidth: '38rem',
          maxHeight: '90vh',
          backgroundColor: 'var(--surface-panel)',
          border: '1px solid var(--surface-border-strong)',
          borderRadius: 'var(--radius-md)',
          boxShadow: '0 16px 40px rgba(0, 0, 0, 0.6)',
          display: 'flex',
          flexDirection: 'column',
          overflow: 'hidden',
          animation: 'fadeIn 0.15s ease',
        }}
        onClick={(e) => e.stopPropagation()}
      >
        {/* Header */}
        <div style={{
          padding: '1rem 1.25rem',
          background: 'var(--surface-elevated)',
          borderBottom: '1px solid var(--surface-border)',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'space-between',
        }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.6rem' }}>
            {type === 'train' && <Train size={20} style={{ color: 'var(--text-accent)' }} />}
            {type === 'station' && <MapPin size={20} style={{ color: 'var(--status-normal)' }} />}
            {type === 'task' && <Wrench size={20} style={{ color: 'var(--state-prediction)' }} />}
            {type === 'block' && <Calendar size={20} style={{ color: 'var(--status-warning)' }} />}
            {type === 'section' && <Layers size={20} style={{ color: 'var(--text-accent)' }} />}

            <div>
              <span style={{ fontSize: '0.68rem', fontWeight: 700, color: 'var(--text-muted)', textTransform: 'uppercase', letterSpacing: '0.08em' }}>
                {type.toUpperCase()} INSPECTOR
              </span>
              <h3 style={{ margin: 0, fontSize: '1.05rem', color: 'var(--text-primary)', display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                {data.name || data.title || data.train_number || data.station_id || data.block_id || data.section_id}
                {data.code && <span style={{ fontSize: '0.8rem', fontFamily: 'var(--font-mono)', color: 'var(--text-secondary)' }}>({data.code})</span>}
              </h3>
            </div>
          </div>

          <button
            type="button"
            onClick={onClose}
            style={{
              background: 'transparent',
              border: 'none',
              color: 'var(--text-muted)',
              cursor: 'pointer',
              padding: '0.35rem',
              borderRadius: 'var(--radius-xs)',
              display: 'grid',
              placeItems: 'center',
            }}
            aria-label="Close modal"
          >
            <X size={18} />
          </button>
        </div>

        {/* Body */}
        <div style={{ padding: '1.25rem', overflowY: 'auto', flex: 1 }}>
          {type === 'train' && (
            <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
              <div style={{ display: 'grid', gridTemplateColumns: 'repeat(2, 1fr)', gap: '0.75rem', background: 'var(--surface-elevated)', padding: '0.85rem', borderRadius: 'var(--radius-sm)', border: '1px solid var(--surface-border)' }}>
                <div>
                  <span style={{ fontSize: '0.7rem', color: 'var(--text-muted)' }}>Train Number</span>
                  <div style={{ fontFamily: 'var(--font-mono)', fontWeight: 700, fontSize: '0.95rem' }}>{data.train_number}</div>
                </div>
                <div>
                  <span style={{ fontSize: '0.7rem', color: 'var(--text-muted)' }}>Service Type / Priority</span>
                  <div style={{ fontWeight: 600, fontSize: '0.9rem' }}>{data.train_type} · P{data.priority}</div>
                </div>
                <div>
                  <span style={{ fontSize: '0.7rem', color: 'var(--text-muted)' }}>Origin → Destination</span>
                  <div style={{ fontFamily: 'var(--font-mono)', fontSize: '0.82rem' }}>{data.origin_station_id} → {data.destination_station_id}</div>
                </div>
                <div>
                  <span style={{ fontSize: '0.7rem', color: 'var(--text-muted)' }}>Punctuality Status</span>
                  <div>
                    <span className="delay-pill" style={{
                      background: data.current_status === 'ON_TIME' ? 'rgba(16, 185, 129, 0.15)' : 'rgba(245, 158, 11, 0.15)',
                      color: data.current_status === 'ON_TIME' ? 'var(--status-normal)' : 'var(--status-warning)',
                      border: `1px solid ${data.current_status === 'ON_TIME' ? 'rgba(16, 185, 129, 0.4)' : 'rgba(245, 158, 11, 0.4)'}`,
                    }}>
                      ● {data.current_status} ({data.current_delay_min > 0 ? `+${data.current_delay_min} min` : '0 min'})
                    </span>
                  </div>
                </div>
              </div>

              <div>
                <h4 style={{ margin: '0 0 0.5rem 0', fontSize: '0.8rem', color: 'var(--text-muted)', textTransform: 'uppercase', letterSpacing: '0.06em' }}>
                  Corridor Timetable Schedule
                </h4>
                {data.schedule && data.schedule.length > 0 ? (
                  <div style={{ display: 'flex', flexDirection: 'column', gap: '0.35rem' }}>
                    {data.schedule.map((s: any, idx: number) => (
                      <div
                        key={idx}
                        style={{
                          display: 'flex',
                          alignItems: 'center',
                          justifyContent: 'space-between',
                          padding: '0.45rem 0.7rem',
                          background: 'var(--surface-elevated)',
                          border: '1px solid var(--surface-border)',
                          borderRadius: 'var(--radius-xs)',
                          fontSize: '0.75rem',
                          fontFamily: 'var(--font-mono)',
                        }}
                      >
                        <span style={{ color: 'var(--text-accent)', fontWeight: 700 }}>{s.section_id}</span>
                        <span style={{ color: 'var(--text-secondary)' }}>
                          Entry: {new Date(s.scheduled_entry).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                          {' → '}
                          Exit: {new Date(s.scheduled_exit).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                        </span>
                        <span style={{ color: s.delay_minutes > 0 ? 'var(--status-warning)' : 'var(--status-normal)' }}>
                          {s.delay_minutes > 0 ? `+${s.delay_minutes}m` : 'On Time'}
                        </span>
                      </div>
                    ))}
                  </div>
                ) : (
                  <p style={{ fontSize: '0.78rem', color: 'var(--text-secondary)' }}>No scheduled checkpoints available</p>
                )}
              </div>
            </div>
          )}

          {type === 'station' && (
            <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
              <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: '0.75rem', background: 'var(--surface-elevated)', padding: '0.85rem', borderRadius: 'var(--radius-sm)', border: '1px solid var(--surface-border)' }}>
                <div>
                  <span style={{ fontSize: '0.7rem', color: 'var(--text-muted)' }}>Station Code</span>
                  <div style={{ fontFamily: 'var(--font-mono)', fontWeight: 700, fontSize: '1rem', color: 'var(--text-accent)' }}>{data.code || data.station_id}</div>
                </div>
                <div>
                  <span style={{ fontSize: '0.7rem', color: 'var(--text-muted)' }}>Platforms</span>
                  <div style={{ fontWeight: 600, fontSize: '0.95rem' }}>{data.platforms || 4} platforms</div>
                </div>
                <div>
                  <span style={{ fontSize: '0.7rem', color: 'var(--text-muted)' }}>Station Category</span>
                  <div style={{ fontWeight: 600, fontSize: '0.85rem', color: data.is_junction ? 'var(--status-normal)' : 'var(--text-secondary)' }}>
                    {data.is_junction ? 'Junction Station' : 'Way Station'}
                  </div>
                </div>
              </div>

              <div>
                <h4 style={{ margin: '0 0 0.5rem 0', fontSize: '0.8rem', color: 'var(--text-muted)', textTransform: 'uppercase', letterSpacing: '0.06em' }}>
                  Station Operational Context
                </h4>
                <p style={{ margin: '0 0 0.75rem 0', fontSize: '0.8rem', color: 'var(--text-secondary)', lineHeight: 1.4 }}>
                  {data.name} is a key operational hub along Corridor C-07. It facilitates passenger turnarounds, OHE neutral sections, and loop line siding switches.
                </p>
                <div style={{ padding: '0.65rem 0.8rem', background: 'var(--surface-elevated)', border: '1px solid var(--surface-border)', borderRadius: 'var(--radius-xs)', fontSize: '0.75rem', color: 'var(--text-secondary)' }}>
                  Interlocking Status: <strong style={{ color: 'var(--status-normal)' }}>Electronic Interlocking (EI) Active</strong> · Loop Capacity: <strong>2 Freight Loops</strong>
                </div>
              </div>
            </div>
          )}

          {type === 'task' && (
            <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
              <div style={{ display: 'grid', gridTemplateColumns: 'repeat(2, 1fr)', gap: '0.75rem', background: 'var(--surface-elevated)', padding: '0.85rem', borderRadius: 'var(--radius-sm)', border: '1px solid var(--surface-border)' }}>
                <div>
                  <span style={{ fontSize: '0.7rem', color: 'var(--text-muted)' }}>Task ID</span>
                  <div style={{ fontFamily: 'var(--font-mono)', fontWeight: 700, fontSize: '0.9rem', color: 'var(--text-accent)' }}>{data.task_id}</div>
                </div>
                <div>
                  <span style={{ fontSize: '0.7rem', color: 'var(--text-muted)' }}>Department</span>
                  <div style={{ fontWeight: 600 }}>{data.department}</div>
                </div>
                <div>
                  <span style={{ fontSize: '0.7rem', color: 'var(--text-muted)' }}>Section / Asset</span>
                  <div style={{ fontFamily: 'var(--font-mono)', fontSize: '0.8rem' }}>{data.section_id} · {data.asset_id || 'Track'}</div>
                </div>
                <div>
                  <span style={{ fontSize: '0.7rem', color: 'var(--text-muted)' }}>Expected Duration</span>
                  <div style={{ fontWeight: 600 }}>{data.expected_duration_min || data.duration_min} min</div>
                </div>
              </div>

              <div>
                <span style={{ fontSize: '0.7rem', color: 'var(--text-muted)', textTransform: 'uppercase' }}>Scope of Work</span>
                <p style={{ margin: '0.35rem 0 0 0', fontSize: '0.82rem', color: 'var(--text-secondary)', lineHeight: 1.4 }}>
                  {data.description || data.title}
                </p>
              </div>
            </div>
          )}

          {type === 'block' && (
            <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
              <div style={{ display: 'grid', gridTemplateColumns: 'repeat(2, 1fr)', gap: '0.75rem', background: 'var(--surface-elevated)', padding: '0.85rem', borderRadius: 'var(--radius-sm)', border: '1px solid var(--surface-border)' }}>
                <div>
                  <span style={{ fontSize: '0.7rem', color: 'var(--text-muted)' }}>Block ID</span>
                  <div style={{ fontFamily: 'var(--font-mono)', fontWeight: 700, color: 'var(--text-accent)' }}>{data.block_id}</div>
                </div>
                <div>
                  <span style={{ fontSize: '0.7rem', color: 'var(--text-muted)' }}>Track Section</span>
                  <div style={{ fontFamily: 'var(--font-mono)', fontWeight: 600 }}>{data.section_id}</div>
                </div>
                <div>
                  <span style={{ fontSize: '0.7rem', color: 'var(--text-muted)' }}>Possession Duration</span>
                  <div style={{ fontWeight: 700 }}>{data.duration_min} min</div>
                </div>
                <div>
                  <span style={{ fontSize: '0.7rem', color: 'var(--text-muted)' }}>Multi-Dept Bundling</span>
                  <div style={{ color: data.is_bundled ? 'var(--status-normal)' : 'var(--text-secondary)', fontWeight: 600 }}>
                    {data.is_bundled ? '✓ Yes (Bundled)' : 'Single Dept'}
                  </div>
                </div>
              </div>

              {data.assigned_task_ids && (
                <div>
                  <span style={{ fontSize: '0.7rem', color: 'var(--text-muted)', textTransform: 'uppercase' }}>Assigned Maintenance Tasks</span>
                  <div style={{ display: 'flex', gap: '0.4rem', flexWrap: 'wrap', marginTop: '0.35rem' }}>
                    {data.assigned_task_ids.map((tid: string) => (
                      <span key={tid} style={{ padding: '2px 6px', background: 'var(--surface-elevated)', border: '1px solid var(--surface-border)', borderRadius: '3px', fontFamily: 'var(--font-mono)', fontSize: '0.72rem' }}>
                        🔧 {tid}
                      </span>
                    ))}
                  </div>
                </div>
              )}
            </div>
          )}

          {type === 'section' && (
            <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
              <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: '0.75rem', background: 'var(--surface-elevated)', padding: '0.85rem', borderRadius: 'var(--radius-sm)', border: '1px solid var(--surface-border)' }}>
                <div>
                  <span style={{ fontSize: '0.7rem', color: 'var(--text-muted)' }}>Section ID</span>
                  <div style={{ fontFamily: 'var(--font-mono)', fontWeight: 700, color: 'var(--text-accent)' }}>{data.section_id}</div>
                </div>
                <div>
                  <span style={{ fontSize: '0.7rem', color: 'var(--text-muted)' }}>Length / Tracks</span>
                  <div style={{ fontWeight: 600 }}>{data.length_km} km · {data.track_count} track(s)</div>
                </div>
                <div>
                  <span style={{ fontSize: '0.7rem', color: 'var(--text-muted)' }}>Max Speed</span>
                  <div style={{ fontFamily: 'var(--font-mono)', fontWeight: 600 }}>{data.max_speed_kmph || 110} km/h</div>
                </div>
              </div>

              <div style={{ padding: '0.75rem', background: 'var(--surface-elevated)', border: '1px solid var(--surface-border)', borderRadius: 'var(--radius-xs)', fontSize: '0.8rem' }}>
                <span style={{ color: 'var(--text-muted)' }}>End-Points:</span>{' '}
                <strong style={{ color: 'var(--text-primary)' }}>{data.from_station_id}</strong>
                {' ➔ '}
                <strong style={{ color: 'var(--text-primary)' }}>{data.to_station_id}</strong>
              </div>
            </div>
          )}
        </div>

        {/* Footer */}
        <div style={{
          padding: '0.85rem 1.25rem',
          background: 'var(--surface-elevated)',
          borderTop: '1px solid var(--surface-border)',
          display: 'flex',
          justifyContent: 'flex-end',
          gap: '0.5rem',
        }}>
          {type === 'task' && (
            <Button
              variant="primary"
              size="sm"
              onClick={() => {
                onClose();
                window.location.href = `/planning?taskId=${data.task_id}`;
              }}
            >
              ⚡ Schedule in Block Planning
            </Button>
          )}
          {type === 'train' && (
            <Button
              variant="secondary"
              size="sm"
              onClick={() => {
                onClose();
                window.location.href = `/trains?train=${data.train_number}`;
              }}
            >
              View in Train Movements
            </Button>
          )}
          <Button variant="secondary" size="sm" onClick={onClose}>
            Close
          </Button>
        </div>
      </div>
    </div>
  );
}
