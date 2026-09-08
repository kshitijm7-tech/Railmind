import { describe, it, expect } from 'vitest';
import React from 'react';
import { render, screen } from '@testing-library/react';
import { StateBadge } from '../components/state/StateBadge';

describe('StateBadge Primitives', () => {
  it('renders PLAN state correctly with designated prefix', () => {
    render(<StateBadge stateType="PLAN" label="APPROVED SCHEDULE" />);
    expect(screen.getByText(/PLAN:/i)).toBeDefined();
    expect(screen.getByText(/APPROVED SCHEDULE/i)).toBeDefined();
  });

  it('renders ACTUAL state correctly with designated prefix', () => {
    render(<StateBadge stateType="ACTUAL" label="TRACK TELEMETRY" />);
    expect(screen.getByText(/ACTUAL:/i)).toBeDefined();
    expect(screen.getByText(/TRACK TELEMETRY/i)).toBeDefined();
  });

  it('renders PREDICTION state correctly', () => {
    render(<StateBadge stateType="PREDICTION" label="DELAY MODEL" />);
    expect(screen.getByText(/PRED:/i)).toBeDefined();
    expect(screen.getByText(/DELAY MODEL/i)).toBeDefined();
  });

  it('renders SCENARIO state correctly', () => {
    render(<StateBadge stateType="SCENARIO" label="WHAT-IF SIMULATION" />);
    expect(screen.getByText(/WHAT-IF:/i)).toBeDefined();
    expect(screen.getByText(/WHAT-IF SIMULATION/i)).toBeDefined();
  });
});
