// Required for static export compatibility
export function generateStaticParams() {
  return [];
}

export default function JobLayout({ children }: { children: React.ReactNode }) {
  return <>{children}</>;
}
