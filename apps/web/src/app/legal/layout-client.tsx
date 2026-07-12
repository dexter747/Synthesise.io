import Link from "next/link";
import { ArrowLeft, Database } from "lucide-react";

interface LegalLayoutProps {
  children: React.ReactNode;
  title: string;
  lastUpdated: string;
}

export default function LegalLayout({ children, title, lastUpdated }: LegalLayoutProps) {
  return (
    <div className="min-h-screen bg-black">
      {/* Header */}
      <header className="border-b border-white/5">
        <div className="container mx-auto px-4 py-6">
          <div className="flex items-center justify-between">
            <Link href="/" className="flex items-center gap-2">
              <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-teal-400 to-emerald-500 flex items-center justify-center">
                <Database className="w-5 h-5 text-white" />
              </div>
              <span className="text-xl font-medium text-white">Synthesize</span>
            </Link>
            <Link 
              href="/"
              className="flex items-center gap-2 text-sm text-zinc-400 hover:text-white transition-colors"
            >
              <ArrowLeft className="w-4 h-4" />
              Back to Home
            </Link>
          </div>
        </div>
      </header>

      {/* Content */}
      <main className="container mx-auto px-4 py-16 max-w-4xl">
        <div className="mb-12">
          <h1 className="text-4xl font-medium text-white mb-4">{title}</h1>
          <p className="text-zinc-500">Last updated: {lastUpdated}</p>
        </div>
        
        <div className="prose prose-invert prose-zinc max-w-none prose-headings:font-medium prose-h2:text-2xl prose-h2:mt-12 prose-h2:mb-6 prose-h3:text-xl prose-h3:mt-8 prose-h3:mb-4 prose-p:text-zinc-300 prose-p:leading-relaxed prose-li:text-zinc-300 prose-strong:text-white prose-a:text-teal-400 prose-a:no-underline hover:prose-a:text-teal-300">
          {children}
        </div>
      </main>

      {/* Footer */}
      <footer className="border-t border-white/5 py-8">
        <div className="container mx-auto px-4 text-center text-sm text-zinc-500">
          © {new Date().getFullYear()} Synthesize.io. All rights reserved.
        </div>
      </footer>
    </div>
  );
}
