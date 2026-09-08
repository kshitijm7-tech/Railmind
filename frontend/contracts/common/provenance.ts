import { ISOTimestamp } from './ids';

export type DataSource = 'BDMS' | 'TMS' | 'SMMS' | 'TDMS' | 'COA' | 'USER' | 'AI' | 'SIMULATION' | 'SYNTHETIC' | 'IMPORT' | 'SYSTEM';
export type DataState = 'REAL' | 'MOCKED' | 'SIMULATED' | 'STUBBED' | 'PLANNED';

export interface Provenance {
  readonly source: DataSource;
  readonly state: DataState;
  readonly recordedAt: ISOTimestamp;
  readonly version?: string;
  readonly actor?: string;
}
