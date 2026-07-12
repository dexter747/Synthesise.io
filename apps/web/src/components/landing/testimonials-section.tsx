"use client";

import { useRef, useEffect, useState } from "react";
import { motion, useInView, useAnimationControls } from "framer-motion";
import { Star, Quote } from "lucide-react";

const testimonials = [
  {
    name: "Sarah Chen",
    role: "Senior QA Engineer",
    company: "TechFlow Inc",
    avatar: "SC",
    content: "Synthesize.io cut our test data generation time from hours to minutes. The quality is indistinguishable from real data, and our test coverage has improved dramatically.",
    rating: 5
  },
  {
    name: "Marcus Rodriguez",
    role: "Lead Developer",
    company: "DataDriven Labs",
    avatar: "MR",
    content: "Finally, a synthetic data tool that doesn't cost a fortune! We were paying $3,000/month before. Same quality at 95% less cost. The AI understanding of our data needs is remarkable.",
    rating: 5
  },
  {
    name: "Emily Watson",
    role: "Data Scientist",
    company: "ML Innovations",
    avatar: "EW",
    content: "The relational data generation is a game-changer. Complex foreign key relationships are maintained perfectly. Our ML models now have realistic training data.",
    rating: 5
  },
  {
    name: "James Park",
    role: "CTO",
    company: "StartupXYZ",
    avatar: "JP",
    content: "As a startup, we needed affordable, high-quality test data. Synthesize.io delivers enterprise features at a price we can actually afford. Setup took 5 minutes.",
    rating: 5
  },
  {
    name: "Lisa Thompson",
    role: "DevOps Lead",
    company: "CloudScale Systems",
    avatar: "LT",
    content: "The API integration was seamless. We've automated synthetic data generation in our CI/CD pipeline. Every test environment now gets fresh, unique data automatically.",
    rating: 5
  },
  {
    name: "David Kim",
    role: "Product Manager",
    company: "FinTech Solutions",
    avatar: "DK",
    content: "Compliance was our biggest concern. Synthesize.io's 100% synthetic approach solved our GDPR headaches. No more worrying about using production data in staging.",
    rating: 5
  },
  {
    name: "Anna Kowalski",
    role: "Backend Engineer",
    company: "API Masters",
    avatar: "AK",
    content: "I used to spend days creating mock data for API testing. Now I describe what I need in plain English and get thousands of realistic records instantly.",
    rating: 5
  },
  {
    name: "Michael Brown",
    role: "Engineering Manager",
    company: "ScaleUp Tech",
    avatar: "MB",
    content: "The team loves it. No more fighting over who creates the test data. Self-service access means everyone can generate what they need, when they need it.",
    rating: 5
  }
];

// Duplicate for infinite scroll
const row1 = testimonials.slice(0, 4);
const row2 = testimonials.slice(4, 8);

export function TestimonialsSection() {
  const ref = useRef(null);
  const isInView = useInView(ref, { once: true, margin: "-100px" });

  return (
    <section id="testimonials" ref={ref} className="relative overflow-hidden">

      <div className="container mx-auto px-4">
        {/* Section Header */}
        <motion.div
          initial={{ opacity: 0, y: 30 }}
          animate={isInView ? { opacity: 1, y: 0 } : {}}
          transition={{ duration: 0.6 }}
          className="text-center mb-16"
        >
          <span className="inline-block px-4 py-1.5 rounded-full bg-purple-500/10 border border-purple-500/20 text-purple-400 text-sm font-medium mb-4">
            Testimonials
          </span>
          <h2 className="text-3xl sm:text-4xl lg:text-5xl font-medium text-white mb-4">
            Loved by{" "}
            <span className="gradient-teal-text">Developers</span>{" "}
            Worldwide
          </h2>
          <p className="text-lg text-zinc-400 max-w-2xl mx-auto">
            Join thousands of teams using Synthesize.io for their synthetic data needs.
          </p>
        </motion.div>

        {/* Testimonial Marquee */}
        <div className="space-y-6 overflow-hidden">
          {/* Row 1 - Left to Right */}
          <motion.div
            initial={{ opacity: 0 }}
            animate={isInView ? { opacity: 1 } : {}}
            transition={{ duration: 0.6, delay: 0.2 }}
            className="relative"
          >
            <div className="flex animate-marquee-left gap-6">
              {[...row1, ...row1].map((testimonial, index) => (
                <TestimonialCard key={index} testimonial={testimonial} />
              ))}
            </div>
          </motion.div>

          {/* Row 2 - Right to Left */}
          <motion.div
            initial={{ opacity: 0 }}
            animate={isInView ? { opacity: 1 } : {}}
            transition={{ duration: 0.6, delay: 0.4 }}
            className="relative"
          >
            <div className="flex animate-marquee-right gap-6">
              {[...row2, ...row2].map((testimonial, index) => (
                <TestimonialCard key={index} testimonial={testimonial} />
              ))}
            </div>
          </motion.div>
        </div>
      </div>

      {/* Marquee Animation Styles */}
      <style jsx global>{`
        @keyframes marquee-left {
          0% {
            transform: translateX(0);
          }
          100% {
            transform: translateX(-50%);
          }
        }
        
        @keyframes marquee-right {
          0% {
            transform: translateX(-50%);
          }
          100% {
            transform: translateX(0);
          }
        }
        
        .animate-marquee-left {
          animation: marquee-left 40s linear infinite;
        }
        
        .animate-marquee-right {
          animation: marquee-right 40s linear infinite;
        }
        
        .animate-marquee-left:hover,
        .animate-marquee-right:hover {
          animation-play-state: paused;
        }
      `}</style>
    </section>
  );
}

function TestimonialCard({ testimonial }: { testimonial: typeof testimonials[0] }) {
  return (
    <div className="flex-shrink-0 w-[380px] p-5 bg-black border border-white/10 rounded-sm transition-all duration-300">
      {/* Quote Icon */}
      <Quote className="w-6 h-6 text-teal-500/30 mb-3" />
      
      {/* Rating */}
      <div className="flex gap-1 mb-3">
        {Array.from({ length: testimonial.rating }).map((_, i) => (
          <Star key={i} className="w-3 h-3 fill-yellow-500 text-yellow-500" />
        ))}
      </div>

      {/* Content */}
      <p className="text-zinc-300 mb-4 leading-relaxed text-sm line-clamp-3">
        &ldquo;{testimonial.content}&rdquo;
      </p>

      {/* Author */}
      <div className="flex items-center gap-3">
        <div className="w-8 h-8 rounded-full bg-gradient-to-br from-teal-500 to-emerald-500 flex items-center justify-center text-white font-medium text-xs">
          {testimonial.avatar}
        </div>
        <div>
          <p className="font-medium text-white text-sm">{testimonial.name}</p>
          <p className="text-xs text-zinc-500">
            {testimonial.role} at {testimonial.company}
          </p>
        </div>
      </div>
    </div>
  );
}
