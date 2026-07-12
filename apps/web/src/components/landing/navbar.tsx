"use client";

import { useState, useEffect, useRef } from "react";
import Link from "next/link";
import Image from "next/image";
import { cn } from "@/lib/utils";
import { Button } from "@/components/ui/button";
import { Menu, X, ChevronDown, DollarSign, Zap, Shield, Clock, Database, FileJson } from "lucide-react";
import { motion, AnimatePresence } from "framer-motion";

const featureItems = [
  { href: "/features/cost-savings", label: "95% Cost Savings", icon: DollarSign, description: "Pay-as-you-go pricing" },
  { href: "/features/instant-generation", label: "Instant Generation", icon: Zap, description: "1M+ rows per minute" },
  { href: "/features/privacy-compliance", label: "Privacy Compliant", icon: Shield, description: "GDPR, HIPAA, CCPA ready" },
  { href: "/features/quick-setup", label: "5-Minute Setup", icon: Clock, description: "No-code UI & API ready" },
  { href: "/features/relational-data", label: "Relational Data", icon: Database, description: "Foreign keys & integrity" },
  { href: "/features/multiple-formats", label: "Multiple Formats", icon: FileJson, description: "CSV, JSON, SQL, Parquet" },
];

const navLinks = [
  { href: "#how-it-works", label: "How It Works" },
  { href: "#pricing", label: "Pricing" },
  { href: "#testimonials", label: "Testimonials" },
  { href: "/contact", label: "Contact" },
];

