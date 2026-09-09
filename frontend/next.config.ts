import type { NextConfig } from "next";

/**
 * F01 — Dev integration proxy.
 *
 * Browser traffic to /api/v1/* is proxied to FastAPI so local development
 * stays same-origin and does not require backend CORS changes (backend
 * ownership boundary). Production should terminate behind the same origin
 * or configure CORS explicitly (see README).
 */
const BACKEND_ORIGIN = (process.env.NEXT_PUBLIC_API_BASE_URL ?? 'http://localhost:8000').replace(/\/+$/, '');

const nextConfig: NextConfig = {
  async rewrites() {
    return [
      { source: '/api/v1/:path*', destination: `${BACKEND_ORIGIN}/api/v1/:path*` },
      { source: '/health', destination: `${BACKEND_ORIGIN}/health` },
    ];
  },
};

export default nextConfig;
