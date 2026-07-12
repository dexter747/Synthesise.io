"use client";

import { useEffect, useState, Suspense } from "react";
import { useRouter, useSearchParams } from "next/navigation";
import Link from "next/link";
import { CheckCircle, XCircle, Loader2 } from "lucide-react";

function VerifyEmailContent() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const token = searchParams.get("token");

  const [status, setStatus] = useState<"loading" | "success" | "error">("loading");
  const [message, setMessage] = useState("");

  useEffect(() => {
    if (!token) {
      setStatus("error");
      setMessage("No verification token provided");
      return;
    }

    // Verify email
    const verifyEmail = async () => {
      try {
        const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/auth/verify-email`, {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify({ token }),
        });

        const data = await response.json();

        if (response.ok) {
          setStatus("success");
          setMessage("Your email has been verified successfully!");
          
          // Redirect to login after 3 seconds
          setTimeout(() => {
            router.push("/auth/login");
          }, 3000);
        } else {
          setStatus("error");
          setMessage(data.message || "Verification failed");
        }
      } catch (error) {
        setStatus("error");
        setMessage("An error occurred during verification");
      }
    };

    verifyEmail();
  }, [token, router]);

  return (
    <div className="min-h-screen bg-black flex items-center justify-center p-4">
      <div className="max-w-md w-full">
        <div className="bg-zinc-900 border border-zinc-800 rounded-2xl p-8 text-center">
          {status === "loading" && (
            <>
              <Loader2 className="w-16 h-16 text-teal-500 mx-auto mb-4 animate-spin" />
              <h1 className="text-2xl font-medium text-white mb-2">
                Verifying Email
              </h1>
              <p className="text-zinc-400">
                Please wait while we verify your email address...
              </p>
            </>
          )}

          {status === "success" && (
            <>
              <CheckCircle className="w-16 h-16 text-emerald-500 mx-auto mb-4" />
              <h1 className="text-2xl font-medium text-white mb-2">
                Email Verified!
              </h1>
              <p className="text-zinc-400 mb-6">
                {message}
              </p>
              <p className="text-sm text-zinc-500">
                Redirecting to login...
              </p>
            </>
          )}

          {status === "error" && (
            <>
              <XCircle className="w-16 h-16 text-red-500 mx-auto mb-4" />
              <h1 className="text-2xl font-medium text-white mb-2">
                Verification Failed
              </h1>
              <p className="text-zinc-400 mb-6">
                {message}
              </p>
              <div className="space-y-3">
                <Link
                  href="/auth/login"
                  className="block w-full px-6 py-3 bg-teal-500 hover:bg-teal-600 text-white rounded-lg font-medium transition-colors"
                >
                  Go to Login
                </Link>
                <Link
                  href="/auth/register"
                  className="block w-full px-6 py-3 bg-zinc-800 hover:bg-zinc-700 text-white rounded-lg font-medium transition-colors"
                >
                  Register Again
                </Link>
              </div>
            </>
          )}
        </div>
      </div>
    </div>
  );
}

export default function VerifyEmailPage() {
  return (
    <Suspense fallback={
      <div className="min-h-screen bg-black flex items-center justify-center">
        <Loader2 className="w-8 h-8 text-teal-500 animate-spin" />
      </div>
    }>
      <VerifyEmailContent />
    </Suspense>
  );
}
