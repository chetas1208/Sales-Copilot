# RAG-Powered Product Knowledge System

This system provides intelligent, context-aware responses to customer questions about TechCorp's products, modules, features, and pricing using Retrieval-Augmented Generation (RAG).

## Overview

The RAG pipeline enables the Meetstream bot to:
- Answer customer questions about products and features
- Provide accurate pricing information
- Suggest appropriate licenses based on customer needs
- Search product documentation semantically
- Respond intelligently during sales calls

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    Product Knowledge Base                    │
│  (data/product_knowledge_base.json)                         │
│  - Products & Modules                                        │
│  - Features & Capabilities                                   │
│  - Pricing Tiers & Licenses                                  │
│  - Common Questions & Answers                                │
│  - Bundles & Discounts                                       │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────┐
│                    RAG Service Layer                         │
│  (services/rag_service.py)                                  │
│                                                              │
│  1. Document Extraction                                      │
│     └─ Breaks knowledge base into searchable chunks         │
│                                                              │
│  2. Embedding Generation                                     │
│     └─ Uses sentence-transformers (all-MiniLM-L6-v2)        │
│                                                              │
│  3. Vector Index                                             │
│     └─ FAISS for fast similarity search                     │
│                                                              │
│  4. Query Processing                                         │
│     └─ Semantic search + answer generation                  │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────┐
│              Meetstream Service Integration                  │
│  (services/meetstream_service.py)                           │
│                                                              │
│  - answer_product_question()                                 │
│  - search_product_knowledge()                                │
│  - get_product_catalog()                                     │
│  - process_transcript_with_rag()                             │
└─────────────────────────────────────────────────────────────┘
```

## Components

### 1. Product Knowledge Base
**Location:** `backend/data/product_knowledge_base.json`

A comprehensive JSON database containing:

#### Products (3 Main Suites)
1. **CloudOps Suite** - Cloud infrastructure management
   - Cloud Monitor Pro
   - Cost Optimizer AI
   - Security Command Center

2. **DataFlow Analytics Platform** - Data pipeline & analytics
   - Data Pipeline Builder
   - ML Model Hub
   - Business Intelligence Studio

3. **Collaboration Hub** - Communication & teamwork
   - Meet Pro
   - Workspace Manager

#### Each Module Includes:
- Detailed descriptions
- Feature lists (5-10 key features)
- License tiers (Starter/Basic, Professional, Enterprise)
- Pricing information
- Support levels
- Usage limits

#### Additional Data:
- 10 common Q&A pairs (trials, discounts, support, etc.)
- 3 pricing bundles with discounts
- Integration information

### 2. RAG Service
**Location:** `backend/services/rag_service.py`

Core functionality:

#### Document Processing
```python
# Automatically indexes 57 documents from the knowledge base:
# - Product overviews
# - Module descriptions
# - Feature lists
# - License details
# - FAQ entries
# - Bundle information
```

#### Semantic Search
```python
rag = get_rag_service()

# Search for relevant information
results = rag.search("cloud monitoring features", top_k=5)
# Returns: List of SearchResult with content, score, metadata

# Get formatted context for LLM
context = rag.get_context_for_query("What security features do you have?")
```

#### Question Answering
```python
# Direct question answering
answer = rag.answer_question("How much does the enterprise plan cost?")

# Returns:
{
    "answer": "For Cloud Monitor Pro, the Enterprise tier costs $2,499/month...",
    "confidence": "high",  # high/medium/low
    "source": "knowledge_base",  # or "faq"
    "results": [...]  # Supporting documents
}
```

#### Product Information
```python
# Get all products
products = rag.list_all_products()

# Get specific product/module info
info = rag.get_product_info(product_name="CloudOps Suite", module_name="Cloud Monitor Pro")

# Get pricing for a module
pricing = rag.get_pricing_for_module("ML Model Hub")
```

### 3. Meetstream Integration
**Location:** `backend/services/meetstream_service.py`

The Meetstream service now includes RAG capabilities:

#### Automatic Question Detection
```python
# During meetings, transcripts are analyzed for questions
# Automatically detects questions based on:
# - Question marks (?)
# - Question words (what, how, why, etc.)
# - Keywords (price, cost, feature, license, etc.)

result = await meetstream_service.process_transcript_with_rag(
    bot_id="meeting_123",
    transcript="What cloud monitoring solutions do you have?"
)
# Automatically broadcasts answer to meeting participants
```

#### Manual Question Answering
```python
# Direct API call for answering questions
answer = await meetstream_service.answer_product_question(
    "Tell me about your ML capabilities"
)
```

#### Search Product Knowledge
```python
# Search for specific information
results = meetstream_service.search_product_knowledge(
    "security compliance",
    top_k=5
)
```

## How It Works

### Indexing Pipeline (Initialization)

1. **Load Knowledge Base**
   - Reads `product_knowledge_base.json`
   - Validates structure

2. **Extract Documents**
   - Breaks down products into searchable chunks
   - Creates 57 documents with metadata
   - Each document represents:
     - A product overview
     - A module description
     - A feature list
     - A license tier
     - An FAQ entry
     - A bundle offer

3. **Generate Embeddings**
   - Uses `sentence-transformers` (all-MiniLM-L6-v2 model)
   - Converts text to 384-dimensional vectors
   - Fast and accurate for semantic similarity

4. **Build Vector Index**
   - Uses FAISS (Facebook AI Similarity Search)
   - Creates efficient index for similarity search
   - Supports cosine similarity matching

### Query Pipeline (Runtime)

1. **User asks a question**
   ```
   "What's the pricing for the Professional tier?"
   ```

2. **Generate Query Embedding**
   - Convert question to 384-d vector
   - Same model as document embeddings

3. **Similarity Search**
   - FAISS finds top-k most similar documents
   - Returns documents with similarity scores (0-1)
   - Filters by minimum threshold (default: 0.3)

4. **Answer Generation**
   - Analyzes top results
   - Formats answer based on result type:
     - License info → Structured pricing response
     - Module info → Description + features
     - FAQ → Direct answer
     - Bundle → Bundle details + pricing

5. **Response with Confidence**
   ```json
   {
     "answer": "For Cloud Monitor Pro, the Professional tier costs $899/month...",
     "confidence": "high",
     "source": "knowledge_base",
     "results": [...]
   }
   ```

## Usage Examples

### Test the RAG System

```bash
cd backend
python3 test_rag.py
```

This will:
- Initialize the RAG service
- Test 15 sample questions
- Perform semantic searches
- Display product catalog
- Show pricing lookups

### Integration in Code

```python
from services.rag_service import get_rag_service

