'use client';

import React, { useState, useMemo } from 'react';
import type { Plan, Block, TrainService } from '../../domain';
import { Clock, Layers, Calendar, CheckCircle2, AlertTriangle, Filter } from 'lucide-react';
import { DetailModal, DetailItemType } from './DetailModal';

interface RailwayGanttTimelineProps {
  plan: Plan;
  trains?: TrainService[];
  onSelectBlock?: (blockId: string) => void;
}

// 8 sections of canonical Corridor C-07 (data/railway_demo/sections.json)
const CORRIDOR_SECTIONS = [
  { id: 'SEC-01', name: 'Anandpur – Madhogarh Main', length: '34.8 km' },
  { id: 'SEC-02', name: 'Madhogarh – Khandepur Main', length: '32.4 km' },
  { id: 'SEC-03', name: 'Khandepur – Nandgaon Road Main', length: '34.3 km' },
  { id: 'SEC-04', name: 'Nandgaon Road – Vijaypur Main', length: '42.2 km' },
  { id: 'SEC-05', name: 'Vijaypur – Fatehgarh Main', length: '42.7 km' },
  { id: 'SEC-06', name: 'Khandepur – Vijaypur Freight Bypass', length: '76.5 km' },
  { id: 'SEC-07', name: 'Khandepur Loop Siding', length: '3.2 km' },
  { id: 'SEC-08', name: 'Nandgaon Road Goods Loop', length: '2.4 km' },
];

// Timeline window: 00:00 to 12:00 (12 hours / 720 minutes)
const TIMELINE_HOURS = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12];
const TOTAL_MINUTES = 720;

