'use client';

import React, { createContext, useContext, useState, useEffect, useCallback } from 'react';
import { RailwayStateMetadata, StateMode, Scenario } from '../domain';
import { services } from '../services';

interface OperationalContextType {
  metadata: RailwayStateMetadata;
  activeScenario: Scenario | null;
  isLoading: boolean;
  setMode: (mode: StateMode) => void;
  enterScenario: (scenario: Scenario) => void;
  exitScenario: () => void;
  refreshState: () => Promise<void>;
}

const defaultMetadata: RailwayStateMetadata = {
  version: 'v1024',
  divisionId: 'DIV-01',
  divisionName: 'Central Railway Division',
  corridorId: 'CORR-07',
  corridorName: 'Grand Trunk Northern Corridor (6 Stns, 9 Secs)',
  planningHorizonHours: 72,
  mode: 'LIVE',
  lastUpdated: new Date().toISOString()
};

const OperationalContext = createContext<OperationalContextType>({
  metadata: defaultMetadata,
  activeScenario: null,
  isLoading: false,
  setMode: () => {},
  enterScenario: () => {},
  exitScenario: () => {},
  refreshState: async () => {},
});

export function OperationalProvider({ children }: { children: React.ReactNode }) {
  const [metadata, setMetadata] = useState<RailwayStateMetadata>(defaultMetadata);
  const [activeScenario, setActiveScenarioState] = useState<Scenario | null>(null);
  const [isLoading, setIsLoading] = useState<boolean>(false);

  const loadMetadata = useCallback(async () => {
    try {
      setIsLoading(true);
      const data = await services.network.getStateMetadata();
      setMetadata(data);
    } catch (e) {
      console.error('Failed to load operational state metadata:', e);
    } finally {
      setIsLoading(false);
    }
  }, []);

  useEffect(() => {
    let isMounted = true;
    services.network.getStateMetadata().then(data => {
      if (isMounted) {
        setMetadata(data);
      }
    });
    return () => {
      isMounted = false;
    };
  }, []);

  const setMode = (mode: StateMode) => {
    setMetadata(prev => ({
      ...prev,
      mode
    }));
  };

  const enterScenario = (scenario: Scenario) => {
    setActiveScenarioState(scenario);
    setMetadata(prev => ({
      ...prev,
      mode: 'SCENARIO',
      activeScenarioId: scenario.scenario_id,
      activeScenarioName: scenario.name
    }));
  };

  const exitScenario = () => {
    setActiveScenarioState(null);
    setMetadata(prev => ({
      ...prev,
      mode: 'LIVE',
      activeScenarioId: undefined,
      activeScenarioName: undefined
    }));
  };

  return (
    <OperationalContext.Provider
      value={{
        metadata,
        activeScenario,
        isLoading,
        setMode,
        enterScenario,
        exitScenario,
        refreshState: loadMetadata
      }}
    >
      {children}
    </OperationalContext.Provider>
  );
}

export function useOperationalContext() {
  const context = useContext(OperationalContext);
  if (!context) {
    throw new Error('useOperationalContext must be used within an OperationalProvider');
  }
  return context;
}
