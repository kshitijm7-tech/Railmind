import { 
  MockNetworkService, 
  MockMaintenanceService, 
  MockTrainService, 
  MockPlanningService, 
  MockSimulationService, 
  MockDisruptionService, 
  MockRecommendationService, 
  MockDecisionService, 
  MockAuditService, 
  MockSearchService 
} from './mock/mockServices';

import {
  INetworkService,
  IMaintenanceService,
  ITrainService,
  IPlanningService,
  ISimulationService,
  IDisruptionService,
  IRecommendationService,
  IDecisionService,
  IAuditService,
  ISearchService
} from './types';

export * from './types';

export interface ServiceContainer {
  network: INetworkService;
  maintenance: IMaintenanceService;
  trains: ITrainService;
  planning: IPlanningService;
  simulation: ISimulationService;
  disruption: IDisruptionService;
  recommendations: IRecommendationService;
  decisions: IDecisionService;
  audit: IAuditService;
  search: ISearchService;
}

export const services: ServiceContainer = {
  network: new MockNetworkService(),
  maintenance: new MockMaintenanceService(),
  trains: new MockTrainService(),
  planning: new MockPlanningService(),
  simulation: new MockSimulationService(),
  disruption: new MockDisruptionService(),
  recommendations: new MockRecommendationService(),
  decisions: new MockDecisionService(),
  audit: new MockAuditService(),
  search: new MockSearchService(),
};
