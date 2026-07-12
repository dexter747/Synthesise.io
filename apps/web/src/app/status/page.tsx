import { Metadata } from 'next';
import { CheckCircle, AlertCircle, Clock } from 'lucide-react';

export const metadata: Metadata = {
  title: 'Status - Synthesize.io',
  description: 'Real-time status and uptime monitoring for Synthesize.io services.',
};

const services = [
  { name: 'API', status: 'operational', uptime: '99.99%' },
  { name: 'Web Application', status: 'operational', uptime: '99.98%' },
  { name: 'Data Generation', status: 'operational', uptime: '99.95%' },
  { name: 'Authentication', status: 'operational', uptime: '100%' },
  { name: 'Payment Processing', status: 'operational', uptime: '99.99%' },
  { name: 'Webhook Delivery', status: 'operational', uptime: '99.92%' }
];

const incidents = [
  {
    date: '2026-01-10',
    title: 'Elevated API Latency',
    description: 'Brief increase in API response times resolved within 15 minutes.',
    status: 'resolved',
    duration: '15 min'
  }
];

const statusIcons = {
  operational: CheckCircle,
  degraded: AlertCircle,
  outage: AlertCircle
};

const statusColors = {
  operational: 'text-teal-400',
  degraded: 'text-yellow-400',
  outage: 'text-red-400'
};

export default function StatusPage() {
  const allOperational = services.every(s => s.status === 'operational');

  return (
    <div className="min-h-screen bg-black text-white">
      <section className="container mx-auto px-4 py-24">
        <div className="max-w-5xl mx-auto">
          {/* Overall Status */}
          <div className="text-center mb-16">
            <div className="inline-flex items-center gap-3 mb-4">
              {allOperational ? (
                <>
                  <CheckCircle className="w-12 h-12 text-teal-400" />
                  <h1 className="text-4xl font-medium">
                    <span className="gradient-teal-text">All Systems Operational</span>
                  </h1>
                </>
              ) : (
                <>
                  <AlertCircle className="w-12 h-12 text-yellow-400" />
                  <h1 className="text-4xl font-medium">
                    <span className="text-yellow-400">Some Services Degraded</span>
                  </h1>
                </>
              )}
            </div>
            <p className="text-zinc-400">
              Last updated: {new Date().toLocaleString()}
            </p>
          </div>

          {/* Services Status */}
          <div className="mb-16">
            <h2 className="text-2xl font-medium mb-6">Service Status</h2>
            <div className="space-y-3">
              {services.map((service) => {
                const Icon = statusIcons[service.status as keyof typeof statusIcons];
                const colorClass = statusColors[service.status as keyof typeof statusColors];
                return (
                  <div
                    key={service.name}
                    className="flex items-center justify-between p-6 rounded-xl bg-white/5 border border-white/10"
                  >
                    <div className="flex items-center gap-4">
                      <Icon className={`w-6 h-6 ${colorClass}`} />
                      <span className="text-lg font-medium">{service.name}</span>
                    </div>
                    <div className="flex items-center gap-8">
                      <span className="text-sm text-zinc-500">
                        {service.uptime} uptime
                      </span>
                      <span className={`capitalize ${colorClass}`}>
                        {service.status}
                      </span>
                    </div>
                  </div>
                );
              })}
            </div>
          </div>

          {/* Incident History */}
          <div>
            <h2 className="text-2xl font-medium mb-6">Recent Incidents</h2>
            {incidents.length > 0 ? (
              <div className="space-y-4">
                {incidents.map((incident, index) => (
                  <div
                    key={index}
                    className="p-6 rounded-xl bg-white/5 border border-white/10"
                  >
                    <div className="flex items-start justify-between gap-4 mb-3">
                      <div>
                        <h3 className="text-lg font-medium mb-1">{incident.title}</h3>
                        <div className="flex items-center gap-4 text-sm text-zinc-500">
                          <span>{new Date(incident.date).toLocaleDateString()}</span>
                          <span className="flex items-center gap-1">
                            <Clock className="w-4 h-4" />
                            {incident.duration}
                          </span>
                        </div>
                      </div>
                      <span className="px-3 py-1 rounded-full bg-teal-500/10 text-teal-400 text-sm">
                        Resolved
                      </span>
                    </div>
                    <p className="text-zinc-400">{incident.description}</p>
                  </div>
                ))}
              </div>
            ) : (
              <div className="p-12 rounded-xl bg-white/5 border border-white/10 text-center">
                <CheckCircle className="w-16 h-16 text-teal-400 mx-auto mb-4" />
                <p className="text-lg text-zinc-400">
                  No incidents in the past 90 days
                </p>
              </div>
            )}
          </div>

          {/* Subscribe */}
          <div className="mt-16 text-center p-8 rounded-2xl bg-gradient-to-br from-teal-500/10 to-purple-500/10 border border-white/10">
            <h3 className="text-xl font-medium mb-2">Get Status Updates</h3>
            <p className="text-zinc-400">
              Subscribe to receive notifications about service disruptions
            </p>
          </div>
        </div>
      </section>
    </div>
  );
}
