'use client';

/**
 * F02 — Command Center data aggregation.
 *
 * Flow:
 *   CommandCenterPage
 *     -> useCommandCenterData
 *     -> parallel section fetches via services.*  (network / maintenance / trains /
 *        planning / decisions / disruption / recommendations / system)
 *     -> per-section SectionSnapshot<{ok|error}>  (so a single failed section does
 *        not destroy the whole dashboard)
 *     -> UI sections render independent states.
 *
 * No new data-fetching framework. Uses existing services and useApiQuery-style
 * cancellation. One AbortController per refresh.
 */

import { useCallback, useEffect, useMemo, useRef, useState } from 'react';
import { services } from '../services';
import { RailmindApiError, toUserMessage } from '../services/api/client/errors';
import type {
  DecisionRecord,
  Incident,
  MaintenanceTask,
  Plan,
  Recommendation,
  RailwayNetwork,
  TrainService,
} from '../domain';
import { probeBackendReachability, fetchBackendVersion } from '../services/api/systemApiService';

export type SectionStatus = 'idle' | 'loading' | 'success' | 'error';

export interface SectionSnapshot<T> {
  status: SectionStatus;
  data: T | null;
  error: RailmindApiError | null;
  errorMessage: string | null;
  /** True when data came from the real backend (vs mock fallback). */
  source: 'REAL' | 'MOCK' | 'UNKNOWN';
  /** When the data was last successfully fetched (epoch ms). */
  fetchedAt: number | null;
}

export interface CommandCenterData {
  network: SectionSnapshot<RailwayNetwork>;
  maintenance: SectionSnapshot<MaintenanceTask[]>;
  defects: SectionSnapshot<Incident[]>;
  trains: SectionSnapshot<TrainService[]>;
  plans: SectionSnapshot<Plan[]>;
  decisions: SectionSnapshot<DecisionRecord[]>;
  incidents: SectionSnapshot<Incident[]>;
  recommendation: SectionSnapshot<Recommendation | null>;
  system: SectionSnapshot<{ healthy: boolean; version: string | null }>;
}

function emptySnapshot<T>(): SectionSnapshot<T> {
  return {
    status: 'idle',
    data: null,
    error: null,
    errorMessage: null,
    source: 'UNKNOWN',
    fetchedAt: null,
  };
}

function isMockSource(value: unknown): 'REAL' | 'MOCK' | 'UNKNOWN' {
  if (value === 'REAL' || value === 'MOCK') return value;
  return 'UNKNOWN';
}

interface SectionDescriptor<T> {
  key: keyof CommandCenterData;
  fetch: () => Promise<T>;
  /** Inspect the fetch result for the F01 `_source` provenance tag. */
  detectSource: (data: T) => 'REAL' | 'MOCK' | 'UNKNOWN';
}

