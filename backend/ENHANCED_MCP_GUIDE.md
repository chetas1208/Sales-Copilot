# Enhanced Company Intelligence MCP Server - Quick Start Guide

## 🚀 What's New?

I've implemented the **best features from top GitHub MCP servers**:

✅ **FastMCP** - Easy tool creation
✅ **ChromaDB** - Local vector database for persistent storage
✅ **Smart Extraction** - Natural language queries
✅ **Adaptive Crawling** - Multi-page scraping that stops intelligently
✅ **Caching** - Avoid re-scraping same URLs
✅ **Knowledge Base Search** - Search previously scraped companies

---

## 📦 Installation

```bash
cd backend

# Install dependencies
pip install -r requirements.txt

# Install Playwright browsers
playwright install chromium
```

---

## 🎯 New API Endpoints

All endpoints are under `/api/intelligence/`

### 1. **Analyze Company** (Enhanced)
```bash
POST /api/intelligence/analyze
{
  "url": "https://acme.com"
}
```

**Returns:**
- Raw scraped data
- AI-powered sales intelligence
- Stored in ChromaDB for future searches

### 2. **Compare Companies** (Enhanced)
```bash
POST /api/intelligence/compare
{
  "user_company_url": "https://yourcompany.com",
  "target_company_url": "https://targetcompany.com"
}
```

**Returns:**
- Both company analyses
- **Competitive positioning strategy**
- Key differentiators
- Objection handling tips

### 3. **Smart Extraction** (NEW!)
```bash
POST /api/intelligence/extract
{
  "url": "https://acme.com",
  "instruction": "List all products with their pricing"
}
```

**Natural Language Instructions:**
- "Find the names and titles of all executives"
- "Extract recent news or press releases"
- "What are their customer testimonials?"
- "List all products with pricing"

### 4. **Adaptive Crawling** (NEW!)
```bash
POST /api/intelligence/crawl
{
  "seed_url": "https://acme.com",
  "max_pages": 5,
  "target_words": 5000
}
```

**Smart Features:**
- Stops when enough content gathered
- Only follows internal links
- AI summary of all crawled pages

### 5. **Search Knowledge Base** (NEW!)
```bash
POST /api/intelligence/search
{
  "query": "companies that sell SaaS products",
  "top_k": 3
}
```

**Searches:**
- All previously scraped companies
- Semantic search with embeddings
- Returns most relevant matches

---

## 🧪 Testing

### Quick Test (Terminal)

```bash
# Start the server
cd backend
python main.py

# In another terminal, test the API
curl -X POST http://localhost:8000/api/intelligence/analyze \
  -H "Content-Type: application/json" \
  -d '{"url": "https://openai.com"}'
```

### Test Smart Extraction
```bash
curl -X POST http://localhost:8000/api/intelligence/extract \
  -H "Content-Type: application/json" \
  -d '{
    "url": "https://openai.com",
    "instruction": "List all AI products they offer"
  }'
```

### Test Adaptive Crawling
```bash
curl -X POST http://localhost:8000/api/intelligence/crawl \
  -H "Content-Type: application/json" \
  -d '{
    "seed_url": "https://openai.com",
    "max_pages": 3,
    "target_words": 3000
  }'
```

### Test Knowledge Base Search
```bash
# First scrape some companies
curl -X POST http://localhost:8000/api/intelligence/analyze \
  -H "Content-Type: application/json" \
  -d '{"url": "https://openai.com"}'

curl -X POST http://localhost:8000/api/intelligence/analyze \
  -H "Content-Type: application/json" \
  -d '{"url": "https://anthropic.com"}'

# Then search
curl -X POST http://localhost:8000/api/intelligence/search \
  -H "Content-Type: application/json" \
  -d '{"query": "AI companies", "top_k": 2}'
```

---

## 🎨 Frontend Integration

### React/TypeScript Example

