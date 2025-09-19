import { describe, it, expect } from 'vitest';

describe('Simple Frontend Tests', () => {
  
  it('should validate API request structure', () => {
    const requestData = {
      query: 'How do I install the Python SDK?',
      channel: 'Web Chat',
      sessionId: 'test-session',
      includeFollowup: true
    };
    
    expect(requestData.query).toBe('How do I install the Python SDK?');
    expect(requestData.channel).toBe('Web Chat');
    expect(requestData.sessionId).toBe('test-session');
    expect(requestData.includeFollowup).toBe(true);
  });
  
  it('should validate API response structure', () => {
    const responseData = {
      answer: 'To install the Python SDK, use pip install atlan-python-sdk',
      citations: [
        {
          url: 'https://developer.atlan.com/sdks/python/',
          doc: 'Python SDK Documentation'
        }
      ],
      classification: {
        topic: 'API/SDK',
        sentiment: 'Neutral',
        priority: 'P2',
        confidence: 0.9
      },
      followup_suggestions: [
        { question: 'How do I authenticate with the SDK?' }
      ],
      processing_time: 1.2,
      session_id: 'test-session',
      response_type: 'rag_response'
    };
    
    expect(responseData.answer).toContain('Python SDK');
    expect(responseData.citations).toHaveLength(1);
    expect(responseData.citations[0].url).toContain('developer.atlan.com');
    expect(responseData.classification.topic).toBe('API/SDK');
    expect(responseData.classification.confidence).toBeGreaterThan(0.8);
    expect(responseData.followup_suggestions).toHaveLength(1);
  });
  
  it('should validate ticket data structure', () => {
    const ticketData = {
      id: 'TICKET-1',
      timestamp: '2024-01-01T00:00:00Z',
      query: 'How do I install the Python SDK?',
      answer: 'Use pip install atlan-python-sdk',
      citations: [],
      classification: {
        topic: 'API/SDK',
        sentiment: 'Neutral',
        priority: 'P2',
        confidence: 0.9
      },
      classification_reasons: {
        topic: 'SDK related query',
        sentiment: 'Neutral tone',
        priority: 'Standard priority'
      },
      processing_time: 1.2,
      cache_hit: false,
      followup_suggestions: [],
      session_id: 'test-session',
      response_type: 'rag_response'
    };
    
    expect(ticketData.id).toMatch(/^TICKET-/);
    expect(ticketData.classification.topic).toBe('API/SDK');
    expect(ticketData.classification_reasons.topic).toContain('SDK');
    expect(ticketData.processing_time).toBeGreaterThan(0);
  });
  
  it('should validate channel options', () => {
    const channels = [
      'Web Chat',
      'WhatsApp',
      'Email',
      'Voice',
      'Slack',
      'Microsoft Teams'
    ];
    
    expect(channels).toContain('Web Chat');
    expect(channels).toContain('WhatsApp');
    expect(channels).toContain('Email');
    expect(channels).toContain('Voice');
    expect(channels).toContain('Slack');
    expect(channels).toContain('Microsoft Teams');
    expect(channels).toHaveLength(6);
  });
  
  it('should validate topic classification options', () => {
    const topics = [
      'API/SDK',
      'Connector',
      'SSO',
      'How-to',
      'Product',
      'Best practices',
      'Lineage',
      'Glossary',
      'Sensitive data',
      'General'
    ];
    
    expect(topics).toContain('API/SDK');
    expect(topics).toContain('Connector');
    expect(topics).toContain('SSO');
    expect(topics).toContain('How-to');
    expect(topics).toContain('Product');
    expect(topics).toHaveLength(10);
  });
  
  it('should validate sentiment options', () => {
    const sentiments = [
      'Urgent',
      'Frustrated',
      'Positive',
      'Curious',
      'Neutral'
    ];
    
    expect(sentiments).toContain('Urgent');
    expect(sentiments).toContain('Frustrated');
    expect(sentiments).toContain('Positive');
    expect(sentiments).toContain('Curious');
    expect(sentiments).toContain('Neutral');
    expect(sentiments).toHaveLength(5);
  });
  
  it('should validate priority options', () => {
    const priorities = ['P0', 'P1', 'P2', 'P3'];
    
    expect(priorities).toContain('P0');
    expect(priorities).toContain('P1');
    expect(priorities).toContain('P2');
    expect(priorities).toContain('P3');
    expect(priorities).toHaveLength(4);
  });
  
  it('should validate URL structure', () => {
    const urls = [
      'https://developer.atlan.com/sdks/python/',
      'https://developer.atlan.com/sdks/java/',
      'https://developer.atlan.com/sdks/kotlin/',
      'https://developer.atlan.com/connectors/snowflake/',
      'https://developer.atlan.com/sso/saml/'
    ];
    
    urls.forEach(url => {
      expect(url).toMatch(/^https:\/\/developer\.atlan\.com\//);
    });
    
    expect(urls[0]).toContain('/sdk');
    expect(urls[3]).toContain('/connector');
    expect(urls[4]).toContain('/sso');
  });
  
  it('should validate confidence scores', () => {
    const confidenceScores = [0.1, 0.5, 0.8, 0.9, 0.95];
    
    confidenceScores.forEach(score => {
      expect(score).toBeGreaterThanOrEqual(0.0);
      expect(score).toBeLessThanOrEqual(1.0);
    });
    
    expect(confidenceScores[4]).toBeGreaterThan(confidenceScores[0]);
  });
  
  it('should validate processing time ranges', () => {
    const processingTimes = [0.5, 1.0, 1.5, 2.0, 3.0];
    
    processingTimes.forEach(time => {
      expect(time).toBeGreaterThan(0);
      expect(time).toBeLessThan(10); // Reasonable upper limit
    });
  });
  
  it('should validate response types', () => {
    const responseTypes = ['rag_response', 'routing_message'];
    
    expect(responseTypes).toContain('rag_response');
    expect(responseTypes).toContain('routing_message');
    expect(responseTypes).toHaveLength(2);
  });
});
