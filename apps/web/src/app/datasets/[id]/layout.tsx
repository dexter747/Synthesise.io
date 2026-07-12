// Required for static export compatibility
export function generateStaticParams() {
  return [];
}

export default function DatasetLayout({ children }: { children: React.ReactNode }) {
  return <>{children}</>;
}
