import { Metadata } from 'next';
import Link from 'next/link';
import { Button } from '@/components/ui/button';
import { ArrowRight, Handshake, Target, Zap } from 'lucide-react';

export const metadata: Metadata = {
  title: 'Partners - Synthesize.io',
  description: 'Partner with Synthesize.io to bring synthetic data generation to your customers.',
};

const partnerTypes = [
  {
    icon: Handshake,
    title: 'Technology Partners',
    description: 'Integrate Synthesize.io into your platform and offer synthetic data generation to your users.',
    benefits: ['Revenue share', 'Technical support', 'Co-marketing opportunities']
  },
  {
    icon: Target,
    title: 'Reseller Partners',
    description: 'Resell Synthesize.io to your customers and earn commission on every sale.',
    benefits: ['Attractive margins', 'Sales enablement', 'Dedicated partner manager']
  },
  {
    icon: Zap,
    title: 'Agency Partners',
    description: 'Help your clients implement and optimize synthetic data workflows.',
    benefits: ['Partner certification', 'Priority support', 'Joint case studies']
  }
];

export default function PartnersPage() {
  return (
    <div className="min-h-screen bg-black text-white">
      {/* Hero */}
      <section className="container mx-auto px-4 py-24">
        <div className="max-w-4xl mx-auto text-center">
          <h1 className="text-5xl sm:text-6xl font-medium mb-6">
            Partner with{' '}
            <span className="gradient-teal-text">Synthesize.io</span>
          </h1>
          <p className="text-xl text-zinc-400 mb-8 max-w-2xl mx-auto">
            Join our partner ecosystem and help developers worldwide access affordable, 
            AI-powered synthetic data generation.
          </p>
        </div>
      </section>

      {/* Partner Types */}
      <section className="container mx-auto px-4 py-16">
        <div className="max-w-6xl mx-auto">
          <h2 className="text-4xl font-medium mb-12 text-center">Partner Programs</h2>
          <div className="grid md:grid-cols-3 gap-8">
            {partnerTypes.map((type) => (
              <div
                key={type.title}
                className="p-8 rounded-2xl bg-white/5 border border-white/10 hover:border-teal-500/50 transition-all"
              >
                <type.icon className="w-12 h-12 text-teal-400 mb-4" />
                <h3 className="text-2xl font-medium mb-4">{type.title}</h3>
                <p className="text-zinc-400 mb-6">{type.description}</p>
                <ul className="space-y-2">
                  {type.benefits.map((benefit, index) => (
                    <li key={index} className="flex items-center gap-2 text-zinc-300">
                      <div className="w-1.5 h-1.5 rounded-full bg-teal-400" />
                      {benefit}
                    </li>
                  ))}
                </ul>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Benefits */}
      <section className="container mx-auto px-4 py-16">
        <div className="max-w-5xl mx-auto">
          <div className="p-12 rounded-3xl bg-gradient-to-br from-teal-500/10 to-purple-500/10 border border-white/10">
            <h2 className="text-3xl font-medium mb-8 text-center">Why Partner With Us?</h2>
            <div className="grid md:grid-cols-2 gap-8">
              {[
                {
                  title: 'Generous Revenue Share',
                  description: 'Earn up to 30% recurring commission on all referred customers.'
                },
                {
                  title: 'Technical Support',
                  description: 'Dedicated technical team to help with integration and implementation.'
                },
                {
                  title: 'Co-Marketing',
                  description: 'Joint webinars, case studies, and marketing campaigns.'
                },
                {
                  title: 'Growing Market',
                  description: 'Tap into the $2B+ synthetic data generation market.'
                }
              ].map((benefit) => (
                <div key={benefit.title}>
                  <h3 className="text-xl font-medium mb-2">{benefit.title}</h3>
                  <p className="text-zinc-400">{benefit.description}</p>
                </div>
              ))}
            </div>
          </div>
        </div>
      </section>

      {/* CTA */}
      <section className="container mx-auto px-4 py-24">
        <div className="max-w-3xl mx-auto text-center p-12 rounded-3xl bg-gradient-to-br from-teal-500/10 to-purple-500/10 border border-white/10">
          <h2 className="text-4xl font-medium mb-4">Ready to Partner?</h2>
          <p className="text-xl text-zinc-400 mb-8">
            Let's discuss how we can grow together
          </p>
          <Link href="/contact">
            <Button variant="gradient" size="lg" className="group">
              Become a Partner
              <ArrowRight className="ml-2 w-4 h-4 transition-transform group-hover:translate-x-1" />
            </Button>
          </Link>
        </div>
      </section>
    </div>
  );
}
