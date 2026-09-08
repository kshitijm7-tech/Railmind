import { RailwayAsset } from '../../infrastructure/asset';
import { TrackSection } from '../../infrastructure/track-section';
import { Corridor } from '../../infrastructure/corridor';
import { ApiResponse, ApiListResponse } from '../common/envelope';

export type AssetResponse = ApiResponse<RailwayAsset>;
export type AssetListResponse = ApiListResponse<RailwayAsset>;
export type TrackSectionResponse = ApiResponse<TrackSection>;
export type TrackSectionListResponse = ApiListResponse<TrackSection>;
export type CorridorResponse = ApiResponse<Corridor>;
export type CorridorListResponse = ApiListResponse<Corridor>;
