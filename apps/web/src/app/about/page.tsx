import { Metadata } from 'next';
import Link from 'next/link';
import { Button } from '@/components/ui/button';
import { ArrowRight, Users, Target, Zap, Heart } from 'lucide-react';

export const metadata: Metadata = {
  title: 'About Us - Synthesize.io',
  description: 'Learn about Synthesize.io - the AI-powered synthetic data generation platform built for developers.',
};

export default function AboutPage() {
  return (
    <div className="min-h-screen bg-black text-white">
      {/* Hero Section */}
      <section className="container mx-auto px-4 py-24">
        <div className="max-w-4xl mx-auto text-center">
          <h1 className="text-5xl sm:text-6xl font-medium mb-6">
            Building the Future of{' '}
            <span className="gradient-teal-text">Data Generation</span>
          </h1>
          <p className="text-xl text-zinc-400 mb-8 max-w-2xl mx-auto">
            We're on a mission to make synthetic data generation accessible, affordable, 
            and incredibly easy for every developer and team.
          </p>
        </div>
      </section>

      {/* Mission & Vision */}
      <section className="container mx-auto px-4 py-16">
        <div className="grid md:grid-cols-2 gap-12 max-w-6xl mx-auto">
          <div className="p-8 rounded-2xl bg-gradient-to-br from-teal-500/10 to-purple-500/10 border border-white/10">
            <Target className="w-12 h-12 text-teal-400 mb-4" />
            <h2 className="text-3xl font-medium mb-4">Our Mission</h2>
            <p className="text-zinc-400 text-lg">
              To democratize synthetic data generation by providing developers with 
              affordable, AI-powered tools that create production-quality test data in minutes.
            </p>
          </div>
          <div className="p-8 rounded-2xl bg-gradient-to-br from-purple-500/10 to-pink-500/10 border border-white/10">
            <Zap className="w-12 h-12 text-purple-400 mb-4" />
            <h2 className="text-3xl font-medium mb-4">Our Vision</h2>
            <p className="text-zinc-400 text-lg">
              A world where every developer has instant access to high-quality test data, 
              accelerating innovation and reducing costs by 95%.
            </p>
          </div>
        </div>
      </section>

      {/* Story Section */}
      <section className="container mx-auto px-4 py-16">
        <div className="max-w-4xl mx-auto">
          <h2 className="text-4xl font-medium mb-8 text-center">Our Story</h2>
          <div className="prose prose-invert prose-lg max-w-none">
            <p className="text-zinc-400 text-lg leading-relaxed mb-6">
              Synthesize.io was born from a simple frustration: why does generating quality test data 
              have to be so expensive and time-consuming?
            </p>
            <p className="text-zinc-400 text-lg leading-relaxed mb-6">
              After spending countless hours manually creating test datasets and paying exorbitant 
              fees to legacy providers, we knew there had to be a better way. By combining cutting-edge 
              AI with thoughtful design, we built a platform that makes synthetic data generation 
              10x faster and 95% cheaper.
            </p>
            <p className="text-zinc-400 text-lg leading-relaxed">
              Today, thousands of developers trust Synthesize.io to power their testing workflows, 
              from solo indie hackers to enterprise teams at Fortune 500 companies.
            </p>
          </div>
        </div>
      </section>

      {/* Values */}
      <section className="container mx-auto px-4 py-16">
        <div className="max-w-6xl mx-auto">
          <h2 className="text-4xl font-medium mb-12 text-center">Our Values</h2>
          <div className="grid md:grid-cols-3 gap-8">
            {[
              {
                icon: Users,
                title: 'Developer-First',
                description: 'Every feature, every decision is made with developers in mind. Clean APIs, excellent docs, fast support.'
              },
              {
                icon: Zap,
                title: 'Speed & Simplicity',
                description: 'Complex problems deserve elegant solutions. We make synthetic data generation ridiculously simple.'
              },
              {
                icon: Heart,
                title: 'Transparency',
                description: 'No hidden fees, no surprises. Clear pricing, open communication, and honest limitations.'
              }
            ].map((value) => (
              <div key={value.title} className="p-6 rounded-xl bg-white/5 border border-white/10">
                <value.icon className="w-10 h-10 text-teal-400 mb-4" />
                <h3 className="text-xl font-medium mb-3">{value.title}</h3>
                <p className="text-zinc-400">{value.description}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* CTA */}
      <section className="container mx-auto px-4 py-24">
        <div className="max-w-3xl mx-auto text-center p-12 rounded-3xl bg-gradient-to-br from-teal-500/10 to-purple-500/10 border border-white/10">
          <h2 className="text-4xl font-medium mb-4">Join Our Journey</h2>
          <p className="text-xl text-zinc-400 mb-8">
            Start generating synthetic data today and see why developers love Synthesize.io
          </p>
          <div className="flex flex-col sm:flex-row items-center justify-center gap-4">
            <Link href="/auth/register">
              <Button variant="gradient" size="lg" className="group">
                Start Free Trial
                <ArrowRight className="ml-2 w-4 h-4 transition-transform group-hover:translate-x-1" />
              </Button>
            </Link>
            <Link href="/contact">
              <Button variant="outline" size="lg">
                Contact Us
              </Button>
            </Link>
          </div>
        </div>
      </section>
    </div>
  );
}
