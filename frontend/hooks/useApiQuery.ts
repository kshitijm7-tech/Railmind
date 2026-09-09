'use client';

/**
 * F01 — Loading-state + cancellation helper for API-backed views.
 *
 * Supports idle | loading | success | error so the UI never shows stale or
 * ambiguous data after a silent failure. Handles component unmount, rapid
 * navigation, and repeated requests via AbortController + stale-response
 * guards. No new state-management framework.
 */

import { useCallback, useEffect, useRef, useState } from 'react';
import { RailmindApiError, toUserMessage } from '../services/api/client/errors';

export type QueryStatus = 'idle' | 'loading' | 'success' | 'error';

export type SourceType = 'REAL' | 'MOCK' | 'UNKNOWN';

export interface ApiQueryState<T> {
  data: T | null;
  error: RailmindApiError | null;
  errorMessage: string | null;
  status: QueryStatus;
  reload: () => void;
  abort: () => void;
  source: SourceType;
  fetchedAt: number | null;
}

export type SectionSnapshot<T> = ApiQueryState<T>;

export function useApiQuery<T>(
  fetcher: (signal: AbortSignal) => Promise<T>,
  options: { immediate?: boolean; depsKey?: string } = {},
): ApiQueryState<T> {
  const { immediate = true, depsKey = '' } = options;
  const [data, setData] = useState<T | null>(null);
  const [error, setError] = useState<RailmindApiError | null>(null);
  const [status, setStatus] = useState<QueryStatus>('idle');
  const [fetchedAt, setFetchedAt] = useState<number | null>(null);
  const requestIdRef = useRef(0);
  const abortRef = useRef<AbortController | null>(null);
  const fetcherRef = useRef(fetcher);

  useEffect(() => {
    fetcherRef.current = fetcher;
  }, [fetcher]);

  const abort = useCallback(() => {
    abortRef.current?.abort();
  }, []);

  const runRequest = useCallback(() => {
    const requestId = requestIdRef.current + 1;
    requestIdRef.current = requestId;
    abortRef.current?.abort();
    const controller = new AbortController();
    abortRef.current = controller;
    setStatus('loading');
    setError(null);
    const run = async (): Promise<void> => {
      try {
        const result = await fetcherRef.current(controller.signal);
        if (requestIdRef.current !== requestId || controller.signal.aborted) return;
        setData(result);
        setStatus('success');
        setFetchedAt(Date.now());
      } catch (err: unknown) {
        if (requestIdRef.current !== requestId || controller.signal.aborted) return;
        const normalized =
          err instanceof RailmindApiError
            ? err
            : new RailmindApiError({ kind: 'UNKNOWN', message: 'An unexpected integration error occurred.' });
        setError(normalized);
        setStatus('error');
      }
    };
    void run();
  }, []);

  const reload = useCallback(() => {
    runRequest();
  }, [runRequest]);

  useEffect(() => {
    if (!immediate) return undefined;
    const timer = setTimeout(() => {
      runRequest();
    }, 0);
    return () => {
      clearTimeout(timer);
      abortRef.current?.abort();
    };
    // depsKey lets callers refetch when query identity changes.
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [immediate, depsKey]);

  // Source provenance for raw queries is UNKNOWN: the F01 service factory
  // resolves mock/real internally, and mapped domain objects carry _source.
  return { data, error, errorMessage: error ? toUserMessage(error) : null, status, reload, abort, source: 'UNKNOWN' as SourceType, fetchedAt };
}