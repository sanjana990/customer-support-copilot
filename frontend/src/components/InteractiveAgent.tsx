import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Card } from '@/components/ui/card';
import { Input } from '@/components/ui/input';
import { ScrollArea } from '@/components/ui/scroll-area';
import { useToast } from '@/hooks/use-toast';
import { apiService } from '@/lib/api';
import { QueryResponse } from '@/types/api';
import { Bot, Brain, CheckCircle, ExternalLink, Loader2, Send, Trash2, X, MessageSquare, ArrowRight, Info } from 'lucide-react';
import { useEffect, useRef, useState } from 'react';
import ReactMarkdown from 'react-markdown';
import { Prism as SyntaxHighlighter } from 'react-syntax-highlighter';
import { oneLight } from 'react-syntax-highlighter/dist/esm/styles/prism';
import { Message } from '@/hooks/useConversation';

function getTopicColor(topic: string) {
  const colors = {
    'How-to': 'bg-green-50 text-green-700 border-green-200',
    'Product': 'bg-blue-50 text-blue-700 border-blue-200',
    'Connector': 'bg-purple-50 text-purple-700 border-purple-200',
    'Lineage': 'bg-indigo-50 text-indigo-700 border-indigo-200',
    'API/SDK': 'bg-cyan-50 text-cyan-700 border-cyan-200',
    'SSO': 'bg-orange-50 text-orange-700 border-orange-200',
    'Glossary': 'bg-emerald-50 text-emerald-700 border-emerald-200',
    'Best practices': 'bg-violet-50 text-violet-700 border-violet-200',
    'Sensitive data': 'bg-red-50 text-red-700 border-red-200',
    'General': 'bg-gray-50 text-gray-700 border-gray-200',
  };
  return colors[topic as keyof typeof colors] || colors['General'];
}

function getSentimentColor(sentiment: string) {
  const colors = {
    'Urgent': 'bg-red-50 text-red-700 border-red-200',
    'Frustrated': 'bg-red-50 text-red-700 border-red-200',
    'Positive': 'bg-green-50 text-green-700 border-green-200',
    'Curious': 'bg-blue-50 text-blue-700 border-blue-200',
    'Neutral': 'bg-gray-50 text-gray-700 border-gray-200',
  };
  return colors[sentiment as keyof typeof colors] || colors['Neutral'];
}

function getPriorityColor(priority: string) {
  const colors = {
    'P0': 'bg-red-50 text-red-700 border-red-200',
    'P1': 'bg-orange-50 text-orange-700 border-orange-200',
    'P2': 'bg-yellow-50 text-yellow-700 border-yellow-200',
  };
  return colors[priority as keyof typeof colors] || colors['P2'];
}

interface InteractiveAgentProps {
  sessionId: string;
  messages: Message[];
  onAddMessage: (message: Message) => void;
  onClearSession: () => void;
}

function CopyButton({ text }: { text: string }) {
  const [copied, setCopied] = useState(false);

  const handleCopy = async () => {
    try {
      await navigator.clipboard.writeText(text);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    } catch (err) {
      console.error('Failed to copy text: ', err);
    }
  };

  return (
    <Button
      variant="ghost"
      size="sm"
      onClick={handleCopy}
      className="h-8 w-8 p-0 hover:bg-gray-100"
    >
      {copied ? (
        <CheckCircle className="h-4 w-4 text-green-600" />
      ) : (
        <ExternalLink className="h-4 w-4" />
      )}
    </Button>
  );
}

