// Required for static export compatibility
export function generateStaticParams() {
  return [];
}

export default function OrganizationLayout({ children }: { children: React.ReactNode }) {
  return <>{children}</>;
}
