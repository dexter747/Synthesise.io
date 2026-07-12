'use client';

import Link from 'next/link'
import { ArrowLeft, Home } from 'lucide-react'

export default function NotFound() {
  return (
    <div className="min-h-screen flex items-center justify-center bg-black px-4">
      <div className="max-w-2xl w-full text-center">
        {/* 404 Animation */}
        <div className="mb-8">
          <h1 className="text-9xl font-medium text-transparent bg-clip-text bg-gradient-to-r from-teal-400 to-teal-600 animate-pulse">
            404
          </h1>
        </div>

        {/* Error Message */}
        <div className="space-y-4 mb-8">
          <h2 className="text-3xl font-medium text-white">
            Page Not Found
          </h2>
          <p className="text-lg text-gray-400">
            Oops! The page you&apos;re looking for doesn&apos;t exist or has been moved.
          </p>
        </div>

        {/* Illustration */}
        <div className="mb-8 flex justify-center">
          <svg
            className="w-64 h-64 text-gray-300 dark:text-gray-700"
            viewBox="0 0 24 24"
            fill="none"
            xmlns="http://www.w3.org/2000/svg"
          >
            <path
              d="M12 2L2 7L12 12L22 7L12 2Z"
              stroke="currentColor"
              strokeWidth="2"
              strokeLinecap="round"
              strokeLinejoin="round"
            />
            <path
              d="M2 17L12 22L22 17"
              stroke="currentColor"
              strokeWidth="2"
              strokeLinecap="round"
              strokeLinejoin="round"
            />
            <path
              d="M2 12L12 17L22 12"
              stroke="currentColor"
              strokeWidth="2"
              strokeLinecap="round"
              strokeLinejoin="round"
            />
          </svg>
        </div>

        {/* Action Buttons */}
        <div className="flex flex-col sm:flex-row gap-4 justify-center items-center">
          <Link
            href="/"
            className="inline-flex items-center gap-2 px-6 py-3 bg-gradient-to-r from-teal-500 to-emerald-500 text-black font-medium rounded-lg hover:from-teal-400 hover:to-emerald-400 transition-all duration-200 shadow-lg hover:shadow-xl"
          >
            <Home className="w-5 h-5" />
            Go Home
          </Link>
          
          <button
            onClick={() => window.history.back()}
            className="inline-flex items-center gap-2 px-6 py-3 bg-white/5 text-white font-medium rounded-lg border-2 border-white/10 hover:border-white/20 transition-all duration-200"
          >
            <ArrowLeft className="w-5 h-5" />
            Go Back
          </button>
        </div>

        {/* Help Text */}
        <div className="mt-12 text-sm text-gray-400">
          <p>If you believe this is a mistake, please contact our support team.</p>
        </div>
      </div>
    </div>
  )
}
