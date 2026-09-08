import React from 'react';

export interface ColumnDef<T> {
  header: string;
  accessorKey?: keyof T;
  cell?: (row: T) => React.ReactNode;
  width?: string;
  align?: 'left' | 'center' | 'right';
}

interface DataTableProps<T> {
  columns: ColumnDef<T>[];
  data: T[];
  keyExtractor: (row: T) => string;
  emptyMessage?: string;
  onRowClick?: (row: T) => void;
  selectedRowId?: string | null;
}

export function DataTable<T>({
  columns,
  data,
  keyExtractor,
  emptyMessage = 'No records found',
  onRowClick,
  selectedRowId,
}: DataTableProps<T>) {
  if (!data || data.length === 0) {
    return (
      <div className="dense-table-wrapper" style={{ padding: '2rem', textAlign: 'center', color: 'var(--text-muted)' }}>
        {emptyMessage}
      </div>
    );
  }

  return (
    <div className="dense-table-wrapper">
      <table className="dense-table">
        <thead>
          <tr>
            {columns.map((col, idx) => (
              <th
                key={idx}
                style={{
                  width: col.width,
                  textAlign: col.align || 'left',
                }}
              >
                {col.header}
              </th>
            ))}
          </tr>
        </thead>
        <tbody>
          {data.map((row) => {
            const rowId = keyExtractor(row);
            const isSelected = selectedRowId !== undefined && selectedRowId === rowId;
            return (
              <tr
                key={rowId}
                onClick={() => onRowClick && onRowClick(row)}
                style={{
                  cursor: onRowClick ? 'pointer' : 'default',
                  backgroundColor: isSelected ? 'var(--surface-hover)' : undefined,
                }}
              >
                {columns.map((col, idx) => (
                  <td
                    key={idx}
                    style={{
                      textAlign: col.align || 'left',
                    }}
                  >
                    {col.cell
                      ? col.cell(row)
                      : col.accessorKey
                        ? String(row[col.accessorKey] ?? '')
                        : null}
                  </td>
                ))}
              </tr>
            );
          })}
        </tbody>
      </table>
    </div>
  );
}