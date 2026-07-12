'use client';

import { useState } from 'react';
import Link from 'next/link';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { z } from 'zod';
import { motion } from 'framer-motion';
import { getAPI } from '@synthesize/api-client';
import { AuthLayout } from '@/components/auth/auth-layout';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { ArrowLeft, CheckCircle, Mail } from 'lucide-react';

const forgotPasswordSchema = z.object({
  email: z.string().email('Please enter a valid email'),
});

type ForgotPasswordFormData = z.infer<typeof forgotPasswordSchema>;

export default function ForgotPasswordPage() {
  const [isLoading, setIsLoading] = useState(false);
  const [isSubmitted, setIsSubmitted] = useState(false);

  const {
    register,
    handleSubmit,
    formState: { errors },
  } = useForm<ForgotPasswordFormData>({
    resolver: zodResolver(forgotPasswordSchema),
  });

  const onSubmit = async (data: ForgotPasswordFormData) => {
    setIsLoading(true);
    try {
      const api = getAPI();
      await api.forgotPassword(data.email);
      setIsSubmitted(true);
    } catch (error: any) {
      // Don't reveal if email exists or not
      setIsSubmitted(true);
    } finally {
      setIsLoading(false);
    }
  };

  if (isSubmitted) {
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
              <Mail className="w-8 h-8 text-teal-400" />
            </div>
            <h2 className="text-2xl font-medium text-white mb-3">Check your email</h2>
            <p className="text-zinc-400 mb-8">
              If an account exists with that email, we've sent password reset instructions.
            </p>
            <Link href="/auth/login">
              <Button variant="outline" className="w-full border-white/10 text-white hover:bg-white/5">
                <ArrowLeft className="w-4 h-4 mr-2" />
                Back to sign in
              </Button>
            </Link>
          </div>
        </motion.div>
      </div>
    );
  }

  return (
    <AuthLayout 
      title="Forgot your password?" 
      description="Enter your email and we'll send you instructions to reset it."
    >
      <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
        <div className="space-y-2">
          <label className="text-sm font-medium text-zinc-300">Email</label>
          <Input
            type="email"
            placeholder="you@example.com"
            className="bg-white/5 border-white/10 text-white placeholder:text-zinc-500 focus:border-teal-500/50 focus:ring-teal-500/20"
            {...register('email')}
          />
          {errors.email && (
            <p className="text-sm text-red-400">{errors.email.message}</p>
          )}
        </div>

        <Button type="submit" variant="gradient" className="w-full" disabled={isLoading}>
          {isLoading ? 'Sending...' : 'Send reset instructions'}
        </Button>
      </form>

      <p className="mt-6 text-center text-sm text-zinc-400">
        Remember your password?{' '}
        <Link href="/auth/login" className="text-teal-400 hover:text-teal-300 font-medium transition-colors">
          Sign in
        </Link>
      </p>
    </AuthLayout>
  );
}