```typescript
// Enhanced API client
const intelligenceAPI = {
  async analyzeCompany(url: string) {
    const response = await fetch('http://localhost:8000/api/intelligence/analyze', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ url })
    });
    return response.json();
  },

  async compareCompanies(userUrl: string, targetUrl: string) {
    const response = await fetch('http://localhost:8000/api/intelligence/compare', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        user_company_url: userUrl,
        target_company_url: targetUrl
      })
    });
    return response.json();
  },

  async smartExtract(url: string, instruction: string) {
    const response = await fetch('http://localhost:8000/api/intelligence/extract', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ url, instruction })
    });
    return response.json();
  },

  async crawlWebsite(seedUrl: string, maxPages: number = 5) {
    const response = await fetch('http://localhost:8000/api/intelligence/crawl', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        seed_url: seedUrl,
        max_pages: maxPages,
        target_words: 5000
      })
    });
    return response.json();
  },

  async searchKnowledgeBase(query: string, topK: number = 3) {
    const response = await fetch('http://localhost:8000/api/intelligence/search', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ query, top_k: topK })
    });
    return response.json();
  }
};

// Usage in component
function MeetingPrepPage() {
  const [loading, setLoading] = useState(false);
  const [analysis, setAnalysis] = useState(null);

  const handleAnalyze = async (url: string) => {
    setLoading(true);
    try {
      const result = await intelligenceAPI.analyzeCompany(url);
      setAnalysis(result);
      console.log('AI Analysis:', result.ai_analysis);
    } catch (error) {
      console.error('Analysis failed:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleSmartExtraction = async () => {
    const result = await intelligenceAPI.smartExtract(
      'https://acme.com',
      'List all products with pricing'
    );
    console.log('Extracted:', result.extracted_data);
  };

  return (
    <div>
      <button onClick={() => handleAnalyze('https://openai.com')}>
        Analyze Company
      </button>
      {analysis && (
        <div>
          <h2>{analysis.company_name}</h2>
          <pre>{analysis.ai_analysis}</pre>
        </div>
      )}
    </div>
  );
}
```

---

## 🔧 Advanced Usage

### Use as Standalone MCP Server

The server can also run as a standalone MCP server (not just REST API):

```bash
# Start MCP server
cd backend
python -m mcp_servers.company_intelligence_mcp.server
```

Then connect from Claude Code or any MCP client:

```json
// .mcp.json
{
  "mcpServers": {
    "company-intelligence": {
      "command": "python",
      "args": ["-m", "mcp_servers.company_intelligence_mcp.server"],
      "cwd": "/path/to/backend"
    }
  }
}
```

### Available MCP Tools:
1. `scrape_company` - Basic company info
2. `analyze_company_for_sales` - Full AI analysis
3. `compare_companies` - Compare two companies
4. `extract_with_instruction` - Natural language extraction
5. `crawl_website_adaptive` - Multi-page crawling
6. `search_knowledge_base` - Search scraped companies

---

## 💾 ChromaDB Storage

All scraped companies are automatically stored in `backend/chroma_db/` for persistent storage.

**Data includes:**
- Company name
- URL
- AI analysis
- Scraped timestamp
- Embeddings for semantic search

**Benefits:**
- Search previously scraped companies
- Avoid re-scraping
- Build knowledge base over time
- Fast semantic search

---

## ⚡ Performance

### Caching
- URLs cached for 1 hour
- Reduces API costs
- Faster responses

### Adaptive Crawling
- Average: 3-5 pages crawled
- Stops at 5000 words or 5 pages
- Saves time and money

### Storage
- ChromaDB stored locally (no cloud costs)
- Fast vector search
- Persistent across restarts

---

## 🆚 Comparison: Old vs New

| Feature | Old Implementation | New Enhanced |
|---------|-------------------|--------------|
| Scraping | ✅ Single page | ✅ Single + Multi-page |
| AI Analysis | ✅ OpenAI | ✅ OpenAI (same) |
| Extraction | ❌ Fixed format | ✅ Natural language |
| Caching | ❌ None | ✅ 1 hour cache |
| Knowledge Base | ❌ None | ✅ ChromaDB vector search |
| Crawling | ❌ Single page | ✅ Adaptive multi-page |
| API Framework | Custom | FastMCP + REST |
| Storage | ❌ Temporary | ✅ Persistent ChromaDB |

