# Atlan Customer Support Copilot API Documentation

## Overview
The Atlan Customer Support Copilot API provides AI-powered customer support assistance with intelligent query classification and reasoning capabilities.

## Base URL
```
http://localhost:8000
```

## Authentication
Currently no authentication required for development.

---

## Endpoints

### 1. Submit Query
**POST** `/api/query`

Submit a customer query and receive an AI-powered response with classification reasoning.

#### Request Body
```json
{
  "query": "string",
  "channel": "string",
  "session_id": "string (optional)",
  "include_followup": "boolean (optional)"
}
```

#### Request Parameters
| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `query` | string | Yes | The customer's question or issue description |
| `channel` | string | No | Communication channel (Web Chat, WhatsApp, Email, Voice) |
| `session_id` | string | No | Session ID for conversation continuity |
| `include_followup` | boolean | No | Whether to include follow-up suggestions |

#### Response
```json
{
  "answer": "string",
  "citations": [
    {
      "doc": "string",
      "url": "string"
    }
  ],
  "classification": {
    "topic": "string",
    "sentiment": "string", 
    "priority": "string",
    "confidence": "number"
  },
  "classification_reasons": {
    "topic": "string",
    "sentiment": "string",
    "priority": "string"
  },
  "processing_time": "number",
  "cache_hit": "boolean",
  "followup_suggestions": [
    {
      "question": "string"
    }
  ],
  "session_id": "string"
}
```

#### Response Fields
| Field | Type | Description |
|-------|------|-------------|
| `answer` | string | AI-generated response to the query |
| `citations` | array | Sources and documentation links |
| `classification` | object | Query classification details |
| `classification_reasons` | object | **NEW** - Reasoning behind classification decisions |
| `processing_time` | number | Time taken to process the query (seconds) |
| `cache_hit` | boolean | Whether response was served from cache |
| `followup_suggestions` | array | Suggested follow-up questions |
| `session_id` | string | Unique session identifier |

#### Classification Values
**Topic:**
- `API/SDK` - Technical API and SDK questions
- `How-to` - Step-by-step guidance requests
- `Connector` - Data connector and integration questions
- `SSO` - Authentication and SSO setup
- `Product` - General product questions

**Sentiment:**
- `Urgent` - Critical/emergency situations
- `Frustrated` - Negative/problematic issues
- `Positive` - Positive feedback or satisfaction
- `Curious` - Inquisitive questions
- `Neutral` - Standard informational queries

**Priority:**
- `P0` - Critical (immediate attention required)
- `P1` - High (important but not critical)
- `P2` - Medium (standard priority)

#### Example Request
```bash
curl -X POST "http://localhost:8000/api/query" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "My API authentication is not working and I need help immediately",
    "channel": "Web Chat",
    "include_followup": true
  }'
```

#### Example Response
```json
{
  "answer": "I understand you're having issues with API authentication. Let me help you troubleshoot this...",
  "citations": [
    {
      "doc": "API Authentication Guide",
      "url": "https://docs.atlan.com/api/authentication"
    }
  ],
  "classification": {
    "topic": "API/SDK",
    "sentiment": "Frustrated",
    "priority": "P0",
    "confidence": 0.92
  },
  "classification_reasons": {
    "topic": "Mentions 'api, authentication' → classified under API/SDK.",
    "sentiment": "Negative wording 'not working, error' → classified as Frustrated.",
    "priority": "Contains critical words 'urgent, blocked' → urgent priority (P0)."
  },
  "processing_time": 2.34,
  "cache_hit": false,
  "followup_suggestions": [
    {
      "question": "Can you show me an example of how to use this API?"
    },
    {
      "question": "What are the authentication requirements?"
    }
  ],
  "session_id": "550e8400-e29b-41d4-a716-446655440000"
}
```

---

### 2. Get Conversation History
**GET** `/api/conversation/{session_id}`

Retrieve the conversation history for a specific session.

#### Path Parameters
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `session_id` | string | Yes | Unique session identifier |

#### Response
```json
{
  "conversation": {
    "session_id": "string",
    "messages": [
      {
        "role": "string",
        "content": "string",
        "timestamp": "string"
      }
    ],
    "created_at": "string",
    "updated_at": "string"
  },
  "total_messages": "number",
  "last_activity": "string"
}
```

#### Example Request
```bash
curl -X GET "http://localhost:8000/api/conversation/550e8400-e29b-41d4-a716-446655440000"
```

---

### 3. Clear Conversation
**DELETE** `/api/conversation/{session_id}`

Clear the conversation history for a specific session.

#### Path Parameters
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `session_id` | string | Yes | Unique session identifier |

#### Response
```json
{
  "message": "Conversation cleared successfully"
}
```

#### Example Request
```bash
curl -X DELETE "http://localhost:8000/api/conversation/550e8400-e29b-41d4-a716-446655440000"
```

---

### 4. Submit Follow-up Query
**POST** `/api/query/conversation`

Submit a follow-up query in the context of an existing conversation.

#### Request Body
```json
{
  "query": "string",
  "channel": "string",
  "session_id": "string",
  "include_followup": "boolean (optional)"
}
```

**Note:** This endpoint requires a `session_id` and behaves identically to the main query endpoint but maintains conversation context.

---

### 5. Health Check
**GET** `/health`

Check the API health status.

#### Response
```json
{
  "status": "healthy",
  "message": "Atlan Customer Support Copilot API is running"
}
```

#### Example Request
```bash
curl -X GET "http://localhost:8000/health"
```

---

### 6. Root Endpoint
**GET** `/`

Welcome message and API information.

#### Response
```json
{
  "message": "Welcome to Atlan Customer Support Copilot API"
}
```

---

## New Features

### Classification Reasoning
The API now provides detailed reasoning for classification decisions through the `classification_reasons` field:

```json
{
  "classification_reasons": {
    "topic": "Mentions 'api, authentication' → classified under API/SDK.",
    "sentiment": "Negative wording 'not working, error' → classified as Frustrated.",
    "priority": "Contains critical words 'urgent, blocked' → urgent priority (P0)."
  }
}
```

This helps understand:
- **Why** a query was classified as a specific topic
- **What** language patterns led to sentiment detection
- **How** priority was determined based on urgency indicators

### Intelligent Classification
The system analyzes:
- **Keywords**: Technical terms, urgency indicators, emotional language
- **Context**: Question patterns, problem descriptions
- **Language Patterns**: Sentiment indicators, priority markers

---

## Error Responses

### 400 Bad Request
```json
{
  "detail": "Session ID required for follow-up queries"
}
```

### 404 Not Found
```json
{
  "detail": "Conversation not found"
}
```

### 500 Internal Server Error
```json
{
  "detail": "Error processing query: [error details]"
}
```

---

## Rate Limits
Currently no rate limits implemented for development.

---

## Interactive API Documentation
Visit `http://localhost:8000/docs` for interactive Swagger UI documentation.

---

## Support
For API support or questions, contact the development team.
