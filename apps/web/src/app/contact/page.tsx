'use client';

import { useState } from 'react';
import { Navbar } from '@/components/landing/navbar';
import { Footer } from '@/components/landing/footer';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { motion } from 'framer-motion';
import {
  Mail,
  MapPin,
  Phone,
  Send,
  MessageSquare,
  Building2,
  User,
  FileText,
  Loader2,
  CheckCircle,
  AlertCircle,
  Globe,
  Clock,
  Shield,
} from 'lucide-react';

interface FormData {
  name: string;
  email: string;
  company: string;
  phone: string;
  subject: string;
  message: string;
  category: string;
}

const categories = [
  { value: 'general', label: 'General Inquiry' },
  { value: 'sales', label: 'Sales & Pricing' },
  { value: 'support', label: 'Technical Support' },
  { value: 'partnership', label: 'Partnership' },
  { value: 'other', label: 'Other' },
];

const contactInfo = [
  {
    icon: Mail,
    title: 'Email Us',
    value: 'hello@synthesize.io',
    description: 'For general inquiries',
  },
  {
    icon: MessageSquare,
    title: 'Live Chat',
    value: 'Available 24/7',
    description: 'Get instant help',
  },
  {
    icon: Clock,
    title: 'Response Time',
    value: '< 24 hours',
    description: 'Average response',
  },
];

