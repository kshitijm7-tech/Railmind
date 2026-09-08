import { describe, it, expect, vi } from 'vitest';
import React from 'react';
import { render, screen, act, fireEvent } from '@testing-library/react';
import { SearchProvider, useGlobalSearch } from '../hooks/useGlobalSearch';

function TestSearch() {
  const { isOpen, openSearch, closeSearch, query, setQuery } = useGlobalSearch();
  return (
    <div>
      <span data-testid="is-open">{isOpen ? 'open' : 'closed'}</span>
      <span data-testid="query">{query}</span>
      <button onClick={openSearch}>Open</button>
      <button onClick={closeSearch}>Close</button>
      <input 
        data-testid="search-input" 
        value={query} 
        onChange={(e) => setQuery(e.target.value)} 
      />
    </div>
  );
}

describe('Search Context Provider', () => {
  it('manages search modal state correctly', () => {
    render(
      <SearchProvider>
        <TestSearch />
      </SearchProvider>
    );

    expect(screen.getByTestId('is-open').textContent).toBe('closed');
    
    act(() => {
      screen.getByText('Open').click();
    });
    
    expect(screen.getByTestId('is-open').textContent).toBe('open');

    act(() => {
      fireEvent.change(screen.getByTestId('search-input'), { target: { value: 'train 12' } });
    });

    expect(screen.getByTestId('query').textContent).toBe('train 12');
  });

  it('handles Ctrl+K shortcut', () => {
    render(
      <SearchProvider>
        <TestSearch />
      </SearchProvider>
    );

    act(() => {
      fireEvent.keyDown(window, { key: 'k', ctrlKey: true });
    });

    expect(screen.getByTestId('is-open').textContent).toBe('open');
    
    act(() => {
      fireEvent.keyDown(window, { key: 'Escape' });
    });

    expect(screen.getByTestId('is-open').textContent).toBe('closed');
  });
});
