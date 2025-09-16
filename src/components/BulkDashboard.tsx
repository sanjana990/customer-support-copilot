import { useState } from 'react';
import { ChevronDown, ChevronUp, Eye, Clock, ExternalLink, Brain, MessageSquare } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Card } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Collapsible, CollapsibleContent, CollapsibleTrigger } from '@/components/ui/collapsible';
import { TicketData, TopicType, SentimentType, PriorityType } from '@/types/api';

// Mock data for demonstration
const mockTickets: TicketData[] = [
  {
    id: '1',
    timestamp: new Date().toISOString(),
    query: 'My API authentication is not working and I need help immediately',
    answer: 'I understand you\'re having issues with API authentication. Let me help you troubleshoot this...',
    citations: [
      { doc: 'API Authentication Guide', url: 'https://docs.atlan.com/api/authentication' }
    ],
    classification: {
      topic: 'API/SDK' as TopicType,
      sentiment: 'Frustrated' as SentimentType,
      priority: 'P0' as PriorityType,
      confidence: 0.92
    },
    classification_reasons: {
      topic: 'Mentions \'API, authentication\' → classified under API/SDK.',
      sentiment: 'Negative wording \'not working, error\' → classified as Frustrated.',
      priority: 'Contains critical words \'urgent, blocked\' → urgent priority (P0).'
    },
    processing_time: 2.34,
    cache_hit: false,
    followup_suggestions: [
      { question: 'Can you show me an example of how to use this API?' }
    ],
    session_id: '550e8400-e29b-41d4-a716-446655440000'
  }
];

function getTopicColor(topic: string) {
  const colors = {
    'API/SDK': 'bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-300',
    'How-to': 'bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-300',
    'Connector': 'bg-purple-100 text-purple-800 dark:bg-purple-900 dark:text-purple-300',
    'SSO': 'bg-orange-100 text-orange-800 dark:bg-orange-900 dark:text-orange-300',
    'Product': 'bg-gray-100 text-gray-800 dark:bg-gray-900 dark:text-gray-300',
  };
  return colors[topic as keyof typeof colors] || colors['Product'];
}

function getSentimentColor(sentiment: string) {
  const colors = {
    'Urgent': 'bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-300',
    'Frustrated': 'bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-300',
    'Positive': 'bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-300',
    'Curious': 'bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-300',
    'Neutral': 'bg-gray-100 text-gray-800 dark:bg-gray-900 dark:text-gray-300',
  };
  return colors[sentiment as keyof typeof colors] || colors['Neutral'];
}

function getPriorityColor(priority: string) {
  const colors = {
    'P0': 'bg-red-100 text-red-800 border-red-200 dark:bg-red-900 dark:text-red-300 dark:border-red-800',
    'P1': 'bg-orange-100 text-orange-800 border-orange-200 dark:bg-orange-900 dark:text-orange-300 dark:border-orange-800',
    'P2': 'bg-yellow-100 text-yellow-800 border-yellow-200 dark:bg-yellow-900 dark:text-yellow-300 dark:border-yellow-800',
  };
  return colors[priority as keyof typeof colors] || colors['P2'];
}

interface ExpandedRowProps {
  ticket: TicketData;
}

