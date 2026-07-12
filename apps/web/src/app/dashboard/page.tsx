'use client';

import { useState, useRef, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import Image from 'next/image';
import { DashboardLayout } from '@/components/layouts/dashboard-layout';
import { Button } from '@/components/ui/button';
import { useAuth } from '@/providers/auth-provider';
import { useCreateDataset } from '@/hooks/use-api';
import { useChatHistory, ChatSession } from '@/hooks/use-chat-history';
import { toast } from 'sonner';
import Link from 'next/link';
import {
  Send,
  Loader2,
  Paperclip,
  X,
  Database,
  FileSpreadsheet,
  ArrowRight,
  RotateCcw,
  Pencil,
  GraduationCap,
  Code2,
  Briefcase,
  ChevronDown,
  Clock,
  Check,
  Zap,
  Brain,
  Cpu,
  Sparkles,
  Copy,
  ThumbsUp,
  ThumbsDown,
  Plus,
  Trash2,
  Wand2,
  Edit3,
  MessageSquare,
  History,
  PanelLeftClose,
  PanelLeft,
} from 'lucide-react';

// Schema field interface
interface SchemaField {
  name: string;
  data_type: string;
  description?: string;
  constraints?: {
    required?: boolean;
    unique?: boolean;
    min?: number;
    max?: number;
  };
}

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

// Available AI models
const AI_MODELS = [
  { id: 'faker', name: 'Faker Engine', description: 'Fast rule-based generation', icon: Zap },
  { id: 'llm', name: 'LLM (Groq)', description: 'AI-powered realistic data', icon: Brain },
  { id: 'sdv', name: 'SDV/Synthcity', description: 'ML statistical models', icon: Cpu },
];

// Quick action categories
const QUICK_ACTIONS = [
  { icon: Pencil, label: 'Customer Data', prompt: 'Generate 1000 customer records with names, emails, phone numbers, and addresses' },
  { icon: GraduationCap, label: 'E-commerce', prompt: 'Create product catalog with 500 items including SKU, name, price, category, and stock' },
  { icon: Code2, label: 'Transactions', prompt: 'Generate 5000 sales transactions with order ID, customer, products, total, and timestamp' },
  { icon: Briefcase, label: 'Employees', prompt: 'Create employee records with ID, name, department, salary, job title, and hire date - 200 rows' },
];

// Time-based greeting
function getGreeting(): string {
  const hour = new Date().getHours();
  if (hour < 12) return 'Good morning';
  if (hour < 17) return 'Good afternoon';
  return 'Good evening';
}

export default function DashboardPage() {
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
  const [showModelSelector, setShowModelSelector] = useState(false);
  const [selectedModel, setSelectedModel] = useState(AI_MODELS[0]);
  
  // Chat history
  const chatHistory = useChatHistory();
  const [showChatHistory, setShowChatHistory] = useState(true);
  
  // Schema editing state
  const [isEditingSchema, setIsEditingSchema] = useState(false);
  const [editableSchema, setEditableSchema] = useState<SchemaField[]>([]);
  const [newFieldName, setNewFieldName] = useState('');
  const [newFieldType, setNewFieldType] = useState('string');
  const [isRefiningSchema, setIsRefiningSchema] = useState(false);
  
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);
  const inputRef = useRef<HTMLTextAreaElement>(null);
  
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

  // Auto-resize textarea
  useEffect(() => {
    if (inputRef.current) {
      inputRef.current.style.height = 'auto';
      inputRef.current.style.height = Math.min(inputRef.current.scrollHeight, 200) + 'px';
    }
  }, [inputValue]);

  // Handle file attachment - only CSV, Excel, JSON
  const handleFileChange = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;

    if (file.size > 10 * 1024 * 1024) {
      toast.error('File too large. Maximum size is 10MB');
      return;
    }

    const validExtensions = ['.csv', '.json', '.xlsx', '.xls'];
    const validMimeTypes = [
      'text/csv',
      'application/json',
      'application/vnd.ms-excel',
      'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    ];
    const fileExtension = '.' + file.name.split('.').pop()?.toLowerCase();
    
    if (!validExtensions.includes(fileExtension) && !validMimeTypes.includes(file.type)) {
      toast.error('Invalid file type. Please upload CSV, Excel (.xlsx), or JSON files only');
      return;
    }

    setAttachedFile(file);

    if (fileExtension === '.csv' || fileExtension === '.json') {
      const reader = new FileReader();
      reader.onload = (event) => {
        const content = event.target?.result as string;
        setAttachedContent(content.slice(0, 10000));
        toast.success(`Attached: ${file.name}`);
      };
      reader.readAsText(file);
    } else {
      setAttachedContent('[Excel file attached - will be parsed on server]');
      toast.success(`Attached: ${file.name}`);
    }
  };

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

    let outputFormat: 'csv' | 'json' | 'sql' = 'csv';
    if (lowerMessage.includes('json')) outputFormat = 'json';
    else if (lowerMessage.includes('sql')) outputFormat = 'sql';

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

  // Schema editing functions
  const startEditingSchema = () => {
    if (currentSchema?.fields) {
      setEditableSchema([...currentSchema.fields]);
      setIsEditingSchema(true);
    }
  };

  const cancelEditingSchema = () => {
    setIsEditingSchema(false);
    setEditableSchema([]);
    setNewFieldName('');
  };

  const addField = () => {
    if (!newFieldName.trim()) {
      toast.error('Please enter a field name');
      return;
    }
    if (editableSchema.some(f => f.name.toLowerCase() === newFieldName.toLowerCase())) {
      toast.error('Field already exists');
      return;
    }
    setEditableSchema(prev => [...prev, {
      name: newFieldName.trim(),
      data_type: newFieldType,
      description: '',
    }]);
    setNewFieldName('');
    toast.success(`Added field: ${newFieldName}`);
  };

  const removeField = (index: number) => {
    const fieldName = editableSchema[index].name;
    setEditableSchema(prev => prev.filter((_, i) => i !== index));
    toast.success(`Removed field: ${fieldName}`);
  };

  const updateFieldType = (index: number, newType: string) => {
    setEditableSchema(prev => prev.map((field, i) => 
      i === index ? { ...field, data_type: newType } : field
    ));
  };

  // Refine schema with AI
  const refineSchemaWithAI = async () => {
    if (editableSchema.length === 0) {
      toast.error('Please add at least one field');
      return;
    }

    setIsRefiningSchema(true);
    
    try {
      const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api/v1';
      const originalDescription = messages.find(m => m.role === 'user')?.content || '';
      
      // Build refinement request
      const fieldsDescription = editableSchema.map(f => `${f.name} (${f.data_type})`).join(', ');
      const refinementPrompt = `Original request: ${originalDescription}

User has modified the schema to have these fields: ${fieldsDescription}

Please refine and optimize this schema, keeping all the user's specified fields but improving data types, adding appropriate constraints, and filling in descriptions.`;

      const response = await fetch(`${apiUrl}/datasets/preview-schema`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('access_token')}`,
        },
        body: JSON.stringify({
          name: currentSettings.name || 'Refined Dataset',
          description: refinementPrompt,
        }),
      });

      if (!response.ok) {
        throw new Error('Failed to refine schema');
      }

      const data = await response.json();
      const refinedSchema = data.schema;

      // Merge: keep user's fields, update with AI refinements
      const mergedFields = editableSchema.map(userField => {
        const aiField = refinedSchema.fields?.find((f: SchemaField) => 
          f.name.toLowerCase() === userField.name.toLowerCase()
        );
        return aiField ? { ...userField, ...aiField, name: userField.name } : userField;
      });

      // Add any new AI-suggested fields that user might want
      const newAiFields = refinedSchema.fields?.filter((aiField: SchemaField) => 
        !editableSchema.some(f => f.name.toLowerCase() === aiField.name.toLowerCase())
      ) || [];

      setEditableSchema([...mergedFields]);
      setCurrentSchema({ ...currentSchema, fields: mergedFields });
      setIsEditingSchema(false);

      // Update message
      setMessages(prev => [...prev, {
        id: `refined-${Date.now()}`,
        role: 'assistant',
        content: `Schema refined! ${mergedFields.length} fields optimized.${
          newAiFields.length > 0 
            ? `\n\nI also suggest adding: ${newAiFields.map((f: SchemaField) => `**${f.name}**`).join(', ')}. You can add them by clicking Edit Schema.`
            : ''
        }`,
        timestamp: new Date(),
        metadata: { 
          schema: { ...currentSchema, fields: mergedFields },
          status: 'ready',
        },
      }]);

      toast.success('Schema refined successfully!');

    } catch (error: any) {
      toast.error(error.message || 'Failed to refine schema');
    } finally {
      setIsRefiningSchema(false);
    }
  };

  // Apply schema changes without AI refinement
  const applySchemaChanges = () => {
    if (editableSchema.length === 0) {
      toast.error('Please add at least one field');
      return;
    }

    setCurrentSchema({ ...currentSchema, fields: editableSchema });
    setIsEditingSchema(false);

    setMessages(prev => [...prev, {
      id: `updated-${Date.now()}`,
      role: 'assistant',
      content: `Schema updated with ${editableSchema.length} fields. Ready to generate!`,
      timestamp: new Date(),
      metadata: { 
        schema: { ...currentSchema, fields: editableSchema },
        status: 'ready',
      },
    }]);

    toast.success('Schema updated!');
  };

  // Available data types for the dropdown
  const DATA_TYPES = [
    'string', 'integer', 'float', 'boolean', 'date', 'datetime', 'timestamp',
    'email', 'phone', 'url', 'uuid', 'name', 'first_name', 'last_name',
    'address', 'city', 'state', 'country', 'zipcode', 'company',
    'credit_card', 'currency', 'price', 'text', 'paragraph',
  ];

  // Send message and get schema
  const handleSendMessage = async () => {
    if (!inputValue.trim() && !attachedContent) return;
    if (isProcessing) return;

    const userMessage = inputValue.trim();
    const { rowCount, outputFormat, name } = parseUserIntent(userMessage);

    const userMsgId = `user-${Date.now()}`;
    const newUserMessage: ChatMessage = {
      id: userMsgId,
      role: 'user',
      content: userMessage + (attachedFile ? `\n\n📎 ${attachedFile.name}` : ''),
      timestamp: new Date(),
    };
    
    setMessages(prev => [...prev, newUserMessage]);
    setInputValue('');
    setIsProcessing(true);

    const thinkingMsgId = `thinking-${Date.now()}`;
    setMessages(prev => [...prev, {
      id: thinkingMsgId,
      role: 'assistant',
      content: '',
      timestamp: new Date(),
      metadata: { status: 'thinking' },
    }]);

    try {
      // FIX: NEXT_PUBLIC_API_URL already includes /api/v1, don't duplicate
      const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api/v1';
      const response = await fetch(`${apiUrl}/datasets/preview-schema`, {
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
        const errorData = await response.json().catch(() => ({}));
        throw new Error(errorData.detail || 'Failed to analyze request');
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

      // Build field list with proper formatting
      const fieldsList = schema.fields?.map((f: any) => 
        `**${f.name}** _(${f.data_type})_${f.description ? ` — ${f.description}` : ''}`
      ).join('\n') || 'No fields detected';

      setMessages(prev => {
        const filtered = prev.filter(m => m.id !== thinkingMsgId);
        return [...filtered, {
          id: `assistant-${Date.now()}`,
          role: 'assistant',
          content: `I've analyzed your request and created a schema with **${schema.fields?.length || 0} fields**:

${fieldsList}

Ready to generate **${rowCount.toLocaleString()} rows** in **${outputFormat.toUpperCase()}** format.

Would you like to proceed, or should I make any adjustments?`,
          timestamp: new Date(),
          metadata: {
            schema,
            settings: { name: name || generateDatasetName(userMessage), rowCount, outputFormat },
            status: 'ready',
          },
        }];
      });

      handleRemoveFile();

    } catch (error: any) {
      setMessages(prev => {
        const filtered = prev.filter(m => m.id !== thinkingMsgId);
        return [...filtered, {
          id: `error-${Date.now()}`,
          role: 'assistant',
          content: `I couldn't process that request. ${error.message || 'Please try again.'}

Try describing:
- What type of data you need (customers, products, orders)
- Which fields/columns to include
- How many rows to generate`,
          timestamp: new Date(),
          metadata: { status: 'error' },
        }];
      });
    } finally {
      setIsProcessing(false);
      inputRef.current?.focus();
    }
  };

  // Handle dataset generation
  const handleGenerateDataset = async () => {
    if (!currentSchema || !isReadyToGenerate) return;

    setIsProcessing(true);

    const genMsgId = `generating-${Date.now()}`;
    setMessages(prev => [...prev, {
      id: genMsgId,
      role: 'assistant',
      content: `Generating ${currentSettings.rowCount.toLocaleString()} rows...`,
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

      setMessages(prev => {
        const filtered = prev.filter(m => m.id !== genMsgId);
        return [...filtered, {
          id: `complete-${Date.now()}`,
          role: 'assistant',
          content: job 
            ? `Your dataset **"${currentSettings.name}"** is being generated. Redirecting to track progress...`
            : `Your dataset **"${currentSettings.name}"** has been created successfully.`,
          timestamp: new Date(),
          metadata: {
            status: 'complete',
            jobId: job?.id,
            datasetId: dataset.id,
          },
        }];
      });

      setTimeout(() => {
        if (job) {
          router.push(`/jobs/${job.id}`);
        } else {
          router.push(`/datasets/${dataset.id}`);
        }
      }, 1500);

    } catch (error: any) {
      setMessages(prev => {
        const filtered = prev.filter(m => m.id !== genMsgId);
        return [...filtered, {
          id: `error-${Date.now()}`,
          role: 'assistant',
          content: `Generation failed: ${error.message || 'Unknown error'}. Please try again.`,
          timestamp: new Date(),
          metadata: { status: 'error' },
        }];
      });
    } finally {
      setIsProcessing(false);
    }
  };

  // Handle quick action click
  const handleQuickAction = (prompt: string) => {
    if (prompt) {
      setInputValue(prompt);
      inputRef.current?.focus();
    }
  };

  // Reset conversation
  const handleReset = () => {
    setMessages([]);
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

  // Update settings
  const updateRowCount = (count: number) => {
    setCurrentSettings(prev => ({ ...prev, rowCount: Math.min(count, maxRows) }));
  };

  const updateFormat = (format: 'csv' | 'json' | 'sql') => {
    setCurrentSettings(prev => ({ ...prev, outputFormat: format }));
  };

  // Check if we're in conversation mode
  const isInConversation = messages.length > 0;

  // Render markdown-like content
  const renderContent = (content: string) => {
    return content.split('\n').map((line, i) => {
      // Handle bold **text**
      const parts = line.split(/\*\*(.+?)\*\*/g);
      const processedParts = parts.map((part, j) => {
        if (j % 2 === 1) {
          return <strong key={j} className="font-medium text-zinc-100">{part}</strong>;
        }
        // Process italics _text_
        const italicParts = part.split(/_(.+?)_/g);
        return italicParts.map((ip, k) => 
          k % 2 === 1 ? <span key={`${j}-${k}`} className="text-zinc-500">{ip}</span> : ip
        );
      });
      
      // Handle list items
      if (line.startsWith('- ')) {
        return (
          <div key={i} className="flex gap-2 my-1">
            <span className="text-teal-500">•</span>
            <span className="text-zinc-300">{line.slice(2)}</span>
          </div>
        );
      }
      
      return line ? <p key={i} className="my-1">{processedParts}</p> : <div key={i} className="h-2" />;
    });
  };

  // Save current session to history when generation completes
  const saveCurrentSession = () => {
    if (messages.length === 0) return;
    
    const userMessage = messages.find(m => m.role === 'user')?.content || 'Untitled Session';
    const title = userMessage.slice(0, 50) + (userMessage.length > 50 ? '...' : '');
    
    // Create new session - it sets currentSessionId automatically
    const session = chatHistory.createSession(title);
    
    // Add each message to the session (addMessage works on currentSession)
    messages.forEach(msg => {
      chatHistory.addMessage({
        role: msg.role,
        content: msg.content,
        metadata: msg.metadata ? {
          schema: msg.metadata.schema,
          settings: {
            rowCount: msg.metadata.settings?.rowCount,
            outputFormat: msg.metadata.settings?.outputFormat,
          },
          status: msg.metadata.status,
          jobId: msg.metadata.jobId,
        } : undefined,
      });
    });
    
    return session;
  };

  // Load a previous session
  const loadSessionHandler = (sessionId: string) => {
    const session = chatHistory.sessions.find(s => s.id === sessionId);
    if (!session) return;
    
    // Set as current session in chat history
    chatHistory.loadSession(sessionId);
    
    const loadedMessages: ChatMessage[] = session.messages.map((msg, i) => ({
      id: `loaded-${i}-${Date.now()}`,
      role: msg.role,
      content: msg.content,
      timestamp: new Date(msg.timestamp),
      metadata: msg.metadata ? {
        schema: msg.metadata.schema,
        settings: {
          rowCount: msg.metadata.settings?.rowCount,
          outputFormat: msg.metadata.settings?.outputFormat,
        },
        status: msg.metadata.status,
        jobId: msg.metadata.jobId,
      } : undefined,
    }));
    
    setMessages(loadedMessages);
    
    // Restore schema if present
    const lastSchemaMsg = [...loadedMessages].reverse().find(m => m.metadata?.schema);
    if (lastSchemaMsg?.metadata?.schema) {
      setCurrentSchema(lastSchemaMsg.metadata.schema);
      setCurrentSettings({
        name: currentSettings.name,
        rowCount: lastSchemaMsg.metadata.settings?.rowCount || 100,
        outputFormat: (lastSchemaMsg.metadata.settings?.outputFormat as 'csv' | 'json' | 'sql') || 'csv',
      });
      setIsReadyToGenerate(true);
    }
    
    toast.success('Session loaded');
  };

  // Start new chat (with option to save current)
  const startNewChat = (saveFirst = true) => {
    if (saveFirst && messages.length > 0) {
      saveCurrentSession();
    }
    chatHistory.startNewChat();
    handleReset();
  };

  // Format date for display
  const formatSessionDate = (dateString: string) => {
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
    return date.toLocaleDateString();
  };

  return (
    <DashboardLayout>
      <div className="h-[calc(100vh-64px)] flex bg-zinc-950">
        
        {/* Chat History Sidebar */}
        {showChatHistory && (
          <div className="w-72 flex-shrink-0 border-r border-zinc-800 bg-zinc-900/50 flex flex-col">
            {/* Sidebar Header */}
            <div className="flex items-center justify-between px-4 py-4 border-b border-zinc-800/60">
              <div className="flex items-center gap-2">
                <History className="w-4 h-4 text-teal-500" />
                <span className="text-sm font-medium text-zinc-300">Chat History</span>
              </div>
              <button
                onClick={() => setShowChatHistory(false)}
                className="p-1.5 text-zinc-500 hover:text-zinc-300 hover:bg-zinc-800 rounded-lg transition-colors"
                title="Hide sidebar"
              >
                <PanelLeftClose className="w-4 h-4" />
              </button>
            </div>
            
            {/* New Chat Button */}
            <div className="px-3 py-3">
              <button
                onClick={() => startNewChat(true)}
                className="w-full flex items-center gap-2 px-3 py-2.5 bg-teal-500/10 hover:bg-teal-500/20 border border-teal-500/20 text-teal-400 rounded-xl text-sm font-medium transition-colors"
              >
                <Plus className="w-4 h-4" />
                New Chat
              </button>
            </div>
            
            {/* Session List */}
            <div className="flex-1 overflow-y-auto px-3 pb-3">
              {chatHistory.sessions.length === 0 ? (
                <div className="text-center py-8">
                  <MessageSquare className="w-8 h-8 text-zinc-700 mx-auto mb-3" />
                  <p className="text-sm text-zinc-500">No chat history yet</p>
                  <p className="text-xs text-zinc-600 mt-1">Your conversations will appear here</p>
                </div>
              ) : (
                <div className="space-y-1">
                  {chatHistory.sessions.map(session => (
                    <button
                      key={session.id}
                      onClick={() => loadSessionHandler(session.id)}
                      className="w-full text-left p-3 rounded-xl hover:bg-zinc-800/80 transition-colors group"
                    >
                      <div className="flex items-start justify-between gap-2">
                        <div className="flex-1 min-w-0">
                          <p className="text-sm text-zinc-300 truncate font-medium">
                            {session.title}
                          </p>
                          <p className="text-xs text-zinc-500 mt-0.5">
                            {formatSessionDate(session.updatedAt)} • {session.messages.length} messages
                          </p>
                        </div>
                        <button
                          onClick={(e) => {
                            e.stopPropagation();
                            chatHistory.deleteSession(session.id);
                          }}
                          className="p-1.5 text-zinc-600 hover:text-red-400 hover:bg-red-500/10 rounded-lg opacity-0 group-hover:opacity-100 transition-all"
                        >
                          <Trash2 className="w-3.5 h-3.5" />
                        </button>
                      </div>
                    </button>
                  ))}
                </div>
              )}
            </div>
            
            {/* Sidebar Footer */}
            {chatHistory.sessions.length > 0 && (
              <div className="px-3 py-3 border-t border-zinc-800/60">
                <button
                  onClick={() => {
                    if (confirm('Clear all chat history?')) {
                      chatHistory.clearAllSessions();
                      toast.success('Chat history cleared');
                    }
                  }}
                  className="w-full flex items-center justify-center gap-2 px-3 py-2 text-xs text-zinc-500 hover:text-red-400 hover:bg-red-500/10 rounded-lg transition-colors"
                >
                  <Trash2 className="w-3.5 h-3.5" />
                  Clear History
                </button>
              </div>
            )}
          </div>
        )}
        
        {/* Main Content */}
        <div className="flex-1 flex flex-col min-w-0">
          
          {/* Toggle Sidebar Button (when hidden) */}
          {!showChatHistory && (
            <button
              onClick={() => setShowChatHistory(true)}
              className="fixed left-4 top-20 z-10 p-2 bg-zinc-800 hover:bg-zinc-700 border border-zinc-700 rounded-lg text-zinc-400 hover:text-zinc-200 transition-colors shadow-lg"
              title="Show chat history"
            >
              <PanelLeft className="w-4 h-4" />
            </button>
          )}
        
        {/* Empty State */}
        {!isInConversation && (
          <div className="flex-1 flex flex-col items-center justify-center px-4">
            <div className="w-full max-w-2xl mx-auto">
              {/* Logo & Greeting */}
              <div className="text-center mb-10">
                <div className="inline-flex items-center justify-center w-14 h-14 rounded-2xl bg-gradient-to-br from-teal-500 to-emerald-600 mb-6 shadow-xl shadow-teal-500/20">
                  <Image src="/logo.svg" alt="Synthesize" width={32} height={32} className="invert" />
                </div>
                <h1 className="text-3xl font-light text-zinc-100 tracking-tight">
                  {getGreeting()}, {user?.name?.split(' ')[0] || user?.email?.split('@')[0] || 'there'}
                </h1>
                <p className="text-zinc-500 mt-3">What data would you like to generate?</p>
              </div>
              
              {/* Input Box */}
              <div className="relative">
                <div className="bg-zinc-900 rounded-2xl border border-zinc-800 shadow-2xl overflow-hidden transition-all focus-within:border-zinc-700">
                  {/* Attached File */}
                  {attachedFile && (
                    <div className="mx-4 mt-4 flex items-center gap-3 p-3 bg-zinc-800/60 rounded-xl border border-zinc-700/50">
                      <div className="w-10 h-10 rounded-lg bg-teal-500/10 flex items-center justify-center">
                        <FileSpreadsheet className="w-5 h-5 text-teal-400" />
                      </div>
                      <div className="flex-1 min-w-0">
                        <p className="text-sm text-zinc-200 truncate font-medium">{attachedFile.name}</p>
                        <p className="text-xs text-zinc-500">Training data</p>
                      </div>
                      <button 
                        onClick={handleRemoveFile} 
                        className="p-2 hover:bg-zinc-700 rounded-lg transition-colors"
                      >
                        <X className="w-4 h-4 text-zinc-400" />
                      </button>
                    </div>
                  )}
                  
                  {/* Textarea */}
                  <textarea
                    ref={inputRef}
                    value={inputValue}
                    onChange={(e) => setInputValue(e.target.value)}
                    onKeyDown={handleKeyPress}
                    placeholder="Describe the synthetic data you want to generate..."
                    className="w-full bg-transparent text-zinc-100 placeholder-zinc-600 px-5 pt-5 pb-16 resize-none focus:outline-none text-base leading-relaxed min-h-[120px] max-h-[240px]"
                    rows={3}
                  />
                  
                  {/* Toolbar */}
                  <div className="absolute bottom-3 left-3 right-3 flex items-center justify-between">
                    <div className="flex items-center gap-0.5">
                      <input
                        ref={fileInputRef}
                        type="file"
                        accept=".csv,.json,.xlsx,.xls"
                        onChange={handleFileChange}
                        className="hidden"
                      />
                      <button
                        onClick={() => fileInputRef.current?.click()}
                        className="p-2.5 text-zinc-500 hover:text-zinc-300 hover:bg-zinc-800 rounded-lg transition-colors"
                        title="Attach dataset"
                      >
                        <Paperclip className="w-5 h-5" />
                      </button>
                      
                      <Link href="/jobs">
                        <button className="p-2.5 text-zinc-500 hover:text-zinc-300 hover:bg-zinc-800 rounded-lg transition-colors" title="Recent jobs">
                          <Clock className="w-5 h-5" />
                        </button>
                      </Link>
                    </div>
                    
                    <div className="flex items-center gap-2">
                      {/* Model Selector */}
                      <div className="relative">
                        <button 
                          className="flex items-center gap-2 px-3 py-2 text-sm text-zinc-400 hover:text-zinc-200 transition-colors rounded-lg hover:bg-zinc-800"
                          onClick={() => setShowModelSelector(!showModelSelector)}
                        >
                          <selectedModel.icon className="w-4 h-4" />
                          <span className="hidden sm:inline">{selectedModel.name}</span>
                          <ChevronDown className={`w-3.5 h-3.5 transition-transform ${showModelSelector ? 'rotate-180' : ''}`} />
                        </button>
                        
                        {showModelSelector && (
                          <>
                            <div className="fixed inset-0 z-40" onClick={() => setShowModelSelector(false)} />
                            <div className="absolute bottom-full mb-2 right-0 w-72 bg-zinc-900 border border-zinc-700 rounded-xl shadow-2xl overflow-hidden z-50">
                              <div className="p-2">
                                {AI_MODELS.map((model) => (
                                  <button
                                    key={model.id}
                                    onClick={() => {
                                      setSelectedModel(model);
                                      setShowModelSelector(false);
                                    }}
                                    className={`w-full flex items-center gap-3 px-3 py-3 rounded-lg text-left transition-colors ${
                                      selectedModel.id === model.id 
                                        ? 'bg-teal-500/10' 
                                        : 'hover:bg-zinc-800'
                                    }`}
                                  >
                                    <div className={`w-9 h-9 rounded-lg flex items-center justify-center ${
                                      selectedModel.id === model.id ? 'bg-teal-500/20' : 'bg-zinc-800'
                                    }`}>
                                      <model.icon className={`w-5 h-5 ${selectedModel.id === model.id ? 'text-teal-400' : 'text-zinc-400'}`} />
                                    </div>
                                    <div className="flex-1 min-w-0">
                                      <p className={`text-sm font-medium ${selectedModel.id === model.id ? 'text-teal-400' : 'text-zinc-200'}`}>
                                        {model.name}
                                      </p>
                                      <p className="text-xs text-zinc-500">{model.description}</p>
                                    </div>
                                    {selectedModel.id === model.id && (
                                      <Check className="w-4 h-4 text-teal-400" />
                                    )}
                                  </button>
                                ))}
                              </div>
                            </div>
                          </>
                        )}
                      </div>
                      
                      {/* Send Button */}
                      <button
                        onClick={handleSendMessage}
                        disabled={(!inputValue.trim() && !attachedContent) || isProcessing}
                        className="p-2.5 rounded-xl bg-gradient-to-r from-teal-500 to-emerald-500 hover:from-teal-400 hover:to-emerald-400 disabled:opacity-30 disabled:cursor-not-allowed transition-all shadow-lg shadow-teal-500/20"
                      >
                        {isProcessing ? (
                          <Loader2 className="w-5 h-5 animate-spin text-white" />
                        ) : (
                          <ArrowRight className="w-5 h-5 text-white" />
                        )}
                      </button>
                    </div>
                  </div>
                </div>
              </div>
              
              {/* Quick Actions */}
              <div className="flex flex-wrap items-center justify-center gap-2 mt-6">
                {QUICK_ACTIONS.map((action, i) => (
                  <button
                    key={i}
                    onClick={() => handleQuickAction(action.prompt)}
                    className="flex items-center gap-2 px-4 py-2.5 rounded-xl bg-zinc-900/80 border border-zinc-800 text-sm text-zinc-400 hover:text-teal-400 hover:border-teal-500/30 hover:bg-zinc-900 transition-all"
                  >
                    <action.icon className="w-4 h-4" />
                    {action.label}
                  </button>
                ))}
              </div>
              
              {/* Plan Info */}
              <div className="text-center mt-10">
                <span className="text-xs text-zinc-600 uppercase tracking-wider">
                  {user?.subscription_tier || 'FREE'} Plan • Up to {maxRows.toLocaleString()} rows
                </span>
              </div>
            </div>
          </div>
        )}
        
        {/* Conversation Mode */}
        {isInConversation && (
          <div className="flex-1 flex flex-col overflow-hidden">
            {/* Header */}
            <div className="flex-shrink-0 flex items-center justify-between px-6 py-4 border-b border-zinc-800/60">
              <div className="flex items-center gap-3">
                <div className="w-8 h-8 rounded-xl bg-gradient-to-br from-teal-500 to-emerald-600 flex items-center justify-center shadow-lg shadow-teal-500/20">
                  <Image src="/logo.svg" alt="Synthesize" width={18} height={18} className="invert" />
                </div>
                <span className="text-sm font-medium text-zinc-300">Data Generator</span>
              </div>
              <button 
                onClick={handleReset} 
                className="flex items-center gap-2 px-3 py-2 text-sm text-zinc-500 hover:text-zinc-200 hover:bg-zinc-800 rounded-lg transition-colors"
              >
                <RotateCcw className="w-4 h-4" />
                New
              </button>
            </div>
            
            {/* Messages */}
            <div className="flex-1 overflow-y-auto">
              <div className="max-w-3xl mx-auto py-8 px-6 space-y-8">
                {messages.map((message) => (
                  <div key={message.id} className="group">
                    {message.role === 'user' ? (
                      // User Message
                      <div className="flex justify-end">
                        <div className="max-w-[85%] bg-zinc-800 rounded-2xl rounded-br-lg px-5 py-4">
                          <p className="text-[15px] text-zinc-100 leading-relaxed whitespace-pre-wrap">
                            {message.content}
                          </p>
                        </div>
                      </div>
                    ) : (
                      // Assistant Message
                      <div className="flex gap-4">
                        <div className="flex-shrink-0 w-8 h-8 rounded-xl bg-gradient-to-br from-teal-500 to-emerald-600 flex items-center justify-center shadow-lg shadow-teal-500/20">
                          <Sparkles className="w-4 h-4 text-white" />
                        </div>
                        <div className="flex-1 min-w-0 pt-1">
                          {message.metadata?.status === 'thinking' ? (
                            <div className="flex items-center gap-3 text-zinc-400">
                              <div className="flex gap-1">
                                <span className="w-2 h-2 bg-teal-400 rounded-full animate-bounce" style={{ animationDelay: '0ms' }} />
                                <span className="w-2 h-2 bg-teal-400 rounded-full animate-bounce" style={{ animationDelay: '150ms' }} />
                                <span className="w-2 h-2 bg-teal-400 rounded-full animate-bounce" style={{ animationDelay: '300ms' }} />
                              </div>
                              <span className="text-sm">Analyzing your request...</span>
                            </div>
                          ) : message.metadata?.status === 'generating' ? (
                            <div className="flex items-center gap-3 text-teal-400">
                              <Loader2 className="w-5 h-5 animate-spin" />
                              <span>{message.content}</span>
                            </div>
                          ) : (
                            <>
                              <div className="text-[15px] text-zinc-300 leading-relaxed">
                                {renderContent(message.content)}
                              </div>
                              
                              {/* Schema Preview */}
                              {message.metadata?.status === 'ready' && message.metadata.schema?.fields && (
                                <div className="mt-5">
                                  <div className="flex items-center gap-2 mb-3">
                                    <span className="text-xs font-medium text-zinc-500 uppercase tracking-wide">Schema Fields</span>
                                    <button 
                                      onClick={startEditingSchema}
                                      className="flex items-center gap-1.5 px-2.5 py-1 text-xs text-teal-400 hover:text-teal-300 hover:bg-teal-500/10 rounded-lg transition-colors"
                                    >
                                      <Edit3 className="w-3 h-3" />
                                      Edit Schema
                                    </button>
                                  </div>
                                  <div className="flex flex-wrap gap-2">
                                    {message.metadata.schema.fields.slice(0, 12).map((field: any, i: number) => (
                                      <span 
                                        key={i} 
                                        className="inline-flex items-center gap-1.5 px-3 py-1.5 bg-zinc-800/80 border border-zinc-700/50 rounded-lg text-xs text-zinc-300 group/field hover:border-teal-500/50 transition-colors cursor-default"
                                        title={`${field.data_type}${field.description ? ` — ${field.description}` : ''}`}
                                      >
                                        <Database className="w-3 h-3 text-teal-500" />
                                        {field.name}
                                        <span className="text-zinc-600 text-[10px] ml-0.5">{field.data_type}</span>
                                      </span>
                                    ))}
                                    {message.metadata.schema.fields.length > 12 && (
                                      <span className="inline-flex items-center px-3 py-1.5 bg-zinc-800/50 rounded-lg text-xs text-zinc-500">
                                        +{message.metadata.schema.fields.length - 12} more
                                      </span>
                                    )}
                                  </div>
                                </div>
                              )}
                              
                              {/* Feedback */}
                              {(message.metadata?.status === 'ready' || message.metadata?.status === 'complete') && (
                                <div className="flex items-center gap-1 mt-4 opacity-0 group-hover:opacity-100 transition-opacity">
                                  <button className="p-2 text-zinc-600 hover:text-zinc-300 hover:bg-zinc-800 rounded-lg transition-colors">
                                    <Copy className="w-4 h-4" />
                                  </button>
                                  <button className="p-2 text-zinc-600 hover:text-zinc-300 hover:bg-zinc-800 rounded-lg transition-colors">
                                    <ThumbsUp className="w-4 h-4" />
                                  </button>
                                  <button className="p-2 text-zinc-600 hover:text-zinc-300 hover:bg-zinc-800 rounded-lg transition-colors">
                                    <ThumbsDown className="w-4 h-4" />
                                  </button>
                                </div>
                              )}
                            </>
                          )}
                        </div>
                      </div>
                    )}
                  </div>
                ))}
                <div ref={messagesEndRef} />
              </div>
            </div>

            {/* Schema Editor Modal */}
            {isEditingSchema && (
              <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/60 backdrop-blur-sm">
                <div className="w-full max-w-2xl bg-zinc-900 border border-zinc-700 rounded-2xl shadow-2xl overflow-hidden">
                  {/* Header */}
                  <div className="flex items-center justify-between px-6 py-4 border-b border-zinc-800">
                    <div>
                      <h2 className="text-lg font-semibold text-white">Edit Schema</h2>
                      <p className="text-sm text-zinc-400 mt-0.5">Add, remove, or modify fields</p>
                    </div>
                    <button 
                      onClick={cancelEditingSchema}
                      className="p-2 text-zinc-400 hover:text-zinc-200 hover:bg-zinc-800 rounded-lg transition-colors"
                    >
                      <X className="w-5 h-5" />
                    </button>
                  </div>

                  {/* Fields List */}
                  <div className="px-6 py-4 max-h-[400px] overflow-y-auto">
                    <div className="space-y-2">
                      {editableSchema.map((field, index) => (
                        <div 
                          key={index}
                          className="flex items-center gap-3 p-3 bg-zinc-800/50 border border-zinc-700/50 rounded-xl group"
                        >
                          <Database className="w-4 h-4 text-teal-500 flex-shrink-0" />
                          <div className="flex-1 min-w-0">
                            <input
                              type="text"
                              value={field.name}
                              onChange={(e) => {
                                const newSchema = [...editableSchema];
                                newSchema[index] = { ...field, name: e.target.value };
                                setEditableSchema(newSchema);
                              }}
                              className="w-full bg-transparent text-zinc-200 text-sm font-medium focus:outline-none"
                              placeholder="Field name"
                            />
                          </div>
                          <select
                            value={field.data_type}
                            onChange={(e) => updateFieldType(index, e.target.value)}
                            className="px-2 py-1 bg-zinc-700 border border-zinc-600 rounded-lg text-xs text-zinc-300 focus:outline-none focus:border-teal-500 cursor-pointer"
                          >
                            {DATA_TYPES.map(type => (
                              <option key={type} value={type}>{type}</option>
                            ))}
                          </select>
                          <button
                            onClick={() => removeField(index)}
                            className="p-1.5 text-zinc-600 hover:text-red-400 hover:bg-red-500/10 rounded-lg transition-colors opacity-0 group-hover:opacity-100"
                          >
                            <Trash2 className="w-4 h-4" />
                          </button>
                        </div>
                      ))}
                    </div>

                    {/* Add New Field */}
                    <div className="flex items-center gap-3 mt-4 p-3 border border-dashed border-zinc-700 rounded-xl">
                      <Plus className="w-4 h-4 text-zinc-500" />
                      <input
                        type="text"
                        value={newFieldName}
                        onChange={(e) => setNewFieldName(e.target.value)}
                        onKeyDown={(e) => e.key === 'Enter' && addField()}
                        placeholder="New field name..."
                        className="flex-1 bg-transparent text-zinc-200 text-sm focus:outline-none placeholder-zinc-600"
                      />
                      <select
                        value={newFieldType}
                        onChange={(e) => setNewFieldType(e.target.value)}
                        className="px-2 py-1 bg-zinc-800 border border-zinc-700 rounded-lg text-xs text-zinc-400 focus:outline-none cursor-pointer"
                      >
                        {DATA_TYPES.map(type => (
                          <option key={type} value={type}>{type}</option>
                        ))}
                      </select>
                      <button
                        onClick={addField}
                        disabled={!newFieldName.trim()}
                        className="px-3 py-1.5 bg-teal-500/10 text-teal-400 text-xs font-medium rounded-lg hover:bg-teal-500/20 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
                      >
                        Add
                      </button>
                    </div>
                  </div>

                  {/* Footer */}
                  <div className="flex items-center justify-between px-6 py-4 border-t border-zinc-800 bg-zinc-900/50">
                    <span className="text-sm text-zinc-500">
                      {editableSchema.length} field{editableSchema.length !== 1 ? 's' : ''}
                    </span>
                    <div className="flex items-center gap-3">
                      <button
                        onClick={cancelEditingSchema}
                        className="px-4 py-2 text-sm text-zinc-400 hover:text-zinc-200 transition-colors"
                      >
                        Cancel
                      </button>
                      <button
                        onClick={applySchemaChanges}
                        className="px-4 py-2 bg-zinc-800 hover:bg-zinc-700 text-zinc-200 text-sm font-medium rounded-lg transition-colors"
                      >
                        Apply Changes
                      </button>
                      <button
                        onClick={refineSchemaWithAI}
                        disabled={isRefiningSchema || editableSchema.length === 0}
                        className="flex items-center gap-2 px-4 py-2 bg-gradient-to-r from-teal-500 to-emerald-500 hover:from-teal-400 hover:to-emerald-400 text-white text-sm font-medium rounded-lg disabled:opacity-50 disabled:cursor-not-allowed transition-all"
                      >
                        {isRefiningSchema ? (
                          <>
                            <Loader2 className="w-4 h-4 animate-spin" />
                            Refining...
                          </>
                        ) : (
                          <>
                            <Wand2 className="w-4 h-4" />
                            Refine with AI
                          </>
                        )}
                      </button>
                    </div>
                  </div>
                </div>
              </div>
            )}
            
            {/* Generation Controls */}
            {isReadyToGenerate && currentSchema && !isEditingSchema && (
              <div className="flex-shrink-0 border-t border-zinc-800/60 bg-zinc-900/50 backdrop-blur-sm">
                <div className="max-w-3xl mx-auto px-6 py-5">
                  <div className="flex flex-wrap items-center gap-6 mb-4">
                    {/* Row Count */}
                    <div className="flex items-center gap-3">
                      <span className="text-xs text-zinc-500 uppercase tracking-wide">Rows</span>
                      <div className="flex gap-1">
                        {[100, 500, 1000, 5000, 10000].filter(n => n <= maxRows).map(count => (
                          <button
                            key={count}
                            onClick={() => updateRowCount(count)}
                            className={`px-3 py-1.5 text-xs rounded-lg font-medium transition-colors ${
                              currentSettings.rowCount === count
                                ? 'bg-teal-500 text-white'
                                : 'bg-zinc-800 text-zinc-400 hover:bg-zinc-700 hover:text-zinc-200'
                            }`}
                          >
                            {count >= 1000 ? `${count / 1000}K` : count}
                          </button>
                        ))}
                      </div>
                    </div>
                    
                    {/* Format */}
                    <div className="flex items-center gap-3">
                      <span className="text-xs text-zinc-500 uppercase tracking-wide">Format</span>
                      <div className="flex gap-1">
                        {(['csv', 'json', 'sql'] as const).map(format => (
                          <button
                            key={format}
                            onClick={() => updateFormat(format)}
                            className={`px-3 py-1.5 text-xs rounded-lg font-medium uppercase transition-colors ${
                              currentSettings.outputFormat === format
                                ? 'bg-teal-500 text-white'
                                : 'bg-zinc-800 text-zinc-400 hover:bg-zinc-700 hover:text-zinc-200'
                            }`}
                          >
                            {format}
                          </button>
                        ))}
                      </div>
                    </div>
                  </div>

                  <Button
                    className="w-full bg-gradient-to-r from-teal-500 to-emerald-500 hover:from-teal-400 hover:to-emerald-400 text-white font-medium py-3 rounded-xl shadow-xl shadow-teal-500/20 text-base"
                    onClick={handleGenerateDataset}
                    disabled={isProcessing || createDataset.isPending}
                  >
                    {isProcessing || createDataset.isPending ? (
                      <>
                        <Loader2 className="w-5 h-5 mr-2 animate-spin" />
                        Generating...
                      </>
                    ) : (
                      <>
                        <Zap className="w-5 h-5 mr-2" />
                        Generate {currentSettings.rowCount.toLocaleString()} Rows
                      </>
                    )}
                  </Button>
                </div>
              </div>
            )}
            
            {/* Input */}
            <div className="flex-shrink-0 border-t border-zinc-800/60 bg-zinc-950">
              <div className="max-w-3xl mx-auto px-6 py-4">
                <div className="relative bg-zinc-900 rounded-xl border border-zinc-800 overflow-hidden transition-all focus-within:border-zinc-700">
                  {attachedFile && (
                    <div className="mx-3 mt-3 flex items-center gap-2 p-2.5 bg-zinc-800/60 rounded-lg border border-zinc-700/50">
                      <FileSpreadsheet className="w-4 h-4 text-teal-400" />
                      <span className="text-sm text-zinc-300 flex-1 truncate">{attachedFile.name}</span>
                      <button onClick={handleRemoveFile} className="p-1 hover:bg-zinc-700 rounded transition-colors">
                        <X className="w-4 h-4 text-zinc-400" />
                      </button>
                    </div>
                  )}
                  
                  <textarea
                    ref={inputRef}
                    value={inputValue}
                    onChange={(e) => setInputValue(e.target.value)}
                    onKeyDown={handleKeyPress}
                    placeholder="Refine your request or describe new data..."
                    className="w-full bg-transparent text-zinc-100 placeholder-zinc-600 px-4 pt-4 pb-14 resize-none focus:outline-none text-[15px] min-h-[56px] max-h-[160px]"
                    rows={1}
                    disabled={isProcessing}
                  />
                  
                  <div className="absolute bottom-2.5 left-2.5 right-2.5 flex items-center justify-between">
                    <div className="flex items-center gap-0.5">
                      <input
                        ref={fileInputRef}
                        type="file"
                        accept=".csv,.json,.xlsx,.xls"
                        onChange={handleFileChange}
                        className="hidden"
                      />
                      <button
                        onClick={() => fileInputRef.current?.click()}
                        className="p-2 text-zinc-500 hover:text-zinc-300 hover:bg-zinc-800 rounded-lg transition-colors"
                      >
                        <Paperclip className="w-4 h-4" />
                      </button>
                    </div>
                    
                    <button
                      onClick={handleSendMessage}
                      disabled={(!inputValue.trim() && !attachedContent) || isProcessing}
                      className="p-2 rounded-lg bg-teal-500 hover:bg-teal-400 disabled:opacity-30 disabled:cursor-not-allowed transition-colors"
                    >
                      {isProcessing ? (
                        <Loader2 className="w-4 h-4 animate-spin text-white" />
                      ) : (
                        <ArrowRight className="w-4 h-4 text-white" />
                      )}
                    </button>
                  </div>
                </div>
              </div>
            </div>
          </div>
        )}
        </div>
      </div>
    </DashboardLayout>
  );
}
