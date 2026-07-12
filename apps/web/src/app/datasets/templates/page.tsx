'use client';

import { useState } from 'react';
import { DashboardLayout } from '@/components/layouts/dashboard-layout';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Input } from '@/components/ui/input';
import {
  Database,
  Users,
  ShoppingCart,
  CreditCard,
  FileText,
  MessageSquare,
  Building,
  Activity,
  Search,
  Star,
  Download,
  Eye,
} from 'lucide-react';
import Link from 'next/link';

interface Template {
  id: string;
  name: string;
  description: string;
  icon: typeof Database;
  category: string;
  fields: number;
  downloads: number;
  featured: boolean;
}

const templates: Template[] = [
  {
    id: 'users',
    name: 'User Profiles',
    description: 'Complete user data including names, emails, addresses, and preferences',
    icon: Users,
    category: 'Users',
    fields: 15,
    downloads: 12500,
    featured: true,
  },
  {
    id: 'ecommerce',
    name: 'E-Commerce Orders',
    description: 'Order data with products, quantities, prices, and shipping information',
    icon: ShoppingCart,
    category: 'Commerce',
    fields: 22,
    downloads: 8900,
    featured: true,
  },
  {
    id: 'transactions',
    name: 'Financial Transactions',
    description: 'Banking transactions with amounts, dates, and account references',
    icon: CreditCard,
    category: 'Finance',
    fields: 12,
    downloads: 7800,
    featured: true,
  },
  {
    id: 'healthcare',
    name: 'Patient Records',
    description: 'HIPAA-compliant synthetic patient data for healthcare applications',
    icon: Activity,
    category: 'Healthcare',
    fields: 28,
    downloads: 5400,
    featured: false,
  },
  {
    id: 'logs',
    name: 'Server Logs',
    description: 'Application and server log data with timestamps and severity levels',
    icon: FileText,
    category: 'DevOps',
    fields: 10,
    downloads: 4200,
    featured: false,
  },
  {
    id: 'chat',
    name: 'Chat Messages',
    description: 'Conversational data with users, timestamps, and message content',
    icon: MessageSquare,
    category: 'Social',
    fields: 8,
    downloads: 3800,
    featured: false,
  },
  {
    id: 'company',
    name: 'Company Directory',
    description: 'Business data with company names, industries, and contact details',
    icon: Building,
    category: 'Business',
    fields: 18,
    downloads: 6100,
    featured: true,
  },
  {
    id: 'products',
    name: 'Product Catalog',
    description: 'Product listings with SKUs, descriptions, pricing, and inventory',
    icon: Database,
    category: 'Commerce',
    fields: 16,
    downloads: 5600,
    featured: false,
  },
];

const categories = ['All', 'Users', 'Commerce', 'Finance', 'Healthcare', 'DevOps', 'Social', 'Business'];

