import JobDetailPage from './page-client';

export function generateStaticParams() {
  return [{ id: 'demo' }];
}

export default function Page() {
  return <JobDetailPage />;
}
