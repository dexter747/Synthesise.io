import { Metadata } from 'next';
import { Calendar, Plus, Bug, Zap } from 'lucide-react';

export const metadata: Metadata = {
  title: 'Changelog - Synthesize.io',
  description: 'Latest updates, features, and improvements to Synthesize.io.',
};

const updates = [
  {
    version: 'v1.2.0',
    date: '2026-01-15',
    changes: [
      { type: 'feature', text: 'Added Beginner plan at $19/month for solo developers' },
      { type: 'feature', text: 'New bulk CSV import for schema definition' },
      { type: 'improvement', text: 'Improved data generation speed by 40%' },
      { type: 'fix', text: 'Fixed edge case in date field generation' }
    ]
  },
  {
    version: 'v1.1.0',
    date: '2026-01-01',
    changes: [
      { type: 'feature', text: 'Real-time collaboration on dataset templates' },
      { type: 'feature', text: 'API key management dashboard' },
      { type: 'improvement', text: 'Enhanced webhook delivery monitoring' },
      { type: 'fix', text: 'Resolved timezone issues in exports' }
    ]
  },
  {
    version: 'v1.0.0',
    date: '2025-12-15',
    changes: [
      { type: 'feature', text: '🎉 Initial public release!' },
      { type: 'feature', text: 'AI-powered data generation' },
      { type: 'feature', text: 'REST API with comprehensive documentation' },
      { type: 'feature', text: 'Export to CSV, JSON, SQL formats' }
    ]
  }
];

const typeIcons = {
  feature: Plus,
  improvement: Zap,
  fix: Bug
};

const typeColors = {
  feature: 'text-teal-400 bg-teal-500/10',
  improvement: 'text-purple-400 bg-purple-500/10',
  fix: 'text-pink-400 bg-pink-500/10'
};

export default function ChangelogPage() {
  return (
    <div className="min-h-screen bg-black text-white">
      <section className="container mx-auto px-4 py-24">
        <div className="max-w-4xl mx-auto">
          <h1 className="text-5xl sm:text-6xl font-medium mb-6 text-center">
            <span className="gradient-teal-text">Changelog</span>
          </h1>
          <p className="text-xl text-zinc-400 text-center mb-16">
            Track all updates, features, and improvements
          </p>

          <div className="space-y-12">
            {updates.map((update) => (
              <div key={update.version} className="relative pl-8 border-l-2 border-white/10">
                <div className="absolute -left-2 top-0 w-4 h-4 rounded-full bg-teal-500" />
                <div className="mb-4">
                  <div className="flex items-center gap-4 mb-2">
                    <h2 className="text-2xl font-medium">{update.version}</h2>
                    <div className="flex items-center gap-2 text-sm text-zinc-500">
                      <Calendar className="w-4 h-4" />
                      {new Date(update.date).toLocaleDateString('en-US', { 
                        month: 'long', 
                        day: 'numeric', 
                        year: 'numeric' 
                      })}
                    </div>
                  </div>
                </div>
                <ul className="space-y-3">
                  {update.changes.map((change, index) => {
                    const Icon = typeIcons[change.type as keyof typeof typeIcons];
                    const colorClass = typeColors[change.type as keyof typeof typeColors];
                    return (
                      <li key={index} className="flex items-start gap-3">
                        {Icon && (
                          <span className={`p-1.5 rounded-lg ${colorClass} flex-shrink-0`}>
                            <Icon className="w-4 h-4" />
                          </span>
                        )}
                        <span className="text-zinc-300">{change.text}</span>
                      </li>
                    );
                  })}
                </ul>
              </div>
            ))}
          </div>
        </div>
      </section>
    </div>
  );
}
