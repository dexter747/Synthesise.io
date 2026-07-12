'use client';

import { useState, useRef, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { DashboardLayout } from '@/components/layouts/dashboard-layout';
import { Card, CardContent } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Badge } from '@/components/ui/badge';
import { useCreateDataset } from '@/hooks/use-api';
import { useAuth } from '@/providers/auth-provider';
import { toast } from 'sonner';
import {
  Send,
  Loader2,
  Sparkles,
  User,
  Bot,
  Paperclip,
  X,
  Database,
  FileSpreadsheet,
  ArrowRight,
  RotateCcw,
} from 'lucide-react';

// Message types for the chat
interface ChatMessage {
  id: string;
  role: 'user' | 'assistant' | 'system';
  content: string;
  timestamp: Date;
  metadata?: {
    schema?: any;
    settings?: {
      name?: string;
      rowCount?: number;
      outputFormat?: string;
    };
    status?: 'thinking' | 'ready' | 'generating' | 'complete' | 'error';
    jobId?: string;
    datasetId?: string;
  };
}

// Suggested prompts for new users
const SUGGESTED_PROMPTS = [
  "I need 1000 rows of customer data with names, emails, phone numbers, and addresses",
  "Generate a product catalog with 500 items including SKU, name, price, category, and stock",
  "Create employee records with ID, name, department, salary, and hire date - 200 rows",
  "I need realistic e-commerce orders with order ID, customer, products, total, and status",
];

