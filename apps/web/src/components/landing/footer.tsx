"use client";

import { useRef } from "react";
import Link from "next/link";
import Image from "next/image";
import { motion, useInView } from "framer-motion";
import { 
  Twitter, 
  Linkedin, 
  Github, 
  ArrowRight
} from "lucide-react";
import { Button } from "@/components/ui/button";

const footerLinks = {
  product: [
    { name: "Features", href: "#features" },
    { name: "Pricing", href: "#pricing" },
    { name: "How It Works", href: "#how-it-works" },
    { name: "API Documentation", href: "/docs/api" },
    { name: "Changelog", href: "/changelog" }
  ],
  resources: [
    { name: "Documentation", href: "/docs" },
    { name: "Tutorials", href: "/tutorials" },
    { name: "FAQ", href: "/faq" },
    { name: "Status Page", href: "/status" },
    { name: "Support", href: "/support" }
  ],
  legal: [
    { name: "Privacy Policy", href: "/legal/privacy" },
    { name: "Terms of Service", href: "/legal/terms" },
    { name: "Refund Policy", href: "/legal/refund" },
    { name: "Cookie Policy", href: "/legal/cookies" },
    { name: "GDPR", href: "/legal/gdpr" }
  ]
};

const socialLinks = [
  { name: "Twitter", icon: Twitter, href: "https://twitter.com/synthesize_io" },
  { name: "LinkedIn", icon: Linkedin, href: "https://linkedin.com/company/synthesize-io" },
  { name: "GitHub", icon: Github, href: "https://github.com/synthesize-io" }
];

