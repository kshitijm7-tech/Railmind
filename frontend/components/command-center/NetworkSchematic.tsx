'use client';

import React, { useState } from 'react';
import type { Section, Station, TrainService, MaintenanceTask } from '../../domain';
import { CriticalityBadge, DepartmentBadge } from '../railway/RailwayBadges';
import { RailwayNetworkSchematic } from '../railway/RailwayNetworkSchematic';
import { LayoutGrid, Network } from 'lucide-react';

interface SectionSummary {
  total: number;
  restricted: number;
  operational: number;
}

interface NetworkSchematicProps {
  corridorName: string;
  sections: Section[];
  summary: SectionSummary;
  assetsBySection?: Record<string, number>;
  stations?: Station[];
  trains?: TrainService[];
  tasks?: MaintenanceTask[];
}

export function NetworkSchematic({
  corridorName,
  sections,
  summary,
  assetsBySection,
  stations,
  trains,
  tasks,
}: NetworkSchematicProps) {
  const [viewMode, setViewMode] = useState<'schematic' | 'list'>('schematic');

  return (
    <div className="cc-network-schematic" aria-label="Railway network schematic">
      <header className="cc-network-header">
        <div>
          <span className="cc-section-eyebrow">CORRIDOR</span>
          <strong className="cc-network-name">{corridorName}</strong>
       </div>
        <div style={{ display: 'flex', alignItems: 'center', gap: '1rem' }}>
          <div className="cc-network-summary">
            <span>
              <strong>{sections.length}</strong> sections
            </span>
            <span>
              <strong>{summary.operational}</strong> operational
            </span>
            {summary.restricted > 0 && (
              <span className="cc-network-warn">
                <strong>{summary.restricted}</strong> restricted
              </span>
            )}
          </div>
          <div style={{
            display: 'flex',
            background: 'var(--surface-panel)',
            padding: '2px',
            borderRadius: 'var(--radius-xs)',
            border: '1px solid var(--surface-border)',
            gap: '2px',
          }}>
            <button
              type="button"
              onClick={() => setViewMode('schematic')}
              style={{
                display: 'flex',
                alignItems: 'center',
                gap: '4px',
                padding: '4px 8px',
                fontSize: '0.72rem',
                fontWeight: 600,
                border: 'none',
                borderRadius: 'var(--radius-xs)',
                cursor: 'pointer',
                background: viewMode === 'schematic' ? 'var(--surface-elevated)' : 'transparent',
                color: viewMode === 'schematic' ? 'var(--text-accent)' : 'var(--text-secondary)',
              }}
            >
              <Network size={13} />
              Synoptic SVG
            </button>
            <button
              type="button"
              onClick={() => setViewMode('list')}
              style={{
                display: 'flex',
                alignItems: 'center',
                gap: '4px',
                padding: '4px 8px',
                fontSize: '0.72rem',
                fontWeight: 600,
                border: 'none',
                borderRadius: 'var(--radius-xs)',
                cursor: 'pointer',
                background: viewMode === 'list' ? 'var(--surface-elevated)' : 'transparent',
                color: viewMode === 'list' ? 'var(--text-accent)' : 'var(--text-secondary)',
              }}
            >
              <LayoutGrid size={13} />
              Section Telemetry
            </button>
          </div>
        </div>
      </header>

      {viewMode === 'schematic' ? (
        <div style={{ padding: '0.5rem 0' }}>
          <RailwayNetworkSchematic
            corridorName={corridorName}
            stations={stations}
            sections={sections}
            trains={trains}
            tasks={tasks}
          />
        </div>
      ) : (
        <ol className="cc-network-list">
        {sections.map((section) => {
          const assetCount = assetsBySection ? assetsBySection[section.section_id] ?? 0 : 0;
          const toneClass =
            section.status === 'OPERATIONAL'
              ? 'cc-network-row-ok'
              : section.status === 'RESTRICTED'
                ? 'cc-network-row-warn'
                : section.status === 'BLOCKED' || section.status === 'MAINTENANCE'
                  ? 'cc-network-row-crit'
                  : 'cc-network-row-neutral';
          return (
            <li
              key={section.section_id}
              className={`cc-network-row ${toneClass}`}
              aria-label={`Section ${section.section_id}, status ${section.status}`}
            >
              <span className="cc-network-glyph" aria-hidden="true">◧</span>
              <div className="cc-network-body">
                <div className="cc-network-line1">
                  <strong className="cc-network-id">{section.section_id}</strong>
                  <span className="cc-network-name-line">{section.name}</span>
               </div>
                <div className="cc-network-line2">
                  <span>
                    {section.from_station_id} → {section.to_station_id}
                 </span>
                  <span>·</span>
                  <span>{section.length_km} km</span>
                  <span>·</span>
                  <span>{section.track_count} tracks</span>
                  {assetCount > 0 && (
                    <>
                      <span>·</span>
                      <span>{assetCount} asset(s)</span>
                    </>
                  )}
               </div>
             </div>
              <div className="cc-network-meta">
                <CriticalityBadge criticality={section.criticality} />
                <span className="cc-network-status" aria-label={`Status ${section.status}`}>
                  ● {section.status}
               </span>
                <div className="cc-network-depts">
                  {section.department_owners.map((dept) => (
                    <DepartmentBadge key={dept} department={dept} />
                  ))}
               </div>
             </div>
           </li>
          );
        })}
      </ol>
      )}
      {sections.length === 0 && <div className="cc-empty">No sections in the current corridor scope</div>}
    </div>
  );
}
