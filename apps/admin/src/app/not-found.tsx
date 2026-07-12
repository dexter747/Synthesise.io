'use client';

import Link from 'next/link'
import { ArrowLeft, Home, Shield } from 'lucide-react'

export default function NotFound() {
  return (
    <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-slate-50 to-slate-100 dark:from-slate-900 dark:to-slate-800 px-4">
      <div className="max-w-2xl w-full text-center">
        {/* 404 Animation */}
        <div className="mb-8">
          <h1 className="text-9xl font-medium text-transparent bg-clip-text bg-gradient-to-r from-red-600 to-orange-600 animate-pulse">
            404
          </h1>
        </div>

        {/* Error Message */}
        <div className="space-y-4 mb-8">
          <div className="flex items-center justify-center gap-2 mb-4">
            <Shield className="w-8 h-8 text-red-600" />
            <h2 className="text-3xl font-medium text-gray-900 dark:text-white">
              Admin Page Not Found
            </h2>
          </div>
          <p className="text-lg text-gray-600 dark:text-gray-400">
            The admin page you&apos;re trying to access doesn&apos;t exist or you don&apos;t have permission to view it.
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
              d="M12 2C6.48 2 2 6.48 2 12C2 17.52 6.48 22 12 22C17.52 22 22 17.52 22 12C22 6.48 17.52 2 12 2Z"
              stroke="currentColor"
              strokeWidth="2"
              strokeLinecap="round"
              strokeLinejoin="round"
            />
            <path
              d="M15 9L9 15"
              stroke="currentColor"
              strokeWidth="2"
              strokeLinecap="round"
              strokeLinejoin="round"
            />
            <path
              d="M9 9L15 15"
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
            href="/admin"
            className="inline-flex items-center gap-2 px-6 py-3 bg-gradient-to-r from-red-600 to-orange-600 text-white font-medium rounded-lg hover:from-red-700 hover:to-orange-700 transition-all duration-200 shadow-lg hover:shadow-xl"
          >
            <Home className="w-5 h-5" />
            Admin Dashboard
          </Link>
          
          <button
            onClick={() => window.history.back()}
            className="inline-flex items-center gap-2 px-6 py-3 bg-white dark:bg-slate-800 text-gray-900 dark:text-white font-medium rounded-lg border-2 border-slate-300 dark:border-slate-600 hover:border-slate-400 dark:hover:border-slate-500 transition-all duration-200"
          >
            <ArrowLeft className="w-5 h-5" />
            Go Back
          </button>
        </div>

        {/* Help Text */}
        <div className="mt-12 text-sm text-gray-500 dark:text-gray-400 space-y-2">
          <p>If you need access to this page, please contact your administrator.</p>
          <p className="font-mono text-xs">Error Code: 404 - Resource Not Found</p>
        </div>
      </div>
    </div>
  )
}