export function RailwayGanttTimeline({ plan, trains = [], onSelectBlock }: RailwayGanttTimelineProps) {
  const [selectedItem, setSelectedItem] = useState<{ type: DetailItemType; data: any } | null>(null);
  const [activeFilter, setActiveFilter] = useState<'ALL' | 'BLOCKS' | 'TRAINS'>('ALL');

  // Convert an ISO or HH:MM time to minutes from 00:00
  const parseTimeToMinutes = (timeStr?: string): number => {
    if (!timeStr) return 0;
    try {
      const date = new Date(timeStr);
      if (!isNaN(date.getTime())) {
        return date.getUTCHours() * 60 + date.getUTCMinutes();
      }
      const parts = timeStr.split(':');
      if (parts.length >= 2) {
        return parseInt(parts[0], 10) * 60 + parseInt(parts[1], 10);
      }
    } catch {
      return 0;
    }
    return 0;
  };

  // Process blocks
  const blocksBySection = useMemo(() => {
    const map: Record<string, Block[]> = {};
    (plan.blocks || []).forEach(b => {
      if (!map[b.section_id]) map[b.section_id] = [];
      map[b.section_id].push(b);
    });
    return map;
  }, [plan.blocks]);

  // Process train paths per section
  const trainOccupanciesBySection = useMemo(() => {
    const map: Record<string, Array<{ train: TrainService; startMin: number; endMin: number }>> = {};
    trains.forEach(trn => {
      (trn.schedule || []).forEach(sched => {
        const startMin = parseTimeToMinutes(sched.scheduled_entry);
        const endMin = parseTimeToMinutes(sched.scheduled_exit) || (startMin + 25);
        if (!map[sched.section_id]) map[sched.section_id] = [];
        map[sched.section_id].push({ train: trn, startMin, endMin });
      });
    });
    return map;
  }, [trains]);

  const handleBlockClick = (b: Block) => {
    setSelectedItem({ type: 'block', data: b });
    if (onSelectBlock) onSelectBlock(b.block_id);
  };

  const handleTrainClick = (trn: TrainService) => {
    setSelectedItem({ type: 'train', data: trn });
  };

  return (
    <div style={{
      background: 'var(--surface-elevated)',
      border: '1px solid var(--surface-border)',
      borderRadius: 'var(--radius-md)',
      overflow: 'hidden',
    }}>
      {/* Header bar */}
      <div style={{
        padding: '0.85rem 1.25rem',
        background: 'rgba(15, 23, 42, 0.85)',
        borderBottom: '1px solid var(--surface-border)',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'space-between',
        flexWrap: 'wrap',
        gap: '0.75rem',
      }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
          <div style={{
            width: '28px',
            height: '28px',
            borderRadius: 'var(--radius-xs)',
            background: 'rgba(56, 189, 248, 0.15)',
            border: '1px solid rgba(56, 189, 248, 0.3)',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            color: 'var(--text-accent)',
          }}>
            <Clock size={16} />
          </div>
          <div>
            <div style={{ fontSize: '0.68rem', fontFamily: 'var(--font-mono)', color: 'var(--text-muted)', textTransform: 'uppercase', letterSpacing: '0.08em' }}>
              TIME-SPACE CORRIDOR SCHEDULE (GANTT)
            </div>
            <div style={{ fontSize: '0.92rem', fontWeight: 700, color: 'var(--text-primary)' }}>
              Possession Plan: {plan.plan_id} · {plan.strategy}
            </div>
          </div>
        </div>

        {/* Layer Filters & Legend */}
        <div style={{ display: 'flex', alignItems: 'center', gap: '1rem', flexWrap: 'wrap' }}>
          <div style={{
            display: 'flex',
            background: 'var(--surface-panel)',
            padding: '2px',
            borderRadius: 'var(--radius-xs)',
            border: '1px solid var(--surface-border)',
            gap: '2px',
          }}>
            {(['ALL', 'BLOCKS', 'TRAINS'] as const).map(filter => (
              <button
                key={filter}
                type="button"
                onClick={() => setActiveFilter(filter)}
                style={{
                  padding: '3px 8px',
                  fontSize: '0.7rem',
                  fontWeight: 600,
                  border: 'none',
                  borderRadius: 'var(--radius-xs)',
                  cursor: 'pointer',
                  background: activeFilter === filter ? 'var(--surface-elevated)' : 'transparent',
                  color: activeFilter === filter ? 'var(--text-accent)' : 'var(--text-secondary)',
                }}
              >
                {filter}
              </button>
            ))}
          </div>

          <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem', fontSize: '0.7rem', color: 'var(--text-secondary)' }}>
            <span style={{ display: 'flex', alignItems: 'center', gap: '4px' }}>
              <span style={{ width: '12px', height: '8px', background: 'rgba(239, 68, 68, 0.4)', border: '1px solid var(--status-critical)', borderRadius: '2px' }} />
              Possession Block
            </span>
            <span style={{ display: 'flex', alignItems: 'center', gap: '4px' }}>
              <span style={{ width: '12px', height: '8px', background: 'rgba(56, 189, 248, 0.4)', border: '1px solid var(--text-accent)', borderRadius: '2px' }} />
              Train Path
            </span>
          </div>
        </div>
      </div>

      {/* Gantt Chart Container */}
      <div style={{ overflowX: 'auto', background: '#070b12' }}>
        <div style={{ minWidth: '860px', padding: '0.75rem 1rem' }}>
          {/* Time axis header */}
          <div style={{ display: 'flex', borderBottom: '1px solid var(--surface-border-strong)', paddingBottom: '0.5rem', marginBottom: '0.5rem' }}>
            <div style={{ width: '180px', flexShrink: 0, fontSize: '0.72rem', color: 'var(--text-muted)', fontFamily: 'var(--font-mono)', fontWeight: 700 }}>
              SECTION ID
            </div>
            <div style={{ flex: 1, display: 'flex', position: 'relative' }}>
              {TIMELINE_HOURS.map(h => (
                <div
                  key={h}
                  style={{
                    flex: 1,
                    textAlign: 'left',
                    fontSize: '0.68rem',
                    fontFamily: 'var(--font-mono)',
                    color: 'var(--text-muted)',
                    borderLeft: '1px dashed rgba(255, 255, 255, 0.08)',
                    paddingLeft: '4px',
                  }}
                >
                  {String(h).padStart(2, '0')}:00
                </div>
              ))}
            </div>
          </div>

          {/* Section rows */}
          {CORRIDOR_SECTIONS.map((sec, idx) => {
            const secBlocks = blocksBySection[sec.id] || [];
            const secTrains = trainOccupanciesBySection[sec.id] || [];

            return (
              <div
                key={sec.id}
                style={{
                  display: 'flex',
                  alignItems: 'center',
                  minHeight: '44px',
                  borderBottom: '1px solid rgba(255, 255, 255, 0.04)',
                  background: idx % 2 === 0 ? 'rgba(15, 23, 42, 0.25)' : 'transparent',
                }}
              >
                {/* Section label */}
                <div style={{ width: '180px', flexShrink: 0, paddingRight: '0.5rem' }}>
                  <div style={{ fontFamily: 'var(--font-mono)', fontSize: '0.75rem', fontWeight: 700, color: 'var(--text-primary)' }}>
                    {sec.id}
                  </div>
                  <div style={{ fontSize: '0.68rem', color: 'var(--text-secondary)', whiteSpace: 'nowrap', overflow: 'hidden', textOverflow: 'ellipsis' }}>
                    {sec.name}
                  </div>
                </div>

                {/* Timeline track for section */}
                <div style={{ flex: 1, height: '36px', position: 'relative', background: 'rgba(0, 0, 0, 0.3)', borderRadius: '3px', border: '1px solid rgba(255, 255, 255, 0.05)' }}>
                  {/* Grid hour marks */}
                  {TIMELINE_HOURS.map(h => (
                    <div
                      key={h}
                      style={{
                        position: 'absolute',
                        left: `${(h / 12) * 100}%`,
                        top: 0,
                        bottom: 0,
                        width: '1px',
                        borderLeft: '1px dashed rgba(255, 255, 255, 0.04)',
                        pointerEvents: 'none',
                      }}
                    />
                  ))}

                  {/* Render Planned Maintenance Blocks */}
                  {(activeFilter === 'ALL' || activeFilter === 'BLOCKS') && secBlocks.map((b) => {
                    const startMin = parseTimeToMinutes(b.start_time) || (b.duration_min > 120 ? 120 : 180);
                    const dur = b.duration_min || 180;
                    const leftPct = Math.max(0, Math.min(100, (startMin / TOTAL_MINUTES) * 100));
                    const widthPct = Math.max(2, Math.min(100 - leftPct, (dur / TOTAL_MINUTES) * 100));

                    return (
                      <div
                        key={b.block_id}
                        onClick={() => handleBlockClick(b)}
                        title={`Block ${b.block_id}: ${dur} min (${b.status})`}
                        style={{
                          position: 'absolute',
                          left: `${leftPct}%`,
                          width: `${widthPct}%`,
                          top: '4px',
                          bottom: '4px',
                          background: 'rgba(239, 68, 68, 0.25)',
                          border: '1.5px solid #ef4444',
                          borderRadius: '3px',
                          display: 'flex',
                          alignItems: 'center',
                          padding: '0 6px',
                          fontSize: '0.68rem',
                          fontFamily: 'var(--font-mono)',
                          color: '#fca5a5',
                          cursor: 'pointer',
                          boxShadow: '0 2px 8px rgba(239, 68, 68, 0.3)',
                          zIndex: 2,
                          overflow: 'hidden',
                          whiteSpace: 'nowrap',
                        }}
                      >
                        <span style={{ fontWeight: 700 }}>🚧 {b.block_id}</span>
                        <span style={{ marginLeft: '4px', opacity: 0.85 }}>({dur}m)</span>
                      </div>
                    );
                  })}

                  {/* Render Train Paths */}
                  {(activeFilter === 'ALL' || activeFilter === 'TRAINS') && secTrains.map((to, tIdx) => {
                    const leftPct = Math.max(0, Math.min(100, (to.startMin / TOTAL_MINUTES) * 100));
                    const dur = Math.max(15, to.endMin - to.startMin);
                    const widthPct = Math.max(2, Math.min(100 - leftPct, (dur / TOTAL_MINUTES) * 100));

                    return (
                      <div
                        key={`${to.train.train_id}-${tIdx}`}
                        onClick={() => handleTrainClick(to.train)}
                        title={`Train ${to.train.train_number} (${to.train.name})`}
                        style={{
                          position: 'absolute',
                          left: `${leftPct}%`,
                          width: `${widthPct}%`,
                          top: '18px',
                          bottom: '3px',
                          background: 'rgba(56, 189, 248, 0.2)',
                          border: '1px solid #38bdf8',
                          borderRadius: '2px',
                          display: 'flex',
                          alignItems: 'center',
                          padding: '0 4px',
                          fontSize: '0.62rem',
                          fontFamily: 'var(--font-mono)',
                          color: '#bae6fd',
                          cursor: 'pointer',
                          zIndex: 3,
                          overflow: 'hidden',
                          whiteSpace: 'nowrap',
                        }}
                      >
                        🚆 {to.train.train_number}
                      </div>
                    );
                  })}
                </div>
              </div>
            );
          })}
        </div>
      </div>

      {/* Footer information */}
      <div style={{
        padding: '0.6rem 1.25rem',
        background: 'rgba(15, 23, 42, 0.5)',
        borderTop: '1px solid var(--surface-border)',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'space-between',
        fontSize: '0.72rem',
        color: 'var(--text-secondary)',
      }}>
        <div style={{ display: 'flex', gap: '1.25rem' }}>
          <span>Horizon: <strong>12 Hours (00:00 – 12:00)</strong></span>
          <span>Solver: <strong>CP-SAT (E09) Headway & Overlap Verified</strong></span>
        </div>
        <div style={{ color: 'var(--text-muted)' }}>
          Click any block or train to view scheduling parameters
        </div>
      </div>

      {/* Detail Modal */}
      {selectedItem && (
        <DetailModal
          isOpen={true}
          onClose={() => setSelectedItem(null)}
          type={selectedItem.type}
          data={selectedItem.data}
          onAction={(action, payload) => {
            if (action === 'simulate_plan') {
              window.location.href = `/simulation?planId=${plan.plan_id}`;
            }
          }}
        />
      )}
    </div>
  );
}
