'use client';

import React, { useState } from 'react';
import type { Section, Station, TrainService, MaintenanceTask } from '../../domain';
import { DetailModal, DetailItemType } from './DetailModal';
import { Layers, Train, Wrench, AlertTriangle, CheckCircle2, ChevronRight } from 'lucide-react';

interface RailwayNetworkSchematicProps {
  corridorName: string;
  stations?: Station[];
  sections: Section[];
  trains?: TrainService[];
  tasks?: MaintenanceTask[];
  onSelectSection?: (sectionId: string) => void;
  onSelectStation?: (stationId: string) => void;
}

// Station coordinate layout along the schematic line (X coordinates across 1000px canvas)
const STATION_COORDS: Record<string, { x: number; y: number; code: string; name: string }> = {
  'STN-A': { x: 80, y: 130, code: 'ANPT', name: 'Anandpur Terminal' },
  'STN-B': { x: 250, y: 130, code: 'BPLJ', name: 'Bhopal Junction' },
  'STN-C': { x: 440, y: 130, code: 'CHTP', name: 'Chhatarpur' },
  'STN-D': { x: 620, y: 130, code: 'DVPS', name: 'Devpuri South' },
  'STN-E': { x: 800, y: 130, code: 'EKTN', name: 'Ekta Nagar' },
  'STN-F': { x: 950, y: 130, code: 'FTHC', name: 'Fatehgarh Central' },
};