export default function TemplatesPage() {
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedCategory, setSelectedCategory] = useState('All');

  const filteredTemplates = templates.filter((template) => {
    const matchesSearch = 
      template.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
      template.description.toLowerCase().includes(searchQuery.toLowerCase());
    const matchesCategory = selectedCategory === 'All' || template.category === selectedCategory;
    return matchesSearch && matchesCategory;
  });

  const featuredTemplates = templates.filter((t) => t.featured);

  return (
    <DashboardLayout>
      <div className="space-y-8">
        {/* Header */}
        <div>
          <h1 className="text-2xl font-medium text-white">Dataset Templates</h1>
          <p className="text-zinc-400 mt-1">Start with a pre-built schema and customize to your needs</p>
        </div>

        {/* Featured Templates */}
        <div>
          <h2 className="text-lg font-medium text-white mb-4 flex items-center gap-2">
            <Star className="w-5 h-5 text-yellow-400" />
            Featured Templates
          </h2>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
            {featuredTemplates.map((template) => (
              <Card 
                key={template.id}
                className="bg-gradient-to-br from-teal-500/10 to-emerald-500/5 border-teal-500/20 hover:border-teal-500/40 transition-colors"
              >
                <CardContent className="p-4">
                  <div className="flex items-start justify-between mb-3">
                    <div className="w-10 h-10 rounded-lg bg-teal-500/20 flex items-center justify-center">
                      <template.icon className="w-5 h-5 text-teal-400" />
                    </div>
                    <Badge className="bg-yellow-500/20 text-yellow-400 border-yellow-500/30">
                      Featured
                    </Badge>
                  </div>
                  <h3 className="font-medium text-white">{template.name}</h3>
                  <p className="text-sm text-zinc-400 mt-1 line-clamp-2">{template.description}</p>
                  <div className="flex items-center gap-4 mt-3 text-xs text-zinc-500">
                    <span>{template.fields} fields</span>
                    <span>{(template.downloads / 1000).toFixed(1)}k uses</span>
                  </div>
                  <div className="flex gap-2 mt-4">
                    <Link href={`/datasets/new?template=${template.id}`} className="flex-1">
                      <Button variant="gradient" size="sm" className="w-full">
                        Use Template
                      </Button>
                    </Link>
                    <Button variant="outline" size="sm">
                      <Eye className="w-4 h-4" />
                    </Button>
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>
        </div>

        {/* Search and Filter */}
        <div className="flex flex-col sm:flex-row gap-4">
          <div className="relative flex-1">
            <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 w-4 h-4 text-zinc-400" />
            <Input
              placeholder="Search templates..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="pl-10 bg-zinc-900/50 border-white/10"
            />
          </div>
          <div className="flex gap-2 flex-wrap">
            {categories.map((category) => (
              <Button
                key={category}
                variant={selectedCategory === category ? 'gradient' : 'outline'}
                size="sm"
                onClick={() => setSelectedCategory(category)}
              >
                {category}
              </Button>
            ))}
          </div>
        </div>

        {/* All Templates */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {filteredTemplates.map((template) => (
            <Card 
              key={template.id}
              className="bg-zinc-900/50 border-white/10 hover:border-teal-500/30 transition-colors"
            >
              <CardContent className="p-5">
                <div className="flex items-start gap-4">
                  <div className="w-12 h-12 rounded-lg bg-zinc-800 flex items-center justify-center shrink-0">
                    <template.icon className="w-6 h-6 text-zinc-400" />
                  </div>
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center gap-2">
                      <h3 className="font-medium text-white">{template.name}</h3>
                      {template.featured && (
                        <Star className="w-4 h-4 text-yellow-400" />
                      )}
                    </div>
                    <p className="text-sm text-zinc-400 mt-1">{template.description}</p>
                    <div className="flex items-center gap-4 mt-3">
                      <Badge className="text-xs border border-white/20 bg-transparent">{template.category}</Badge>
                      <span className="text-xs text-zinc-500">{template.fields} fields</span>
                      <span className="text-xs text-zinc-500 flex items-center gap-1">
                        <Download className="w-3 h-3" />
                        {(template.downloads / 1000).toFixed(1)}k
                      </span>
                    </div>
                  </div>
                </div>
                <div className="flex gap-2 mt-4">
                  <Link href={`/datasets/new?template=${template.id}`} className="flex-1">
                    <Button variant="outline" size="sm" className="w-full">
                      Use Template
                    </Button>
                  </Link>
                  <Button variant="ghost" size="sm">
                    <Eye className="w-4 h-4" />
                  </Button>
                </div>
              </CardContent>
            </Card>
          ))}
        </div>

        {filteredTemplates.length === 0 && (
          <Card className="bg-zinc-900/50 border-white/10">
            <CardContent className="p-12 text-center">
              <Database className="w-12 h-12 text-zinc-500 mx-auto mb-4" />
              <h3 className="text-lg font-medium text-white">No templates found</h3>
              <p className="text-zinc-400 mt-1">Try adjusting your search or filter criteria</p>
            </CardContent>
          </Card>
        )}
      </div>
    </DashboardLayout>
  );
}
