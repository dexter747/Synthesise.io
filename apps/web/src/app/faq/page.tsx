import { Metadata } from 'next';
import Link from 'next/link';
import { Button } from '@/components/ui/button';
import { ChevronDown } from 'lucide-react';

export const metadata: Metadata = {
  title: 'FAQ - Synthesize.io',
  description: 'Frequently asked questions about Synthesize.io synthetic data generation.',
};

const faqs = [
  {
    category: 'General',
    questions: [
      {
        q: 'What is synthetic data?',
        a: 'Synthetic data is artificially generated data that mimics the statistical properties and patterns of real data, without containing any actual sensitive information. It\'s perfect for testing, development, and training purposes.'
      },
      {
        q: 'How is Synthesize.io different from competitors?',
        a: 'We\'re 95% cheaper and 10x faster than traditional providers. We use AI to generate high-quality data instantly, with simple pricing starting at just $19/month instead of $2,000+.'
      },
      {
        q: 'Is my data secure?',
        a: 'Absolutely. We never store your actual data. All generation happens in isolated environments, and we\'re SOC 2 compliant with enterprise-grade security.'
      }
    ]
  },
  {
    category: 'Pricing & Plans',
    questions: [
      {
        q: 'What\'s included in the free trial?',
        a: 'Get 14 days of full access to all features with no credit card required. Generate up to 10,000 rows to test our platform.'
      },
      {
        q: 'Can I upgrade or downgrade anytime?',
        a: 'Yes! Change your plan anytime. Upgrades take effect immediately, and downgrades apply at the next billing cycle.'
      },
      {
        q: 'What happens if I exceed my plan limits?',
        a: 'We\'ll notify you when you approach your limits. You can upgrade anytime or wait until your next billing cycle resets.'
      }
    ]
  },
  {
    category: 'Technical',
    questions: [
      {
        q: 'What data formats do you support?',
        a: 'We support CSV, JSON, SQL (PostgreSQL, MySQL, SQLite), and Parquet exports. API access provides programmatic generation.'
      },
      {
        q: 'How fast can you generate data?',
        a: 'Small datasets (< 1K rows) generate instantly. Large datasets (1M+ rows) typically complete in under 60 seconds.'
      },
      {
        q: 'Do you have an API?',
        a: 'Yes! We have a comprehensive REST API with excellent documentation. API keys are available on all paid plans.'
      }
    ]
  },
  {
    category: 'Billing',
    questions: [
      {
        q: 'What payment methods do you accept?',
        a: 'We accept all major credit cards through our secure payment processor, Dodo Payments.'
      },
      {
        q: 'Can I get a refund?',
        a: 'Yes! We offer a 30-day money-back guarantee if you\'re not satisfied. See our refund policy for details.'
      },
      {
        q: 'Do you offer annual plans?',
        a: 'Yes! Annual plans save you 2 months compared to monthly billing. Switch anytime from your billing dashboard.'
      }
    ]
  }
];

export default function FAQPage() {
  return (
    <div className="min-h-screen bg-black text-white">
      <section className="container mx-auto px-4 py-24">
        <div className="max-w-4xl mx-auto">
          <h1 className="text-5xl sm:text-6xl font-medium mb-6 text-center">
            Frequently Asked{' '}
            <span className="gradient-teal-text">Questions</span>
          </h1>
          <p className="text-xl text-zinc-400 text-center mb-16">
            Everything you need to know about Synthesize.io
          </p>

          <div className="space-y-12">
            {faqs.map((category) => (
              <div key={category.category}>
                <h2 className="text-2xl font-medium mb-6 text-teal-400">{category.category}</h2>
                <div className="space-y-4">
                  {category.questions.map((faq, index) => (
                    <details
                      key={index}
                      className="group p-6 rounded-xl bg-white/5 border border-white/10 hover:border-teal-500/50 transition-all"
                    >
                      <summary className="flex items-center justify-between cursor-pointer list-none">
                        <span className="text-lg font-medium">{faq.q}</span>
                        <ChevronDown className="w-5 h-5 text-zinc-400 transition-transform group-open:rotate-180" />
                      </summary>
                      <p className="mt-4 text-zinc-400 leading-relaxed">{faq.a}</p>
                    </details>
                  ))}
                </div>
              </div>
            ))}
          </div>

          <div className="mt-16 text-center p-8 rounded-2xl bg-gradient-to-br from-teal-500/10 to-purple-500/10 border border-white/10">
            <h3 className="text-2xl font-medium mb-4">Still have questions?</h3>
            <p className="text-zinc-400 mb-6">
              Our support team is here to help
            </p>
            <Link href="/contact">
              <Button variant="gradient" size="lg">
                Contact Support
              </Button>
            </Link>
          </div>
        </div>
      </section>
    </div>
  );
}
