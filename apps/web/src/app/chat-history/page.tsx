'use client';

import { useState } from 'react';
import { useRouter } from 'next/navigation';
import { DashboardLayout } from '@/components/layouts/dashboard-layout';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { useChatHistory } from '@/hooks/use-chat-history';
import { toast } from 'sonner';
import {
  MessageSquare,
  Trash2,
  Clock,
  ArrowRight,
  Database,
  Search,
  Plus,
  FileText,
  Sparkles,
  ChevronRight,
} from 'lucide-react';

export default function ChatHistoryPage() {
  const router = useRouter();
  const chatHistory = useChatHistory();
  const [searchQuery, setSearchQuery] = useState('');

  const filteredSessions = chatHistory.sessions.filter(session => {
    if (!searchQuery) return true;
    const q = searchQuery.toLowerCase();
    return (
      session.title.toLowerCase().includes(q) ||
      session.preview.toLowerCase().includes(q) ||
      session.messages.some(m => m.content.toLowerCase().includes(q))
    );
  });

  const formatDate = (dateString: string) => {
    const date = new Date(dateString);
    const now = new Date();
    const diffMs = now.getTime() - date.getTime();
    const diffMins = Math.floor(diffMs / 60000);
    const diffHours = Math.floor(diffMins / 60);
    const diffDays = Math.floor(diffHours / 24);

    if (diffMins < 1) return 'Just now';
    if (diffMins < 60) return `${diffMins}m ago`;
    if (diffHours < 24) return `${diffHours}h ago`;
    if (diffDays === 1) return 'Yesterday';
    if (diffDays < 7) return `${diffDays}d ago`;
    return date.toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: date.getFullYear() !== now.getFullYear() ? 'numeric' : undefined });
  };

  const getStatusBadge = (status: string) => {
    switch (status) {
      case 'completed':
        return <Badge variant="default" className="bg-green-500/20 text-green-400 border-green-500/30 text-xs">Completed</Badge>;
      case 'error':
        return <Badge variant="default" className="bg-red-500/20 text-red-400 border-red-500/30 text-xs">Error</Badge>;
      default:
        return <Badge variant="outline" className="text-xs">Active</Badge>;
    }
  };

  const handleLoadSession = (sessionId: string) => {
    chatHistory.loadSession(sessionId);
    router.push('/dashboard');
  };

  const handleDeleteSession = (e: React.MouseEvent, sessionId: string) => {
    e.stopPropagation();
    chatHistory.deleteSession(sessionId);
    toast.success('Chat session deleted');
  };

  const handleClearAll = () => {
    if (confirm('Are you sure you want to clear all chat history? This cannot be undone.')) {
      chatHistory.clearAllSessions();
      toast.success('All chat history cleared');
    }
  };

  return (
    <DashboardLayout>
      <div className="space-y-6 max-w-4xl mx-auto">
        {/* Header */}
        <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
          <div>
            <h1 className="text-2xl font-medium text-white">Chat History</h1>
            <p className="text-zinc-400 mt-1">
              View and resume past data generation conversations
            </p>
          </div>
          <div className="flex gap-2">
            {chatHistory.sessions.length > 0 && (
              <Button variant="outline" size="sm" onClick={handleClearAll}>
                <Trash2 className="w-4 h-4 mr-2" />
                Clear All
              </Button>
            )}
            <Button variant="gradient" size="sm" onClick={() => router.push('/dashboard')}>
              <Plus className="w-4 h-4 mr-2" />
              New Chat
            </Button>
          </div>
        </div>

        {/* Search */}
        {chatHistory.sessions.length > 0 && (
          <div className="relative">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-zinc-500" />
            <input
              type="text"
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              placeholder="Search conversations..."
              className="w-full pl-10 pr-4 py-2.5 bg-white/5 border border-white/10 rounded-xl text-white text-sm placeholder-zinc-500 focus:border-teal-500 focus:ring-1 focus:ring-teal-500 transition-colors"
            />
          </div>
        )}

        {/* Sessions List */}
        {filteredSessions.length === 0 ? (
          <Card glass>
            <CardContent className="py-16 text-center">
              <MessageSquare className="w-16 h-16 text-zinc-700 mx-auto mb-4" />
              <h3 className="text-lg font-medium text-white mb-2">
                {searchQuery ? 'No matching conversations' : 'No conversations yet'}
              </h3>
              <p className="text-zinc-400 mb-6 max-w-md mx-auto">
                {searchQuery
                  ? 'Try a different search term'
                  : 'Start a conversation on the Dashboard to generate synthetic data. Your chat history will appear here.'}
              </p>
              {!searchQuery && (
                <Button variant="gradient" onClick={() => router.push('/dashboard')}>
                  <Sparkles className="w-4 h-4 mr-2" />
                  Start Generating
                </Button>
              )}
            </CardContent>
          </Card>
        ) : (
          <div className="space-y-2">
            {filteredSessions.map((session) => {
              const schemaMsg = session.messages.find(m => m.metadata?.schema);
              const fieldCount = schemaMsg?.metadata?.schema?.fields?.length || 0;
              const rowCount = schemaMsg?.metadata?.settings?.rowCount;
              const hasJob = session.messages.some(m => m.metadata?.jobId);

              return (
                <Card
                  key={session.id}
                  glass
                  className="group cursor-pointer hover:border-teal-500/20 transition-all"
                  onClick={() => handleLoadSession(session.id)}
                >
                  <CardContent className="py-4 px-5">
                    <div className="flex items-center gap-4">
                      {/* Icon */}
                      <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-teal-500/20 to-emerald-500/20 flex items-center justify-center flex-shrink-0">
                        <MessageSquare className="w-5 h-5 text-teal-400" />
                      </div>

                      {/* Content */}
                      <div className="flex-1 min-w-0">
                        <div className="flex items-center gap-2 mb-1">
                          <h3 className="text-sm font-medium text-white truncate group-hover:text-teal-400 transition-colors">
                            {session.title}
                          </h3>
                          {getStatusBadge(session.status)}
                        </div>
                        <div className="flex items-center gap-3 text-xs text-zinc-500">
                          <span className="flex items-center gap-1">
                            <Clock className="w-3 h-3" />
                            {formatDate(session.updatedAt)}
                          </span>
                          <span>{session.messages.length} messages</span>
                          {fieldCount > 0 && (
                            <span className="flex items-center gap-1">
                              <Database className="w-3 h-3" />
                              {fieldCount} fields
                            </span>
                          )}
                          {rowCount && (
                            <span className="flex items-center gap-1">
                              <FileText className="w-3 h.3" />
                              {rowCount.toLocaleString()} rows
                            </span>
                          )}
                        </div>
                      </div>

                      {/* Actions */}
                      <div className="flex items-center gap-2">
                        <button
                          onClick={(e) => handleDeleteSession(e, session.id)}
                          className="p-2 text-zinc-600 hover:text-red-400 hover:bg-red-500/10 rounded-lg opacity-0 group-hover:opacity-100 transition-all"
                        >
                          <Trash2 className="w-4 h-4" />
                        </button>
                        <ChevronRight className="w-4 h-4 text-zinc-600 group-hover:text-teal-400 transition-colors" />
                      </div>
                    </div>
                  </CardContent>
                </Card>
              );
            })}
          </div>
        )}

        {/* Stats */}
        {chatHistory.sessions.length > 0 && (
          <p className="text-center text-xs text-zinc-600">
            {chatHistory.sessions.length} conversation{chatHistory.sessions.length !== 1 ? 's' : ''} stored locally
          </p>
        )}
      </div>
    </DashboardLayout>
  );
}
