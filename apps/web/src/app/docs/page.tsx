'use client';

import { useState } from 'react';
import { DashboardLayout } from '@/components/layouts/dashboard-layout';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Badge } from '@/components/ui/badge';
import {
  Book,
  Code,
  FileText,
  Search,
  ChevronRight,
  ExternalLink,
  Zap,
  Database,
  Key,
  Webhook,
  Settings,
  Users,
  GitBranch,
  Terminal,
} from 'lucide-react';
import Link from 'next/link';

interface DocSection {
  title: string;
  description: string;
  icon: typeof Book;
  articles: { title: string; href: string }[];
}

const docSections: DocSection[] = [
  {
    title: 'Getting Started',
    description: 'Learn the basics of Synthesize.io',
    icon: Zap,
    articles: [
      { title: 'Quick Start Guide', href: '#quickstart' },
      { title: 'Creating Your First Dataset', href: '#first-dataset' },
      { title: 'Understanding Schemas', href: '#schemas' },
      { title: 'Running Your First Job', href: '#first-job' },
    ],
  },
  {
    title: 'Datasets',
    description: 'Configure and manage your data schemas',
    icon: Database,
    articles: [
      { title: 'Dataset Overview', href: '#dataset-overview' },
      { title: 'Schema Definition', href: '#schema-definition' },
      { title: 'Field Types & Constraints', href: '#field-types' },
      { title: 'Templates & Presets', href: '#templates' },
    ],
  },
  {
    title: 'API Reference',
    description: 'Complete API documentation',
    icon: Code,
    articles: [
      { title: 'Authentication', href: '#api-auth' },
      { title: 'Datasets API', href: '#datasets-api' },
      { title: 'Jobs API', href: '#jobs-api' },
      { title: 'Webhooks API', href: '#webhooks-api' },
    ],
  },
  {
    title: 'API Keys',
    description: 'Manage authentication and access',
    icon: Key,
    articles: [
      { title: 'Creating API Keys', href: '#create-keys' },
      { title: 'Key Permissions', href: '#permissions' },
      { title: 'Rotating Keys', href: '#rotation' },
      { title: 'Best Practices', href: '#best-practices' },
    ],
  },
  {
    title: 'Webhooks',
    description: 'Real-time event notifications',
    icon: Webhook,
    articles: [
      { title: 'Setting Up Webhooks', href: '#webhook-setup' },
      { title: 'Event Types', href: '#events' },
      { title: 'Payload Format', href: '#payload' },
      { title: 'Retry Logic', href: '#retry' },
    ],
  },
  {
    title: 'Team Management',
    description: 'Collaborate with your team',
    icon: Users,
    articles: [
      { title: 'Inviting Members', href: '#inviting' },
      { title: 'Roles & Permissions', href: '#roles' },
      { title: 'Organizations', href: '#organizations' },
      { title: 'SSO Setup', href: '#sso' },
    ],
  },
];

const popularArticles = [
  { title: 'Quick Start Guide', category: 'Getting Started', href: '#quickstart' },
  { title: 'Authentication', category: 'API Reference', href: '#api-auth' },
  { title: 'Schema Definition', category: 'Datasets', href: '#schema-definition' },
  { title: 'Creating API Keys', category: 'API Keys', href: '#create-keys' },
];

