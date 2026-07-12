import { Metadata } from 'next';
import Link from 'next/link';
import { Button } from '@/components/ui/button';
import { ArrowRight, Briefcase, MapPin, Clock } from 'lucide-react';

export const metadata: Metadata = {
  title: 'Careers - Synthesize.io',
  description: 'Join our team and help build the future of synthetic data generation.',
};

const openRoles = [
  {
    id: 1,
    title: 'Senior Backend Engineer',
    department: 'Engineering',
    location: 'Remote',
    type: 'Full-time',
    description: 'Build scalable data generation infrastructure using Python, FastAPI, and modern cloud technologies.'
  },
  {
    id: 2,
    title: 'Frontend Engineer',
    department: 'Engineering',
    location: 'Remote',
    type: 'Full-time',
    description: 'Create beautiful, intuitive interfaces using Next.js, React, and Tailwind CSS.'
  },
  {
    id: 3,
    title: 'AI/ML Engineer',
    department: 'Data Science',
    location: 'Remote',
    type: 'Full-time',
    description: 'Improve our AI models for synthetic data generation using state-of-the-art LLMs and techniques.'
  }
];

const benefits = [
  '🏖️ Unlimited PTO',
  '💰 Competitive salary + equity',
  '🏥 Health, dental, vision insurance',
  '💻 Latest tech equipment',
  '🌍 100% remote-first',
  '📚 Learning & development budget',
  '🎯 Quarterly team offsites',
  '🚀 High-impact work from day one'
];

export default function CareersPage() {
  return (
    <div className="min-h-screen bg-black text-white">
      {/* Hero */}
      <section className="container mx-auto px-4 py-24">
        <div className="max-w-4xl mx-auto text-center">
          <h1 className="text-5xl sm:text-6xl font-medium mb-6">
            Build the Future of{' '}
            <span className="gradient-teal-text">Data Generation</span>
          </h1>
          <p className="text-xl text-zinc-400 mb-8 max-w-2xl mx-auto">
            Join our remote-first team and help developers worldwide create better software 
            with AI-powered synthetic data.
          </p>
        </div>
      </section>

      {/* Benefits */}
      <section className="container mx-auto px-4 py-16">
        <div className="max-w-6xl mx-auto">
          <h2 className="text-3xl font-medium mb-8 text-center">Why Join Synthesize.io?</h2>
          <div className="grid md:grid-cols-4 gap-4">
            {benefits.map((benefit, index) => (
              <div
                key={index}
                className="p-4 rounded-xl bg-white/5 border border-white/10 text-center"
              >
                <p className="text-zinc-300">{benefit}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Open Positions */}
      <section className="container mx-auto px-4 py-16">
        <div className="max-w-5xl mx-auto">
          <h2 className="text-4xl font-medium mb-12 text-center">Open Positions</h2>
          <div className="grid gap-6">
            {openRoles.map((role) => (
              <div
                key={role.id}
                className="p-8 rounded-2xl bg-white/5 border border-white/10 hover:border-teal-500/50 transition-all"
              >
                <div className="flex flex-col md:flex-row md:items-start md:justify-between gap-4 mb-4">
                  <div>
                    <h3 className="text-2xl font-medium mb-2">{role.title}</h3>
                    <div className="flex flex-wrap items-center gap-4 text-sm text-zinc-400">
                      <div className="flex items-center gap-2">
                        <Briefcase className="w-4 h-4" />
                        {role.department}
                      </div>
                      <div className="flex items-center gap-2">
                        <MapPin className="w-4 h-4" />
                        {role.location}
                      </div>
                      <div className="flex items-center gap-2">
                        <Clock className="w-4 h-4" />
                        {role.type}
                      </div>
                    </div>
                  </div>
                  <Link href="/contact">
                    <Button variant="gradient" className="group">
                      Apply Now
                      <ArrowRight className="ml-2 w-4 h-4 transition-transform group-hover:translate-x-1" />
                    </Button>
                  </Link>
                </div>
                <p className="text-zinc-400">{role.description}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* CTA */}
      <section className="container mx-auto px-4 py-24">
        <div className="max-w-3xl mx-auto text-center p-12 rounded-3xl bg-gradient-to-br from-teal-500/10 to-purple-500/10 border border-white/10">
          <h2 className="text-4xl font-medium mb-4">Don't See Your Role?</h2>
          <p className="text-xl text-zinc-400 mb-8">
            We're always looking for exceptional talent. Send us your resume and let's talk!
          </p>
          <Link href="/contact">
            <Button variant="gradient" size="lg" className="group">
              Get in Touch
              <ArrowRight className="ml-2 w-4 h-4 transition-transform group-hover:translate-x-1" />
            </Button>
          </Link>
        </div>
      </section>
    </div>
  );
}
