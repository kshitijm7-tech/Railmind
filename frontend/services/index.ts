import type { ServiceContainer } from './types';

export * from './types';
export { createServices, getConfiguredApiMode } from './api/serviceFactory';
export type { ServiceMode } from './api/serviceFactory';

import { createServices } from './api/serviceFactory';

/**
 * F01 — Default service container.
 *
 * Mode is resolved from NEXT_PUBLIC_API_MODE (auto | real | mock).
 * - auto (default): real backend when reachable, mock fallback for
 *   offline development. Validation/malformed errors still surface.
 * - real: strict backend integration, no silent mock fallback.
 * - mock: deterministic fixtures for offline/demo.
 */
export const services: ServiceContainer = createServices();
