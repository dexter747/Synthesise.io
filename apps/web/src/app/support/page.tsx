'use client';

import { useState } from 'react';
import { DashboardLayout } from '@/components/layouts/dashboard-layout';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Badge } from '@/components/ui/badge';
import {
  HelpCircle,
  MessageSquare,
  FileText,
  Mail,
  ChevronDown,
  ChevronUp,
  ExternalLink,
  Search,
  Zap,
  Database,
  CreditCard,
  Users,
  Shield,
  Settings,
} from 'lucide-react';
import Link from 'next/link';

interface FAQItem {
  question: string;
  answer: string;
  category: string;
}

const faqs: FAQItem[] = [
  {
    question: 'How do I create my first dataset?',
    answer: 'Navigate to Datasets > New Dataset. You can start from scratch by defining your schema, use one of our templates, or import existing data in JSON or CSV format.',
    category: 'Getting Started',
  },
  {
    question: 'What is a synthetic data generation job?',
    answer: 'A job is a request to generate synthetic data based on your dataset schema and configuration. Jobs are queued and processed by our AI engine, which creates realistic data matching your specifications.',
    category: 'Getting Started',
  },
  {
    question: 'How do I upgrade my subscription plan?',
    answer: 'Go to Settings > Subscription to view available plans. Select the plan that fits your needs and complete the checkout process. Upgrades take effect immediately.',
    category: 'Billing',
  },
  {
    question: 'What payment methods do you accept?',
    answer: 'We accept payments through Dodo Payments (our primary payment processor supporting multiple currencies worldwide) and Razorpay for customers in India. Both credit cards and bank transfers are supported.',
    category: 'Billing',
  },
  {
    question: 'How do I invite team members?',
    answer: 'Navigate to Settings > Team and click "Invite Member". Enter their email address and select a role. They will receive an invitation email to join your organization.',
    category: 'Team',
  },
  {
    question: 'What are the different team roles?',
    answer: 'Owner: Full access including billing. Admin: Can manage team and resources. Member: Can create and manage own resources. Viewer: Read-only access to resources.',
    category: 'Team',
  },
  {
    question: 'How do I enable two-factor authentication?',
    answer: 'Go to Settings > Security and click "Enable" under Two-Factor Authentication. You will need an authenticator app like Google Authenticator or Authy.',
    category: 'Security',
  },
  {
    question: 'Can I export my generated data?',
    answer: 'Yes! Once a job completes, you can download the generated data in multiple formats including JSON, CSV, SQL, and Parquet from the job details page.',
    category: 'Data',
  },
];

const helpCategories = [
  { icon: Zap, label: 'Getting Started', count: 2 },
  { icon: Database, label: 'Data', count: 1 },
  { icon: CreditCard, label: 'Billing', count: 2 },
  { icon: Users, label: 'Team', count: 2 },
  { icon: Shield, label: 'Security', count: 1 },
];

