export type StateMode = 'LIVE' | 'SCENARIO';

export type StateType = 'PLAN' | 'ACTUAL' | 'PREDICTION' | 'SCENARIO';

export interface RailwayStateMetadata {
  version: string;
  divisionId: string;
  divisionName: string;
  corridorId: string;
  corridorName: string;
  planningHorizonHours: number;
  mode: StateMode;
  activeScenarioId?: string;
  activeScenarioName?: string;
  lastUpdated: string;
}
