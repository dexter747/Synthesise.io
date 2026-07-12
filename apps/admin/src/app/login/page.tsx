'use client';

import { useState } from 'react';
import Link from 'next/link';
import Image from 'next/image';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { z } from 'zod';
import { useAdminAuth } from '@/providers/auth-provider';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/card';
import { toast } from 'sonner';
import { Shield, Mail, Lock, ArrowRight, Sparkles } from 'lucide-react';

const loginSchema = z.object({
  email: z.string().email('Please enter a valid email'),
  password: z.string().min(1, 'Password is required'),
});

type LoginFormData = z.infer<typeof loginSchema>;

export default function AdminLoginPage() {
  const { login } = useAdminAuth();
  const [isLoading, setIsLoading] = useState(false);

  const {
    register,
    handleSubmit,
    formState: { errors },
  } = useForm<LoginFormData>({
    resolver: zodResolver(loginSchema),
  });

  const onSubmit = async (data: LoginFormData) => {
    setIsLoading(true);
    try {
      await login(data);
      toast.success('Welcome to the admin portal');
    } catch (error: any) {
      toast.error(error.message || 'Failed to sign in');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-black relative overflow-hidden px-4">
      {/* Background Effects */}
      <div className="absolute inset-0 overflow-hidden">
        {/* Grid pattern */}
        <div 
          className="absolute inset-0 opacity-[0.03]"
          style={{
            backgroundImage: `linear-gradient(rgba(255,255,255,0.05) 1px, transparent 1px), 
                              linear-gradient(90deg, rgba(255,255,255,0.05) 1px, transparent 1px)`,
            backgroundSize: '50px 50px'
          }}
        />
        
        {/* Gradient orbs */}
        <div className="absolute top-1/4 -left-32 w-96 h-96 bg-teal-500/20 rounded-full blur-3xl animate-pulse" />
        <div className="absolute bottom-1/4 -right-32 w-96 h-96 bg-cyan-500/20 rounded-full blur-3xl animate-pulse" style={{ animationDelay: '1s' }} />
        <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[500px] h-[500px] bg-teal-600/10 rounded-full blur-3xl" />
      </div>

      <div className="w-full max-w-md relative z-10">
        {/* Logo Section */}
        <div className="text-center mb-10">
          <div className="inline-flex items-center justify-center">
            <div className="relative">
              <div className="w-20 h-20 bg-gradient-to-br from-teal-400 to-cyan-500 rounded-2xl flex items-center justify-center shadow-2xl shadow-teal-500/30 transform hover:scale-105 transition-transform p-3">
                <Image
                  src="/logo.svg"
                  alt="Synthesize.io"
                  width={64}
                  height={64}
                  className="w-full h-full object-contain"
                />
              </div>
              <div className="absolute -top-1 -right-1 w-4 h-4 bg-green-400 rounded-full border-2 border-black animate-pulse" />
            </div>
          </div>
          <h1 className="text-3xl font-medium text-white mt-6 tracking-tight">
            Admin Portal
          </h1>
          <p className="text-gray-400 mt-2">
            Synthesize.io Platform Management
          </p>
        </div>

        {/* Login Card */}
        <div className="glass rounded-2xl border border-white/10 overflow-hidden shadow-2xl shadow-black/50">
          <div className="p-8">
            <div className="text-center mb-6">
              <h2 className="text-xl font-medium text-white">Welcome Back</h2>
              <p className="text-gray-400 text-sm mt-1">Enter your admin credentials to continue</p>
            </div>

            <form onSubmit={handleSubmit(onSubmit)} className="space-y-5">
              <div className="space-y-2">
                <label className="text-sm font-medium text-gray-300">Email</label>
                <div className="relative">
                  <Mail className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-500" />
                  <input
                    type="email"
                    placeholder="admin@synthesize.io"
                    className="w-full pl-10 pr-4 py-3 bg-white/[0.03] border border-white/10 rounded-xl text-white
                      placeholder:text-gray-500 focus:outline-none focus:ring-2 focus:ring-teal-500/50 focus:border-teal-500/50
                      transition-all"
                    {...register('email')}
                  />
                </div>
                {errors.email && (
                  <p className="text-red-400 text-xs mt-1">{errors.email.message}</p>
                )}
              </div>

              <div className="space-y-2">
                <label className="text-sm font-medium text-gray-300">Password</label>
                <div className="relative">
                  <Lock className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-500" />
                  <input
                    type="password"
                    placeholder="••••••••"
                    className="w-full pl-10 pr-4 py-3 bg-white/[0.03] border border-white/10 rounded-xl text-white
                      placeholder:text-gray-500 focus:outline-none focus:ring-2 focus:ring-teal-500/50 focus:border-teal-500/50
                      transition-all"
                    {...register('password')}
                  />
                </div>
                {errors.password && (
                  <p className="text-red-400 text-xs mt-1">{errors.password.message}</p>
                )}
              </div>

              <button
                type="submit"
                disabled={isLoading}
                className="w-full py-3 bg-gradient-to-r from-teal-500 to-cyan-500 text-white font-medium rounded-xl
                  hover:from-teal-400 hover:to-cyan-400 transition-all duration-300 shadow-lg shadow-teal-500/25
                  disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center gap-2 group"
              >
                {isLoading ? (
                  <div className="w-5 h-5 border-2 border-white/30 border-t-white rounded-full animate-spin" />
                ) : (
                  <>
                    Sign in to Admin Portal
                    <ArrowRight className="w-4 h-4 group-hover:translate-x-1 transition-transform" />
                  </>
                )}
              </button>
            </form>

            <div className="mt-6 pt-6 border-t border-white/5">
              <p className="text-center text-xs text-gray-500">
                This portal is restricted to authorized administrators only.
              </p>
            </div>
          </div>
        </div>

        {/* Footer */}
        <div className="mt-8 text-center">
          <div className="flex items-center justify-center gap-2 text-gray-500 text-sm">
            <Sparkles className="w-4 h-4 text-teal-400" />
            <span>Powered by Synthesize.io</span>
          </div>
        </div>
      </div>
    </div>
  );
}
