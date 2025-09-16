import { useState, useRef, useEffect } from 'react';
import { Send, Bot, User, Brain, ExternalLink, Loader2, Trash2 } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Card } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Separator } from '@/components/ui/separator';
import { ScrollArea } from '@/components/ui/scroll-area';
import { Collapsible, CollapsibleContent, CollapsibleTrigger } from '@/components/ui/collapsible';
import { apiService } from '@/lib/api';
import { QueryResponse } from '@/types/api';
import { useToast } from '@/hooks/use-toast';

interface Message {
  id: string;
  type: 'user' | 'assistant';
  content: string;
  timestamp: Date;
  response?: QueryResponse;
  showAnalysis?: boolean;
}

interface InteractiveAgentProps {
  sessionId: string;
  onClearSession: () => void;
}

export function InteractiveAgent({ sessionId, onClearSession }: InteractiveAgentProps) {
  const [messages, setMessages] = useState<Message[]>([]);
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

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!input.trim() || isLoading) return;

    const userMessage: Message = {
      id: Date.now().toString(),
      type: 'user',
      content: input.trim(),
      timestamp: new Date(),
    };

    setMessages(prev => [...prev, userMessage]);
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
        showAnalysis: false,
      };

      setMessages(prev => [...prev, assistantMessage]);
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

  const toggleAnalysis = (messageId: string) => {
    setMessages(prev => prev.map(msg => 
      msg.id === messageId 
        ? { ...msg, showAnalysis: !msg.showAnalysis }
        : msg
    ));
  };

  const clearConversation = async () => {
    try {
      await apiService.clearConversation(sessionId);
      setMessages([]);
      onClearSession();
      toast({
        title: 'Success',
        description: 'Conversation cleared successfully',
      });
    } catch (error) {
      toast({
        title: 'Error', 
        description: 'Failed to clear conversation',
        variant: 'destructive',
      });
    }
  };

  const getTopicColor = (topic: string) => {
    const colors = {
      'API/SDK': 'bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-300',
      'How-to': 'bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-300',
      'Connector': 'bg-purple-100 text-purple-800 dark:bg-purple-900 dark:text-purple-300',
      'SSO': 'bg-orange-100 text-orange-800 dark:bg-orange-900 dark:text-orange-300',
      'Product': 'bg-gray-100 text-gray-800 dark:bg-gray-900 dark:text-gray-300',
    };
    return colors[topic as keyof typeof colors] || colors['Product'];
  };

  const getSentimentColor = (sentiment: string) => {
    const colors = {
      'Urgent': 'bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-300',
      'Frustrated': 'bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-300',
      'Positive': 'bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-300',
      'Curious': 'bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-300',
      'Neutral': 'bg-gray-100 text-gray-800 dark:bg-gray-900 dark:text-gray-300',
    };
    return colors[sentiment as keyof typeof colors] || colors['Neutral'];
  };

  const getPriorityColor = (priority: string) => {
    const colors = {
      'P0': 'bg-red-100 text-red-800 border-red-200',
      'P1': 'bg-orange-100 text-orange-800 border-orange-200',
      'P2': 'bg-yellow-100 text-yellow-800 border-yellow-200',
    };
    return colors[priority as keyof typeof colors] || colors['P2'];
  };

  return (
    <div className="flex flex-col h-[600px]">
      <div className="flex items-center justify-between p-4 border-b border-dashboard-border">
        <div>
          <h2 className="text-xl font-semibold">Interactive AI Agent</h2>
          <p className="text-sm text-muted-foreground">
            Chat with AI and see classification analysis in real-time
          </p>
        </div>
        <Button
          variant="outline"
          size="sm"
          onClick={clearConversation}
          className="text-danger hover:bg-danger/10"
        >
          <Trash2 className="w-4 h-4 mr-2" />
          Clear Chat
        </Button>
      </div>

      <ScrollArea ref={scrollAreaRef} className="flex-1 p-4">
        <div className="space-y-4">
          {messages.length === 0 ? (
            <div className="text-center text-muted-foreground py-8">
              <Bot className="w-12 h-12 mx-auto mb-4 opacity-50" />
              <p>Start a conversation with the AI agent</p>
              <p className="text-sm">Ask any question about your product or service</p>
            </div>
          ) : (
            messages.map((message) => (
              <div
                key={message.id}
                className={`flex gap-3 ${message.type === 'user' ? 'justify-end' : 'justify-start'}`}
              >
                <div className={`flex gap-3 max-w-[80%] ${message.type === 'user' ? 'flex-row-reverse' : 'flex-row'}`}>
                  <div className={`p-2 rounded-lg ${message.type === 'user' ? 'bg-brand-primary text-white' : 'bg-muted'}`}>
                    {message.type === 'user' ? (
                      <User className="w-5 h-5" />
                    ) : (
                      <Bot className="w-5 h-5" />
                    )}
                  </div>
                  
                  <div className="space-y-2 flex-1">
                    <Card className={`p-3 ${message.type === 'user' ? 'bg-brand-primary text-white' : 'bg-card'}`}>
                      <p className="text-sm leading-relaxed">{message.content}</p>
                    </Card>
                    
                    {message.type === 'assistant' && message.response && (
                      <div className="space-y-2">
                        {/* Classification badges */}
                        <div className="flex flex-wrap gap-2">
                          <Badge className={getPriorityColor(message.response.classification.priority)}>
                            {message.response.classification.priority}
                          </Badge>
                          <Badge variant="outline" className={getTopicColor(message.response.classification.topic)}>
                            {message.response.classification.topic}
                          </Badge>
                          <Badge variant="outline" className={getSentimentColor(message.response.classification.sentiment)}>
                            {message.response.classification.sentiment}
                          </Badge>
                        </div>

                        {/* Internal Analysis Toggle */}
                        <Collapsible
                          open={message.showAnalysis}
                          onOpenChange={() => toggleAnalysis(message.id)}
                        >
                          <CollapsibleTrigger asChild>
                            <Button
                              variant="ghost"
                              size="sm"
                              className="text-brand-primary hover:bg-brand-primary/10 p-1 h-auto"
                            >
                              <Brain className="w-4 h-4 mr-1" />
                              {message.showAnalysis ? 'Hide' : 'Show'} Internal Analysis
                            </Button>
                          </CollapsibleTrigger>
                          
                          <CollapsibleContent>
                            <Card className="p-3 mt-2 bg-muted/50">
                              <div className="space-y-3">
                                <div>
                                  <p className="text-xs font-medium text-muted-foreground mb-1">Topic Analysis</p>
                                  <p className="text-sm">{message.response.classification_reasons.topic}</p>
                                </div>
                                <Separator />
                                <div>
                                  <p className="text-xs font-medium text-muted-foreground mb-1">Sentiment Analysis</p>
                                  <p className="text-sm">{message.response.classification_reasons.sentiment}</p>
                                </div>
                                <Separator />
                                <div>
                                  <p className="text-xs font-medium text-muted-foreground mb-1">Priority Analysis</p>
                                  <p className="text-sm">{message.response.classification_reasons.priority}</p>
                                </div>
                              </div>
                            </Card>
                          </CollapsibleContent>
                        </Collapsible>

                        {/* Citations */}
                        {message.response.citations.length > 0 && (
                          <Card className="p-3 bg-muted/30">
                            <p className="text-xs font-medium text-muted-foreground mb-2">Sources</p>
                            <div className="space-y-1">
                              {message.response.citations.map((citation, index) => (
                                <Button
                                  key={index}
                                  variant="ghost"
                                  size="sm"
                                  className="justify-start h-auto p-1 text-xs"
                                  asChild
                                >
                                  <a href={citation.url} target="_blank" rel="noopener noreferrer">
                                    <ExternalLink className="w-3 h-3 mr-1" />
                                    {citation.doc}
                                  </a>
                                </Button>
                              ))}
                            </div>
                          </Card>
                        )}
                      </div>
                    )}
                    
                    <p className="text-xs text-muted-foreground">
                      {message.timestamp.toLocaleTimeString()}
                    </p>
                  </div>
                </div>
              </div>
            ))
          )}
          
          {isLoading && (
            <div className="flex justify-start">
              <div className="flex gap-3">
                <div className="p-2 rounded-lg bg-muted">
                  <Bot className="w-5 h-5" />
                </div>
                <Card className="p-3 bg-card">
                  <div className="flex items-center gap-2 text-sm text-muted-foreground">
                    <Loader2 className="w-4 h-4 animate-spin" />
                    AI is thinking...
                  </div>
                </Card>
              </div>
            </div>
          )}
        </div>
      </ScrollArea>

      <form onSubmit={handleSubmit} className="p-4 border-t border-dashboard-border">
        <div className="flex gap-2">
          <Input
            value={input}
            onChange={(e) => setInput(e.target.value)}
            placeholder="Ask a question..."
            disabled={isLoading}
            className="flex-1"
          />
          <Button type="submit" disabled={isLoading || !input.trim()}>
            {isLoading ? (
              <Loader2 className="w-4 h-4 animate-spin" />
            ) : (
              <Send className="w-4 h-4" />
            )}
          </Button>
        </div>
      </form>
    </div>
  );
}