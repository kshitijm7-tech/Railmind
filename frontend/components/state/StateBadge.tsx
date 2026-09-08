import React from 'react';
import { StateType } from '../../domain';

interface StateBadgeProps {
  stateType: StateType;
  label?: string;
  size?: 'sm' | 'md';
}

export function StateBadge({ stateType, label, size = 'sm' }: StateBadgeProps) {
  const displayLabel = label || stateType;
  
  const getBadgeClass = () => {
    switch (stateType) {
      case 'PLAN':
        return 'state-badge state-badge-plan';
      case 'ACTUAL':
        return 'state-badge state-badge-actual';
      case 'PREDICTION':
        return 'state-badge state-badge-prediction';
      case 'SCENARIO':
        return 'state-badge state-badge-scenario';
      default:
        return 'state-badge';
    }
  };

  const getPrefix = () => {
    switch (stateType) {
      case 'PLAN': return '◈ PLAN:';
      case 'ACTUAL': return '● ACTUAL:';
      case 'PREDICTION': return '◆ PRED:';
      case 'SCENARIO': return '▲ WHAT-IF:';
    }
  };

  return (
    <span 
      className={getBadgeClass()} 
      style={{ fontSize: size === 'sm' ? '0.68rem' : '0.8rem' }}
      title={`State Type: ${stateType}`}
    >
      <span style={{ opacity: 0.8 }}>{getPrefix()}</span> {displayLabel}
    </span>
  );
}
