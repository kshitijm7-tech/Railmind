import { describe, it, expect } from 'vitest';
import React from 'react';
import { render, screen } from '@testing-library/react';
import { DataTable, ColumnDef } from '../components/operational/DataTable';

interface TestItem {
  id: string;
  name: string;
  speed: number;
}

describe('DataTable Component', () => {
  const columns: ColumnDef<TestItem>[] = [
    { header: 'ID', accessorKey: 'id' },
    { header: 'Section Name', accessorKey: 'name' },
    { header: 'Speed', cell: (item) => `${item.speed} km/h` }
  ];

  const data: TestItem[] = [
    { id: 'SEC-01', name: 'Main Line', speed: 130 },
    { id: 'SEC-02', name: 'Chord Line', speed: 100 }
  ];

  it('renders table headers and rows accurately', () => {
    render(
      <DataTable
        columns={columns}
        data={data}
        keyExtractor={(item) => item.id}
      />
    );

    expect(screen.getByText('Section Name')).toBeDefined();
    expect(screen.getByText('Main Line')).toBeDefined();
    expect(screen.getByText('130 km/h')).toBeDefined();
    expect(screen.getByText('Chord Line')).toBeDefined();
  });

  it('renders empty message when no records are present', () => {
    render(
      <DataTable
        columns={columns}
        data={[]}
        keyExtractor={(item) => item.id}
        emptyMessage="No active track sections"
      />
    );

    expect(screen.getByText('No active track sections')).toBeDefined();
  });
});
