import { describe, it, expect, vi } from 'vitest';
import React from 'react';
import { render, screen, act } from '@testing-library/react';
import { AppShell } from '../components/layout/AppShell';

// Mock navigation
vi.mock('next/navigation', () => ({
  usePathname: () => '/operations',
}));

describe('AppShell & Workspace Context', () => {
  it('renders correctly with default config title for /operations', () => {
    render(
      <AppShell>
        <div data-testid="child-content">Content</div>
      </AppShell>
    );

    // From WORKSPACE_CONFIG['/operations'] -> 'Live Operations'
    expect(screen.getByText('Live Operations')).toBeDefined();
    expect(screen.getByText('Corridor C-07 | Real-Time Telemetry')).toBeDefined();
    expect(screen.getByTestId('child-content')).toBeDefined();
  });

  it('allows overriding title via props', () => {
    render(
      <AppShell title="Custom Title Override">
        <div>Content</div>
      </AppShell>
    );

    expect(screen.getByText('Custom Title Override')).toBeDefined();
  });
});
