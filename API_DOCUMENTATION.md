# Atlan Customer Support Copilot API Documentation

## Overview
The Atlan Customer Support Copilot API provides AI-powered customer support assistance with intelligent query classification, RAG (Retrieval Augmented Generation), and ticket management capabilities.

## Base URL
```
http://localhost:8000
```

## Authentication
Currently no authentication required for development.

---

## Endpoints

### 1. RAG Query
**POST** `/api/rag/query`

Submit a customer query and receive an AI-powered response with classification reasoning and intelligent citations.

#### Request Body
```json
{
  "query": "string",
  "channel": "string (optional)",
  "session_id": "string (optional)",
  "include_followup": "boolean (optional)"
}
```

#### Request Parameters
| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `query` | string | Yes | The customer's question or issue description |
| `channel` | string | No | Communication channel (Web Chat, WhatsApp, Email, Voice, Slack, Teams) |
| `session_id` | string | No | Session ID for conversation continuity (default: "default") |
| `include_followup` | boolean | No | Whether to include follow-up suggestions (default: true) |

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
    "confidence": "number",
    "topic_reasoning": "string",
    "sentiment_reasoning": "string",
    "priority_reasoning": "string"
  },
  "classification_reasons": {
    "topic_reasoning": "string",
    "sentiment_reasoning": "string",
    "priority_reasoning": "string"
  },
  "processing_time": "number",
  "cache_hit": "boolean",
  "followup_suggestions": [
    {
      "question": "string"
    }
  ],
  "session_id": "string",
  "response_type": "string"
}
```

#### Response Fields
| Field | Type | Description |
|-------|------|-------------|
| `answer` | string | AI-generated response to the query |
| `citations` | array | Sources and documentation links |
| `classification` | object | Query classification details with reasoning |
| `classification_reasons` | object | Reasoning behind classification decisions |
| `processing_time` | number | Time taken to process the query (milliseconds) |
| `cache_hit` | boolean | Whether response was served from cache |
| `followup_suggestions` | array | Suggested follow-up questions |
| `session_id` | string | Unique session identifier |
| `response_type` | string | "rag_response" or "routing_message" |

#### Classification Values
**Topic:**
- `API/SDK` - Technical API and SDK questions
- `How-to` - Step-by-step guidance requests
- `Product` - General product questions
- `Best practices` - Best practice recommendations
- `SSO` - Authentication and SSO setup
- `Connector` - Data connector and integration questions
- `Lineage` - Data lineage and tracking
- `Glossary` - Business glossary and terminology
- `Sensitive data` - Data privacy and security
- `General` - General inquiries

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
- `P3` - Low (routine requests)

#### Example Request
```bash
curl -X POST "http://localhost:8000/api/rag/query" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "How do I install the Python SDK for Atlan?",
    "channel": "Web Chat",
    "session_id": "user-session-123",
    "include_followup": true
  }'