export function Navbar() {
  const [isScrolled, setIsScrolled] = useState(false);
  const [isMobileMenuOpen, setIsMobileMenuOpen] = useState(false);
  const [isFeaturesOpen, setIsFeaturesOpen] = useState(false);
  const featuresRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const handleScroll = () => {
      setIsScrolled(window.scrollY > 20);
    };
    window.addEventListener("scroll", handleScroll);
    return () => window.removeEventListener("scroll", handleScroll);
  }, []);

  // Close dropdown when clicking outside
  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (featuresRef.current && !featuresRef.current.contains(event.target as Node)) {
        setIsFeaturesOpen(false);
      }
    };
    document.addEventListener("mousedown", handleClickOutside);
    return () => document.removeEventListener("mousedown", handleClickOutside);
  }, []);

  return (
    <>
      <div className="fixed top-4 left-0 right-0 z-50 flex justify-center px-4 transition-all duration-500">
        <nav
          className={cn(
            "transition-all duration-500",
            isScrolled ? "-translate-y-2" : ""
          )}
        >
          <motion.div
            initial={{ y: -100, opacity: 0 }}
            animate={{ y: 0, opacity: 1 }}
            transition={{ duration: 0.6, ease: "easeOut" }}
            className={cn(
                  "flex items-center justify-between px-4 gap-24 py-1 transition-all duration-300 w-full",
                  isScrolled
                    ? "bg-black/40 backdrop-blur-3xl backdrop-saturate-200 shadow-2xl shadow-black/40"
                    : "bg-white/3 backdrop-blur-3xl backdrop-saturate-150"
            )}
                style={{ maxWidth: '98vw' }}
          >
          {/* Logo */}
          <Link
            href="/"
            className="flex items-center gap-2 px-3 py-1.5 rounded-sm hover:bg-white/5 transition-colors flex-shrink-0 mr-8"
          >
            <div className="relative">
              <div className="w-8 h-8 rounded-sm flex items-center justify-center overflow-hidden">
                <Image
                  src="/logo.svg"
                  alt="Synthesize.io Logo"
                  width={32}
                  height={32}
                  className="object-contain"
                />
              </div>
            </div>
            <span className="font-medium text-lg text-white hidden sm:block">
              Synthesize
            </span>
          </Link>

          {/* Desktop Navigation */}
          <div className="hidden md:flex items-center px-4 flex-1 justify-center">
            {/* Features Dropdown */}
            <div ref={featuresRef} className="relative">
              <button
                onClick={() => setIsFeaturesOpen(!isFeaturesOpen)}
                onMouseEnter={() => setIsFeaturesOpen(true)}
                className="flex items-center gap-1 px-3 py-2 text-sm font-medium text-zinc-400 hover:text-white transition-all duration-200"
              >
                Features
                <ChevronDown className={cn("w-4 h-4 transition-transform duration-200", isFeaturesOpen && "rotate-180")} />
              </button>

              <AnimatePresence>
                {isFeaturesOpen && (
                  <motion.div
                    initial={{ opacity: 0, y: 10, scale: 0.95 }}
                    animate={{ opacity: 1, y: 0, scale: 1 }}
                    exit={{ opacity: 0, y: 10, scale: 0.95 }}
                    transition={{ duration: 0.2 }}
                    onMouseLeave={() => setIsFeaturesOpen(false)}
                    className="absolute top-full left-1/2 -translate-x-1/2 mt-2 w-80 bg-black/95 backdrop-blur-xl border border-white/10 rounded-xl shadow-2xl shadow-black/50 overflow-hidden z-50"
                  >
                    <div className="p-2">
                      <div className="px-3 py-2 mb-1">
                        <span className="text-xs font-medium text-teal-400 uppercase tracking-wider">Features</span>
                      </div>
                      {featureItems.map((item, index) => (
                        <Link
                          key={item.href}
                          href={item.href}
                          onClick={() => setIsFeaturesOpen(false)}
                          className="block px-3 py-2.5 rounded-lg hover:bg-white/5 transition-colors group"
                        >
                          <div className="text-sm font-medium text-white group-hover:text-teal-400 transition-colors">
                            {item.label}
                          </div>
                          <div className="text-xs text-zinc-500">{item.description}</div>
                        </Link>
                      ))}
                      <div className="border-t border-white/5 mt-2 pt-2">
                        <Link
                          href="/features"
                          onClick={() => setIsFeaturesOpen(false)}
                          className="flex items-center justify-center gap-2 px-3 py-2 text-sm font-medium text-teal-400 hover:text-teal-300 hover:bg-teal-500/10 rounded-lg transition-colors"
                        >
                          View All Features
                          <ChevronDown className="w-4 h-4 -rotate-90" />
                        </Link>
                      </div>
                    </div>
                  </motion.div>
                )}
              </AnimatePresence>
            </div>

            {navLinks.map((link) => (
              <Link
                key={link.href}
                href={link.href}
                className="px-3 py-2 text-sm font-medium text-zinc-400 hover:text-white transition-all duration-200"
              >
                {link.label}
              </Link>
            ))}
          </div>

          {/* CTA Buttons */}
          <div className="flex items-center gap-2 flex-shrink-0 ml-8">
            <Link 
              href="/auth/login"
              className="px-4 py-2 text-sm font-medium bg-gradient-to-r from-teal-500 to-emerald-500 text-white rounded hover:from-teal-600 hover:to-emerald-600 transition-all"
            >
              Sign In
            </Link>

            {/* Mobile Menu Toggle */}
            <button
              onClick={() => setIsMobileMenuOpen(!isMobileMenuOpen)}
              className="md:hidden p-2 rounded hover:bg-white/5 transition-colors"
            >
              {isMobileMenuOpen ? (
                <X className="w-5 h-5 text-white" />
              ) : (
                <Menu className="w-5 h-5 text-white" />
              )}
            </button>
          </div>
        </motion.div>
        </nav>
      </div>

      {/* Mobile Menu */}
      <AnimatePresence>
        {isMobileMenuOpen && (
          <motion.div
            initial={{ opacity: 0, y: -20 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -20 }}
            transition={{ duration: 0.2 }}
            className="fixed top-20 left-4 right-4 z-40 md:hidden"
          >
            <div className="bg-black/95 backdrop-blur-xl border border-white/10 rounded-xl p-4 shadow-2xl max-h-[80vh] overflow-y-auto">
              {/* Features Section */}
              <div className="mb-4">
                <div className="px-4 py-2 text-xs font-medium text-teal-400 uppercase tracking-wider">
                  Features
                </div>
                {featureItems.map((item, index) => (
                  <motion.div
                    key={item.href}
                    initial={{ opacity: 0, x: -20 }}
                    animate={{ opacity: 1, x: 0 }}
                    transition={{ delay: index * 0.05 }}
                  >
                    <Link
                      href={item.href}
                      onClick={() => setIsMobileMenuOpen(false)}
                      className="block px-4 py-3 text-base font-medium text-zinc-300 hover:text-white hover:bg-white/5 rounded-lg transition-colors"
                    >
                      {item.label}
                    </Link>
                  </motion.div>
                ))}
                <motion.div
                  initial={{ opacity: 0, x: -20 }}
                  animate={{ opacity: 1, x: 0 }}
                  transition={{ delay: featureItems.length * 0.05 }}
                >
                  <Link
                    href="/features"
                    onClick={() => setIsMobileMenuOpen(false)}
                    className="flex items-center gap-3 px-4 py-3 text-base font-medium text-teal-400 hover:text-teal-300 hover:bg-teal-500/10 rounded-lg transition-colors"
                  >
                    View All Features →
                  </Link>
                </motion.div>
              </div>

              <div className="border-t border-white/10 pt-4">
                {navLinks.map((link, index) => (
                  <motion.div
                    key={link.href}
                    initial={{ opacity: 0, x: -20 }}
                    animate={{ opacity: 1, x: 0 }}
                    transition={{ delay: (featureItems.length + index) * 0.05 }}
                  >
                    <Link
                      href={link.href}
                      onClick={() => setIsMobileMenuOpen(false)}
                      className="block px-4 py-3 text-base font-medium text-zinc-300 hover:text-white hover:bg-white/5 rounded transition-colors"
                    >
                      {link.label}
                    </Link>
                  </motion.div>
                ))}
              </div>
              
              <div className="mt-4 pt-4 border-t border-white/10">
                <Link href="/auth/login" className="block">
                  <button className="w-full py-2 px-4 bg-gradient-to-r from-teal-500 to-emerald-500 text-white rounded font-medium hover:from-teal-600 hover:to-emerald-600 transition-all">
                    Sign In
                  </button>
                </Link>
              </div>
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </>
  );
}
