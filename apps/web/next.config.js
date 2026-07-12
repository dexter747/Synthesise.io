const isCloudflareBuild = process.env.CLOUDFLARE_BUILD === '1';

/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true,
  ...(isCloudflareBuild && { output: 'export' }),
  ...(isCloudflareBuild && {
    typescript: { ignoreBuildErrors: true },
    eslint: { ignoreDuringBuilds: true },
  }),
  transpilePackages: ['@synthesize/ui', '@synthesize/types', '@synthesize/utils', '@synthesize/api-client'],

  images: {
    domains: ['localhost', 'images.unsplash.com'],
    formats: ['image/avif', 'image/webp'],
    ...(isCloudflareBuild && { unoptimized: true }),
  },

  env: {
    NEXT_PUBLIC_APP_NAME: 'Synthesize.io',
    NEXT_PUBLIC_APP_URL: process.env.NEXT_PUBLIC_APP_URL || 'http://localhost:3000',
    NEXT_PUBLIC_API_URL: process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api/v1',
  },

  ...(!isCloudflareBuild && {
    async rewrites() {
      return [
        {
          source: '/api/:path*',
          destination: `${process.env.NEXT_PUBLIC_API_URL}/:path*`,
        },
      ];
    },

    async headers() {
      return [
        {
          source: '/:path*',
          headers: [
            { key: 'X-DNS-Prefetch-Control', value: 'on' },
            { key: 'Strict-Transport-Security', value: 'max-age=63072000; includeSubDomains; preload' },
            { key: 'X-Frame-Options', value: 'SAMEORIGIN' },
            { key: 'X-Content-Type-Options', value: 'nosniff' },
            { key: 'X-XSS-Protection', value: '1; mode=block' },
            { key: 'Referrer-Policy', value: 'origin-when-cross-origin' },
          ],
        },
      ];
    },
  }),
};

module.exports = nextConfig;