export function InteractiveAgent({ sessionId, messages, onAddMessage, onClearSession }: InteractiveAgentProps) {
  const [input, setInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const scrollAreaRef = useRef<HTMLDivElement>(null);
  const { toast } = useToast();

  const scrollToBottom = () => {
    if (scrollAreaRef.current) {
      const scrollContainer = scrollAreaRef.current.querySelector('[data-radix-scroll-area-viewport]');
      if (scrollContainer) {
        scrollContainer.scrollTop = scrollContainer.scrollHeight;
      }
    }
  };

  // Only scroll to bottom when a user message is added, not for assistant responses
  useEffect(() => {
    if (messages.length > 0) {
      const lastMessage = messages[messages.length - 1];
      // Only scroll if the last message is from user, not assistant
      if (lastMessage.type === 'user') {
        const timer = setTimeout(() => {
          scrollToBottom();
        }, 100);
        return () => clearTimeout(timer);
      }
    }
  }, [messages.length, messages]); // Trigger when message count changes or messages change

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!input.trim() || isLoading) return;

    const userMessage: Message = {
      id: Date.now().toString(),
      type: 'user',
      content: input.trim(),
      timestamp: new Date(),
    };

    onAddMessage(userMessage);
    setInput('');
    setIsLoading(true);

    try {
      const response = await apiService.submitQuery({
        query: userMessage.content,
        session_id: sessionId,
        channel: 'Web Chat',
        include_followup: true,
      });

      const assistantMessage: Message = {
        id: (Date.now() + 1).toString(),
        type: 'assistant',
        content: response.answer,
        timestamp: new Date(),
        response,
      };

      onAddMessage(assistantMessage);
    } catch (error) {
      toast({
        title: 'Error',
        description: error instanceof Error ? error.message : 'Failed to send message',
        variant: 'destructive',
      });
    } finally {
      setIsLoading(false);
    }
  };

  const handleFollowup = async (question: string) => {
    if (isLoading) return;

    const userMessage: Message = {
      id: Date.now().toString(),
      type: 'user',
      content: question,
      timestamp: new Date(),
    };

    onAddMessage(userMessage);
    setIsLoading(true);

    try {
      const response = await apiService.submitFollowupQuery({
        query: question,
        session_id: sessionId,
        channel: 'Web Chat',
        include_followup: true,
      });

      const assistantMessage: Message = {
        id: (Date.now() + 1).toString(),
        type: 'assistant',
        content: response.answer,
        timestamp: new Date(),
        response,
      };

      onAddMessage(assistantMessage);
    } catch (error) {
      toast({
        title: 'Error',
        description: error instanceof Error ? error.message : 'Failed to send follow-up',
        variant: 'destructive',
      });
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="flex flex-col h-[600px]">
      {/* Header */}
      <div className="flex items-center justify-between p-4 border-b border-gray-200 bg-gray-50">
        <div className="flex items-center gap-3">
          <div className="p-2 bg-blue-50 rounded-lg">
            <Bot className="w-6 h-6 text-blue-600" />
          </div>
          <div>
            <h2 className="text-lg font-semibold text-gray-900">Interactive AI Agent</h2>
            <p className="text-sm text-gray-600">Submit tickets and get AI-powered analysis with intelligent routing</p>
          </div>
        </div>
        <Button
          variant="destructive"
          size="sm"
          onClick={onClearSession}
          className="flex items-center gap-2"
        >
          <Trash2 className="w-4 h-4" />
          Clear Chat
        </Button>
      </div>

      {/* Messages */}
      <ScrollArea ref={scrollAreaRef} className="flex-1 p-4 space-y-4">
        {messages.length === 0 ? (
          <div className="flex flex-col items-center justify-center h-full text-center">
            <MessageSquare className="w-12 h-12 text-gray-400 mb-4" />
            <h3 className="text-lg font-medium text-gray-900 mb-2">Start a conversation</h3>
            <p className="text-gray-600">Ask me anything about Atlan or submit a support ticket</p>
          </div>
        ) : (
          messages.map((message) => (
            <div
              key={message.id}
              className={`flex ${message.type === 'user' ? 'justify-end' : 'justify-start'}`}
            >
              <div
                className={`max-w-[80%] rounded-lg p-4 ${
                  message.type === 'user'
                    ? 'bg-blue-600 text-white'
                    : 'bg-white border border-gray-200'
                }`}
              >
                {message.type === 'assistant' && message.response ? (
                  <div className="space-y-4">
                    {/* AI Response */}
                    <div>
                      <div className="flex items-center gap-2 mb-2">
                        <Badge variant="outline" className="text-xs">
                          {message.response.response_type === 'rag_response' ? 'AI Response' : 'Routing Message'}
                        </Badge>
                        <span className="text-xs text-gray-500">
                          {message.response.processing_time.toFixed(2)}s
                        </span>
                      </div>
                      <div className="prose prose-sm max-w-none">
                        <ReactMarkdown
                          components={{
                            code({ node, inline, className, children, ...props }: any) {
                              const match = /language-(\w+)/.exec(className || '');
                              return !inline && match ? (
                                <div className="relative">
                                  <CopyButton text={String(children).replace(/\n$/, '')} />
                                  <SyntaxHighlighter
                                    style={oneLight}
                                    language={match[1]}
                                    PreTag="div"
                                    {...props}
                                  >
                                    {String(children).replace(/\n$/, '')}
                                  </SyntaxHighlighter>
                                </div>
                              ) : (
                                <code className={className} {...props}>
                                  {children}
                                </code>
                              );
                            },
                          }}
                        >
                          {message.content}
                        </ReactMarkdown>
                      </div>
                    </div>

                    {/* Citations */}
                    {message.response.citations && message.response.citations.length > 0 && (
                      <div className="mt-4 p-3 bg-gray-50 rounded-lg">
                        <h4 className="text-sm font-medium text-gray-900 mb-2">Sources:</h4>
                        <div className="space-y-1">
                          {message.response.citations.map((citation, index) => (
                            <a
                              key={index}
                              href={citation.url}
                              target="_blank"
                              rel="noopener noreferrer"
                              className="flex items-center gap-2 text-sm text-blue-600 hover:text-blue-800"
                            >
                              <ExternalLink className="w-3 h-3" />
                              {citation.doc}
                            </a>
                          ))}
                        </div>
                      </div>
                    )}

                    {/* Analysis */}
                    <div className="border-t pt-4">
                      <div className="flex items-center gap-2 mb-3">
                        <Brain className="w-4 h-4 text-blue-600" />
                        <h4 className="text-sm font-medium text-gray-900">Analysis</h4>
                      </div>
                      
                      <div className="grid grid-cols-3 gap-3 mb-4">
                        <div className="text-center p-2 bg-gray-50 rounded">
                          <div className="text-xs text-gray-600 mb-1">Topic</div>
                          <Badge variant="outline" className={`text-xs ${getTopicColor(message.response.classification.topic)}`}>
                            {message.response.classification.topic}
                          </Badge>
                        </div>
                        <div className="text-center p-2 bg-gray-50 rounded">
                          <div className="text-xs text-gray-600 mb-1">Sentiment</div>
                          <Badge variant="outline" className={`text-xs ${getSentimentColor(message.response.classification.sentiment)}`}>
                            {message.response.classification.sentiment}
                          </Badge>
                        </div>
                        <div className="text-center p-2 bg-gray-50 rounded">
                          <div className="text-xs text-gray-600 mb-1">Priority</div>
                          <Badge className={`text-xs ${getPriorityColor(message.response.classification.priority)}`}>
                            {message.response.classification.priority}
                          </Badge>
                        </div>
                      </div>

                      {/* Follow-up Questions */}
                      {message.response.followup_suggestions && message.response.followup_suggestions.length > 0 && (
                        <div className="mt-4">
                          <h5 className="text-sm font-medium text-gray-900 mb-2">Follow-up Questions:</h5>
                          <div className="space-y-2">
                            {message.response.followup_suggestions.map((suggestion, index) => (
                              <Button
                                key={index}
                                variant="outline"
                                size="sm"
                                onClick={() => handleFollowup(suggestion.question)}
                                className="w-full justify-start text-left h-auto p-3 hover:bg-gray-50 hover:text-gray-900"
                              >
                                <ArrowRight className="w-3 h-3 mr-2 flex-shrink-0" />
                                <span className="text-sm">{suggestion.question}</span>
                              </Button>
                            ))}
                          </div>
                        </div>
                      )}
                    </div>
                  </div>
                ) : (
                  <p className="text-sm">{message.content}</p>
                )}
              </div>
            </div>
          ))
        )}
        
        {isLoading && (
          <div className="flex justify-start">
            <div className="bg-white border border-gray-200 rounded-lg p-4">
              <div className="flex items-center gap-2">
                <Loader2 className="w-4 h-4 animate-spin" />
                <span className="text-sm text-gray-600">AI is thinking...</span>
              </div>
            </div>
          </div>
        )}
      </ScrollArea>

      {/* Input */}
      <div className="border-t border-gray-200 p-4">
        <form onSubmit={handleSubmit} className="flex gap-2">
          <Input
            value={input}
            onChange={(e) => setInput(e.target.value)}
            placeholder="Ask me anything about Atlan..."
            className="flex-1"
            disabled={isLoading}
          />
          <Button type="submit" disabled={isLoading || !input.trim()}>
            <Send className="w-4 h-4" />
          </Button>
        </form>
      </div>
    </div>
  );
}
