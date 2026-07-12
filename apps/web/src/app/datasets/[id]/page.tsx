import { Suspense } from 'react';
import DatasetDetailPage from './page-client';

export function generateStaticParams() {
  return [{ id: 'demo' }];
}

export default function Page() {
  return (
    <Suspense fallback={null}>
      <DatasetDetailPage />
    </Suspense>
  );
}
