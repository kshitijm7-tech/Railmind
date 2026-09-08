import { describe, it, expect } from 'vitest';
import React from 'react';
import { render, screen, act } from '@testing-library/react';
import { OperationalProvider, useOperationalContext } from '../context/OperationalContext';

function TestConsumer() {
  const { metadata, enterScenario, exitScenario } = useOperationalContext();
  return (
    <div>
      <span data-testid="mode">{metadata.mode}</span>
      <span data-testid="version">{metadata.version}</span>
      <button
        onClick={() =>
          enterScenario({
            scenario_id: 'SCN-TEST',
            name: 'Test Scenario',
            scenario_type: 'DURATION_OVERRUN',
            base_state_version: 'v1024',
            description: 'Test what-if branch',
            parameters: {},
            created_at: new Date().toISOString()
          })
        }
      >
        Enter Scenario
      </button>
      <button onClick={exitScenario}>Exit Scenario</button>
    </div>
  );
}

describe('OperationalContext Provider', () => {
  it('provides baseline live telemetry and supports scenario switching', async () => {
    render(
      <OperationalProvider>
        <TestConsumer />
      </OperationalProvider>
    );

    expect(screen.getByTestId('mode').textContent).toBe('LIVE');
    expect(screen.getByTestId('version').textContent).toBe('v1024');

    act(() => {
      screen.getByText('Enter Scenario').click();
    });

    expect(screen.getByTestId('mode').textContent).toBe('SCENARIO');

    act(() => {
      screen.getByText('Exit Scenario').click();
    });

    expect(screen.getByTestId('mode').textContent).toBe('LIVE');
  });
});