export function useCommandCenterData(): {
  data: CommandCenterData;
  loading: boolean;
  reload: () => void;
  lastRefreshedAt: number | null;
} {
  const [data, setData] = useState<CommandCenterData>(() => ({
    network: emptySnapshot(),
    maintenance: emptySnapshot(),
    defects: emptySnapshot(),
    trains: emptySnapshot(),
    plans: emptySnapshot(),
    decisions: emptySnapshot(),
    incidents: emptySnapshot(),
    recommendation: emptySnapshot(),
    system: emptySnapshot(),
  }));
  const [lastRefreshedAt, setLastRefreshedAt] = useState<number | null>(null);
  const requestIdRef = useRef(0);
  const abortRef = useRef<AbortController | null>(null);

  const fetchAll = useCallback(() => {
    const requestId = requestIdRef.current + 1;
    requestIdRef.current = requestId;
    abortRef.current?.abort();
    const controller = new AbortController();
    abortRef.current = controller;

    setData((prev) => ({
      network: { ...prev.network, status: 'loading', error: null, errorMessage: null },
      maintenance: { ...prev.maintenance, status: 'loading', error: null, errorMessage: null },
      defects: { ...prev.defects, status: 'loading', error: null, errorMessage: null },
      trains: { ...prev.trains, status: 'loading', error: null, errorMessage: null },
      plans: { ...prev.plans, status: 'loading', error: null, errorMessage: null },
      decisions: { ...prev.decisions, status: 'loading', error: null, errorMessage: null },
      incidents: { ...prev.incidents, status: 'loading', error: null, errorMessage: null },
      recommendation: { ...prev.recommendation, status: 'loading', error: null, errorMessage: null },
      system: { ...prev.system, status: 'loading', error: null, errorMessage: null },
    }));

    const sections: SectionDescriptor<unknown>[] = [
      {
        key: 'system',
        fetch: async () => {
          const healthy = await probeBackendReachability(controller.signal);
          const version = healthy ? await fetchBackendVersion(controller.signal) : null;
          return { healthy, version };
        },
        detectSource: () => 'REAL',
      },
      {
        key: 'network',
        fetch: () => services.network.getNetwork(),
        detectSource: (result) => {
          const maybe = result as RailwayNetwork | null;
          if (maybe && typeof maybe === 'object' && (maybe as { _source?: string })._source) {
            return isMockSource((maybe as { _source?: string })._source);
          }
          return 'UNKNOWN';
        },
      },
      {
        key: 'maintenance',
        fetch: () => services.maintenance.getTasks(),
        detectSource: (result) => {
          if (Array.isArray(result) && result[0]) {
            return isMockSource((result[0] as { _source?: string })._source);
          }
          return 'UNKNOWN';
        },
      },
      {
        key: 'defects',
        fetch: () => services.maintenance.getDefects(),
        detectSource: (result) => {
          if (Array.isArray(result) && result[0]) {
            return isMockSource((result[0] as { _source?: string })._source);
          }
          return 'UNKNOWN';
        },
      },
      {
        key: 'trains',
        fetch: () => services.trains.getTrains(),
        detectSource: (result) => {
          if (Array.isArray(result) && result[0]) {
            return isMockSource((result[0] as { _source?: string })._source);
          }
          return 'UNKNOWN';
        },
      },
      {
        key: 'plans',
        fetch: () => services.planning.getPlans(),
        detectSource: (result) => {
          if (Array.isArray(result) && result[0]) {
            return isMockSource((result[0] as { _source?: string })._source);
          }
          return 'UNKNOWN';
        },
      },
      {
        key: 'decisions',
        fetch: () => services.decisions.getDecisionHistory(),
        detectSource: () => 'UNKNOWN',
      },
      {
        key: 'incidents',
        fetch: () => services.disruption.getActiveIncidents(),
        detectSource: () => 'UNKNOWN',
      },
      {
        key: 'recommendation',
        fetch: () => services.recommendations.getLatestRecommendation(),
        detectSource: () => 'UNKNOWN',
      },
    ];

    const run = async (): Promise<void> => {
      const settled = await Promise.allSettled(
        sections.map(async (section) => ({
          key: section.key,
          result: await section.fetch(),
          detect: section.detectSource,
        })),
      );

      if (requestIdRef.current !== requestId || controller.signal.aborted) return;
      const now = Date.now();

      setData((prev) => {
        const next: CommandCenterData = { ...prev };
        for (let i = 0; i < settled.length; i += 1) {
          const outcome = settled[i];
          const descriptor = sections[i];
          if (!descriptor) continue;
          const key = descriptor.key as keyof CommandCenterData;
          const previous = prev[key];
          if (outcome?.status === 'fulfilled') {
            const payload = outcome.value.result as never;
            const source = outcome.value.detect(payload);
            next[key] = {
              ...previous,
              status: 'success',
              data: payload,
              error: null,
              errorMessage: null,
              source,
              fetchedAt: now,
            } as SectionSnapshot<unknown> as never;
          } else {
            const rawError = outcome?.reason;
            const normalized =
              rawError instanceof RailmindApiError
                ? rawError
                : new RailmindApiError({
                    kind: 'UNKNOWN',
                    message: 'An unexpected integration error occurred.',
                  });
            next[key] = {
              ...previous,
              status: 'error',
              error: normalized,
              errorMessage: toUserMessage(normalized),
              fetchedAt: now,
            } as SectionSnapshot<unknown> as never;
          }
        }
        return next;
      });
      setLastRefreshedAt(now);
    };

    void run();
  }, []);

  useEffect(() => {
    const timer = setTimeout(() => {
      fetchAll();
    }, 0);
    return () => {
      clearTimeout(timer);
      abortRef.current?.abort();
    };
  }, [fetchAll]);

  const loading = useMemo(
    () => Object.values(data).some((s) => s.status === 'loading' || s.status === 'idle'),
    [data],
  );

  return { data, loading, reload: fetchAll, lastRefreshedAt };
}
