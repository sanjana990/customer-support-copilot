import { useState } from 'react';
import { ChevronDown, ChevronUp, Eye, Clock, ExternalLink, Brain, MessageSquare, AlertTriangle, CheckSquare2, BarChart3 } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Card } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Checkbox } from '@/components/ui/checkbox';
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '@/components/ui/table';
import { Collapsible, CollapsibleContent } from '@/components/ui/collapsible';
import { TicketData, TopicType, SentimentType, PriorityType } from '@/types/api';

// Mock data for demonstration
const mockTickets: TicketData[] = [
  {
    id: 'TICKET-001',
    timestamp: new Date(Date.now() - 86400000).toISOString(),
    query: 'My API authentication is not working and I need help immediately',
    answer: 'I understand you\'re having issues with API authentication. Let me help you troubleshoot this step by step. First, ensure your API key is correctly formatted...',
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
  },
  {
    id: 'TICKET-002',
    timestamp: new Date(Date.now() - 43200000).toISOString(),
    query: 'How do I set up SSO with SAML for my organization?',
    answer: 'Setting up SAML SSO involves several steps. I\'ll guide you through the configuration process for your organization...',
    citations: [
      { doc: 'SAML SSO Setup Guide', url: 'https://docs.atlan.com/sso/saml-setup' },
      { doc: 'Organization Management', url: 'https://docs.atlan.com/admin/organization' }
    ],
    classification: {
      topic: 'SSO' as TopicType,
      sentiment: 'Curious' as SentimentType,
      priority: 'P1' as PriorityType,
      confidence: 0.87
    },
    classification_reasons: {
      topic: 'Mentions \'SSO, SAML\' → classified under SSO.',
      sentiment: 'Question format with learning intent → classified as Curious.',
      priority: 'Important organizational feature → high priority (P1).'
    },
    processing_time: 1.89,
    cache_hit: true,
    followup_suggestions: [
      { question: 'What are the prerequisites for SAML SSO setup?' }
    ],
    session_id: '550e8400-e29b-41d4-a716-446655440001'
  },
  {
    id: 'TICKET-003',
    timestamp: new Date(Date.now() - 21600000).toISOString(),
    query: 'I want to understand how to create custom connectors for our data sources',
    answer: 'Creating custom connectors is a great way to integrate your specific data sources. Let me walk you through the connector development process...',
    citations: [
      { doc: 'Connector Development Guide', url: 'https://docs.atlan.com/connectors/development' }
    ],
    classification: {
      topic: 'Connector' as TopicType,
      sentiment: 'Positive' as SentimentType,
      priority: 'P2' as PriorityType,
      confidence: 0.94
    },
    classification_reasons: {
      topic: 'Mentions \'connectors, data sources\' → classified under Connector.',
      sentiment: 'Positive language \'want to understand\' → classified as Positive.',
      priority: 'Development question, not urgent → normal priority (P2).'
    },
    processing_time: 3.12,
    cache_hit: false,
    followup_suggestions: [
      { question: 'What programming languages are supported for custom connectors?' }
    ],
    session_id: '550e8400-e29b-41d4-a716-446655440002'
  },
  {
    id: 'TICKET-004',
    timestamp: new Date(Date.now() - 10800000).toISOString(),
    query: 'The data lineage view is not loading properly and showing errors',
    answer: 'I understand the lineage view is having issues. This could be related to several factors. Let me help you troubleshoot...',
    citations: [
      { doc: 'Lineage Troubleshooting', url: 'https://docs.atlan.com/lineage/troubleshooting' }
    ],
    classification: {
      topic: 'Product' as TopicType,
      sentiment: 'Frustrated' as SentimentType,
      priority: 'P1' as PriorityType,
      confidence: 0.89
    },
    classification_reasons: {
      topic: 'Core product feature issue → classified under Product.',
      sentiment: 'Error reporting with negative tone → classified as Frustrated.',
      priority: 'Product functionality broken → high priority (P1).'
    },
    processing_time: 2.67,
    cache_hit: false,
    followup_suggestions: [
      { question: 'Are you seeing specific error messages in the browser console?' }
    ],
    session_id: '550e8400-e29b-41d4-a716-446655440003'
  },
  {
    id: 'TICKET-005',
    timestamp: new Date(Date.now() - 3600000).toISOString(),
    query: 'Can you explain the best practices for data governance policies?',
    answer: 'Data governance is crucial for maintaining data quality and compliance. Here are the key best practices I recommend...',
    citations: [
      { doc: 'Data Governance Guide', url: 'https://docs.atlan.com/governance/best-practices' },
      { doc: 'Policy Templates', url: 'https://docs.atlan.com/governance/templates' }
    ],
    classification: {
      topic: 'How-to' as TopicType,
      sentiment: 'Curious' as SentimentType,
      priority: 'P2' as PriorityType,
      confidence: 0.91
    },
    classification_reasons: {
      topic: 'Educational question about practices → classified under How-to.',
      sentiment: 'Learning-focused inquiry → classified as Curious.',
      priority: 'Educational content, not urgent → normal priority (P2).'
    },
    processing_time: 1.45,
    cache_hit: true,
    followup_suggestions: [
      { question: 'How do I implement automated policy enforcement?' }
    ],
    session_id: '550e8400-e29b-41d4-a716-446655440004'
  }
];

