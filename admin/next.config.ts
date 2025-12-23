import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  allowedDevOrigins: [
    '75b0aa88-92c4-4424-ab49-9d1664b48129-00-1g9yoro9o3zfq.sisko.replit.dev',
    'localhost',
    '127.0.0.1',
    '0.0.0.0',
  ],
  async headers() {
    return [
      {
        source: '/(.*)',
        headers: [
          {
            key: 'Cache-Control',
            value: 'no-store, must-revalidate',
          },
          {
            key: 'Access-Control-Allow-Origin',
            value: '*',
          },
        ],
      },
    ];
  },
};

export default nextConfig;
