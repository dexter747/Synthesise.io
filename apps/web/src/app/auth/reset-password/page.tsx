'use client';

import { useState, Suspense } from 'react';
import { useRouter, useSearchParams } from 'next/navigation';
import Link from 'next/link';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { z } from 'zod';
import { motion } from 'framer-motion';
import { AuthLayout } from '@/components/auth/auth-layout';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { getAPI } from '@synthesize/api-client';
import { toast } from 'sonner';
import { CheckCircle, ArrowLeft, AlertCircle } from 'lucide-react';

const resetSchema = z
  .object({
    password: z.string().min(8, 'Password must be at least 8 characters'),
    confirmPassword: z.string(),
  })
  .refine((data) => data.password === data.confirmPassword, {
    message: "Passwords don't match",
    path: ['confirmPassword'],
  });

type ResetFormData = z.infer<typeof resetSchema>;

function ResetPasswordForm() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const token = searchParams.get('token');
  const [isLoading, setIsLoading] = useState(false);
  const [success, setSuccess] = useState(false);

  const {
    register,
    handleSubmit,
    formState: { errors },
  } = useForm<ResetFormData>({
    resolver: zodResolver(resetSchema),
  });

  const onSubmit = async (data: ResetFormData) => {
    if (!token) {
      toast.error('Invalid reset token');
      return;
    }

    setIsLoading(true);
    try {
      const api = getAPI();
      await api.resetPassword(token, data.password);
      setSuccess(true);
      toast.success('Password reset successfully!');
      setTimeout(() => {
        router.push('/auth/login');
      }, 2000);
    } catch (error: any) {
      toast.error(error.message || 'Failed to reset password');
    } finally {
      setIsLoading(false);
    }
  };

  if (!token) {
    return (
      <div className="min-h-screen bg-black flex items-center justify-center px-4">
        <motion.div
          initial={{ opacity: 0, scale: 0.95 }}
          animate={{ opacity: 1, scale: 1 }}
          transition={{ duration: 0.3 }}
          className="w-full max-w-md"
        >
          <div className="bg-zinc-900/50 border border-white/10 rounded-2xl p-8 backdrop-blur-xl text-center">
            <div className="w-16 h-16 bg-red-500/20 rounded-full flex items-center justify-center mx-auto mb-6">
              <AlertCircle className="w-8 h-8 text-red-400" />
            </div>
            <h2 className="text-2xl font-medium text-white mb-3">Invalid Reset Link</h2>
            <p className="text-zinc-400 mb-8">
              This password reset link is invalid or has expired.
            </p>
            <Link href="/auth/forgot-password">
              <Button variant="outline" className="w-full border-white/10 text-white hover:bg-white/5">
                <ArrowLeft className="w-4 h-4 mr-2" />
                Request New Link
              </Button>
            </Link>
          </div>
        </motion.div>
      </div>
    );
  }

  if (success) {
    return (
      <div className="min-h-screen bg-black flex items-center justify-center px-4">
        <motion.div
          initial={{ opacity: 0, scale: 0.95 }}
          animate={{ opacity: 1, scale: 1 }}
          transition={{ duration: 0.3 }}
          className="w-full max-w-md"
        >
          <div className="bg-zinc-900/50 border border-white/10 rounded-2xl p-8 backdrop-blur-xl text-center">
            <div className="w-16 h-16 bg-teal-500/20 rounded-full flex items-center justify-center mx-auto mb-6">
              <CheckCircle className="w-8 h-8 text-teal-400" />
            </div>
            <h2 className="text-2xl font-medium text-white mb-3">Password Reset Successfully</h2>
            <p className="text-zinc-400 mb-8">
              Your password has been reset. Redirecting to login...
            </p>
            <Link href="/auth/login">
              <Button variant="gradient" className="w-full">
                Go to Login
              </Button>
            </Link>
          </div>
        </motion.div>
      </div>
    );
  }

  return (
    <AuthLayout 
      title="Reset Your Password" 
      description="Choose a strong password for your account"
    >
      <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
        <div className="space-y-2">
          <label className="text-sm font-medium text-zinc-300">New Password</label>
          <Input
            type="password"
            placeholder="••••••••"
            className="bg-white/5 border-white/10 text-white placeholder:text-zinc-500 focus:border-teal-500/50 focus:ring-teal-500/20"
            {...register('password')}
          />
          <p className="text-xs text-zinc-500">Must be at least 8 characters</p>
          {errors.password && (
            <p className="text-sm text-red-400">{errors.password.message}</p>
          )}
        </div>

        <div className="space-y-2">
          <label className="text-sm font-medium text-zinc-300">Confirm Password</label>
          <Input
            type="password"
            placeholder="••••••••"
            className="bg-white/5 border-white/10 text-white placeholder:text-zinc-500 focus:border-teal-500/50 focus:ring-teal-500/20"
            {...register('confirmPassword')}
          />
          {errors.confirmPassword && (
            <p className="text-sm text-red-400">{errors.confirmPassword.message}</p>
          )}
        </div>

        <Button type="submit" variant="gradient" className="w-full" disabled={isLoading}>
          {isLoading ? 'Resetting...' : 'Reset Password'}
        </Button>
      </form>

      <p className="mt-6 text-center text-sm text-zinc-400">
        <Link href="/auth/login" className="text-teal-400 hover:text-teal-300 font-medium transition-colors">
          ← Back to Login
        </Link>
      </p>
    </AuthLayout>
  );
}

export default function ResetPasswordPage() {
  return (
    <Suspense fallback={
      <div className="min-h-screen bg-black flex items-center justify-center">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-teal-500"></div>
      </div>
    }>
      <ResetPasswordForm />
    </Suspense>
  );
}