function getTopicColor(topic: string) {
  const colors = {
    'API/SDK': 'bg-blue-50 text-blue-700 border-blue-200 dark:bg-blue-950 dark:text-blue-300 dark:border-blue-800',
    'How-to': 'bg-green-50 text-green-700 border-green-200 dark:bg-green-950 dark:text-green-300 dark:border-green-800',
    'Connector': 'bg-purple-50 text-purple-700 border-purple-200 dark:bg-purple-950 dark:text-purple-300 dark:border-purple-800',
    'SSO': 'bg-orange-50 text-orange-700 border-orange-200 dark:bg-orange-950 dark:text-orange-300 dark:border-orange-800',
    'Product': 'bg-gray-50 text-gray-700 border-gray-200 dark:bg-gray-950 dark:text-gray-300 dark:border-gray-800',
  };
  return colors[topic as keyof typeof colors] || colors['Product'];
}

function getSentimentColor(sentiment: string) {
  const colors = {
    'Urgent': 'bg-red-50 text-red-700 border-red-200 dark:bg-red-950 dark:text-red-300 dark:border-red-800',
    'Frustrated': 'bg-red-50 text-red-700 border-red-200 dark:bg-red-950 dark:text-red-300 dark:border-red-800',
    'Positive': 'bg-green-50 text-green-700 border-green-200 dark:bg-green-950 dark:text-green-300 dark:border-green-800',
    'Curious': 'bg-blue-50 text-blue-700 border-blue-200 dark:bg-blue-950 dark:text-blue-300 dark:border-blue-800',
    'Neutral': 'bg-gray-50 text-gray-700 border-gray-200 dark:bg-gray-950 dark:text-gray-300 dark:border-gray-800',
  };
  return colors[sentiment as keyof typeof colors] || colors['Neutral'];
}

function getPriorityColor(priority: string) {
  const colors = {
    'P0': 'bg-red-50 text-red-700 border-red-200 dark:bg-red-950 dark:text-red-300 dark:border-red-800',
    'P1': 'bg-orange-50 text-orange-700 border-orange-200 dark:bg-orange-950 dark:text-orange-300 dark:border-orange-800',
    'P2': 'bg-yellow-50 text-yellow-700 border-yellow-200 dark:bg-yellow-950 dark:text-yellow-300 dark:border-yellow-800',
  };
  return colors[priority as keyof typeof colors] || colors['P2'];
}

function SummaryCards({ tickets }: { tickets: TicketData[] }) {
  const totalTickets = tickets.length;
  const highPriorityCount = tickets.filter(t => t.classification.priority === 'P0').length;
  const averageConfidence = tickets.reduce((sum, t) => sum + t.classification.confidence, 0) / totalTickets;
  const averageProcessingTime = tickets.reduce((sum, t) => sum + t.processing_time, 0) / totalTickets;

  return (
    <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-6">
      <Card className="p-4">
        <div className="flex items-center gap-3">
          <div className="p-2 bg-primary/10 rounded-lg">
            <BarChart3 className="w-4 h-4 text-primary" />
          </div>
          <div>
            <p className="text-sm font-medium text-muted-foreground">Total Tickets</p>
            <p className="text-2xl font-bold">{totalTickets}</p>
          </div>
        </div>
      </Card>
      
      <Card className="p-4">
        <div className="flex items-center gap-3">
          <div className="p-2 bg-red-50 rounded-lg dark:bg-red-950">
            <AlertTriangle className="w-4 h-4 text-red-600 dark:text-red-400" />
          </div>
          <div>
            <p className="text-sm font-medium text-muted-foreground">High Priority</p>
            <p className="text-2xl font-bold text-red-600 dark:text-red-400">{highPriorityCount}</p>
          </div>
        </div>
      </Card>
      
      <Card className="p-4">
        <div className="flex items-center gap-3">
          <div className="p-2 bg-green-50 rounded-lg dark:bg-green-950">
            <CheckSquare2 className="w-4 h-4 text-green-600 dark:text-green-400" />
          </div>
          <div>
            <p className="text-sm font-medium text-muted-foreground">Avg Confidence</p>
            <p className="text-2xl font-bold text-green-600 dark:text-green-400">{Math.round(averageConfidence * 100)}%</p>
          </div>
        </div>
      </Card>
      
      <Card className="p-4">
        <div className="flex items-center gap-3">
          <div className="p-2 bg-blue-50 rounded-lg dark:bg-blue-950">
            <Clock className="w-4 h-4 text-blue-600 dark:text-blue-400" />
          </div>
          <div>
            <p className="text-sm font-medium text-muted-foreground">Avg Processing</p>
            <p className="text-2xl font-bold text-blue-600 dark:text-blue-400">{averageProcessingTime.toFixed(2)}s</p>
          </div>
        </div>
      </Card>
    </div>
  );
}