# Initialize
rag = get_rag_service()

# Answer a question
result = rag.answer_question("Can I try before buying?")
print(result['answer'])
# Output: "Absolutely! We offer a 14-day free trial..."

# Search for information
results = rag.search("cost optimization", top_k=3)
for r in results:
    print(f"[{r.score:.2f}] {r.content[:100]}...")

# Get product catalog
products = rag.list_all_products()
for p in products:
    print(f"- {p['name']}: {', '.join(p['modules'])}")

# Get pricing
pricing = rag.get_pricing_for_module("Meet Pro")
for tier in pricing:
    print(f"{tier['tier']}: {tier['price']}")
```

### In Meetstream Bot

```python
from services.meetstream_service import get_meetstream_service

meetstream = get_meetstream_service()

# During a meeting, process transcript
await meetstream.process_transcript_with_rag(
    bot_id="bot_123",
    transcript="What security features do you offer?"
)
# Automatically generates and broadcasts answer

# Manual query
answer = await meetstream.answer_product_question(
    "Do you have any bundles or discounts?"
)
print(answer['answer'])
```

## Sample Questions & Answers

The system can handle:

### Product Questions
- "What cloud monitoring solutions do you have?"
- "Tell me about your data analytics platform"
- "What collaboration tools are available?"

### Pricing Questions
- "How much does the enterprise plan cost?"
- "What's the pricing for Cloud Monitor Pro?"
- "Do you have any bundles or discounts?"

### Feature Questions
- "What security features do you offer?"
- "Can you help with cost optimization?"
- "What ML capabilities are included?"

### License Questions
- "What's included in the Professional tier?"
- "What support do I get with the Starter plan?"
- "Tell me about the Enterprise license"

### General Questions
- "Can I try before buying?"
- "What integrations do you support?"
- "How do I get started?"

## Performance Metrics

- **Indexing Time:** ~3 seconds (57 documents)
- **Query Time:** ~50-100ms per question
- **Model Size:** ~90MB (embedding model)
- **Index Size:** ~130KB (FAISS index)
- **Accuracy:** High confidence (>0.6 score) on 80%+ of domain questions

## Configuration

### Environment Variables
```bash
# No special configuration needed
# RAG service auto-initializes with default settings
```

### Customization

**Change Embedding Model:**
```python
rag = RAGService(model_name="all-mpnet-base-v2")  # More accurate, slower
```

**Adjust Score Threshold:**
```python
results = rag.search(query, score_threshold=0.5)  # Higher = stricter
```

**Tune Result Count:**
```python
results = rag.search(query, top_k=10)  # More results
```

## Extending the Knowledge Base

To add new products/modules:

1. Edit `backend/data/product_knowledge_base.json`
2. Add new product/module following the existing structure
3. Restart the service (auto-reindexes)

Example:
```json
{
  "id": "new-product",
  "name": "New Product",
  "description": "Product description",
  "modules": [
    {
      "id": "new-module",
      "name": "Module Name",
      "description": "Module description",
      "features": ["Feature 1", "Feature 2"],
      "licenses": [
        {
          "tier": "Starter",
          "price": "$99/month",
          "limits": "Up to 10 users",
          "support": "Email support"
        }
      ]
    }
  ]
}
```

## Dependencies

```
sentence-transformers==3.3.1  # Embedding generation
faiss-cpu==1.9.0             # Vector similarity search
numpy>=1.25.0                 # Numerical operations
```

## Troubleshooting

### RAG Service Not Available
```python
# Check if RAG initialized
if meetstream.rag:
    print("RAG available")
else:
    print("RAG not available - check logs")
```

### Low Confidence Answers
- Question too vague → Try more specific queries
- Out of domain → Add relevant info to knowledge base
- Score threshold too high → Adjust `score_threshold` parameter

### Slow Performance
- Embedding model loading is one-time cost (~2s)
- Subsequent queries are fast (<100ms)
- Consider caching for frequently asked questions

## Future Enhancements

Potential improvements:
1. **LLM Integration** - Use OpenAI/Claude to generate more natural answers
2. **Conversation Context** - Track multi-turn conversations
3. **Analytics** - Track common questions, confidence scores
4. **Dynamic Updates** - Hot-reload knowledge base without restart
5. **Multi-language** - Support questions in multiple languages
6. **Custom Training** - Fine-tune embeddings on company-specific data

## References

- Sentence Transformers: https://www.sbert.net/
- FAISS: https://github.com/facebookresearch/faiss
- RAG Overview: https://arxiv.org/abs/2005.11401
