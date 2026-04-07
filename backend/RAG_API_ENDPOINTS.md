# RAG System API Endpoints

This document describes the API endpoints for interacting with the RAG-powered product knowledge system.

## Base URL
```
http://localhost:8000/api
```

## Endpoints

### 1. Answer Product Question

Ask a question about products, features, pricing, or licenses.

**Endpoint:** `POST /rag/question`

**Request Body:**
```json
{
  "question": "What cloud monitoring solutions do you have?"
}
```

**Response:**
```json
{
  "answer": "Cloud Monitor Pro features: Real-time metrics tracking across multi-cloud environments...",
  "confidence": "high",
  "source": "knowledge_base",
  "results": [
    {
      "content": "Cloud Monitor Pro features: ...",
      "score": 0.737
    }
  ]
}
```

**Confidence Levels:**
- `high` - Score > 0.6, very relevant answer
- `medium` - Score 0.3-0.6, moderately relevant
- `low` - Score < 0.3, less confident
- `none` - No relevant information found

---

### 2. Search Product Knowledge

Perform semantic search over the product knowledge base.

**Endpoint:** `POST /rag/search`

**Request Body:**
```json
{
  "query": "machine learning deployment",
  "top_k": 5,
  "score_threshold": 0.3
}
```

**Parameters:**
- `query` (required): Search query string
- `top_k` (optional): Number of results to return (default: 5)
- `score_threshold` (optional): Minimum similarity score (default: 0.3)

**Response:**
```json
{
  "results": [
    {
      "content": "Module: ML Model Hub (part of DataFlow Analytics Platform)...",
      "score": 0.562,
      "metadata": {
        "type": "module",
        "product_name": "DataFlow Analytics Platform",
        "module_name": "ML Model Hub"
      },
      "source": "knowledge_base"
    }
  ],
  "total_results": 5
}
```

---

### 3. Get Product Catalog

Retrieve the complete product catalog with all modules.

**Endpoint:** `GET /rag/catalog`

**Response:**
```json
{
  "company": "TechCorp Enterprise Solutions",
  "products": [
    {
      "id": "cloudops-suite",
      "name": "CloudOps Suite",
      "description": "Complete cloud infrastructure management platform...",
      "modules": [
        "Cloud Monitor Pro",
        "Cost Optimizer AI",
        "Security Command Center"
      ]
    }
  ],
  "total_products": 3
}
```

---

### 4. Get Product Information

Get detailed information about a specific product or module.

**Endpoint:** `GET /rag/product`

**Query Parameters:**
- `product_name` (optional): Name of the product (e.g., "CloudOps Suite")
- `module_name` (optional): Name of the module (e.g., "Cloud Monitor Pro")

**Example:** `GET /rag/product?product_name=CloudOps%20Suite&module_name=Cloud%20Monitor%20Pro`

**Response:**
```json
{
  "product": "CloudOps Suite",
  "module": {
    "id": "cloudops-monitor",
    "name": "Cloud Monitor Pro",
    "description": "Real-time infrastructure monitoring with predictive alerts...",
    "features": [
      "Real-time metrics tracking across multi-cloud environments",
      "AI-powered anomaly detection with predictive alerts"
    ],
    "licenses": [
      {
        "tier": "Starter",
        "price": "$299/month",
        "limits": "Up to 50 servers, 10 users, 30-day data retention",
        "support": "Email support (48hr response)"
      }
    ]
  }
}
```

---

### 5. Get Pricing for Module

Get all pricing tiers for a specific module.

**Endpoint:** `GET /rag/pricing`

**Query Parameters:**
- `module_name` (required): Name of the module

**Example:** `GET /rag/pricing?module_name=Cloud%20Monitor%20Pro`

**Response:**
```json
{
  "module_name": "Cloud Monitor Pro",
  "licenses": [
    {
      "tier": "Starter",
      "price": "$299/month",
      "limits": "Up to 50 servers, 10 users, 30-day data retention",
      "support": "Email support (48hr response)"
    },
    {
      "tier": "Professional",
      "price": "$899/month",
      "limits": "Up to 500 servers, 50 users, 90-day data retention",
      "support": "Priority email + chat support (12hr response)",
      "extras": "Advanced analytics, custom integrations"
    },
    {
      "tier": "Enterprise",
      "price": "$2,499/month",
      "limits": "Unlimited servers, unlimited users, 2-year data retention",
      "support": "24/7 phone + dedicated success manager",
      "extras": "White-label options, on-premise deployment, custom SLA"
    }
  ]
}
```

---

### 6. Process Transcript (Meetstream Integration)

