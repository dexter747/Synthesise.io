import { Suspense } from 'react';
import OrganizationDetailPage from './page-client';

export function generateStaticParams() {
  return [{ id: 'demo' }];
}

export default function Page() {
  return (
    <Suspense fallback={null}>
      <OrganizationDetailPage />
    </Suspense>
  );
}