export default function DocsPage() {
  const [searchQuery, setSearchQuery] = useState('');

  const filteredSections = docSections.filter((section) => {
    if (!searchQuery) return true;
    const query = searchQuery.toLowerCase();
    return (
      section.title.toLowerCase().includes(query) ||
      section.description.toLowerCase().includes(query) ||
      section.articles.some((article) => article.title.toLowerCase().includes(query))
    );
  });

  return (
    <DashboardLayout>
      <div className="max-w-6xl mx-auto space-y-8">
        {/* Header */}
        <div className="text-center">
          <h1 className="text-3xl font-medium text-white">Documentation</h1>
          <p className="text-zinc-400 mt-2">Everything you need to build with Synthesize.io</p>
        </div>

        {/* Search */}
        <div className="relative max-w-xl mx-auto">
          <Search className="absolute left-4 top-1/2 transform -translate-y-1/2 w-5 h-5 text-zinc-400" />
          <Input
            placeholder="Search documentation..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="pl-12 h-12 text-lg bg-zinc-900/50 border-white/10"
          />
        </div>

        {/* Quick Links */}
        <div className="flex flex-wrap justify-center gap-3">
          <Link href="#api-auth">
            <Button variant="outline" size="sm" className="gap-2">
              <Terminal className="w-4 h-4" />
              API Reference
            </Button>
          </Link>
          <Link href="#quickstart">
            <Button variant="outline" size="sm" className="gap-2">
              <Zap className="w-4 h-4" />
              Quick Start
            </Button>
          </Link>
          <Link href="https://github.com/synthesize-io" target="_blank">
            <Button variant="outline" size="sm" className="gap-2">
              <GitBranch className="w-4 h-4" />
              GitHub
              <ExternalLink className="w-3 h-3" />
            </Button>
          </Link>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-4 gap-6">
          {/* Popular Articles Sidebar */}
          <div className="lg:col-span-1">
            <Card className="bg-zinc-900/50 border-white/10 sticky top-6">
              <CardHeader>
                <CardTitle className="text-sm text-white">Popular Articles</CardTitle>
              </CardHeader>
              <CardContent className="space-y-2">
                {popularArticles.map((article, index) => (
                  <Link
                    key={index}
                    href={article.href}
                    className="block p-2 rounded-lg hover:bg-white/5 transition-colors"
                  >
                    <p className="text-sm font-medium text-white">{article.title}</p>
                    <p className="text-xs text-zinc-500">{article.category}</p>
                  </Link>
                ))}
              </CardContent>
            </Card>
          </div>

          {/* Doc Sections */}
          <div className="lg:col-span-3 grid grid-cols-1 md:grid-cols-2 gap-4">
            {filteredSections.map((section) => (
              <Card 
                key={section.title} 
                className="bg-zinc-900/50 border-white/10 hover:border-teal-500/30 transition-colors"
              >
                <CardHeader>
                  <div className="flex items-center gap-3">
                    <div className="w-10 h-10 rounded-lg bg-teal-500/20 flex items-center justify-center">
                      <section.icon className="w-5 h-5 text-teal-400" />
                    </div>
                    <div>
                      <CardTitle className="text-white">{section.title}</CardTitle>
                      <CardDescription>{section.description}</CardDescription>
                    </div>
                  </div>
                </CardHeader>
                <CardContent>
                  <ul className="space-y-2">
                    {section.articles.map((article, index) => (
                      <li key={index}>
                        <Link
                          href={article.href}
                          className="flex items-center justify-between text-sm text-zinc-400 hover:text-teal-400 transition-colors group"
                        >
                          <span>{article.title}</span>
                          <ChevronRight className="w-4 h-4 opacity-0 group-hover:opacity-100 transition-opacity" />
                        </Link>
                      </li>
                    ))}
                  </ul>
                </CardContent>
              </Card>
            ))}
          </div>
        </div>

        {/* API Status */}
        <Card className="bg-zinc-900/50 border-white/10">
          <CardContent className="p-6">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-4">
                <div className="w-3 h-3 rounded-full bg-teal-400 animate-pulse" />
                <div>
                  <h3 className="font-medium text-white">All Systems Operational</h3>
                  <p className="text-sm text-zinc-400">API uptime: 99.99% in the last 30 days</p>
                </div>
              </div>
              <Link href="https://status.synthesize.io" target="_blank">
                <Button variant="outline" size="sm" className="gap-2">
                  Status Page
                  <ExternalLink className="w-4 h-4" />
                </Button>
              </Link>
            </div>
          </CardContent>
        </Card>
      </div>
    </DashboardLayout>
  );
}
