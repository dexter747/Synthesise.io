'use client';

import { useState } from 'react';
import Link from 'next/link';
import { useRouter } from 'next/navigation';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { z } from 'zod';
import { useAuth } from '@/providers/auth-provider';
import { AuthLayout } from '@/components/auth/auth-layout';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { PasswordInput } from '@/components/ui/password-input';
import { toast } from 'sonner';

const registerSchema = z
  .object({
    name: z.string().min(2, 'Name must be at least 2 characters'),
    email: z.string().email('Please enter a valid email'),
    password: z.string().min(8, 'Password must be at least 8 characters'),
    confirmPassword: z.string(),
  })
  .refine((data) => data.password === data.confirmPassword, {
    message: "Passwords don't match",
    path: ['confirmPassword'],
  });

type RegisterFormData = z.infer<typeof registerSchema>;

export default function RegisterPage() {
  const { register: registerUser } = useAuth();
  const router = useRouter();
  const [isLoading, setIsLoading] = useState(false);

  const {
    register,
    handleSubmit,
    formState: { errors },
  } = useForm<RegisterFormData>({
    resolver: zodResolver(registerSchema),
  });

  const onSubmit = async (data: RegisterFormData) => {
    setIsLoading(true);
    try {
      await registerUser({
        name: data.name,
        email: data.email,
        password: data.password,
      });
      toast.success('Account created successfully! Please check your email.');
      // Redirect to check-email page instead of dashboard
      router.push(`/auth/check-email?email=${encodeURIComponent(data.email)}`);
    } catch (error: any) {
      toast.error(error.message || 'Failed to create account');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <AuthLayout title="Create an account" description="Start generating synthetic data in minutes">
      <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
        <div className="space-y-2">
          <label className="text-sm font-medium text-zinc-300">Full Name</label>
          <Input
            type="text"
            placeholder="John Doe"
            className="bg-white/5 border-white/10 text-white placeholder:text-zinc-500 focus:border-teal-500/50 focus:ring-teal-500/20"
            {...register('name')}
          />
          {errors.name && (
            <p className="text-sm text-red-400">{errors.name.message}</p>
          )}
        </div>

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

        <div className="space-y-2">
          <label className="text-sm font-medium text-zinc-300">Password</label>
          <PasswordInput
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
          <PasswordInput
            placeholder="••••••••"
            className="bg-white/5 border-white/10 text-white placeholder:text-zinc-500 focus:border-teal-500/50 focus:ring-teal-500/20"
            {...register('confirmPassword')}
          />
          {errors.confirmPassword && (
            <p className="text-sm text-red-400">{errors.confirmPassword.message}</p>
          )}
        </div>

        <div className="flex items-start gap-2">
          <input
            type="checkbox"
            id="terms"
            className="mt-1 rounded border-white/20 bg-white/5 text-teal-500 focus:ring-teal-500/20"
            required
          />
          <label htmlFor="terms" className="text-sm text-zinc-400">
            I agree to the{' '}
            <Link href="/legal/terms" className="text-teal-400 hover:text-teal-300">
              Terms of Service
            </Link>{' '}
            and{' '}
            <Link href="/legal/privacy" className="text-teal-400 hover:text-teal-300">
              Privacy Policy
            </Link>
          </label>
        </div>

        <Button type="submit" variant="gradient" className="w-full" disabled={isLoading}>
          {isLoading ? 'Creating account...' : 'Create account'}
        </Button>
      </form>

      <p className="mt-6 text-center text-sm text-zinc-400">
        Already have an account?{' '}
        <Link href="/auth/login" className="text-teal-400 hover:text-teal-300 font-medium transition-colors">
          Sign in
        </Link>
      </p>
    </AuthLayout>
  );
}
