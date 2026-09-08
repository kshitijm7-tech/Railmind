import { Train } from '../../operations/train';
import { TrainPath } from '../../operations/train-path';
import { OperationalWindow } from '../../operations/operational-window';
import { TrainImpact } from '../../operations/train-impact';
import { ApiResponse, ApiListResponse } from '../common/envelope';

export type TrainResponse = ApiResponse<Train>;
export type TrainListResponse = ApiListResponse<Train>;
export type TrainPathResponse = ApiResponse<TrainPath>;
export type TrainPathListResponse = ApiListResponse<TrainPath>;
export type OperationalWindowResponse = ApiResponse<OperationalWindow>;
export type OperationalWindowListResponse = ApiListResponse<OperationalWindow>;
export type TrainImpactListResponse = ApiListResponse<TrainImpact>;
