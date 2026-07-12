import { MetadataRoute } from 'next';

export const dynamic = 'force-static';

export default function robots(): MetadataRoute.Robots {
  return {
    rules: [
      {
        userAgent: '*',
        allow: '/',
        disallow: [
          '/dashboard/',
          '/api/',
          '/admin/',
          '/auth/',
          '/checkout/',
          '/team/',
        ],
      },
    ],
    sitemap: 'https://synthesize.io/sitemap.xml',
  };
}
