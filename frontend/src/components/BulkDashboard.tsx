import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Card } from '@/components/ui/card';
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogTrigger } from '@/components/ui/dialog';
import { Progress } from '@/components/ui/progress';
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '@/components/ui/table';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { PriorityType, SentimentType, TicketData, TopicType } from '@/types/api';
import { AlertTriangle, BarChart3, Brain, CheckSquare2, Clock, ExternalLink, Eye, Info, MessageSquare, Filter } from 'lucide-react';
import { useState, useEffect } from 'react';
import { apiService } from '@/lib/api';

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
    session_id: '550e8400-e29b-41d4-a716-446655440000',
    response_type: 'rag_response' as const
  }
];

function getTopicColor(topic: string) {
  const colors = {
    'How-to': 'bg-green-50 text-green-700 border-green-200 dark:bg-green-950 dark:text-green-300 dark:border-green-800',
    'Product': 'bg-blue-50 text-blue-700 border-blue-200 dark:bg-blue-950 dark:text-blue-300 dark:border-blue-800',
    'Connector': 'bg-purple-50 text-purple-700 border-purple-200 dark:bg-purple-950 dark:text-purple-300 dark:border-purple-800',
    'Lineage': 'bg-indigo-50 text-indigo-700 border-indigo-200 dark:bg-indigo-950 dark:text-indigo-300 dark:border-indigo-800',
    'API/SDK': 'bg-cyan-50 text-cyan-700 border-cyan-200 dark:bg-cyan-950 dark:text-cyan-300 dark:border-cyan-800',
    'SSO': 'bg-orange-50 text-orange-700 border-orange-200 dark:bg-orange-950 dark:text-orange-300 dark:border-orange-800',
    'Glossary': 'bg-emerald-50 text-emerald-700 border-emerald-200 dark:bg-emerald-950 dark:text-emerald-300 dark:border-emerald-800',
    'Best practices': 'bg-violet-50 text-violet-700 border-violet-200 dark:bg-violet-950 dark:text-violet-300 dark:border-violet-800',
    'Sensitive data': 'bg-red-50 text-red-700 border-red-200 dark:bg-red-950 dark:text-red-300 dark:border-red-800',
    'General': 'bg-gray-50 text-gray-700 border-gray-200 dark:bg-gray-950 dark:text-gray-300 dark:border-gray-800',
  };
  return colors[topic as keyof typeof colors] || colors['General'];
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

interface ClassificationDetailsProps {
  ticket: TicketData;
}

function ClassificationDetails({ ticket }: ClassificationDetailsProps) {
  const confidencePercentage = Math.round(ticket.classification.confidence * 100);
  
  return (
    <div className="space-y-6">
      {/* Header with confidence */}
      <div className="flex items-center justify-between p-4 bg-blue-50 rounded-lg border border-blue-200">
        <div className="flex items-center gap-3">
          <Brain className="w-5 h-5 text-blue-600" />
          <div>
            <h3 className="font-semibold text-blue-900">AI Classification Analysis</h3>
            <p className="text-sm text-blue-700">Ticket {ticket.id}</p>
          </div>
        </div>
        <div className="text-right">
          <div className="text-2xl font-bold text-blue-600">{confidencePercentage}%</div>
          <div className="text-xs text-blue-500">Confidence</div>
        </div>
      </div>

      {/* Full Question */}
      <Card className="p-4 border-l-4 border-l-blue-500">
        <div className="flex items-start gap-3">
          <MessageSquare className="w-5 h-5 text-blue-600 mt-1" />
          <div className="flex-1">
            <p className="font-medium text-sm text-gray-900 mb-2">Full Question</p>
            <p className="text-sm text-gray-700 whitespace-pre-wrap">{ticket.answer}</p>
          </div>
        </div>
      </Card>

      {/* Confidence Progress Bar */}
      <div className="space-y-2">
        <div className="flex justify-between text-sm">
          <span className="text-gray-600">Classification Confidence</span>
          <span className="font-medium">{confidencePercentage}%</span>
        </div>
        <Progress value={confidencePercentage} className="h-2" />
        <div className="text-xs text-gray-500">
          {confidencePercentage >= 90 ? 'Very High Confidence' : 
           confidencePercentage >= 75 ? 'High Confidence' : 
           confidencePercentage >= 60 ? 'Medium Confidence' : 'Low Confidence'}
        </div>
      </div>

      {/* Current Classifications */}
      <div className="grid grid-cols-3 gap-4">
        <div className="text-center p-3 bg-white border rounded-lg">
          <div className="text-sm text-gray-600 mb-1">Topic</div>
          <Badge variant="outline" className={`text-xs ${getTopicColor(ticket.classification.topic)}`}>
            {ticket.classification.topic}
          </Badge>
        </div>
        <div className="text-center p-3 bg-white border rounded-lg">
          <div className="text-sm text-gray-600 mb-1">Sentiment</div>
          <Badge variant="outline" className={`text-xs ${getSentimentColor(ticket.classification.sentiment)}`}>
            {ticket.classification.sentiment}
          </Badge>
        </div>
        <div className="text-center p-3 bg-white border rounded-lg">
          <div className="text-sm text-gray-600 mb-1">Priority</div>
          <Badge className={`text-xs ${getPriorityColor(ticket.classification.priority)}`}>
            {ticket.classification.priority}
          </Badge>
        </div>
      </div>

      {/* Classification Reasoning */}
      <div className="space-y-4">
        <h4 className="font-semibold text-gray-900 flex items-center gap-2">
          <Info className="w-4 h-4" />
          AI Reasoning
        </h4>
        
        <div className="space-y-4">
          <Card className="p-4 border-l-4 border-l-blue-500">
            <div className="flex items-start gap-3">
              <div className="w-2 h-2 bg-blue-500 rounded-full mt-2"></div>
              <div className="flex-1">
                <p className="font-medium text-sm text-gray-900 mb-1">Topic Classification</p>
                <p className="text-sm text-gray-700">{ticket.classification_reasons.topic}</p>
              </div>
            </div>
          </Card>

          <Card className="p-4 border-l-4 border-l-green-500">
            <div className="flex items-start gap-3">
              <div className="w-2 h-2 bg-green-500 rounded-full mt-2"></div>
              <div className="flex-1">
                <p className="font-medium text-sm text-gray-900 mb-1">Sentiment Analysis</p>
                <p className="text-sm text-gray-700">{ticket.classification_reasons.sentiment}</p>
              </div>
            </div>
          </Card>

          <Card className="p-4 border-l-4 border-l-orange-500">
            <div className="flex items-start gap-3">
              <div className="w-2 h-2 bg-orange-500 rounded-full mt-2"></div>
              <div className="flex-1">
                <p className="font-medium text-sm text-gray-900 mb-1">Priority Assessment</p>
                <p className="text-sm text-gray-700">{ticket.classification_reasons.priority}</p>
              </div>
            </div>
          </Card>
        </div>
      </div>

      {/* Processing Info */}
      <div className="flex items-center justify-between p-3 bg-gray-50 rounded-lg text-sm">
        <span className="text-gray-600">Processing Time:</span>
        <span className="font-medium">{ticket.processing_time.toFixed(2)}s</span>
      </div>
    </div>
  );
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
          <div className="p-2 bg-blue-50 rounded-lg">
            <BarChart3 className="w-4 h-4 text-blue-600" />
          </div>
          <div>
            <p className="text-sm font-medium text-muted-foreground">Total Tickets</p>
            <p className="text-2xl font-bold">{totalTickets}</p>
          </div>
        </div>
      </Card>
      
      <Card className="p-4">
        <div className="flex items-center gap-3">
          <div className="p-2 bg-red-50 rounded-lg">
            <AlertTriangle className="w-4 h-4 text-red-600" />
          </div>
          <div>
            <p className="text-sm font-medium text-muted-foreground">High Priority</p>
            <p className="text-2xl font-bold text-red-600">{highPriorityCount}</p>
          </div>
        </div>
      </Card>
      
      <Card className="p-4">
        <div className="flex items-center gap-3">
          <div className="p-2 bg-green-50 rounded-lg">
            <CheckSquare2 className="w-4 h-4 text-green-600" />
          </div>
          <div>
            <p className="text-sm font-medium text-muted-foreground">Avg Confidence</p>
            <p className="text-2xl font-bold text-green-600">{Math.round(averageConfidence * 100)}%</p>
          </div>
        </div>
      </Card>
      
      <Card className="p-4">
        <div className="flex items-center gap-3">
          <div className="p-2 bg-blue-50 rounded-lg">
            <Clock className="w-4 h-4 text-blue-600" />
          </div>
          <div>
            <p className="text-sm font-medium text-muted-foreground">Avg Processing</p>
            <p className="text-2xl font-bold text-blue-600">{averageProcessingTime.toFixed(2)}s</p>
          </div>
        </div>
      </Card>
    </div>
  );
}

