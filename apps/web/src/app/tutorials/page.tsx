import { Metadata } from 'next';
import Link from 'next/link';
import { Button } from '@/components/ui/button';
import { BookOpen, ArrowRight } from 'lucide-react';

export const metadata: Metadata = {
  title: 'Tutorials - Synthesize.io',
  description: 'Learn how to use Synthesize.io with step-by-step tutorials and guides.',
};

const tutorials = [
  {
    id: 1,
    title: 'Getting Started with Synthesize.io',
    description: 'Create your first synthetic dataset in under 5 minutes.',
    duration: '5 min',
    level: 'Beginner',
    category: 'Getting Started'
  },
  {
    id: 2,
    title: 'Using the API for Automated Data Generation',
    description: 'Integrate Synthesize.io API into your CI/CD pipeline.',
    duration: '15 min',
    level: 'Intermediate',
    category: 'API'
  },
  {
    id: 3,
    title: 'Advanced Schema Design for Complex Datasets',
    description: 'Learn how to create relationships and constraints in your data.',
    duration: '20 min',
    level: 'Advanced',
    category: 'Best Practices'
  },
  {
    id: 4,
    title: 'Exporting Data to Multiple Formats',
    description: 'Export your synthetic data as CSV, JSON, SQL, and more.',
    duration: '10 min',
    level: 'Beginner',
    category: 'Features'
  }
];

const levelColors = {
  'Beginner': 'text-teal-400 bg-teal-500/10',
  'Intermediate': 'text-purple-400 bg-purple-500/10',
  'Advanced': 'text-pink-400 bg-pink-500/10'
};

export default function TutorialsPage() {
  return (
    <div className="min-h-screen bg-black text-white">
      <section className="container mx-auto px-4 py-24">
        <div className="max-w-5xl mx-auto">
          <h1 className="text-5xl sm:text-6xl font-medium mb-6 text-center">
            <span className="gradient-teal-text">Tutorials</span>
          </h1>
          <p className="text-xl text-zinc-400 text-center mb-16">
            Step-by-step guides to master synthetic data generation
          </p>

          <div className="grid gap-6">
            {tutorials.map((tutorial) => (
              <div
                key={tutorial.id}
                className="p-8 rounded-2xl bg-white/5 border border-white/10 hover:border-teal-500/50 transition-all group"
              >
                <div className="flex items-start justify-between gap-4 mb-4">
                  <div className="flex-1">
                    <div className="flex items-center gap-3 mb-3">
                      <BookOpen className="w-5 h-5 text-teal-400" />
                      <span className="text-sm text-zinc-500">{tutorial.category}</span>
                      <span className={`px-3 py-1 rounded-full text-xs ${levelColors[tutorial.level as keyof typeof levelColors]}`}>
                        {tutorial.level}
                      </span>
                      <span className="text-sm text-zinc-500">{tutorial.duration}</span>
                    </div>
                    <h3 className="text-2xl font-medium mb-2 group-hover:text-teal-400 transition-colors">
                      {tutorial.title}
                    </h3>
                    <p className="text-zinc-400">{tutorial.description}</p>
                  </div>
                  <Link href="/docs">
                    <Button variant="ghost" size="sm" className="group/btn">
                      Start
                      <ArrowRight className="ml-2 w-4 h-4 transition-transform group-hover/btn:translate-x-1" />
                    </Button>
                  </Link>
                </div>
              </div>
            ))}
          </div>

          <div className="mt-12 text-center p-8 rounded-2xl bg-white/5 border border-white/10">
            <p className="text-zinc-400 mb-4">
              More tutorials coming soon! Check our documentation for detailed guides.
            </p>
            <Link href="/docs">
              <Button variant="gradient">
                View Documentation
              </Button>
            </Link>
          </div>
        </div>
      </section>
    </div>
  );
}