export default function SupportPage() {
  const [searchQuery, setSearchQuery] = useState('');
  const [expandedFAQ, setExpandedFAQ] = useState<number | null>(null);
  const [selectedCategory, setSelectedCategory] = useState<string | null>(null);

  const filteredFAQs = faqs.filter((faq) => {
    const matchesSearch = 
      faq.question.toLowerCase().includes(searchQuery.toLowerCase()) ||
      faq.answer.toLowerCase().includes(searchQuery.toLowerCase());
    const matchesCategory = !selectedCategory || faq.category === selectedCategory;
    return matchesSearch && matchesCategory;
  });

  return (
    <DashboardLayout>
      <div className="max-w-5xl mx-auto space-y-8">
        <div className="text-center">
          <h1 className="text-3xl font-medium text-white">How can we help?</h1>
          <p className="text-zinc-400 mt-2">Search our help center or browse by category</p>
        </div>

        {/* Search */}
        <div className="relative max-w-xl mx-auto">
          <Search className="absolute left-4 top-1/2 transform -translate-y-1/2 w-5 h-5 text-zinc-400" />
          <Input
            placeholder="Search for help..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="pl-12 h-12 text-lg bg-zinc-900/50 border-white/10"
          />
        </div>

        {/* Categories */}
        <div className="flex flex-wrap justify-center gap-3">
          {helpCategories.map(({ icon: Icon, label, count }) => (
            <Button
              key={label}
              variant={selectedCategory === label ? 'gradient' : 'outline'}
              size="sm"
              onClick={() => setSelectedCategory(selectedCategory === label ? null : label)}
              className="gap-2"
            >
              <Icon className="w-4 h-4" />
              {label}
              <Badge className="ml-1 bg-white/10">{count}</Badge>
            </Button>
          ))}
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* FAQ Section */}
          <div className="lg:col-span-2 space-y-4">
            <h2 className="text-xl font-medium text-white">Frequently Asked Questions</h2>
            
            {filteredFAQs.length === 0 ? (
              <Card className="bg-zinc-900/50 border-white/10 p-8 text-center">
                <HelpCircle className="w-12 h-12 text-zinc-500 mx-auto mb-4" />
                <h3 className="text-white font-medium">No results found</h3>
                <p className="text-zinc-400 text-sm mt-1">
                  Try adjusting your search or browse by category
                </p>
              </Card>
            ) : (
              <div className="space-y-3">
                {filteredFAQs.map((faq, index) => (
                  <Card 
                    key={index} 
                    className="bg-zinc-900/50 border-white/10 cursor-pointer hover:border-teal-500/30 transition-colors"
                    onClick={() => setExpandedFAQ(expandedFAQ === index ? null : index)}
                  >
                    <CardContent className="p-4">
                      <div className="flex items-center justify-between">
                        <div className="flex items-center gap-3">
                          <Badge className="text-xs border border-white/20 bg-transparent">{faq.category}</Badge>
                          <h3 className="font-medium text-white">{faq.question}</h3>
                        </div>
                        {expandedFAQ === index ? (
                          <ChevronUp className="w-5 h-5 text-zinc-400" />
                        ) : (
                          <ChevronDown className="w-5 h-5 text-zinc-400" />
                        )}
                      </div>
                      {expandedFAQ === index && (
                        <p className="mt-3 text-zinc-400 pl-0 pt-3 border-t border-white/5">
                          {faq.answer}
                        </p>
                      )}
                    </CardContent>
                  </Card>
                ))}
              </div>
            )}
          </div>

          {/* Contact Options */}
          <div className="space-y-4">
            <h2 className="text-xl font-medium text-white">Contact Us</h2>
            
            <Card className="bg-zinc-900/50 border-white/10">
              <CardContent className="p-4 space-y-4">
                <div className="flex items-center gap-3">
                  <div className="w-10 h-10 rounded-lg bg-teal-500/20 flex items-center justify-center">
                    <MessageSquare className="w-5 h-5 text-teal-400" />
                  </div>
                  <div>
                    <h3 className="font-medium text-white">Live Chat</h3>
                    <p className="text-sm text-zinc-400">Available 24/7</p>
                  </div>
                </div>
                <Button variant="gradient" className="w-full">
                  Start Chat
                </Button>
              </CardContent>
            </Card>

            <Card className="bg-zinc-900/50 border-white/10">
              <CardContent className="p-4 space-y-4">
                <div className="flex items-center gap-3">
                  <div className="w-10 h-10 rounded-lg bg-emerald-500/20 flex items-center justify-center">
                    <Mail className="w-5 h-5 text-emerald-400" />
                  </div>
                  <div>
                    <h3 className="font-medium text-white">Email Support</h3>
                    <p className="text-sm text-zinc-400">Response within 24h</p>
                  </div>
                </div>
                <Button variant="outline" className="w-full">
                  support@synthesize.io
                </Button>
              </CardContent>
            </Card>

            <Card className="bg-zinc-900/50 border-white/10">
              <CardContent className="p-4 space-y-4">
                <div className="flex items-center gap-3">
                  <div className="w-10 h-10 rounded-lg bg-cyan-500/20 flex items-center justify-center">
                    <FileText className="w-5 h-5 text-cyan-400" />
                  </div>
                  <div>
                    <h3 className="font-medium text-white">Documentation</h3>
                    <p className="text-sm text-zinc-400">Detailed guides & API docs</p>
                  </div>
                </div>
                <Link href="/docs">
                  <Button variant="outline" className="w-full gap-2">
                    View Docs
                    <ExternalLink className="w-4 h-4" />
                  </Button>
                </Link>
              </CardContent>
            </Card>
          </div>
        </div>
      </div>
    </DashboardLayout>
  );
}