export function Footer() {
  const ref = useRef(null);
  const isInView = useInView(ref, { once: true, margin: "-100px" });

  return (
    <footer ref={ref} className="border-t border-white/5 bg-black/50">
      {/* CTA Section */}
      <div className="border-b border-white/5">
        <div className="container mx-auto px-4 py-16">
          <motion.div
            initial={{ opacity: 0, y: 30 }}
            animate={isInView ? { opacity: 1, y: 0 } : {}}
            transition={{ duration: 0.6 }}
            className="max-w-4xl mx-auto text-center"
          >
            <h2 className="text-3xl sm:text-4xl font-medium text-white mb-4">
              Ready to Transform Your{" "}
              <span className="gradient-teal-text">Data Workflow?</span>
            </h2>
            <p className="text-lg text-zinc-400 mb-8 max-w-2xl mx-auto">
              Join thousands of developers who are generating production-quality 
              synthetic data in minutes, not months.
            </p>
            <div className="flex flex-col sm:flex-row items-center justify-center gap-4">
              <Link href="/auth/register">
                <Button variant="gradient" size="lg" className="group">
                  Start Free Trial
                  <ArrowRight className="ml-2 w-4 h-4 transition-transform group-hover:translate-x-1" />
                </Button>
              </Link>
              <Link href="/contact">
                <Button variant="outline" size="lg">
                  Talk to Sales
                </Button>
              </Link>
            </div>
            <p className="mt-6 text-sm text-zinc-500">
              No credit card required • 14-day free trial • Cancel anytime
            </p>
          </motion.div>
        </div>
      </div>

      {/* Main Footer */}
      <div className="container mx-auto px-4 py-16">
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-8 lg:gap-12 max-w-6xl mx-auto">
          {/* Brand Column */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={isInView ? { opacity: 1, y: 0 } : {}}
            transition={{ duration: 0.5 }}
            className="col-span-1"
          >
            <Link href="/" className="flex items-center gap-2 mb-4">
              <div className="w-10 h-10 rounded-xl flex items-center justify-center overflow-hidden">
                <Image
                  src="/logo.svg"
                  alt="Synthesize.io Logo"
                  width={40}
                  height={40}
                  className="object-contain"
                />
              </div>
              <span className="text-xl font-medium text-white">Synthesize</span>
            </Link>
            <p className="text-sm text-zinc-400 mb-6 max-w-xs">
              AI-powered synthetic data generation platform. Create production-quality 
              test data at a fraction of the cost.
            </p>
            <div className="flex items-center gap-3">
              {socialLinks.map((social) => (
                <a
                  key={social.name}
                  href={social.href}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="w-10 h-10 rounded-full bg-white/5 flex items-center justify-center text-zinc-400 hover:text-white hover:bg-white/10 transition-all"
                  aria-label={social.name}
                >
                  <social.icon className="w-5 h-5" />
                </a>
              ))}
            </div>
          </motion.div>

          {/* Product Links */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={isInView ? { opacity: 1, y: 0 } : {}}
            transition={{ duration: 0.5, delay: 0.1 }}
          >
            <h4 className="text-sm font-medium text-white mb-4">Product</h4>
            <ul className="space-y-3">
              {footerLinks.product.map((link) => (
                <li key={link.name}>
                  <Link
                    href={link.href}
                    className="text-sm text-zinc-400 hover:text-white transition-colors"
                  >
                    {link.name}
                  </Link>
                </li>
              ))}
            </ul>
          </motion.div>

          {/* Resources Links */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={isInView ? { opacity: 1, y: 0 } : {}}
            transition={{ duration: 0.5, delay: 0.2 }}
          >
            <h4 className="text-sm font-medium text-white mb-4">Resources</h4>
            <ul className="space-y-3">
              {footerLinks.resources.map((link) => (
                <li key={link.name}>
                  <Link
                    href={link.href}
                    className="text-sm text-zinc-400 hover:text-white transition-colors"
                  >
                    {link.name}
                  </Link>
                </li>
              ))}
            </ul>
          </motion.div>

          {/* Legal Links */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={isInView ? { opacity: 1, y: 0 } : {}}
            transition={{ duration: 0.5, delay: 0.25 }}
          >
            <h4 className="text-sm font-medium text-white mb-4">Legal</h4>
            <ul className="space-y-3">
              {footerLinks.legal.map((link) => (
                <li key={link.name}>
                  <Link
                    href={link.href}
                    className="text-sm text-zinc-400 hover:text-white transition-colors"
                  >
                    {link.name}
                  </Link>
                </li>
              ))}
            </ul>
          </motion.div>
        </div>
      </div>

      {/* Bottom Bar */}
      <div className="border-t border-white/5">
        <div className="container mx-auto px-4 py-6">
          <div className="flex flex-col lg:flex-row items-center justify-between gap-6">
            <div className="flex flex-col sm:flex-row items-center gap-4">
              <span className="text-sm text-white">
                Made with ❤️ for developers worldwide
              </span>
              <span className="hidden sm:block text-white">•</span>
              <p className="text-sm text-white">
                © {new Date().getFullYear()} Synthesize.io. All rights reserved.
              </p>
            </div>
            <div className="flex flex-col sm:flex-row items-center gap-6">
              {/* Dodo Payments */}
              <div className="flex items-center gap-2">
                <span className="text-xs text-white">Payments by</span>
                <Image
                  src="/dodo.svg"
                  alt="Dodo Payments"
                  width={100}
                  height={30}
                  className="object-contain"
                />
              </div>
              
              {/* Nexolve Technologies Credit */}
              <div className="flex items-center gap-2">
                <span className="text-xs text-white">Developed and Maintained by</span>
                <Image
                  src="/nexolve-comp.svg"
                  alt="Nexolve Technologies"
                  width={24}
                  height={24}
                  className="object-contain"
                />
                <a
                  href="https://nexolve.tech"
                  target="_blank"
                  rel="noopener noreferrer"
                  className="text-sm text-white hover:text-teal-400 transition-colors"
                >
                  Nexolve Technologies
                </a>
              </div>
            </div>
          </div>
        </div>
      </div>
    </footer>
  );
}
