/** Operational dataset queries — canonical synthetic corridor C-07 (real API). */
export interface StationListQuery {
  page?: number;
  pageSize?: number;
  isJunction?: boolean;
}

export interface SectionListQuery {
  page?: number;
  pageSize?: number;
  corridorId?: string;
  sectionType?: string;
}

export interface TrainMovementListQuery {
  page?: number;
  pageSize?: number;
  trainId?: string;
  sectionId?: string;
  status?: string;
}

export interface DisruptionListQuery {
  page?: number;
  pageSize?: number;
  sectionId?: string;
  severity?: string;
  type?: string;
}