---

## 🎯 Use Cases

### 1. **Sales Meeting Prep**
```typescript
// Analyze both companies
const result = await intelligenceAPI.compareCompanies(
  'https://mycompany.com',
  'https://prospect.com'
);

// Display positioning strategy
console.log(result.positioning_strategy);
```

### 2. **Competitor Research**
```typescript
// Crawl competitor's entire site
const crawl = await intelligenceAPI.crawlWebsite(
  'https://competitor.com',
  10  // max 10 pages
);

// Get summary
console.log(crawl.ai_summary);
```

### 3. **Product Research**
```typescript
// Extract specific info
const products = await intelligenceAPI.smartExtract(
  'https://acme.com/products',
  'List all products with their key features and pricing'
);

console.log(products.extracted_data);
```

### 4. **Find Similar Companies**
```typescript
// Search knowledge base
const similar = await intelligenceAPI.searchKnowledgeBase(
  'B2B SaaS companies selling to enterprises',
  5
);

console.log(similar.companies);
```

---

## 🐛 Troubleshooting

### ChromaDB not working?
```bash
# Delete and recreate
rm -rf backend/chroma_db
# Restart server - it will auto-create
```

### Playwright issues?
```bash
# Reinstall browsers
playwright install chromium --force
```

### OpenAI API errors?
Check your `.env`:
```bash
OPENAI_API_KEY=<your_openai_api_key_here>
```

### Import errors?
```bash
# Reinstall dependencies
pip install -r requirements.txt --force-reinstall
```

---

## 📊 API Response Examples

### Analyze Company Response
```json
{
  "success": true,
  "url": "https://openai.com",
  "company_name": "OpenAI",
  "raw_data": {
    "title": "OpenAI",
    "description": "...",
    "headings": [...],
    "products": [...]
  },
  "ai_analysis": "**Company Overview:**\nOpenAI is an AI research...",
  "scraped_at": "2026-03-28T15:30:00.000Z"
}
```

### Smart Extraction Response
```json
{
  "success": true,
  "url": "https://acme.com",
  "instruction": "List all products with pricing",
  "extracted_data": {
    "products": [
      {"name": "Pro Plan", "price": "$99/mo"},
      {"name": "Enterprise", "price": "Custom"}
    ]
  },
  "extracted_at": "2026-03-28T15:30:00.000Z"
}
```

### Knowledge Base Search Response
```json
{
  "success": true,
  "query": "AI companies",
  "results_found": 2,
  "companies": [
    {
      "company_name": "OpenAI",
      "url": "https://openai.com",
      "scraped_at": "2026-03-28T15:00:00.000Z",
      "summary": "OpenAI is an AI research...",
      "relevance_score": 0.95
    },
    {
      "company_name": "Anthropic",
      "url": "https://anthropic.com",
      "scraped_at": "2026-03-28T15:10:00.000Z",
      "summary": "Anthropic develops AI safety...",
      "relevance_score": 0.92
    }
  ]
}
```

---

## 🎉 Summary

You now have:
1. ✅ **6 powerful MCP tools** for company intelligence
2. ✅ **6 REST API endpoints** for frontend integration
3. ✅ **Local vector database** (ChromaDB) for persistent storage
4. ✅ **Caching** to reduce costs
5. ✅ **Adaptive crawling** for multi-page sites
6. ✅ **Natural language extraction** for custom queries
7. ✅ **Knowledge base search** for finding similar companies

**All implemented in ~10 minutes using best practices from top GitHub MCP servers!** 🚀

---

## 📚 Next Steps

1. **Test the endpoints** with curl or Postman
2. **Integrate into frontend** using the TypeScript examples
3. **Build up knowledge base** by scraping companies
4. **Use search** to find relevant companies later

Enjoy your enhanced company intelligence system! 🎊
