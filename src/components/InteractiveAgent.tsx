import { Button } from '@/components/ui/button';
import { Card } from '@/components/ui/card';
import { Input } from '@/components/ui/input';
import { ScrollArea } from '@/components/ui/scroll-area';
import { useToast } from '@/hooks/use-toast';
import { apiService } from '@/lib/api';
import { QueryResponse } from '@/types/api';
import { Bot, Brain, CheckCircle, ExternalLink, Loader2, Send, Trash2, X } from 'lucide-react';
import { useEffect, useRef, useState } from 'react';

interface Message {
  id: string;
  type: 'user' | 'assistant';
  content: string;
  timestamp: Date;
  response?: QueryResponse;
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

  return (
    <div className="flex flex-col h-[700px] max-w-4xl mx-auto">
      {/* Header */}
      <div className="flex items-center justify-between p-6 border-b border-gray-200">
        <div>
          <h2 className="text-2xl font-semibold text-gray-900">Interactive AI Agent</h2>
          <p className="text-sm text-gray-600 mt-1">
            Chat with AI and get ticket analysis with follow-up suggestions
          </p>
        </div>
        <Button
          variant="outline"
          size="sm"
          onClick={clearConversation}
          className="text-red-600 hover:bg-red-50 border-red-200"
        >
          <Trash2 className="w-4 h-4 mr-2" />
          Clear Chat
        </Button>
      </div>

      <ScrollArea ref={scrollAreaRef} className="flex-1 p-6">
        <div className="space-y-6">
          {messages.length === 0 ? (
            <div className="text-center text-gray-500 py-12">
              <Bot className="w-16 h-16 mx-auto mb-4 opacity-40" />
              <p className="text-lg mb-2">Start a conversation with the AI agent</p>
              <p className="text-sm">Ask any question about your tickets or product issues</p>
            </div>
          ) : (
            messages.map((message) => (
              <div key={message.id} className="space-y-4">
                {message.type === 'user' && (
                  <div className="flex justify-end">
                    <Card className="bg-blue-600 text-white p-4 max-w-[80%] rounded-lg">
                      <p className="text-sm leading-relaxed">{message.content}</p>
                    </Card>
                  </div>
                )}
                
                {message.type === 'assistant' && message.response && (
                  <div className="space-y-6">
                    {/* Analysis Section */}
                    <Card className="p-6 bg-white border border-gray-200 rounded-lg shadow-sm">
                      <div className="flex items-center gap-2 mb-4">
                        <CheckCircle className="w-5 h-5 text-green-600" />
                        <h3 className="text-lg font-semibold text-gray-900">Analysis</h3>
                      </div>
                      
                      <div className="grid grid-cols-3 gap-4">
                        <div className="bg-gray-50 p-4 rounded-lg border border-gray-200">
                          <p className="text-sm text-gray-600 mb-1">Topic:</p>
                          <p className="text-lg font-semibold text-gray-900">
                            {message.response.classification.topic}
                          </p>
                        </div>
                        
                        <div className="bg-gray-50 p-4 rounded-lg border border-gray-200">
                          <p className="text-sm text-gray-600 mb-1">Sentiment:</p>
                          <p className="text-lg font-semibold text-gray-900">
                            {message.response.classification.sentiment}
                          </p>
                        </div>
                        
                        <div className="bg-gray-50 p-4 rounded-lg border border-gray-200">
                          <p className="text-sm text-gray-600 mb-1">Priority:</p>
                          <p className="text-lg font-semibold text-gray-900">
                            {message.response.classification.priority}
                          </p>
                        </div>
                      </div>
                    </Card>

                    {/* AI Response Section */}
                    <Card className="bg-white border border-gray-200 rounded-lg shadow-sm">
                      <div className="p-4 border-b border-gray-200">
                        <div className="flex items-center justify-between">
                          <div className="flex items-center gap-2">
                            <Bot className="w-5 h-5 text-gray-600" />
                            <h3 className="text-lg font-semibold text-gray-900">AI Response (Web Chat)</h3>
                          </div>
                          <div className="flex items-center gap-3">
                            <Button variant="ghost" size="sm" className="text-gray-400 hover:text-gray-600">
                              <X className="w-4 h-4" />
                              Close
                            </Button>
                            <div className="flex items-center gap-1 text-sm text-gray-500">
                              <CheckCircle className="w-4 h-4 text-orange-500" />
                              Cached
                            </div>
                            <div className="text-sm text-gray-500">
                              {(message.response.processing_time / 1000).toFixed(2)}s
                            </div>
                          </div>
                        </div>
                      </div>
                      
                      <div className="p-6">
                        <p className="text-gray-800 leading-relaxed whitespace-pre-line">
                          {message.response.answer}
                        </p>
                        
                        {/* Citations */}
                        {message.response.citations.length > 0 && (
                          <div className="mt-4 pt-4 border-t border-gray-200">
                            <p className="text-sm font-medium text-gray-600 mb-2">Sources:</p>
                            <div className="space-y-1">
                              {message.response.citations.map((citation, index) => (
                                <Button
                                  key={index}
                                  variant="ghost"
                                  size="sm"
                                  className="justify-start h-auto p-1 text-xs text-blue-600 hover:text-blue-800"
                                  asChild
                                >
                                  <a href={citation.url} target="_blank" rel="noopener noreferrer">
                                    <ExternalLink className="w-3 h-3 mr-1" />
                                    {citation.doc}
                                  </a>
                                </Button>
                              ))}
                            </div>
                          </div>
                        )}
                      </div>
                    </Card>

                    {/* Follow-up Questions */}
                    {message.response.followup_suggestions.length > 0 && (
                      <Card className="p-6 bg-green-50 border border-green-200 rounded-lg">
                        <div className="flex items-center gap-2 mb-4">
                          <Brain className="w-5 h-5 text-green-600" />
                          <h3 className="text-lg font-semibold text-gray-900">Suggested Follow-up Questions</h3>
                        </div>
                        
                        <div className="space-y-3">
                          {message.response.followup_suggestions.map((suggestion, index) => (
                            <div key={index} className="flex items-start gap-3">
                              <div className="w-6 h-6 rounded-full bg-green-600 text-white text-sm font-medium flex items-center justify-center flex-shrink-0">
                                {index + 1}
                              </div>
                              <Button
                                variant="ghost"
                                className="text-left h-auto p-0 text-gray-800 hover:text-green-600 font-normal"
                                onClick={() => {
                                  setInput(suggestion.question);
                                }}
                              >
                                {suggestion.question}
                              </Button>
                            </div>
                          ))}
                        </div>
                      </Card>
                    )}
                  </div>
                )}
              </div>
            ))
          )}
          
          {isLoading && (
            <div className="flex justify-center">
              <Card className="p-6 bg-white border border-gray-200 rounded-lg">
                <div className="flex items-center gap-3 text-gray-600">
                  <Loader2 className="w-5 h-5 animate-spin" />
                  <span>AI is analyzing your message...</span>
                </div>
              </Card>
            </div>
          )}
        </div>
      </ScrollArea>

      {/* Input Form */}
      <form onSubmit={handleSubmit} className="p-6 border-t border-gray-200 bg-gray-50">
        <div className="flex gap-3">
          <Input
            value={input}
            onChange={(e) => setInput(e.target.value)}
            placeholder="Ask a question about your tickets..."
            disabled={isLoading}
            className="flex-1 bg-white border-gray-300 focus:border-blue-500 focus:ring-blue-500"
          />
          <Button 
            type="submit" 
            disabled={isLoading || !input.trim()}
            className="bg-blue-600 hover:bg-blue-700 text-white px-6"
          >
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