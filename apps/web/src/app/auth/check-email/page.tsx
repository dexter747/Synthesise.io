'use client';

import Link from 'next/link';
import { useSearchParams } from 'next/navigation';
import { Mail, ArrowLeft } from 'lucide-react';
import { Suspense } from 'react';

function CheckEmailContent() {
  const searchParams = useSearchParams();
  const email = searchParams.get('email') || 'your email';

  return (
    <div className="min-h-screen bg-black flex items-center justify-center p-4">
      <div className="max-w-md w-full">
        <div className="bg-zinc-900 border border-zinc-800 rounded-2xl p-8 text-center">
          <div className="w-16 h-16 bg-teal-500/10 rounded-full flex items-center justify-center mx-auto mb-6">
            <Mail className="w-8 h-8 text-teal-500" />
          </div>
          
          <h1 className="text-2xl font-medium text-white mb-2">
            Check your email
          </h1>
          
          <p className="text-zinc-400 mb-6">
            We've sent a verification link to{' '}
            <span className="text-white font-medium">{email}</span>.
            Click the link in the email to verify your account.
          </p>

          <div className="bg-zinc-800/50 rounded-lg p-4 mb-6 text-left">
            <p className="text-sm text-zinc-400">
              <strong className="text-zinc-300">Didn't receive the email?</strong>
              <br />
              Check your spam folder, or make sure you entered the correct email address.
            </p>
          </div>

          <div className="space-y-3">
            <Link
              href="/auth/login"
              className="block w-full px-6 py-3 bg-teal-500 hover:bg-teal-600 text-white rounded-lg font-medium transition-colors"
            >
              Go to Sign In
            </Link>
            
            <Link
              href="/auth/register"
              className="inline-flex items-center justify-center gap-2 w-full px-6 py-3 text-zinc-400 hover:text-white transition-colors"
            >
              <ArrowLeft className="w-4 h-4" />
              Back to Register
            </Link>
          </div>
        </div>
        
        <p className="text-center text-sm text-zinc-500 mt-6">
          Already verified?{' '}
          <Link href="/auth/login" className="text-teal-400 hover:text-teal-300">
            Sign in to your account
          </Link>
        </p>
      </div>
    </div>
  );
}

export default function CheckEmailPage() {
  return (
    <Suspense fallback={
      <div className="min-h-screen bg-black flex items-center justify-center">
        <div className="text-white">Loading...</div>
      </div>
    }>
      <CheckEmailContent />
    </Suspense>
  );
}