export function RailwayNetworkSchematic({
  corridorName,
  stations,
  sections,
  trains = [],
  tasks = [],
  onSelectSection,
  onSelectStation,
}: RailwayNetworkSchematicProps) {
  const [selectedItem, setSelectedItem] = useState<{ type: DetailItemType; data: any } | null>(null);
  const [hoveredElement, setHoveredElement] = useState<string | null>(null);

  // Group sections by their roles
  const mainlineSections = sections.filter(s => s.section_id !== 'SEC-07' && s.section_id !== 'SEC-08');
  const sidingSection = sections.find(s => s.section_id === 'SEC-07');
  const bypassSection = sections.find(s => s.section_id === 'SEC-08');

  // Find active tasks / blocks per section
  const tasksBySection = React.useMemo(() => {
    const map: Record<string, MaintenanceTask[]> = {};
    tasks.forEach(t => {
      if (!map[t.section_id]) map[t.section_id] = [];
      map[t.section_id].push(t);
    });
    return map;
  }, [tasks]);

  const handleStationClick = (stnId: string) => {
    const stn = stations?.find(s => s.station_id === stnId) || {
      station_id: stnId,
      name: STATION_COORDS[stnId]?.name || stnId,
      code: STATION_COORDS[stnId]?.code || stnId,
      platforms: 4,
      tracks: 6,
      is_junction: stnId === 'STN-A' || stnId === 'STN-B' || stnId === 'STN-F',
    };
    setSelectedItem({ type: 'station', data: stn });
    if (onSelectStation) onSelectStation(stnId);
  };

  const handleSectionClick = (sec: Section) => {
    setSelectedItem({ type: 'section', data: sec });
    if (onSelectSection) onSelectSection(sec.section_id);
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
      position: 'relative',
    }}>
      {/* Schematic Header Bar */}
      <div style={{
        padding: '0.75rem 1.25rem',
        background: 'rgba(15, 23, 42, 0.75)',
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
            <Layers size={16} />
          </div>
          <div>
            <div style={{ fontSize: '0.68rem', fontFamily: 'var(--font-mono)', color: 'var(--text-muted)', textTransform: 'uppercase', letterSpacing: '0.08em' }}>
              INTERACTIVE SYNOPTIC SCHEMATIC
            </div>
            <div style={{ fontSize: '0.92rem', fontWeight: 700, color: 'var(--text-primary)' }}>
              {corridorName}
            </div>
          </div>
        </div>

        {/* Legend */}
        <div style={{ display: 'flex', alignItems: 'center', gap: '1rem', fontSize: '0.72rem', color: 'var(--text-secondary)' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '5px' }}>
            <span style={{ width: '10px', height: '10px', borderRadius: '50%', background: 'var(--status-normal)' }} />
            <span>Station</span>
          </div>
          <div style={{ display: 'flex', alignItems: 'center', gap: '5px' }}>
            <span style={{ width: '14px', height: '3px', background: 'var(--status-normal)' }} />
            <span>Clear Track</span>
          </div>
          <div style={{ display: 'flex', alignItems: 'center', gap: '5px' }}>
            <span style={{ width: '14px', height: '3px', background: 'var(--status-warning)', borderTop: '2px dashed var(--status-warning)' }} />
            <span>Restricted/Siding</span>
          </div>
          <div style={{ display: 'flex', alignItems: 'center', gap: '5px' }}>
            <span style={{ width: '14px', height: '3px', background: 'var(--status-critical)' }} />
            <span>Maintenance Block</span>
          </div>
          <div style={{ display: 'flex', alignItems: 'center', gap: '5px' }}>
            <span style={{ fontSize: '0.75rem' }}>🚆</span>
            <span>Live Train</span>
          </div>
        </div>
      </div>

      {/* SVG Canvas */}
      <div style={{ width: '100%', overflowX: 'auto', background: '#070b12', padding: '1rem 0' }}>
        <svg
          viewBox="0 0 1020 250"
          style={{ width: '100%', minWidth: '780px', height: 'auto', display: 'block' }}
        >
          <defs>
            <linearGradient id="trackGrad" x1="0%" y1="0%" x2="100%" y2="0%">
              <stop offset="0%" stopColor="#0284c7" />
              <stop offset="50%" stopColor="#38bdf8" />
              <stop offset="100%" stopColor="#0284c7" />
            </linearGradient>
            <filter id="glow" x="-20%" y="-20%" width="140%" height="140%">
              <feGaussianBlur stdDeviation="3" result="blur" />
              <feComposite in="SourceGraphic" in2="blur" operator="over" />
            </filter>
          </defs>

          {/* Grid lines in background */}
          <g stroke="rgba(255,255,255,0.03)" strokeWidth="1">
            <line x1="0" y1="50" x2="1020" y2="50" />
            <line x1="0" y1="130" x2="1020" y2="130" />
            <line x1="0" y1="210" x2="1020" y2="210" />
          </g>

          {/* Siding Loop Curve: STN-B (250, 130) -> Upper Arc -> STN-C (440, 130) (SEC-07) */}
          {sidingSection && (
            <g
              onClick={() => handleSectionClick(sidingSection)}
              onMouseEnter={() => setHoveredElement('SEC-07')}
              onMouseLeave={() => setHoveredElement(null)}
              style={{ cursor: 'pointer' }}
            >
              <path
                d="M 250 130 C 290 60, 400 60, 440 130"
                fill="none"
                stroke={hoveredElement === 'SEC-07' ? '#fbbf24' : '#d97706'}
                strokeWidth={hoveredElement === 'SEC-07' ? '4' : '2.5'}
                strokeDasharray="4 3"
              />
              <text x="345" y="65" fill="#fbbf24" fontSize="10" fontFamily="var(--font-mono)" textAnchor="middle" fontWeight="bold">
                SEC-07 (Loop 60km/h)
              </text>
            </g>
          )}

          {/* Goods Bypass: STN-C (440, 130) -> Lower Arc -> STN-E (800, 130) (SEC-08) */}
          {bypassSection && (
            <g
              onClick={() => handleSectionClick(bypassSection)}
              onMouseEnter={() => setHoveredElement('SEC-08')}
              onMouseLeave={() => setHoveredElement(null)}
              style={{ cursor: 'pointer' }}
            >
              <path
                d="M 440 130 C 520 220, 720 220, 800 130"
                fill="none"
                stroke={hoveredElement === 'SEC-08' ? '#38bdf8' : '#0284c7'}
                strokeWidth={hoveredElement === 'SEC-08' ? '4' : '2.5'}
                strokeDasharray="5 3"
              />
              <text x="620" y="215" fill="#38bdf8" fontSize="10" fontFamily="var(--font-mono)" textAnchor="middle" fontWeight="bold">
                SEC-08 (Goods Bypass 42km)
              </text>
            </g>
          )}

          {/* Mainline Segments */}
          {/* SEC-01 & SEC-02: STN-A to STN-B */}
          {(() => {
            const sec1 = sections.find(s => s.section_id === 'SEC-01');
            const hasBlock = (tasksBySection['SEC-01']?.length ?? 0) > 0 || (tasksBySection['SEC-02']?.length ?? 0) > 0;
            const strokeColor = hasBlock ? '#ef4444' : hoveredElement === 'SEC-01' ? '#38bdf8' : '#10b981';
            return (
              <g
                onClick={() => sec1 && handleSectionClick(sec1)}
                onMouseEnter={() => setHoveredElement('SEC-01')}
                onMouseLeave={() => setHoveredElement(null)}
                style={{ cursor: 'pointer' }}
              >
                {/* Up track */}
                <line x1="80" y1="126" x2="250" y2="126" stroke={strokeColor} strokeWidth={hoveredElement === 'SEC-01' ? '4' : '3'} />
                {/* Down track */}
                <line x1="80" y1="134" x2="250" y2="134" stroke={strokeColor} strokeWidth={hoveredElement === 'SEC-01' ? '4' : '3'} />
                <rect x="135" y="105" width="60" height="16" rx="3" fill="#0f172a" stroke={strokeColor} strokeWidth="1" />
                <text x="165" y="117" fill="#cbd5e1" fontSize="9" fontFamily="var(--font-mono)" textAnchor="middle">
                  SEC-01/02
                </text>
              </g>
            );
          })()}

          {/* SEC-03: STN-B to STN-C */}
          {(() => {
            const sec = sections.find(s => s.section_id === 'SEC-03');
            const hasBlock = (tasksBySection['SEC-03']?.length ?? 0) > 0;
            const strokeColor = hasBlock ? '#ef4444' : hoveredElement === 'SEC-03' ? '#38bdf8' : '#10b981';
            return (
              <g
                onClick={() => sec && handleSectionClick(sec)}
                onMouseEnter={() => setHoveredElement('SEC-03')}
                onMouseLeave={() => setHoveredElement(null)}
                style={{ cursor: 'pointer' }}
              >
                <line x1="250" y1="130" x2="440" y2="130" stroke={strokeColor} strokeWidth={hoveredElement === 'SEC-03' ? '4' : '3'} />
                <rect x="315" y="142" width="60" height="16" rx="3" fill="#0f172a" stroke={strokeColor} strokeWidth="1" />
                <text x="345" y="154" fill="#cbd5e1" fontSize="9" fontFamily="var(--font-mono)" textAnchor="middle">
                  SEC-03 Main
                </text>
              </g>
            );
          })()}

          {/* SEC-04: STN-C to STN-D (Crucial single-line section, often has maintenance) */}
          {(() => {
            const sec = sections.find(s => s.section_id === 'SEC-04');
            const hasBlock = (tasksBySection['SEC-04']?.length ?? 0) > 0;
            const strokeColor = hasBlock ? '#ef4444' : hoveredElement === 'SEC-04' ? '#38bdf8' : '#f59e0b';
            return (
              <g
                onClick={() => sec && handleSectionClick(sec)}
                onMouseEnter={() => setHoveredElement('SEC-04')}
                onMouseLeave={() => setHoveredElement(null)}
                style={{ cursor: 'pointer' }}
              >
                <line x1="440" y1="130" x2="620" y2="130" stroke={strokeColor} strokeWidth={hoveredElement === 'SEC-04' ? '5' : '3.5'} strokeDasharray={hasBlock ? '6 3' : 'none'} />
                <rect x="495" y="105" width="70" height="18" rx="3" fill="#0f172a" stroke={strokeColor} strokeWidth="1.5" />
                <text x="530" y="118" fill={hasBlock ? '#ef4444' : '#cbd5e1'} fontSize="9" fontWeight="bold" fontFamily="var(--font-mono)" textAnchor="middle">
                  {hasBlock ? '⚠ SEC-04 (BLOCKED)' : 'SEC-04 Single'}
                </text>
              </g>
            );
          })()}

          {/* SEC-05: STN-D to STN-E */}
          {(() => {
            const sec = sections.find(s => s.section_id === 'SEC-05');
            const hasBlock = (tasksBySection['SEC-05']?.length ?? 0) > 0;
            const strokeColor = hasBlock ? '#ef4444' : hoveredElement === 'SEC-05' ? '#38bdf8' : '#10b981';
            return (
              <g
                onClick={() => sec && handleSectionClick(sec)}
                onMouseEnter={() => setHoveredElement('SEC-05')}
                onMouseLeave={() => setHoveredElement(null)}
                style={{ cursor: 'pointer' }}
              >
                <line x1="620" y1="126" x2="800" y2="126" stroke={strokeColor} strokeWidth={hoveredElement === 'SEC-05' ? '4' : '3'} />
                <line x1="620" y1="134" x2="800" y2="134" stroke={strokeColor} strokeWidth={hoveredElement === 'SEC-05' ? '4' : '3'} />
                <rect x="680" y="142" width="60" height="16" rx="3" fill="#0f172a" stroke={strokeColor} strokeWidth="1" />
                <text x="710" y="154" fill="#cbd5e1" fontSize="9" fontFamily="var(--font-mono)" textAnchor="middle">
                  SEC-05 Chord
                </text>
              </g>
            );
          })()}

          {/* SEC-06 & SEC-09: STN-E to STN-F */}
          {(() => {
            const sec = sections.find(s => s.section_id === 'SEC-06');
            const hasBlock = (tasksBySection['SEC-06']?.length ?? 0) > 0 || (tasksBySection['SEC-09']?.length ?? 0) > 0;
            const strokeColor = hasBlock ? '#ef4444' : hoveredElement === 'SEC-06' ? '#38bdf8' : '#10b981';
            return (
              <g
                onClick={() => sec && handleSectionClick(sec)}
                onMouseEnter={() => setHoveredElement('SEC-06')}
                onMouseLeave={() => setHoveredElement(null)}
                style={{ cursor: 'pointer' }}
              >
                <line x1="800" y1="126" x2="950" y2="126" stroke={strokeColor} strokeWidth={hoveredElement === 'SEC-06' ? '4' : '3'} />
                <line x1="800" y1="134" x2="950" y2="134" stroke={strokeColor} strokeWidth={hoveredElement === 'SEC-06' ? '4' : '3'} />
                <rect x="845" y="105" width="60" height="16" rx="3" fill="#0f172a" stroke={strokeColor} strokeWidth="1" />
                <text x="875" y="117" fill="#cbd5e1" fontSize="9" fontFamily="var(--font-mono)" textAnchor="middle">
                  SEC-06/09
                </text>
              </g>
            );
          })()}

          {/* Live Train Badges on Sections */}
          {trains.map((trn, idx) => {
            // Position trains near their active sections
            let tx = 165;
            let ty = 118;
            if (trn.train_number === '12001') {
              tx = 345;
              ty = 118;
            } else if (trn.train_number === '12952') {
              tx = 710;
              ty = 118;
            } else if (trn.train_id.includes('GOODS')) {
              tx = 620;
              ty = 195;
            } else {
              tx = 160 + (idx * 140);
              ty = 120;
            }

            return (
              <g
                key={trn.train_id}
                onClick={() => handleTrainClick(trn)}
                onMouseEnter={() => setHoveredElement(trn.train_id)}
                onMouseLeave={() => setHoveredElement(null)}
                style={{ cursor: 'pointer' }}
              >
                <circle cx={tx} cy={ty} r="12" fill="#1e293b" stroke={trn.current_delay_min > 0 ? '#ef4444' : '#38bdf8'} strokeWidth="2" filter="url(#glow)" />
                <text x={tx} y={ty + 4} fill="#f8fafc" fontSize="10" textAnchor="middle">
                  🚆
                </text>
                <rect x={tx - 32} y={ty - 26} width="64" height="14" rx="3" fill="rgba(15, 23, 42, 0.9)" stroke="rgba(56, 189, 248, 0.4)" strokeWidth="1" />
                <text x={tx} y={ty - 16} fill="#38bdf8" fontSize="8" fontWeight="bold" fontFamily="var(--font-mono)" textAnchor="middle">
                  #{trn.train_number}
                </text>
              </g>
            );
          })}

          {/* Stations (Nodes) */}
          {Object.entries(STATION_COORDS).map(([stnId, coord]) => {
            const isHovered = hoveredElement === stnId;
            return (
              <g
                key={stnId}
                onClick={() => handleStationClick(stnId)}
                onMouseEnter={() => setHoveredElement(stnId)}
                onMouseLeave={() => setHoveredElement(null)}
                style={{ cursor: 'pointer' }}
              >
                {/* Outer halo */}
                <circle
                  cx={coord.x}
                  cy={coord.y}
                  r={isHovered ? 16 : 12}
                  fill="#0f172a"
                  stroke={isHovered ? '#38bdf8' : '#10b981'}
                  strokeWidth={isHovered ? 3 : 2}
                  filter="url(#glow)"
                />
                {/* Center dot */}
                <circle cx={coord.x} cy={coord.y} r="5" fill={isHovered ? '#38bdf8' : '#10b981'} />
                
                {/* Station Code Badge */}
                <text
                  x={coord.x}
                  y={coord.y - 18}
                  fill={isHovered ? '#38bdf8' : '#f8fafc'}
                  fontSize="11"
                  fontWeight="bold"
                  fontFamily="var(--font-mono)"
                  textAnchor="middle"
                >
                  {coord.code}
                </text>
                {/* Station Full Name */}
                <text
                  x={coord.x}
                  y={coord.y + 24}
                  fill="#94a3b8"
                  fontSize="9"
                  textAnchor="middle"
                >
                  {coord.name}
                </text>
              </g>
            );
          })}
        </svg>
      </div>

      {/* Quick stats strip below SVG */}
      <div style={{
        padding: '0.6rem 1.25rem',
        background: 'rgba(15, 23, 42, 0.5)',
        borderTop: '1px solid var(--surface-border)',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'space-between',
        fontSize: '0.75rem',
        color: 'var(--text-secondary)',
      }}>
        <div style={{ display: 'flex', gap: '1.25rem' }}>
          <span>Topology: <strong>6 Interlocking Stations</strong></span>
          <span>Corridor Length: <strong>166.5 km</strong></span>
          <span>Tracks: <strong>Double with Chord & Goods Bypass</strong></span>
        </div>
        <div style={{ color: 'var(--text-muted)', fontSize: '0.7rem' }}>
          💡 Click any station, track section, or train symbol to inspect telemetry
        </div>
      </div>

      {/* Detail Inspection Modal */}
      {selectedItem && (
        <DetailModal
          isOpen={true}
          onClose={() => setSelectedItem(null)}
          type={selectedItem.type}
          data={selectedItem.data}
          onAction={(action, payload) => {
            if (action === 'plan_task') {
              window.location.href = `/planning?taskId=${payload?.task_id}`;
            } else if (action === 'inspect_section') {
              window.location.href = `/operations?sectionId=${payload?.section_id}`;
            } else if (action === 'track_train') {
              window.location.href = `/operations?trainId=${payload?.train_id}`;
            }
          }}
        />
      )}
    </div>
  );
}
