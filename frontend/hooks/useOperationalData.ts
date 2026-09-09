'use client';

/**
 * Canonical operational dataset hook (corridor C-07).
 *
 * Loads stations, sections, train movements, disruptions and corridor
 * metadata from the real backend (no frontend hardcoded copies).
 * SYNTHETIC DATA: demonstration scenario data, not live railway operations.
 */
import { useCallback, useEffect, useRef, useState } from 'react';
import {
  operationalApi,
  type OperationalCorridor,
  type OperationalDisruption,
  type OperationalSection,
  type OperationalStation,
  type OperationalTrainMovement,
} from '../services/api/operationalApiService';

export interface OperationalData {
  corridor: OperationalCorridor | null;
  stations: OperationalStation[];
  sections: OperationalSection[];
  movements: OperationalTrainMovement[];
  disruptions: OperationalDisruption[];
}

export function useOperationalData(): {
  data: OperationalData;
  loading: boolean;
  error: string | null;
  reload: () => void;
} {
  const [data, setData] = useState<OperationalData>({
    corridor: null,
    stations: [],
    sections: [],
    movements: [],
    disruptions: [],
  });
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const requestIdRef = useRef(0);

  const fetchAll = useCallback(() => {
    const requestId = requestIdRef.current + 1;
    requestIdRef.current = requestId;
    setLoading(true);
    setError(null);

    void (async () => {
      try {
        const [corridor, stations, sections, movements, disruptions] = await Promise.all([
          operationalApi.getCorridor(),
          operationalApi.getStations(),
          operationalApi.getSections(),
          operationalApi.getTrainMovements(),
          operationalApi.getDisruptions(),
        ]);
        if (requestIdRef.current !== requestId) return;
        setData({ corridor, stations, sections, movements, disruptions });
      } catch (err) {
        if (requestIdRef.current !== requestId) return;
        setError(err instanceof Error ? err.message : 'Failed to load operational data.');
      } finally {
        if (requestIdRef.current === requestId) setLoading(false);
      }
    })();
  }, []);

  useEffect(() => {
    const timer = setTimeout(() => {
      fetchAll();
    }, 0);
    return () => {
      clearTimeout(timer);
    };
  }, [fetchAll]);

  return { data, loading, error, reload: fetchAll };
}