function FilterSection({ 
  tickets, 
  filters, 
  onFilterChange 
}: { 
  tickets: TicketData[], 
  filters: { topic: string, sentiment: string, priority: string },
  onFilterChange: (key: string, value: string) => void 
}) {
  // Get unique values for filter options
  const topics = Array.from(new Set(tickets.map(t => t.classification.topic))).sort();
  const sentiments = Array.from(new Set(tickets.map(t => t.classification.sentiment))).sort();
  const priorities = Array.from(new Set(tickets.map(t => t.classification.priority))).sort();

  return (
    <Card className="p-4 mb-6">
      <div className="flex items-center gap-2 mb-4">
        <Filter className="w-4 h-4" />
        <h3 className="font-semibold">Filters</h3>
      </div>
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <div>
          <label className="text-sm font-medium text-gray-700 mb-2 block">Topic</label>
          <Select value={filters.topic} onValueChange={(value) => onFilterChange('topic', value)}>
            <SelectTrigger>
              <SelectValue placeholder="All Topics" />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="all">All Topics</SelectItem>
              {topics.map(topic => (
                <SelectItem key={topic} value={topic}>{topic}</SelectItem>
              ))}
            </SelectContent>
          </Select>
        </div>
        
        <div>
          <label className="text-sm font-medium text-gray-700 mb-2 block">Sentiment</label>
          <Select value={filters.sentiment} onValueChange={(value) => onFilterChange('sentiment', value)}>
            <SelectTrigger>
              <SelectValue placeholder="All Sentiments" />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="all">All Sentiments</SelectItem>
              {sentiments.map(sentiment => (
                <SelectItem key={sentiment} value={sentiment}>{sentiment}</SelectItem>
              ))}
            </SelectContent>
          </Select>
        </div>
        
        <div>
          <label className="text-sm font-medium text-gray-700 mb-2 block">Priority</label>
          <Select value={filters.priority} onValueChange={(value) => onFilterChange('priority', value)}>
            <SelectTrigger>
              <SelectValue placeholder="All Priorities" />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="all">All Priorities</SelectItem>
              {priorities.map(priority => (
                <SelectItem key={priority} value={priority}>{priority}</SelectItem>
              ))}
            </SelectContent>
          </Select>
        </div>
      </div>
    </Card>
  );
}

