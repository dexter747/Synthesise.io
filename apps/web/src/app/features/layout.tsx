import { Navbar } from "@/components/landing/navbar";

export default function FeaturesLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <div className="min-h-screen bg-black">
      <Navbar />
      {children}
    </div>
  );
}
