'use client';

import Link from 'next/link';
import { ArrowLeft, HelpCircle } from 'lucide-react';

export default function HelpPage() {
  return (
    <div className="min-h-screen flex items-center justify-center bg-black px-4">
      <div className="max-w-2xl w-full text-center">
        {/* Icon */}
        <div className="mb-8 flex justify-center">
          <div className="w-32 h-32 rounded-full bg-teal-500/10 flex items-center justify-center">
            <HelpCircle className="w-16 h-16 text-teal-500" />
          </div>
        </div>

        {/* 404 Text */}
        <div className="mb-6">
          <h1 className="text-8xl font-medium text-transparent bg-clip-text bg-gradient-to-r from-teal-400 to-teal-600">
            404
          </h1>
        </div>

        {/* Message */}
        <div className="space-y-4 mb-8">
          <h2 className="text-3xl font-medium text-white">
            Help & Support Coming Soon
          </h2>
          <p className="text-lg text-gray-400">
            Need help? Our support center will be available soon.
          </p>
        </div>

        {/* Actions */}
        <div className="flex flex-col sm:flex-row gap-4 justify-center">
          <Link
            href="/dashboard"
            className="inline-flex items-center justify-center gap-2 px-6 py-3 rounded-lg bg-teal-500 text-black font-medium hover:bg-teal-400 transition-colors"
          >
            <ArrowLeft className="w-4 h-4" />
            Back to Dashboard
          </Link>
        </div>
      </div>
    </div>
  );
}