function ExpandedRow({ ticket }: ExpandedRowProps) {
  return (
    <div className="p-6 bg-muted/30 border-t border-dashboard-border">
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Classification Reasons */}
        <Card className="p-4">
          <div className="flex items-center gap-2 mb-3">
            <Brain className="w-4 h-4 text-brand-primary" />
            <h4 className="font-semibold text-sm">Classification Analysis</h4>
          </div>
          
          <div className="space-y-3">
            <div>
              <p className="text-xs font-medium text-muted-foreground mb-1">Topic Reasoning</p>
              <p className="text-sm">{ticket.classification_reasons.topic}</p>
            </div>
            
            <div>
              <p className="text-xs font-medium text-muted-foreground mb-1">Sentiment Reasoning</p>
              <p className="text-sm">{ticket.classification_reasons.sentiment}</p>
            </div>
            
            <div>
              <p className="text-xs font-medium text-muted-foreground mb-1">Priority Reasoning</p>
              <p className="text-sm">{ticket.classification_reasons.priority}</p>
            </div>
          </div>
        </Card>

        {/* AI Response */}
        <Card className="p-4">
          <div className="flex items-center gap-2 mb-3">
            <MessageSquare className="w-4 h-4 text-brand-primary" />
            <h4 className="font-semibold text-sm">AI Response</h4>
          </div>
          
          <p className="text-sm mb-4">{ticket.answer}</p>
          
          {ticket.citations.length > 0 && (
            <div>
              <p className="text-xs font-medium text-muted-foreground mb-2">Citations</p>
              <div className="space-y-2">
                {ticket.citations.map((citation, index) => (
                  <Button
                    key={index}
                    variant="ghost"
                    size="sm"
                    className="justify-start h-auto p-2 text-xs"
                    asChild
                  >
                    <a href={citation.url} target="_blank" rel="noopener noreferrer">
                      <ExternalLink className="w-3 h-3 mr-2" />
                      {citation.doc}
                    </a>
                  </Button>
                ))}
              </div>
            </div>
          )}
        </Card>
      </div>
    </div>
  );
}

export function BulkDashboard() {
  const [tickets] = useState<TicketData[]>(mockTickets);
  const [expandedRows, setExpandedRows] = useState<Set<string>>(new Set());

  const toggleExpanded = (ticketId: string) => {
    setExpandedRows(prev => {
      const newSet = new Set(prev);
      if (newSet.has(ticketId)) {
        newSet.delete(ticketId);
      } else {
        newSet.add(ticketId);
      }
      return newSet;
    });
  };

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-xl font-semibold">Ticket Classification Dashboard</h2>
          <p className="text-sm text-muted-foreground">
            View and analyze customer support queries with AI-powered classification
          </p>
        </div>
        <Badge variant="secondary" className="px-3 py-1">
          {tickets.length} ticket{tickets.length !== 1 ? 's' : ''}
        </Badge>
      </div>

      <div className="space-y-2">
        {tickets.map((ticket) => (
          <Collapsible 
            key={ticket.id}
            open={expandedRows.has(ticket.id)}
            onOpenChange={() => toggleExpanded(ticket.id)}
          >
            <Card className="overflow-hidden hover:shadow-medium transition-shadow">
              <CollapsibleTrigger asChild>
                <div className="p-4 cursor-pointer hover:bg-muted/30 transition-colors">
                  <div className="flex items-center justify-between">
                    <div className="flex-1 space-y-2">
                      <div className="flex items-center gap-3">
                        <Badge className={getPriorityColor(ticket.classification.priority)}>
                          {ticket.classification.priority}
                        </Badge>
                        <Badge variant="outline" className={getTopicColor(ticket.classification.topic)}>
                          {ticket.classification.topic}
                        </Badge>
                        <Badge variant="outline" className={getSentimentColor(ticket.classification.sentiment)}>
                          {ticket.classification.sentiment}
                        </Badge>
                        <div className="flex items-center gap-1 text-xs text-muted-foreground">
                          <Clock className="w-3 h-3" />
                          {ticket.processing_time}s
                        </div>
                      </div>
                      
                      <p className="text-sm font-medium line-clamp-2">{ticket.query}</p>
                      
                      <p className="text-xs text-muted-foreground">
                        {new Date(ticket.timestamp).toLocaleString()} • 
                        Confidence: {Math.round(ticket.classification.confidence * 100)}%
                      </p>
                    </div>
                    
                    <div className="flex items-center gap-2">
                      <Button variant="ghost" size="sm" className="text-brand-primary">
                        <Eye className="w-4 h-4 mr-1" />
                        View
                      </Button>
                      {expandedRows.has(ticket.id) ? (
                        <ChevronUp className="w-4 h-4 text-muted-foreground" />
                      ) : (
                        <ChevronDown className="w-4 h-4 text-muted-foreground" />
                      )}
                    </div>
                  </div>
                </div>
              </CollapsibleTrigger>
              
              <CollapsibleContent>
                <ExpandedRow ticket={ticket} />
              </CollapsibleContent>
            </Card>
          </Collapsible>
        ))}
      </div>
    </div>
  );
}