"use client";

import { ReactNode } from "react";
import Link from "next/link";
import { ArrowRight, LucideIcon } from "lucide-react";

interface FeatureDetailProps {
  title: string;
  description: string;
  benefits: {
    icon: LucideIcon;
    title: string;
    description: string;
  }[];
  stats?: {
    value: string;
    label: string;
  }[];
}

export function FeatureDetail({ title, description, benefits, stats }: FeatureDetailProps) {
  return (
    <section className="py-24 relative overflow-hidden bg-black">
      <div className="container mx-auto px-4 max-w-6xl">
        {/* Header */}
        <div className="text-center mb-16">
          <h2 className="text-3xl sm:text-4xl lg:text-5xl font-light text-white mb-6">
            {title}
          </h2>
          <p className="text-xl text-zinc-400 max-w-3xl mx-auto leading-relaxed">
            {description}
          </p>
        </div>

        {/* Stats Grid (if provided) */}
        {stats && stats.length > 0 && (
          <div className="grid grid-cols-2 md:grid-cols-4 gap-8 mb-20">
            {stats.map((stat, index) => (
              <div
                key={index}
                className="text-center p-6 rounded-xl bg-zinc-900/50 border border-white/5"
              >
                <div className="text-4xl font-light text-teal-400 mb-2">{stat.value}</div>
                <div className="text-sm text-zinc-500">{stat.label}</div>
              </div>
            ))}
          </div>
        )}

        {/* Benefits Grid */}
        <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-8 mb-16">
          {benefits.map((benefit, index) => (
            <div
              key={index}
              className="group p-6 rounded-xl bg-zinc-900/30 border border-white/5 hover:border-teal-500/30 transition-all duration-300"
            >
              <div className="w-12 h-12 rounded-lg bg-gradient-to-br from-teal-500/20 to-emerald-500/20 border border-teal-500/30 flex items-center justify-center mb-4 group-hover:scale-110 transition-transform">
                <benefit.icon className="w-6 h-6 text-teal-400" />
              </div>
              <h3 className="text-lg font-medium text-white mb-2">{benefit.title}</h3>
              <p className="text-sm text-zinc-400 leading-relaxed">{benefit.description}</p>
            </div>
          ))}
        </div>

        {/* CTA Section */}
        <div className="text-center">
          <div className="inline-flex flex-col sm:flex-row items-center gap-4">
            <Link
              href="/auth/login"
              className="inline-flex items-center gap-3 px-8 py-4 rounded bg-gradient-to-r from-teal-500 to-emerald-500 text-white font-medium hover:shadow-lg hover:shadow-teal-500/20 transition-all hover:scale-105"
            >
              <span>Get Started Free</span>
              <ArrowRight className="w-5 h-5" />
            </Link>
            <Link
              href="/pricing"
              className="inline-flex items-center gap-3 px-8 py-4 rounded border border-zinc-600 text-zinc-200 hover:border-teal-400/60 hover:text-white transition-all hover:scale-105"
            >
              <span>View Pricing</span>
            </Link>
          </div>
          <p className="text-sm text-zinc-500 mt-6">
            No credit card required • Free tier available • Cancel anytime
          </p>
        </div>
      </div>
    </section>
  );
}
