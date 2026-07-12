import type { Metadata } from "next";
import { Inter } from "next/font/google";
import "./globals.css";
import { QueryProvider } from "@/providers/query-provider";
import { AdminAuthProvider } from "@/providers/auth-provider";
import { Toaster } from "sonner";

const inter = Inter({ 
  subsets: ["latin"],
  variable: "--font-inter",
});

export const metadata: Metadata = {
  title: "Synthesize.io Admin - Platform Management",
  description: "Admin portal for managing Synthesize.io platform",
};

// Force dynamic rendering for all admin pages (they require authentication)
export const dynamic = 'force-dynamic';
export const revalidate = 0;

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en" className="dark" suppressHydrationWarning>
      <body className={`${inter.variable} font-sans antialiased`} suppressHydrationWarning>
        <QueryProvider>
          <AdminAuthProvider>
            {children}
            <Toaster 
              position="top-right" 
              richColors 
              theme="dark"
              toastOptions={{
                className: "bg-zinc-900 border-white/10",
              }}
            />
          </AdminAuthProvider>
        </QueryProvider>
      </body>
    </html>
  );
}
