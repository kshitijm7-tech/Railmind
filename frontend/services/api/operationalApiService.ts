/**
 * Real operational-dataset API service (FastAPI).
 *
 * Canonical synthetic corridor C-07 — Anandpur–Fatehgarh Main Line.
 * SYNTHETIC DATA: demonstration scenario data, not live railway operations.
 * These endpoints back stations, canonical sections, train movements,
 * disruptions and corridor metadata with no frontend hardcoded copies.
 */
import { apiClient, extractItemData, extractListData } from './client/httpClient';
import type {
  DisruptionListQuery,
  SectionListQuery,
  StationListQuery,
  TrainMovementListQuery,
} from '../../contracts/api/operational';

export interface OperationalStation {
  station_id: string;
  code: string;
  name: string;
  sequence: number;
  km: number;
  category: string;
  platforms: number;
  loop_lines: number;
  is_junction: boolean;
}

export interface OperationalSection {
  section_id: string;
  from_station_id: string;
  to_station_id: string;
  length_km: number;
  track_count: number;
  electrified: boolean;
  max_speed_kmph: number;
  headway_min: number;
  section_type: string;
}

export interface OperationalTrainMovement {
  movement_id: string;
  train_id: string;
  section_id: string;
  entry_time: string;
  exit_time: string;
  status: string;
  delay_minutes: number;
}

export interface OperationalDisruption {
  scenario_id: string;
  type: string;
  section_id: string;
  related_task_id?: string;
  planned_start?: string;
  planned_end?: string;
  actual_end?: string;
  severity: string;
  description: string;
}

export interface OperationalCorridor {
  corridor_id: string;
  name: string;
  zone: string;
  division: string;
  route_type: string;
  operational_day: string;
  timezone: string;
  total_length_km: number;
  description: string;
}

function toQuery(query?: Record<string, string | number | boolean | undefined>): Record<string, string | number | boolean> {
  const out: Record<string, string | number | boolean> = { page: 1, page_size: 100 };
  if (query) {
    for (const [key, value] of Object.entries(query)) {
      if (value !== undefined) out[key] = value;
    }
  }
  return out;
}

export class ApiOperationalService {
  async getStations(query?: StationListQuery): Promise<OperationalStation[]> {
    const env = await apiClient.get('/stations', {
      query: toQuery({
        page: query?.page,
        page_size: query?.pageSize,
        is_junction: query?.isJunction,
      }),
    });
    return extractListData<OperationalStation>(env, 'GET /stations');
  }

  async getStationById(stationId: string): Promise<OperationalStation | null> {
    const env = await apiClient.get(`/stations/${encodeURIComponent(stationId)}`);
    return extractItemData<OperationalStation>(env, `GET /stations/${stationId}`);
  }

  async getSections(query?: SectionListQuery): Promise<OperationalSection[]> {
    const env = await apiClient.get('/sections', {
      query: toQuery({
        page: query?.page,
        page_size: query?.pageSize,
        corridor_id: query?.corridorId,
        section_type: query?.sectionType,
      }),
    });
    return extractListData<OperationalSection>(env, 'GET /sections');
  }

  async getTrainMovements(query?: TrainMovementListQuery): Promise<OperationalTrainMovement[]> {
    const env = await apiClient.get('/train-movements', {
      query: toQuery({
        page: query?.page,
        page_size: query?.pageSize,
        train_id: query?.trainId,
        section_id: query?.sectionId,
        status: query?.status,
      }),
    });
    return extractListData<OperationalTrainMovement>(env, 'GET /train-movements');
  }

  async getDisruptions(query?: DisruptionListQuery): Promise<OperationalDisruption[]> {
    const env = await apiClient.get('/disruptions', {
      query: toQuery({
        page: query?.page,
        page_size: query?.pageSize,
        section_id: query?.sectionId,
        severity: query?.severity,
        type: query?.type,
      }),
    });
    return extractListData<OperationalDisruption>(env, 'GET /disruptions');
  }

  async getDisruptionById(scenarioId: string): Promise<OperationalDisruption | null> {
    const env = await apiClient.get(`/disruptions/${encodeURIComponent(scenarioId)}`);
    return extractItemData<OperationalDisruption>(env, `GET /disruptions/${scenarioId}`);
  }

  async getCorridor(): Promise<OperationalCorridor | null> {
    const env = await apiClient.get('/corridor');
    return extractItemData<OperationalCorridor>(env, 'GET /corridor');
  }
}

/** Shared real-API instance for hooks and pages (no mock copy of this dataset). */
export const operationalApi = new ApiOperationalService();
