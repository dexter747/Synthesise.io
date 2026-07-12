import { Metadata } from 'next';
import Link from 'next/link';
import { Button } from '@/components/ui/button';
import { Calendar, Clock, ArrowRight } from 'lucide-react';
import { getAllBlogPosts } from '@/lib/blogs';

export const metadata: Metadata = {
  title: 'Blog - Synthesize.io',
  description: 'Latest news, tutorials, and insights about synthetic data generation.',
};

export default function BlogPage() {
  const blogPosts = getAllBlogPosts();
  
  return (
    <div className="min-h-screen bg-black text-white">
      {/* Hero */}
      <section className="container mx-auto px-4 py-24">
        <div className="max-w-4xl mx-auto text-center">
          <h1 className="text-5xl sm:text-6xl font-medium mb-6">
            Latest from{' '}
            <span className="gradient-teal-text">Synthesize.io</span>
          </h1>
          <p className="text-xl text-zinc-400">
            News, tutorials, and insights about synthetic data generation
          </p>
        </div>
      </section>

      {/* Blog Posts */}
      <section className="container mx-auto px-4 pb-24">
        <div className="max-w-5xl mx-auto">
          <div className="grid gap-8">
            {blogPosts.map((post) => (
              <article
                key={post.slug}
                className="p-8 rounded-2xl bg-white/5 border border-white/10 hover:border-teal-500/50 transition-all group"
              >
                <div className="flex items-center gap-4 mb-4">
                  <span className="px-3 py-1 rounded-full bg-teal-500/10 text-teal-400 text-sm">
                    {post.category}
                  </span>
                  <div className="flex items-center gap-2 text-sm text-zinc-500">
                    <Calendar className="w-4 h-4" />
                    {new Date(post.publishedAt).toLocaleDateString('en-US', { 
                      month: 'short', 
                      day: 'numeric', 
                      year: 'numeric' 
                    })}
                  </div>
                  <div className="flex items-center gap-2 text-sm text-zinc-500">
                    <Clock className="w-4 h-4" />
                    {post.readingTime} min read
                  </div>
                </div>
                <h2 className="text-2xl font-medium mb-3 group-hover:text-teal-400 transition-colors">
                  {post.title}
                </h2>
                <p className="text-zinc-400 mb-4">
                  {post.excerpt}
                </p>
                <Link 
                  href={`/blog/${post.slug}`}
                  className="inline-flex items-center text-teal-400 hover:text-teal-300 transition-colors"
                >
                  Read more
                  <ArrowRight className="ml-2 w-4 h-4" />
                </Link>
              </article>
            ))}
          </div>

          {/* Coming Soon Message */}
          <div className="mt-12 text-center p-8 rounded-2xl bg-white/5 border border-white/10">
            <p className="text-zinc-400">
              More articles coming soon! Subscribe to our newsletter to stay updated.
            </p>
            <Link href="/contact">
              <Button variant="outline" className="mt-4">
                Subscribe to Updates
              </Button>
            </Link>
          </div>
        </div>
      </section>
    </div>
  );
}