interface ExpandedRowProps {
  ticket: TicketData;
}

function ExpandedRow({ ticket }: ExpandedRowProps) {
  return (
    <TableRow>
      <TableCell colSpan={7} className="p-0">
        <div className="p-6 bg-muted/30 border-t border-dashboard-border">
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            {/* Classification Reasons */}
            <Card className="p-4">
              <div className="flex items-center gap-2 mb-3">
                <Brain className="w-4 h-4 text-primary" />
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
                <MessageSquare className="w-4 h-4 text-primary" />
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
      </TableCell>
    </TableRow>
  );
}

export function BulkDashboard() {
  const [tickets] = useState<TicketData[]>(mockTickets);
  const [expandedRows, setExpandedRows] = useState<Set<string>>(new Set());
  const [selectedTickets, setSelectedTickets] = useState<Set<string>>(new Set());

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

  const toggleSelected = (ticketId: string) => {
    setSelectedTickets(prev => {
      const newSet = new Set(prev);
      if (newSet.has(ticketId)) {
        newSet.delete(ticketId);
      } else {
        newSet.add(ticketId);
      }
      return newSet;
    });
  };

  const toggleSelectAll = () => {
    if (selectedTickets.size === tickets.length) {
      setSelectedTickets(new Set());
    } else {
      setSelectedTickets(new Set(tickets.map(t => t.id)));
    }
  };

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-xl font-semibold">Ticket Classification Dashboard</h2>
          <p className="text-sm text-muted-foreground">
            View and analyze customer support queries with AI-powered classification
          </p>
        </div>
      </div>

      <SummaryCards tickets={tickets} />

      <Card className="overflow-hidden">
        <Table>
          <TableHeader>
            <TableRow>
              <TableHead className="w-12">
                <Checkbox 
                  checked={selectedTickets.size === tickets.length}
                  onCheckedChange={toggleSelectAll}
                />
              </TableHead>
              <TableHead className="w-24">ID</TableHead>
              <TableHead>Subject</TableHead>
              <TableHead className="w-24">Topic</TableHead>
              <TableHead className="w-24">Priority</TableHead>
              <TableHead className="w-24">Sentiment</TableHead>
              <TableHead className="w-24">Actions</TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            {tickets.map((ticket) => (
              <Collapsible 
                key={ticket.id}
                open={expandedRows.has(ticket.id)}
                onOpenChange={() => toggleExpanded(ticket.id)}
                asChild
              >
                <>
                  <TableRow className="cursor-pointer hover:bg-muted/50">
                    <TableCell>
                      <Checkbox 
                        checked={selectedTickets.has(ticket.id)}
                        onCheckedChange={() => toggleSelected(ticket.id)}
                        onClick={(e) => e.stopPropagation()}
                      />
                    </TableCell>
                    <TableCell className="font-medium text-xs">{ticket.id}</TableCell>
                    <TableCell 
                      className="max-w-0"
                      onClick={() => toggleExpanded(ticket.id)}
                    >
                      <div className="truncate pr-4" title={ticket.query}>
                        {ticket.query}
                      </div>
                      <div className="text-xs text-muted-foreground mt-1">
                        {new Date(ticket.timestamp).toLocaleDateString()} • 
                        {Math.round(ticket.classification.confidence * 100)}% confidence
                      </div>
                    </TableCell>
                    <TableCell>
                      <Badge variant="outline" className={`text-xs ${getTopicColor(ticket.classification.topic)}`}>
                        {ticket.classification.topic}
                      </Badge>
                    </TableCell>
                    <TableCell>
                      <Badge className={`text-xs ${getPriorityColor(ticket.classification.priority)}`}>
                        {ticket.classification.priority}
                      </Badge>
                    </TableCell>
                    <TableCell>
                      <Badge variant="outline" className={`text-xs ${getSentimentColor(ticket.classification.sentiment)}`}>
                        {ticket.classification.sentiment}
                      </Badge>
                    </TableCell>
                    <TableCell>
                      <Button 
                        variant="ghost" 
                        size="sm" 
                        onClick={(e) => {
                          e.stopPropagation();
                          toggleExpanded(ticket.id);
                        }}
                        className="text-primary"
                      >
                        <Eye className="w-4 h-4 mr-1" />
                        View
                        {expandedRows.has(ticket.id) ? (
                          <ChevronUp className="w-4 h-4 ml-1" />
                        ) : (
                          <ChevronDown className="w-4 h-4 ml-1" />
                        )}
                      </Button>
                    </TableCell>
                  </TableRow>
                  
                  <CollapsibleContent asChild>
                    <ExpandedRow ticket={ticket} />
                  </CollapsibleContent>
                </>
              </Collapsible>
            ))}
          </TableBody>
        </Table>
      </Card>
    </div>
  );
}