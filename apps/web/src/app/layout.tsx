import type { Metadata } from "next";
import { Inter } from "next/font/google";
import "./globals.css";
import { QueryProvider } from "@/providers/query-provider";
import { AuthProvider } from "@/providers/auth-provider";
import { OrganizationProvider } from "@/providers/organization-provider";
import { Toaster } from "sonner";
import { CookieConsent } from "@/components/cookie-consent";

const inter = Inter({ 
  subsets: ["latin"],
  variable: "--font-inter",
});

export const metadata: Metadata = {
  title: "Synthesize.io - AI-Powered Synthetic Data Generation",
  description: "Generate high-quality synthetic data for development, testing, and machine learning at a fraction of the cost.",
  keywords: ["synthetic data", "test data", "AI", "data generation", "privacy compliant", "GDPR"],
  authors: [{ name: "Synthesize.io" }],
  openGraph: {
    title: "Synthesize.io - AI-Powered Synthetic Data Generation",
    description: "Generate high-quality synthetic data for development, testing, and machine learning at a fraction of the cost.",
    type: "website",
    locale: "en_US",
    siteName: "Synthesize.io",
  },
  twitter: {
    card: "summary_large_image",
    title: "Synthesize.io - AI-Powered Synthetic Data Generation",
    description: "Generate high-quality synthetic data for development, testing, and machine learning at a fraction of the cost.",
  },
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en" className="dark" suppressHydrationWarning>
      <head>
        <script src="https://checkout.razorpay.com/v1/checkout.js" async></script>
      </head>
      <body className={`${inter.variable} font-sans antialiased`} suppressHydrationWarning>
        <QueryProvider>
          <AuthProvider>
            <OrganizationProvider>
              {children}
              <CookieConsent />
              <Toaster 
                position="top-right" 
                richColors 
                theme="dark"
                toastOptions={{
                  className: "bg-zinc-900 border-white/10",
                }}
              />
            </OrganizationProvider>
          </AuthProvider>
        </QueryProvider>
      </body>
    </html>
  );
}