Process a meeting transcript to detect and answer questions.

**Endpoint:** `POST /rag/process-transcript`

**Request Body:**
```json
{
  "bot_id": "meeting_123",
  "transcript": "What's the pricing for the Professional tier?"
}
```

**Response:**
```json
{
  "question_detected": true,
  "answer": "For Cloud Monitor Pro, the Professional tier costs $899/month...",
  "confidence": "high",
  "source": "knowledge_base",
  "timestamp": "2026-03-28T10:30:00Z"
}
```

---

## Example Usage

### Using cURL

#### Ask a Question
```bash
curl -X POST http://localhost:8000/api/rag/question \
  -H "Content-Type: application/json" \
  -d '{
    "question": "What security features do you offer?"
  }'
```

#### Search Knowledge Base
```bash
curl -X POST http://localhost:8000/api/rag/search \
  -H "Content-Type: application/json" \
  -d '{
    "query": "cost optimization",
    "top_k": 3
  }'
```

#### Get Product Catalog
```bash
curl http://localhost:8000/api/rag/catalog
```

#### Get Pricing
```bash
curl "http://localhost:8000/api/rag/pricing?module_name=ML%20Model%20Hub"
```

### Using Python

```python
import httpx
import asyncio

async def ask_question(question: str):
    async with httpx.AsyncClient() as client:
        response = await client.post(
            "http://localhost:8000/api/rag/question",
            json={"question": question}
        )
        return response.json()

async def search_knowledge(query: str, top_k: int = 5):
    async with httpx.AsyncClient() as client:
        response = await client.post(
            "http://localhost:8000/api/rag/search",
            json={"query": query, "top_k": top_k}
        )
        return response.json()

async def get_catalog():
    async with httpx.AsyncClient() as client:
        response = await client.get(
            "http://localhost:8000/api/rag/catalog"
        )
        return response.json()

# Usage
result = await ask_question("Can I try before buying?")
print(result['answer'])
```

### Using JavaScript/TypeScript

```typescript
// Ask a question
async function askQuestion(question: string) {
  const response = await fetch('http://localhost:8000/api/rag/question', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ question })
  });
  return response.json();
}

// Search knowledge base
async function searchKnowledge(query: string, topK: number = 5) {
  const response = await fetch('http://localhost:8000/api/rag/search', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ query, top_k: topK })
  });
  return response.json();
}

// Get product catalog
async function getCatalog() {
  const response = await fetch('http://localhost:8000/api/rag/catalog');
  return response.json();
}

// Usage
const result = await askQuestion('What integrations do you support?');
console.log(result.answer);
```

## WebSocket Integration

For real-time question answering during meetings:

**WebSocket URL:** `ws://localhost:8000/ws`

### Client Connection

```javascript
const ws = new WebSocket('ws://localhost:8000/ws');

ws.onmessage = (event) => {
  const data = JSON.parse(event.data);

  if (data.type === 'bot_response') {
    console.log('Question:', data.question);
    console.log('Answer:', data.answer);
    console.log('Confidence:', data.confidence);
  }
};

// Send a question
ws.send(JSON.stringify({
  type: 'ask_question',
  question: 'What are the key features of Cloud Monitor Pro?'
}));
```

### Response Format

```json
{
  "type": "bot_response",
  "bot_id": "meeting_123",
  "question": "What are the key features of Cloud Monitor Pro?",
  "answer": "Cloud Monitor Pro features: Real-time metrics tracking...",
  "confidence": "high",
  "timestamp": "2026-03-28T10:30:00Z"
}
```

## Error Handling

All endpoints return standard HTTP status codes:

- `200 OK` - Successful request
- `400 Bad Request` - Invalid parameters
- `404 Not Found` - Resource not found
- `500 Internal Server Error` - Server error

**Error Response Format:**
```json
{
  "error": "Error description",
  "detail": "Detailed error message",
  "code": "ERROR_CODE"
}
```

## Rate Limiting

Currently no rate limiting is implemented. In production, consider:
- 100 requests per minute per IP
- 1000 requests per hour per API key

## Authentication

Current implementation does not require authentication. For production:
- Add API key authentication
- Use JWT tokens for user sessions
- Implement OAuth2 for third-party integrations

## Future Enhancements

Planned API improvements:
1. **Conversation Context** - Track multi-turn conversations
2. **Custom Filters** - Filter by product, price range, features
3. **Bulk Queries** - Process multiple questions in one request
4. **Analytics** - Track question patterns and confidence scores
5. **Webhooks** - Subscribe to new knowledge base updates
