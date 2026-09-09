/** Canonical operational dataset mapping tests (corridor C-07, synthetic data). */
import { describe, expect, it } from 'vitest';
import { mapNetwork } from '../services/api/mappers';

const SECTIONS = [
  { section_id: 'SEC-01', name: 'ANP–MGR', start_station_id: 'STN-A', end_station_id: 'STN-B', length_km: 34.8, max_speed_kmh: 120, track_count: 2 },
  { section_id: 'SEC-06', name: 'KDP–VPR Freight Bypass', start_station_id: 'STN-C', end_station_id: 'STN-E', length_km: 76.5, max_speed_kmh: 80, track_count: 1 },
];

const CORRIDORS = [
  { corridor_id: 'C-07', name: 'Anandpur–Fatehgarh Main Line', start_station_id: 'STN-A', end_station_id: 'STN-F', sections: ['SEC-01', 'SEC-06'] },
];

const STATIONS = [
  { station_id: 'STN-A', code: 'ANP', name: 'Anandpur', sequence: 1, km: 0.0, category: 'Junction', platforms: 5, loop_lines: 2, is_junction: true },
  { station_id: 'STN-C', code: 'KDP', name: 'Khandepur', sequence: 3, km: 67.2, category: 'Major', platforms: 4, loop_lines: 2, is_junction: true },
];

describe('mapNetwork with canonical station registry', () => {
  it('uses real station names, codes and junction flags', () => {
    const network = mapNetwork([], SECTIONS, CORRIDORS, STATIONS);
    const anp = network.stations.find((s) => s.station_id === 'STN-A');
    expect(anp?.code).toBe('ANP');
    expect(anp?.name).toBe('Anandpur');
    expect(anp?.is_junction).toBe(true);
    expect(anp?.tracks).toBe(7);
    const kdp = network.stations.find((s) => s.station_id === 'STN-C');
    expect(kdp?.code).toBe('KDP');
  });

  it('falls back to placeholders when no registry is provided', () => {
    const network = mapNetwork([], SECTIONS, CORRIDORS);
    const anp = network.stations.find((s) => s.station_id === 'STN-A');
    expect(anp?.name).toBe('STN-A');
    expect(anp?.is_junction).toBe(false);
  });
});