export default function NewDatasetPage() {
  const router = useRouter();
  const { user } = useAuth();
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [inputValue, setInputValue] = useState('');
  const [isProcessing, setIsProcessing] = useState(false);
  const [attachedFile, setAttachedFile] = useState<File | null>(null);
  const [attachedContent, setAttachedContent] = useState<string>('');
  const [currentSchema, setCurrentSchema] = useState<any>(null);
  const [currentSettings, setCurrentSettings] = useState({
    name: '',
    rowCount: 100,
    outputFormat: 'csv' as 'csv' | 'json' | 'sql',
  });
  const [isReadyToGenerate, setIsReadyToGenerate] = useState(false);
  
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);
  const inputRef = useRef<HTMLInputElement>(null);
  
  const createDataset = useCreateDataset();

  // Get max rows based on subscription tier
  const getMaxRows = () => {
    const tier = user?.subscription_tier?.toLowerCase();
    switch (tier) {
      case 'business': return 1000000;
      case 'pro': return 100000;
      case 'beginner': return 5000;
      case 'enterprise': return 10000000;
      default: return 5000;
    }
  };
  const maxRows = getMaxRows();

  // Scroll to bottom when messages change
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  // Add initial greeting message
  useEffect(() => {
    if (messages.length === 0) {
      setMessages([{
        id: 'welcome',
        role: 'assistant',
        content: `👋 Hi! I'm your AI data assistant. Tell me what kind of data you need, and I'll generate it for you.

**Just describe your data naturally**, for example:
• "I need 1000 customer records with names, emails, and addresses"
• "Generate product inventory with SKU, price, and stock levels"
• "Create realistic sales transactions for the last 6 months"

You can also **attach a sample file** (CSV, JSON) if you have example data you'd like me to match.

What data would you like to generate today?`,
        timestamp: new Date(),
      }]);
    }
  }, []);

  // Handle file attachment
  const handleFileChange = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;

    // Check file size (max 5MB)
    if (file.size > 5 * 1024 * 1024) {
      toast.error('File too large. Maximum size is 5MB');
      return;
    }

    // Check file type
    const validTypes = ['text/csv', 'application/json', 'text/plain'];
    if (!validTypes.includes(file.type) && !file.name.endsWith('.csv') && !file.name.endsWith('.json')) {
      toast.error('Invalid file type. Please upload CSV or JSON files');
      return;
    }

    setAttachedFile(file);

    // Read file content
    const reader = new FileReader();
    reader.onload = (event) => {
      const content = event.target?.result as string;
      // Truncate if too long
      setAttachedContent(content.slice(0, 10000));
      toast.success(`Attached: ${file.name}`);
    };
    reader.readAsText(file);
  };

  // Remove attached file
  const handleRemoveFile = () => {
    setAttachedFile(null);
    setAttachedContent('');
    if (fileInputRef.current) {
      fileInputRef.current.value = '';
    }
  };

  // Parse user message to extract row count and format
  const parseUserIntent = (message: string) => {
    const lowerMessage = message.toLowerCase();
    
    // Extract row count
    const rowPatterns = [
      /(\d{1,7})\s*rows?/i,
      /(\d{1,7})\s*records?/i,
      /(\d{1,7})\s*entries/i,
      /generate\s*(\d{1,7})/i,
      /need\s*(\d{1,7})/i,
      /create\s*(\d{1,7})/i,
    ];
    
    let rowCount = 100;
    for (const pattern of rowPatterns) {
      const match = message.match(pattern);
      if (match) {
        rowCount = Math.min(parseInt(match[1]), maxRows);
        break;
      }
    }

    // Extract output format
    let outputFormat: 'csv' | 'json' | 'sql' = 'csv';
    if (lowerMessage.includes('json')) outputFormat = 'json';
    else if (lowerMessage.includes('sql')) outputFormat = 'sql';

    // Extract potential dataset name
    const namePatterns = [
      /(?:called|named|name it|title)\s+["']?([^"'\n,]+)["']?/i,
      /["']([^"']+)["']\s+(?:dataset|data|records)/i,
    ];
    
    let name = '';
    for (const pattern of namePatterns) {
      const match = message.match(pattern);
      if (match) {
        name = match[1].trim();
        break;
      }
    }

    return { rowCount, outputFormat, name };
  };

  // Send message and get schema
  const handleSendMessage = async () => {
    if (!inputValue.trim() && !attachedContent) return;
    if (isProcessing) return;

    const userMessage = inputValue.trim();
    const { rowCount, outputFormat, name } = parseUserIntent(userMessage);

    // Add user message to chat
    const userMsgId = `user-${Date.now()}`;
    const newUserMessage: ChatMessage = {
      id: userMsgId,
      role: 'user',
      content: userMessage + (attachedFile ? `\n\n📎 Attached: ${attachedFile.name}` : ''),
      timestamp: new Date(),
    };
    
    setMessages(prev => [...prev, newUserMessage]);
    setInputValue('');
    setIsProcessing(true);

    // Add thinking message
    const thinkingMsgId = `thinking-${Date.now()}`;
    setMessages(prev => [...prev, {
      id: thinkingMsgId,
      role: 'assistant',
      content: 'Analyzing your request...',
      timestamp: new Date(),
      metadata: { status: 'thinking' },
    }]);

    try {
      // Call preview-schema endpoint
      const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/api/v1/datasets/preview-schema`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('access_token')}`,
        },
        body: JSON.stringify({
          name: name || 'Generated Dataset',
          description: userMessage,
          sample_data: attachedContent || undefined,
        }),
      });

      if (!response.ok) {
        throw new Error('Failed to analyze request');
      }

      const data = await response.json();
      const schema = data.schema;
      
      setCurrentSchema(schema);
      setCurrentSettings({
        name: name || generateDatasetName(userMessage),
        rowCount,
        outputFormat,
      });
      setIsReadyToGenerate(true);

      // Remove thinking message and add response
      setMessages(prev => {
        const filtered = prev.filter(m => m.id !== thinkingMsgId);
        return [...filtered, {
          id: `assistant-${Date.now()}`,
          role: 'assistant',
          content: `Perfect! I've analyzed your request and created a schema with **${schema.fields?.length || 0} fields**:

${schema.fields?.map((f: any) => `• **${f.name}** (${f.data_type})${f.description ? ` - ${f.description}` : ''}`).join('\n')}

📊 **Ready to generate:**
• **${rowCount.toLocaleString()} rows** in **${outputFormat.toUpperCase()}** format
• Dataset name: "${name || generateDatasetName(userMessage)}"

Does this look good? Click **Generate Dataset** below, or tell me if you'd like any changes to the schema or settings.`,
          timestamp: new Date(),
          metadata: {
            schema,
            settings: { name: name || generateDatasetName(userMessage), rowCount, outputFormat },
            status: 'ready',
          },
        }];
      });

      // Clear attached file after processing
      handleRemoveFile();

    } catch (error: any) {
      // Remove thinking message and add error
      setMessages(prev => {
        const filtered = prev.filter(m => m.id !== thinkingMsgId);
        return [...filtered, {
          id: `error-${Date.now()}`,
          role: 'assistant',
          content: `I encountered an issue: ${error.message || 'Failed to analyze your request'}. 

Could you try rephrasing your request? Make sure to describe:
• What type of data you need (customers, products, orders, etc.)
• What fields/columns you want
• How many rows you need`,
          timestamp: new Date(),
          metadata: { status: 'error' },
        }];
      });
    } finally {
      setIsProcessing(false);
      inputRef.current?.focus();
    }
  };

  // Generate a dataset name from the description
  const generateDatasetName = (description: string): string => {
    const words = description.toLowerCase();
    if (words.includes('customer')) return 'Customer Records';
    if (words.includes('product')) return 'Product Catalog';
    if (words.includes('employee')) return 'Employee Directory';
    if (words.includes('order')) return 'Order History';
    if (words.includes('transaction')) return 'Transaction Log';
    if (words.includes('user')) return 'User Database';
    if (words.includes('sales')) return 'Sales Data';
    if (words.includes('inventory')) return 'Inventory Records';
    return 'Generated Dataset';
  };

  // Handle dataset generation
  const handleGenerateDataset = async () => {
    if (!currentSchema || !isReadyToGenerate) return;

    setIsProcessing(true);

    // Add generating message
    const genMsgId = `generating-${Date.now()}`;
    setMessages(prev => [...prev, {
      id: genMsgId,
      role: 'assistant',
      content: `🚀 Starting generation of **${currentSettings.rowCount.toLocaleString()} rows**...`,
      timestamp: new Date(),
      metadata: { status: 'generating' },
    }]);

    try {
      const response = await createDataset.mutateAsync({
        name: currentSettings.name,
        description: messages.find(m => m.role === 'user')?.content || 'AI Generated Dataset',
        row_count: currentSettings.rowCount,
        output_format: currentSettings.outputFormat,
      });

      const dataset = response.dataset || response;
      const job = response.job;

      // Update message with success
      setMessages(prev => {
        const filtered = prev.filter(m => m.id !== genMsgId);
        return [...filtered, {
          id: `complete-${Date.now()}`,
          role: 'assistant',
          content: job 
            ? `✅ **Generation started!** 

Your dataset "${currentSettings.name}" is being generated with ${currentSettings.rowCount.toLocaleString()} rows.

I'm redirecting you to the job page where you can track progress and download your data once it's ready.`
            : `✅ **Dataset created!**

"${currentSettings.name}" has been created. You can now generate data from the dataset page.`,
          timestamp: new Date(),
          metadata: {
            status: 'complete',
            jobId: job?.id,
            datasetId: dataset.id,
          },
        }];
      });

      // Redirect after a short delay
      setTimeout(() => {
        if (job) {
          router.push(`/jobs/${job.id}`);
        } else {
          router.push(`/datasets/${dataset.id}`);
        }
      }, 2000);

    } catch (error: any) {
      setMessages(prev => {
        const filtered = prev.filter(m => m.id !== genMsgId);
        return [...filtered, {
          id: `error-${Date.now()}`,
          role: 'assistant',
          content: `❌ Generation failed: ${error.message || 'Unknown error'}

Please try again or adjust your settings.`,
          timestamp: new Date(),
          metadata: { status: 'error' },
        }];
      });
    } finally {
      setIsProcessing(false);
    }
  };

  // Handle suggested prompt click
  const handleSuggestedPrompt = (prompt: string) => {
    setInputValue(prompt);
    inputRef.current?.focus();
  };

  // Reset conversation
  const handleReset = () => {
    setMessages([{
      id: 'welcome',
      role: 'assistant',
      content: `👋 Hi! I'm your AI data assistant. Tell me what kind of data you need, and I'll generate it for you.

**Just describe your data naturally**, for example:
• "I need 1000 customer records with names, emails, and addresses"
• "Generate product inventory with SKU, price, and stock levels"
• "Create realistic sales transactions for the last 6 months"

You can also **attach a sample file** (CSV, JSON) if you have example data you'd like me to match.

What data would you like to generate today?`,
      timestamp: new Date(),
    }]);
    setCurrentSchema(null);
    setCurrentSettings({ name: '', rowCount: 100, outputFormat: 'csv' });
    setIsReadyToGenerate(false);
    handleRemoveFile();
  };

  // Handle key press
  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSendMessage();
    }
  };

  // Update settings from quick actions
  const updateRowCount = (count: number) => {
    setCurrentSettings(prev => ({ ...prev, rowCount: Math.min(count, maxRows) }));
  };

  const updateFormat = (format: 'csv' | 'json' | 'sql') => {
    setCurrentSettings(prev => ({ ...prev, outputFormat: format }));
  };

  return (
    <DashboardLayout>
      <div className="flex flex-col h-[calc(100vh-120px)] max-w-4xl mx-auto">
        {/* Header */}
        <div className="flex items-center justify-between mb-4 px-2">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-teal-500 to-emerald-600 flex items-center justify-center">
              <Sparkles className="w-5 h-5 text-white" />
            </div>
            <div>
              <h1 className="text-lg font-semibold text-white">AI Data Generator</h1>
              <p className="text-xs text-zinc-400">Describe your data in plain English</p>
            </div>
          </div>
          <Button variant="ghost" size="sm" onClick={handleReset}>
            <RotateCcw className="w-4 h-4 mr-2" />
            New Chat
          </Button>
        </div>

        {/* Chat Messages */}
        <Card className="flex-1 overflow-hidden bg-zinc-900/50 border-zinc-800">
          <CardContent className="h-full flex flex-col p-0">
            {/* Messages Area */}
            <div className="flex-1 overflow-y-auto p-4 space-y-4">
              {messages.map((message) => (
                <div
                  key={message.id}
                  className={`flex gap-3 ${message.role === 'user' ? 'justify-end' : 'justify-start'}`}
                >
                  {message.role === 'assistant' && (
                    <div className="w-8 h-8 rounded-lg bg-gradient-to-br from-teal-500 to-emerald-600 flex items-center justify-center flex-shrink-0">
                      <Bot className="w-4 h-4 text-white" />
                    </div>
                  )}
                  
                  <div
                    className={`max-w-[80%] rounded-2xl px-4 py-3 ${
                      message.role === 'user'
                        ? 'bg-teal-600 text-white'
                        : 'bg-zinc-800 text-zinc-100'
                    }`}
                  >
                    {message.metadata?.status === 'thinking' ? (
                      <div className="flex items-center gap-2">
                        <Loader2 className="w-4 h-4 animate-spin" />
                        <span>Analyzing your request...</span>
                      </div>
                    ) : message.metadata?.status === 'generating' ? (
                      <div className="flex items-center gap-2">
                        <Loader2 className="w-4 h-4 animate-spin" />
                        <span>{message.content}</span>
                      </div>
                    ) : (
                      <div className="prose prose-invert prose-sm max-w-none whitespace-pre-wrap">
                        {message.content.split('\n').map((line, i) => {
                          // Handle bold text
                          const parts = line.split(/\*\*(.+?)\*\*/g);
                          
                          return (
                            <p key={i} className="mb-2 last:mb-0 leading-relaxed">
                              {parts.map((part, j) => 
                                j % 2 === 1 ? <strong key={j} className="font-semibold text-white">{part}</strong> : part
                              )}
                            </p>
                          );
                        })}
                      </div>
                    )}

                    {/* Schema preview in message */}
                    {message.metadata?.status === 'ready' && message.metadata.schema && (
                      <div className="mt-4 pt-4 border-t border-white/10">
                        <div className="flex flex-wrap gap-2">
                          {message.metadata.schema.fields?.slice(0, 5).map((field: any, i: number) => (
                            <Badge key={i} variant="outline" className="text-xs bg-white/5">
                              <Database className="w-3 h-3 mr-1" />
                              {field.name}
                            </Badge>
                          ))}
                          {message.metadata.schema.fields?.length > 5 && (
                            <Badge variant="outline" className="text-xs bg-white/5">
                              +{message.metadata.schema.fields.length - 5} more
                            </Badge>
                          )}
                        </div>
                      </div>
                    )}

                    {/* Success actions */}
                    {message.metadata?.status === 'complete' && message.metadata.jobId && (
                      <div className="mt-4 pt-4 border-t border-white/10">
                        <Button
                          size="sm"
                          variant="outline"
                          onClick={() => router.push(`/jobs/${message.metadata?.jobId}`)}
                        >
                          <ArrowRight className="w-4 h-4 mr-2" />
                          View Job Progress
                        </Button>
                      </div>
                    )}
                  </div>

                  {message.role === 'user' && (
                    <div className="w-8 h-8 rounded-lg bg-zinc-700 flex items-center justify-center flex-shrink-0">
                      <User className="w-4 h-4 text-zinc-300" />
                    </div>
                  )}
                </div>
              ))}
              <div ref={messagesEndRef} />
            </div>

            {/* Suggested Prompts (only show at start) */}
            {messages.length === 1 && (
              <div className="px-4 pb-4">
                <p className="text-xs text-zinc-500 mb-2">Try one of these:</p>
                <div className="flex flex-wrap gap-2">
                  {SUGGESTED_PROMPTS.map((prompt, i) => (
                    <button
                      key={i}
                      onClick={() => handleSuggestedPrompt(prompt)}
                      className="text-xs px-3 py-1.5 rounded-full bg-zinc-800 text-zinc-300 hover:bg-zinc-700 hover:text-white transition-colors text-left"
                    >
                      {prompt.slice(0, 50)}...
                    </button>
                  ))}
                </div>
              </div>
            )}

            {/* Generation Controls (show when schema is ready) */}
            {isReadyToGenerate && currentSchema && (
              <div className="px-4 pb-4 border-t border-zinc-800 pt-4">
                <div className="flex flex-wrap items-center gap-3 mb-3">
                  <div className="flex items-center gap-2">
                    <span className="text-xs text-zinc-500">Rows:</span>
                    <div className="flex gap-1">
                      {[100, 500, 1000, 5000, 10000].filter(n => n <= maxRows).map(count => (
                        <button
                          key={count}
                          onClick={() => updateRowCount(count)}
                          className={`text-xs px-2 py-1 rounded transition-colors ${
                            currentSettings.rowCount === count
                              ? 'bg-teal-600 text-white'
                              : 'bg-zinc-800 text-zinc-400 hover:bg-zinc-700'
                          }`}
                        >
                          {count >= 1000 ? `${count / 1000}K` : count}
                        </button>
                      ))}
                    </div>
                  </div>
                  
                  <div className="flex items-center gap-2">
                    <span className="text-xs text-zinc-500">Format:</span>
                    <div className="flex gap-1">
                      {(['csv', 'json', 'sql'] as const).map(format => (
                        <button
                          key={format}
                          onClick={() => updateFormat(format)}
                          className={`text-xs px-2 py-1 rounded uppercase transition-colors ${
                            currentSettings.outputFormat === format
                              ? 'bg-teal-600 text-white'
                              : 'bg-zinc-800 text-zinc-400 hover:bg-zinc-700'
                          }`}
                        >
                          {format}
                        </button>
                      ))}
                    </div>
                  </div>
                </div>

                <Button
                  variant="gradient"
                  className="w-full"
                  onClick={handleGenerateDataset}
                  disabled={isProcessing || createDataset.isPending}
                >
                  {isProcessing || createDataset.isPending ? (
                    <>
                      <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                      Generating...
                    </>
                  ) : (
                    <>
                      <Sparkles className="w-4 h-4 mr-2" />
                      Generate {currentSettings.rowCount.toLocaleString()} Rows
                    </>
                  )}
                </Button>
              </div>
            )}

            {/* Input Area */}
            <div className="p-4 border-t border-zinc-800">
              {/* Attached File Preview */}
              {attachedFile && (
                <div className="mb-3 flex items-center gap-2 p-2 bg-zinc-800 rounded-lg">
                  <FileSpreadsheet className="w-4 h-4 text-teal-400" />
                  <span className="text-sm text-zinc-300 flex-1 truncate">{attachedFile.name}</span>
                  <button
                    onClick={handleRemoveFile}
                    className="p-1 hover:bg-zinc-700 rounded"
                  >
                    <X className="w-4 h-4 text-zinc-400" />
                  </button>
                </div>
              )}

              <div className="flex gap-2">
                {/* File Upload Button */}
                <input
                  ref={fileInputRef}
                  type="file"
                  accept=".csv,.json,.txt"
                  onChange={handleFileChange}
                  className="hidden"
                />
                <Button
                  variant="ghost"
                  size="icon"
                  onClick={() => fileInputRef.current?.click()}
                  className="flex-shrink-0"
                  title="Attach sample file"
                >
                  <Paperclip className="w-5 h-5" />
                </Button>

                {/* Message Input */}
                <div className="flex-1 relative">
                  <Input
                    ref={inputRef}
                    value={inputValue}
                    onChange={(e) => setInputValue(e.target.value)}
                    onKeyDown={handleKeyPress}
                    placeholder="Describe the data you need..."
                    className="pr-12 bg-zinc-800 border-zinc-700 focus:border-teal-500"
                    disabled={isProcessing}
                  />
                </div>

                {/* Send Button */}
                <Button
                  variant="gradient"
                  size="icon"
                  onClick={handleSendMessage}
                  disabled={(!inputValue.trim() && !attachedContent) || isProcessing}
                  className="flex-shrink-0"
                >
                  {isProcessing ? (
                    <Loader2 className="w-5 h-5 animate-spin" />
                  ) : (
                    <Send className="w-5 h-5" />
                  )}
                </Button>
              </div>

              <p className="text-xs text-zinc-500 mt-2 text-center">
                Tip: Include row count and format in your message, e.g., "1000 rows in JSON format"
              </p>
            </div>
          </CardContent>
        </Card>
      </div>
    </DashboardLayout>
  );
}