```

#### Example Response
```json
{
  "answer": "To install the Python SDK for Atlan, you can follow these steps:\n\n1. Install using pip:\n   ```\n   pip install pyatlan\n   ```\n\n2. Configure with environment variables:\n   - ATLAN_API_KEY: Your API token\n   - ATLAN_BASE_URL: Your Atlan URL\n\n3. Basic usage:\n   ```python\n   from pyatlan.atlan import AtlanClient\n   client = AtlanClient()\n   ```",
  "citations": [
    {
      "doc": "Python SDK Documentation",
      "url": "https://developer.atlan.com/sdks/python/"
    }
  ],
  "classification": {
    "topic": "API/SDK",
    "sentiment": "Neutral",
    "priority": "P2",
    "confidence": 0.85,
    "topic_reasoning": "The query asks about installing Python SDK, which falls under API/SDK category.",
    "sentiment_reasoning": "The tone is neutral and informational without emotional indicators.",
    "priority_reasoning": "Standard setup question without urgent indicators, classified as P2."
  },
  "classification_reasons": {
    "topic_reasoning": "The query asks about installing Python SDK, which falls under API/SDK category.",
    "sentiment_reasoning": "The tone is neutral and informational without emotional indicators.",
    "priority_reasoning": "Standard setup question without urgent indicators, classified as P2."
  },
  "processing_time": 1234.5,
  "cache_hit": false,
  "followup_suggestions": [
    {
      "question": "What are the key functionalities provided by the Python SDK for Atlan?"
    },
    {
      "question": "How can I authenticate and access the Atlan API using the Python SDK?"
    },
    {
      "question": "Are there any specific dependencies required for the Python SDK?"
    }
  ],
  "session_id": "user-session-123",
  "response_type": "rag_response"
}
```

---

### 2. Get All Tickets
**GET** `/api/tickets/`

Retrieve all classified tickets from the vector database.

#### Response
```json
{
  "tickets": [
    {
      "id": "string",
      "subject": "string",
      "body": "string",
      "classification": {
        "topic": "string",
        "sentiment": "string",
        "priority": "string",
        "confidence": "number",
        "topic_reasoning": "string",
        "sentiment_reasoning": "string",
        "priority_reasoning": "string"
      },
      "processing_time": "number",
      "cache_hit": "boolean"
    }
  ],
  "count": "number"
}
```

#### Example Request
```bash
curl -X GET "http://localhost:8000/api/tickets/"
```

---

### 3. Classify Tickets
**POST** `/api/tickets/classify`

Classify and store sample tickets in the vector database.

#### Response
```json
{
  "message": "Successfully classified and stored X tickets",
  "count": "number"
}
```

#### Example Request
```bash
curl -X POST "http://localhost:8000/api/tickets/classify"
```

---

### 4. Get Sample Tickets
**GET** `/api/tickets/sample`

Get sample tickets from the JSON file (for testing purposes).

#### Response
```json
{
  "tickets": [
    {
      "id": "string",
      "subject": "string",
      "body": "string"
    }
  ],
  "count": "number"
}
```

#### Example Request
```bash
curl -X GET "http://localhost:8000/api/tickets/sample"
```

---

### 5. Initialize System
**POST** `/api/init`

Initialize the system by classifying sample tickets.

#### Response
```json
{
  "message": "Successfully classified and stored X tickets",
  "count": "number"
}
```

#### Example Request
```bash
curl -X POST "http://localhost:8000/api/init"
```

---

### 6. Health Check
**GET** `/health`

Check the API health status.

#### Response
```json
{
  "status": "healthy",
  "message": "API is running"
}
```

#### Example Request
```bash
curl -X GET "http://localhost:8000/health"
```

---

### 7. Root Endpoint
**GET** `/`

Welcome message and API information.

#### Response
```json
{
  "message": "Atlan Customer Support Backend is running!"
}
```

---

## Key Features

### RAG (Retrieval Augmented Generation)
The system uses RAG to provide accurate, contextual responses by:
1. **Query Classification**: Analyzing the user's question
2. **Vector Search**: Finding relevant documentation chunks
3. **Context Building**: Combining query with retrieved context
4. **Response Generation**: Using GPT-3.5-turbo for intelligent responses
5. **Citation**: Providing relevant documentation URLs

### Intelligent URL Resolution
- **Technology Detection**: Automatically identifies programming languages/SDKs
- **Relevance Scoring**: Ranks documentation URLs by relevance
- **Deduplication**: Removes duplicate citations
- **Fallback URLs**: Provides technology-specific documentation

### Multi-Channel Support
Supports various communication channels:
- Web Chat
- WhatsApp
- Email
- Voice
- Slack
- Microsoft Teams

### Classification Reasoning
The API provides detailed reasoning for classification decisions:
- **Topic Reasoning**: Why a query was classified as a specific topic
- **Sentiment Reasoning**: What language patterns led to sentiment detection
- **Priority Reasoning**: How priority was determined based on urgency indicators

---

## Error Responses

### 400 Bad Request
```json
{
  "detail": "Invalid request format"
}
```

### 404 Not Found
```json
{
  "detail": "Resource not found"
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

## Environment Variables
Required environment variables for the API:

```env
OPENAI_API_KEY=your-openai-api-key
PINECONE_API_KEY=your-pinecone-api-key
PINECONE_ENVIRONMENT=your-pinecone-environment
PINECONE_INDEX_NAME=atlan-docs-rag
```

---

## Support
For API support or questions, contact the development team or create an issue in the GitHub repository.

