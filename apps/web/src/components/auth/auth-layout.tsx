"use client";

import Link from "next/link";
import Image from "next/image";
import { motion } from "framer-motion";
import { CheckCircle } from "lucide-react";

interface AuthLayoutProps {
  children: React.ReactNode;
  title: string;
  description: string;
}

export function AuthLayout({ children, title, description }: AuthLayoutProps) {
  return (
    <div className="min-h-screen bg-black flex">
      {/* Left Side - Branding */}
      <div className="hidden lg:flex lg:w-1/2 relative overflow-hidden">
        {/* Background Effects */}
        <div className="absolute inset-0 bg-gradient-to-br from-teal-500/10 via-black to-emerald-500/10" />
        <div className="absolute top-1/4 left-1/4 w-96 h-96 bg-teal-500/20 rounded-full blur-[150px]" />
        <div className="absolute bottom-1/4 right-1/4 w-96 h-96 bg-emerald-500/20 rounded-full blur-[150px]" />
        
        {/* Grid Pattern */}
        <div className="absolute inset-0 bg-[linear-gradient(rgba(255,255,255,0.02)_1px,transparent_1px),linear-gradient(90deg,rgba(255,255,255,0.02)_1px,transparent_1px)] bg-[size:64px_64px]" />

        {/* Content */}
        <div className="relative z-10 flex flex-col justify-center p-12 w-full">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6 }}
          >
            {/* Logo */}
            <Link href="/" className="flex items-center gap-3 mb-12">
              <div className="relative">
                <div className="w-12 h-12 rounded-xl flex items-center justify-center overflow-hidden">
                  <Image
                    src="/logo.svg"
                    alt="Synthesize.io Logo"
                    width={48}
                    height={48}
                    className="object-contain"
                  />
                </div>
              </div>
              <span className="text-2xl font-medium text-white">Synthesize</span>
            </Link>

            {/* Tagline */}
            <h1 className="text-4xl font-medium text-white mb-4">
              Generate Production-Quality{" "}
              <span className="gradient-teal-text">Synthetic Data</span>
            </h1>
            <p className="text-lg text-zinc-400 max-w-md mb-12">
              Create privacy-compliant test data at scale. Save 95% compared to enterprise solutions.
            </p>

            {/* Feature Highlights */}
            <div className="space-y-4">
              {[
                "AI-powered data generation in seconds",
                "100% GDPR & privacy compliant",
                "Export to CSV, JSON, SQL & more"
              ].map((feature, index) => (
                <motion.div
                  key={feature}
                  initial={{ opacity: 0, x: -20 }}
                  animate={{ opacity: 1, x: 0 }}
                  transition={{ delay: 0.3 + index * 0.1 }}
                  className="flex items-center gap-3"
                >
                  <div className="w-6 h-6 rounded-full bg-teal-500/20 flex items-center justify-center">
                    <CheckCircle className="w-3 h-3 text-teal-400" />
                  </div>
                  <span className="text-zinc-300">{feature}</span>
                </motion.div>
              ))}
            </div>
          </motion.div>
        </div>
      </div>

      {/* Right Side - Form */}
      <div className="flex-1 flex items-center justify-center p-8">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5 }}
          className="w-full max-w-md"
        >
          {/* Mobile Logo */}
          <div className="lg:hidden text-center mb-8">
            <Link href="/" className="inline-flex items-center gap-2">
              <div className="w-10 h-10 rounded-xl flex items-center justify-center overflow-hidden">
                <Image
                  src="/logo.svg"
                  alt="Synthesize.io Logo"
                  width={40}
                  height={40}
                  className="object-contain"
                />
              </div>
              <span className="text-xl font-medium text-white">Synthesize</span>
            </Link>
          </div>

          {/* Form Card */}
          <div className="bg-zinc-900/50 border border-white/10 rounded-2xl p-8 backdrop-blur-xl">
            <div className="text-center mb-8">
              <h2 className="text-2xl font-medium text-white mb-2">{title}</h2>
              <p className="text-zinc-400">{description}</p>
            </div>
            {children}
          </div>
        </motion.div>
      </div>
    </div>
  );
}
