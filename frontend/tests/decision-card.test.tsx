import { describe, it, expect, vi } from 'vitest';
import React from 'react';
import { render, screen, fireEvent } from '@testing-library/react';
import { DecisionCard } from '../components/decision/DecisionCard';
import { DEMO_RECOMMENDATION } from '../fixtures/demoCorridor';

describe('DecisionCard Component', () => {
  it('renders structured recommendation evidence', () => {
    render(<DecisionCard recommendation={DEMO_RECOMMENDATION} />);
    
    expect(screen.getByText(DEMO_RECOMMENDATION.headline)).toBeDefined();
    expect(screen.getByText(DEMO_RECOMMENDATION.primary_rationale)).toBeDefined();
    expect(screen.getByText(/Expected Operational Impact/i)).toBeDefined();
    expect(screen.getByText(/Risk & Robustness/i)).toBeDefined();
  });

  it('triggers approval callback when Authorize button is clicked', () => {
    const handleApprove = vi.fn();
    render(
      <DecisionCard
        recommendation={DEMO_RECOMMENDATION}
        onApprove={handleApprove}
      />
    );

    const approveButton = screen.getByRole('button', { name: /Authorize & Approve Plan/i });
    fireEvent.click(approveButton);
    expect(handleApprove).toHaveBeenCalledWith(DEMO_RECOMMENDATION.recommendation_id);
  });
});