export function BulkDashboard() {
  const [tickets, setTickets] = useState<TicketData[]>([]);
  const [filteredTickets, setFilteredTickets] = useState<TicketData[]>([]);
  const [loading, setLoading] = useState(true);
  const [filters, setFilters] = useState({
    topic: 'all',
    sentiment: 'all',
    priority: 'all'
  });

  useEffect(() => {
    const fetchTickets = async () => {
      try {
        setLoading(true);
        const response = await apiService.getTickets();
        
        const transformedTickets: TicketData[] = response.tickets.map((ticket: any) => ({
          id: ticket.id,
          timestamp: new Date().toISOString(),
          query: ticket.subject || 'No subject',
          answer: ticket.body || 'No content available',
          citations: [],
          classification: {
            topic: (ticket.topic || 'General') as TopicType,
            sentiment: (ticket.sentiment || 'Neutral') as SentimentType,
            priority: (ticket.priority || 'P2') as PriorityType,
            confidence: ticket.confidence || 0.8
          },
          classification_reasons: {
            topic: ticket.topic_reasoning || 'Auto-classified from backend data',
            sentiment: ticket.sentiment_reasoning || 'Neutral classification',
            priority: ticket.priority_reasoning || 'Standard priority'
          },
          processing_time: ticket.processing_time || 1.0,
          cache_hit: ticket.cache_hit || false,
          followup_suggestions: [],
          session_id: 'backend-ticket',
          response_type: (ticket.response_type || 'rag_response') as 'rag_response' | 'routing_message'
        }));
        
        // Sort tickets by ID to maintain order
        transformedTickets.sort((a, b) => {
          const aNum = parseInt(a.id.replace('TICKET-', ''));
          const bNum = parseInt(b.id.replace('TICKET-', ''));
          return aNum - bNum;
        });
        
        setTickets(transformedTickets);
        setFilteredTickets(transformedTickets);
      } catch (error) {
        console.error('Failed to fetch tickets:', error);
        setTickets(mockTickets);
        setFilteredTickets(mockTickets);
      } finally {
        setLoading(false);
      }
    };

    fetchTickets();
  }, []);

  // Apply filters whenever filters or tickets change
  useEffect(() => {
    let filtered = tickets;

    if (filters.topic !== 'all') {
      filtered = filtered.filter(ticket => ticket.classification.topic === filters.topic);
    }
    if (filters.sentiment !== 'all') {
      filtered = filtered.filter(ticket => ticket.classification.sentiment === filters.sentiment);
    }
    if (filters.priority !== 'all') {
      filtered = filtered.filter(ticket => ticket.classification.priority === filters.priority);
    }

    setFilteredTickets(filtered);
  }, [filters, tickets]);

  const handleFilterChange = (key: string, value: string) => {
    setFilters(prev => ({
      ...prev,
      [key]: value
    }));
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

      <SummaryCards tickets={filteredTickets} />

      <FilterSection 
        tickets={tickets} 
        filters={filters} 
        onFilterChange={handleFilterChange} 
      />

      <Card className="overflow-hidden">
        <Table>
          <TableHeader>
            <TableRow>
              <TableHead className="w-20">ID</TableHead>
              <TableHead className="w-80">Subject</TableHead>
              <TableHead className="w-24">Topic</TableHead>
              <TableHead className="w-20">Priority</TableHead>
              <TableHead className="w-24">Sentiment</TableHead>
              <TableHead className="w-20">Actions</TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            {filteredTickets.map((ticket) => (
              <TableRow key={ticket.id} className="hover:bg-muted/50">
                <TableCell className="font-medium text-xs">{ticket.id}</TableCell>
                <TableCell className="max-w-80">
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
                  <Dialog>
                    <DialogTrigger asChild>
                      <Button 
                        variant="ghost" 
                        size="sm" 
                        className="text-blue-600 hover:text-blue-800 hover:bg-blue-50 p-1 h-8 w-8"
                        title="View Classification Details"
                      >
                        <Eye className="w-4 h-4" />
                      </Button>
                    </DialogTrigger>
                    <DialogContent className="max-w-2xl max-h-[80vh] overflow-y-auto">
                      <DialogHeader>
                        <DialogTitle>Classification Analysis</DialogTitle>
                      </DialogHeader>
                      <ClassificationDetails ticket={ticket} />
                    </DialogContent>
                  </Dialog>
                </TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </Card>
    </div>
  );
}