export default function ContactPage() {
  const [formData, setFormData] = useState<FormData>({
    name: '',
    email: '',
    company: '',
    phone: '',
    subject: '',
    message: '',
    category: 'general',
  });
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [submitStatus, setSubmitStatus] = useState<'idle' | 'success' | 'error'>('idle');
  const [errorMessage, setErrorMessage] = useState('');

  const handleInputChange = (
    e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement | HTMLSelectElement>
  ) => {
    const { name, value } = e.target;
    setFormData((prev) => ({ ...prev, [name]: value }));
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsSubmitting(true);
    setSubmitStatus('idle');
    setErrorMessage('');

    try {
      const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
      const response = await fetch(`${apiUrl}/api/v1/queries/submit`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(formData),
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Failed to submit query');
      }

      setSubmitStatus('success');
      setFormData({
        name: '',
        email: '',
        company: '',
        phone: '',
        subject: '',
        message: '',
        category: 'general',
      });
    } catch (error) {
      setSubmitStatus('error');
      setErrorMessage(error instanceof Error ? error.message : 'Something went wrong');
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <main className="min-h-screen bg-black">
      <Navbar />
      
      {/* Hero Section */}
      <section className="relative pt-32 pb-20 overflow-hidden">
        {/* Background Effects */}
        <div className="absolute inset-0">
          <div className="absolute top-1/4 left-1/4 w-96 h-96 bg-teal-500/10 rounded-full blur-3xl" />
          <div className="absolute bottom-1/4 right-1/4 w-96 h-96 bg-emerald-500/10 rounded-full blur-3xl" />
        </div>
        
        <div className="relative max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6 }}
            className="text-center mb-16"
          >
            <div className="inline-flex items-center gap-2 px-4 py-2 rounded-full bg-teal-500/10 border border-teal-500/20 mb-6">
              <MessageSquare className="w-4 h-4 text-teal-400" />
              <span className="text-sm font-medium text-teal-400">Get in Touch</span>
            </div>
            <h1 className="text-4xl md:text-5xl lg:text-6xl font-medium text-white mb-6">
              Let's Start a{' '}
              <span className="bg-gradient-to-r from-teal-400 to-emerald-400 bg-clip-text text-transparent">
                Conversation
              </span>
            </h1>
            <p className="text-xl text-zinc-400 max-w-2xl mx-auto">
              Have questions about our platform? Want to discuss a partnership? 
              We'd love to hear from you.
            </p>
          </motion.div>

          {/* Contact Info Cards */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6, delay: 0.1 }}
            className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-16"
          >
            {contactInfo.map((info, index) => (
              <div
                key={index}
                className="relative group p-6 rounded-2xl bg-zinc-900/50 border border-white/5 hover:border-teal-500/30 transition-all duration-300"
              >
                <div className="absolute inset-0 bg-gradient-to-br from-teal-500/5 to-transparent rounded-2xl opacity-0 group-hover:opacity-100 transition-opacity" />
                <div className="relative">
                  <div className="w-12 h-12 rounded-xl bg-teal-500/10 flex items-center justify-center mb-4">
                    <info.icon className="w-6 h-6 text-teal-400" />
                  </div>
                  <h3 className="text-white font-medium mb-1">{info.title}</h3>
                  <p className="text-teal-400 font-medium">{info.value}</p>
                  <p className="text-zinc-500 text-sm mt-1">{info.description}</p>
                </div>
              </div>
            ))}
          </motion.div>

          {/* Main Content Grid */}
          <div className="grid grid-cols-1 lg:grid-cols-5 gap-8">
            {/* Contact Form */}
            <motion.div
              initial={{ opacity: 0, x: -20 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ duration: 0.6, delay: 0.2 }}
              className="lg:col-span-3"
            >
              <div className="relative p-8 rounded-3xl bg-zinc-900/50 border border-white/5 backdrop-blur-xl">
                <div className="absolute top-0 left-0 right-0 h-1 bg-gradient-to-r from-teal-500 to-emerald-500 rounded-t-3xl" />
                
                <h2 className="text-2xl font-medium text-white mb-2">Send us a Message</h2>
                <p className="text-zinc-400 mb-8">Fill out the form below and we'll get back to you shortly.</p>

                {submitStatus === 'success' ? (
                  <motion.div
                    initial={{ opacity: 0, scale: 0.95 }}
                    animate={{ opacity: 1, scale: 1 }}
                    className="text-center py-12"
                  >
                    <div className="w-20 h-20 rounded-full bg-teal-500/10 flex items-center justify-center mx-auto mb-6">
                      <CheckCircle className="w-10 h-10 text-teal-400" />
                    </div>
                    <h3 className="text-xl font-medium text-white mb-2">Message Sent!</h3>
                    <p className="text-zinc-400 mb-6">
                      Thank you for reaching out. We'll get back to you within 24 hours.
                    </p>
                    <Button
                      onClick={() => setSubmitStatus('idle')}
                      className="bg-teal-500 hover:bg-teal-600 text-white"
                    >
                      Send Another Message
                    </Button>
                  </motion.div>
                ) : (
                  <form onSubmit={handleSubmit} className="space-y-6">
                    {submitStatus === 'error' && (
                      <div className="p-4 rounded-xl bg-red-500/10 border border-red-500/20 flex items-start gap-3">
                        <AlertCircle className="w-5 h-5 text-red-400 flex-shrink-0 mt-0.5" />
                        <div>
                          <p className="text-red-400 font-medium">Failed to send message</p>
                          <p className="text-red-400/70 text-sm">{errorMessage}</p>
                        </div>
                      </div>
                    )}

                    {/* Name & Email */}
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                      <div className="space-y-2">
                        <label className="text-sm font-medium text-zinc-300 flex items-center gap-2">
                          <User className="w-4 h-4" />
                          Full Name *
                        </label>
                        <Input
                          name="name"
                          value={formData.name}
                          onChange={handleInputChange}
                          placeholder="John Doe"
                          required
                          className="h-12 bg-black/50 border-white/10 focus:border-teal-500/50 placeholder:text-zinc-600"
                        />
                      </div>
                      <div className="space-y-2">
                        <label className="text-sm font-medium text-zinc-300 flex items-center gap-2">
                          <Mail className="w-4 h-4" />
                          Email Address *
                        </label>
                        <Input
                          name="email"
                          type="email"
                          value={formData.email}
                          onChange={handleInputChange}
                          placeholder="john@company.com"
                          required
                          className="h-12 bg-black/50 border-white/10 focus:border-teal-500/50 placeholder:text-zinc-600"
                        />
                      </div>
                    </div>

                    {/* Company & Phone */}
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                      <div className="space-y-2">
                        <label className="text-sm font-medium text-zinc-300 flex items-center gap-2">
                          <Building2 className="w-4 h-4" />
                          Company
                        </label>
                        <Input
                          name="company"
                          value={formData.company}
                          onChange={handleInputChange}
                          placeholder="Your Company"
                          className="h-12 bg-black/50 border-white/10 focus:border-teal-500/50 placeholder:text-zinc-600"
                        />
                      </div>
                      <div className="space-y-2">
                        <label className="text-sm font-medium text-zinc-300 flex items-center gap-2">
                          <Phone className="w-4 h-4" />
                          Phone Number
                        </label>
                        <Input
                          name="phone"
                          type="tel"
                          value={formData.phone}
                          onChange={handleInputChange}
                          placeholder="+1 (555) 000-0000"
                          className="h-12 bg-black/50 border-white/10 focus:border-teal-500/50 placeholder:text-zinc-600"
                        />
                      </div>
                    </div>

                    {/* Category */}
                    <div className="space-y-2">
                      <label className="text-sm font-medium text-zinc-300 flex items-center gap-2">
                        <FileText className="w-4 h-4" />
                        Inquiry Type
                      </label>
                      <select
                        name="category"
                        value={formData.category}
                        onChange={handleInputChange}
                        className="w-full h-12 px-4 rounded-lg bg-black/50 border border-white/10 text-white placeholder:text-zinc-600 focus:border-teal-500/50 focus:outline-none focus:ring-1 focus:ring-teal-500/50 transition-colors hover:border-white/20 cursor-pointer appearance-none bg-[url('data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iMTIiIGhlaWdodD0iOCIgdmlld0JveD0iMCAwIDEyIDgiIGZpbGw9Im5vbmUiIHhtbG5zPSJodHRwOi8vd3d3LnczLm9yZy8yMDAwL3N2ZyI+PHBhdGggZD0iTTEgMUw2IDZMMTEgMSIgc3Ryb2tlPSIjNzE3MTcxIiBzdHJva2Utd2lkdGg9IjIiIHN0cm9rZS1saW5lY2FwPSJyb3VuZCIgc3Ryb2tlLWxpbmVqb2luPSJyb3VuZCIvPjwvc3ZnPg==')] bg-[length:12px_8px] bg-[right_1rem_center] bg-no-repeat pr-12"
                      >
                        {categories.map((cat) => (
                          <option key={cat.value} value={cat.value} className="bg-zinc-900 text-white py-2">
                            {cat.label}
                          </option>
                        ))}
                      </select>
                    </div>

                    {/* Subject */}
                    <div className="space-y-2">
                      <label className="text-sm font-medium text-zinc-300 flex items-center gap-2">
                        <FileText className="w-4 h-4" />
                        Subject *
                      </label>
                      <Input
                        name="subject"
                        value={formData.subject}
                        onChange={handleInputChange}
                        placeholder="How can we help you?"
                        required
                        className="h-12 bg-black/50 border-white/10 focus:border-teal-500/50 placeholder:text-zinc-600"
                      />
                    </div>

                    {/* Message */}
                    <div className="space-y-2">
                      <label className="text-sm font-medium text-zinc-300 flex items-center gap-2">
                        <MessageSquare className="w-4 h-4" />
                        Message *
                      </label>
                      <textarea
                        name="message"
                        value={formData.message}
                        onChange={handleInputChange}
                        placeholder="Tell us more about your inquiry..."
                        required
                        rows={5}
                        className="w-full px-4 py-3 rounded-lg bg-black/50 border border-white/10 text-white placeholder:text-zinc-600 focus:border-teal-500/50 focus:outline-none focus:ring-1 focus:ring-teal-500/50 resize-none"
                      />
                    </div>

                    {/* Submit Button */}
                    <Button
                      type="submit"
                      disabled={isSubmitting}
                      className="w-full h-12 bg-gradient-to-r from-teal-500 to-emerald-500 hover:from-teal-600 hover:to-emerald-600 text-white font-medium text-base"
                    >
                      {isSubmitting ? (
                        <>
                          <Loader2 className="w-5 h-5 mr-2 animate-spin" />
                          Sending...
                        </>
                      ) : (
                        <>
                          <Send className="w-5 h-5 mr-2" />
                          Send Message
                        </>
                      )}
                    </Button>
                  </form>
                )}
              </div>
            </motion.div>

            {/* Sidebar */}
            <motion.div
              initial={{ opacity: 0, x: 20 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ duration: 0.6, delay: 0.3 }}
              className="lg:col-span-2 space-y-6"
            >
              {/* Quick Help */}
              <div className="p-6 rounded-2xl bg-zinc-900/50 border border-white/5">
                <h3 className="text-lg font-medium text-white mb-4">Quick Help</h3>
                <div className="space-y-3">
                  <a
                    href="/docs"
                    className="flex items-center gap-3 p-3 rounded-xl bg-black/30 hover:bg-teal-500/10 border border-transparent hover:border-teal-500/20 transition-all group"
                  >
                    <div className="w-10 h-10 rounded-lg bg-teal-500/10 flex items-center justify-center">
                      <FileText className="w-5 h-5 text-teal-400" />
                    </div>
                    <div>
                      <p className="text-white font-medium group-hover:text-teal-400 transition-colors">Documentation</p>
                      <p className="text-zinc-500 text-sm">Browse our guides</p>
                    </div>
                  </a>
                  <a
                    href="/support"
                    className="flex items-center gap-3 p-3 rounded-xl bg-black/30 hover:bg-teal-500/10 border border-transparent hover:border-teal-500/20 transition-all group"
                  >
                    <div className="w-10 h-10 rounded-lg bg-teal-500/10 flex items-center justify-center">
                      <MessageSquare className="w-5 h-5 text-teal-400" />
                    </div>
                    <div>
                      <p className="text-white font-medium group-hover:text-teal-400 transition-colors">Support Center</p>
                      <p className="text-zinc-500 text-sm">FAQs & help articles</p>
                    </div>
                  </a>
                </div>
              </div>

              {/* Enterprise */}
              <div className="relative p-6 rounded-2xl bg-gradient-to-br from-teal-500/10 to-emerald-500/10 border border-teal-500/20 overflow-hidden">
                <div className="absolute -top-10 -right-10 w-40 h-40 bg-teal-500/10 rounded-full blur-3xl" />
                <div className="relative">
                  <div className="w-12 h-12 rounded-xl bg-teal-500/20 flex items-center justify-center mb-4">
                    <Building2 className="w-6 h-6 text-teal-400" />
                  </div>
                  <h3 className="text-lg font-medium text-white mb-2">Enterprise Solutions</h3>
                  <p className="text-zinc-400 text-sm mb-4">
                    Need custom solutions for your organization? Let's discuss your requirements.
                  </p>
                  <a
                    href="/pricing#enterprise"
                    className="w-full flex items-center justify-center px-4 py-2 rounded-lg border border-teal-500/30 text-teal-400 hover:bg-teal-500/10 transition-colors text-sm font-medium"
                  >
                    Learn More
                  </a>
                </div>
              </div>

              {/* Security Note */}
              <div className="p-6 rounded-2xl bg-zinc-900/50 border border-white/5">
                <div className="flex items-start gap-4">
                  <div className="w-10 h-10 rounded-lg bg-zinc-800 flex items-center justify-center flex-shrink-0">
                    <Shield className="w-5 h-5 text-zinc-400" />
                  </div>
                  <div>
                    <h4 className="text-white font-medium mb-1">Your data is safe</h4>
                    <p className="text-zinc-500 text-sm">
                      We use industry-standard encryption and never share your information with third parties.
                    </p>
                  </div>
                </div>
              </div>
            </motion.div>
          </div>
        </div>
      </section>

      <Footer />
    </main>
  );
}
