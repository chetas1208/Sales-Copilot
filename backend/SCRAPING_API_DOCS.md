# Company Scraping API Documentation

## Overview
The Company Scraping API allows the frontend to submit company website URLs and receive comprehensive, AI-analyzed company intelligence for sales conversations.

## Architecture

### Components

1. **MCP Server (Web Scraper)**
   - Location: `backend/mcp_servers/web_scraper_mcp/server.py`
   - Technology: Playwright (headless browser)
   - Purpose: Scrapes websites and extracts structured data

2. **Research Agent**
   - Location: `backend/agents/research_agent.py`
   - Technology: OpenAI GPT-4o (or Claude)
   - Purpose: Analyzes scraped data and generates sales intelligence

3. **API Endpoint**
   - Endpoint: `POST /api/scrape-companies`
   - Technology: FastAPI
   - Purpose: Orchestrates scraping for both user and target companies

## API Endpoint

### POST /api/scrape-companies

Scrapes and analyzes two company websites in parallel.

**Request Body:**
```json
{
  "user_company_url": "https://yourcompany.com",
  "target_company_url": "https://targetcompany.com"
}
```

**Response:**
```json
{
  "status": "success",
  "scraped_at": "2026-03-28T14:30:00.000Z",
  "user_company": {
    "success": true,
    "url": "https://yourcompany.com",
    "company_name": "Your Company",
    "summary": "**Company Overview:**\n[AI-generated summary]\n\n**Products/Services:**\n...",
    "raw_data": {
      "description": "Company meta description",
      "products": ["Product 1", "Product 2"],
      "contact_info": {
        "emails": ["contact@company.com"],
        "phones": ["555-1234"]
      }
    },
    "metadata": {
      "domain": "yourcompany.com",
      "title": "Your Company - Home",
      "og_description": "..."
    }
  },
  "target_company": {
    "success": true,
    "url": "https://targetcompany.com",
    "company_name": "Target Company",
    "summary": "...",
    "raw_data": {...},
    "metadata": {...}
  }
}
```

**Error Response:**
```json
{
  "status": "success",
  "user_company": {
    "success": false,
    "error": "Failed to load page: timeout",
    "url": "https://yourcompany.com"
  },
  "target_company": {
    "success": true,
    ...
  }
}
```

## Frontend Integration

### Example Usage (React/TypeScript)

```typescript
// API call
const scrapeCompanies = async (userUrl: string, targetUrl: string) => {
  const response = await fetch('http://localhost:8000/api/scrape-companies', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      user_company_url: userUrl,
      target_company_url: targetUrl,
    }),
  });

  if (!response.ok) {
    throw new Error(`HTTP error! status: ${response.status}`);
  }

  return await response.json();
};

// Usage in component
const handleSubmit = async () => {
  setLoading(true);
  try {
    const result = await scrapeCompanies(
      'https://mycompany.com',
      'https://prospectcompany.com'
    );

    if (result.user_company.success) {
      console.log('User company:', result.user_company.company_name);
      console.log('Summary:', result.user_company.summary);
    }

    if (result.target_company.success) {
      console.log('Target company:', result.target_company.company_name);
      console.log('Summary:', result.target_company.summary);
    }
  } catch (error) {
    console.error('Scraping failed:', error);
  } finally {
    setLoading(false);
  }
};
```

## AI-Generated Summary Format

The `summary` field contains a structured analysis formatted in Markdown:

```markdown
**Company Overview:**
[2-3 sentences about what the company does]

**Products/Services:**
- Product/service 1
- Product/service 2
- Product/service 3

**Target Market:**
[Who they serve]

**Value Proposition:**
[Key benefits/differentiators]

**Pain Points They Address:**
[What problems they solve]

**Sales Talking Points:**
1. [Key insight 1]
2. [Key insight 2]
3. [Key insight 3]
```

## Configuration

### Environment Variables

Add to `backend/.env`:

```bash
# OpenAI API (for analysis)
OPENAI_API_KEY=sk-...

# Optional: Anthropic Claude (alternative to OpenAI)
ANTHROPIC_API_KEY=<your_anthropic_api_key_here>

# Web Scraping Settings
SCRAPER_USER_AGENT=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)
SCRAPER_MAX_PAGES_PER_SITE=10
SCRAPER_TIMEOUT_SECONDS=30
```

### Dependencies

Ensure these are installed:

```bash
# Install Python dependencies
cd backend
pip install -r requirements.txt

# Install Playwright browsers
playwright install chromium
```

## How It Works

### Step-by-Step Flow

1. **Frontend submits URLs** → `POST /api/scrape-companies`

2. **Backend initializes Research Agent**
   - Creates ResearchAgent instance with AI client (OpenAI or Claude)

3. **Parallel scraping** (both companies scraped simultaneously)
   - ResearchAgent.analyze_website() called for each URL
   - Web scraper (Playwright) loads the page
   - BeautifulSoup extracts structured data:
     - Title, headings, paragraphs
     - Meta tags (description, keywords, Open Graph)
     - Links, images, contact info

4. **AI Analysis**
   - Scraped content sent to AI (GPT-4o)
   - AI generates structured sales intelligence
   - Formatted as markdown summary

5. **Response returned**
   - Both company analyses returned to frontend
   - Frontend can display insights in UI

## Advanced Features

### WebSocket Alternative

For real-time updates during scraping, use the WebSocket endpoint:

```javascript
const ws = new WebSocket('ws://localhost:8000/ws');

ws.onopen = () => {
  ws.send(JSON.stringify({
    type: 'start_research',
    company_url: 'https://targetcompany.com',
    competitor_urls: []
  }));
};

ws.onmessage = (event) => {
  const data = JSON.parse(event.data);

  if (data.type === 'research_started') {
    console.log('Research started');
  } else if (data.type === 'insight') {
    console.log('Insight:', data.title, data.content);
  }
};
```

### Competitor Analysis

Use the existing `/api/research` endpoint for competitor analysis:

```json
POST /api/research
{
  "company_url": "https://targetcompany.com",
  "competitor_urls": [
    "https://competitor1.com",
    "https://competitor2.com"
  ]
}
```

## Error Handling

### Common Errors

1. **Timeout Error**
   - Cause: Website took too long to load
   - Solution: Increase `SCRAPER_TIMEOUT_SECONDS` in .env

2. **Missing API Key**
   - Cause: `OPENAI_API_KEY` not set
   - Solution: Add API key to `backend/.env`

3. **Playwright Not Installed**
   - Cause: Chromium browser not installed
   - Solution: Run `playwright install chromium`

4. **Invalid URL**
   - Cause: Malformed URL submitted
   - Solution: Validate URLs on frontend before submission

### Graceful Degradation

The API handles partial failures gracefully. If one company fails to scrape, the other will still return successfully:

```json
{
  "status": "success",
  "user_company": {"success": false, "error": "..."},
  "target_company": {"success": true, ...}
}
```

## Performance

### Timing
- Average scrape time: 3-8 seconds per company
- Parallel execution: Both companies scraped simultaneously
- AI analysis: 2-5 seconds per company

### Optimization Tips
1. Cache results in frontend to avoid re-scraping
2. Use loading states to improve UX
3. Consider background processing for large batch jobs

## Testing

### Manual Testing

```bash
# Start backend
cd backend
python main.py

# Test endpoint
curl -X POST http://localhost:8000/api/scrape-companies \
  -H "Content-Type: application/json" \
  -d '{
    "user_company_url": "https://openai.com",
    "target_company_url": "https://anthropic.com"
  }'
```

### Unit Tests

```python
# tests/test_scraping.py
import pytest
from agents.research_agent import ResearchAgent
from services.openai_client import get_openai_client

@pytest.mark.asyncio
async def test_analyze_website():
    client = get_openai_client()
    agent = ResearchAgent(client)

    result = await agent.analyze_website("https://example.com")

    assert result["success"] == True
    assert "company_name" in result
    assert "summary" in result
```

## Security Considerations

1. **Rate Limiting**: Implement rate limiting to prevent abuse
2. **URL Validation**: Validate and sanitize URLs before scraping
3. **API Key Security**: Never expose API keys to frontend
4. **CORS**: Properly configure CORS for your frontend domain
5. **Timeouts**: Set reasonable timeouts to prevent resource exhaustion

## Future Enhancements

- [ ] Add caching layer (Redis) to avoid re-scraping
- [ ] Support for LinkedIn profile scraping via Apify
- [ ] PDF/document parsing for company materials
- [ ] Image analysis (logos, screenshots)
- [ ] Real-time streaming of scraping progress
- [ ] Batch processing for multiple companies
- [ ] Company comparison matrix generation

## Support

For issues or questions:
1. Check logs: `backend/logs/`
2. Enable debug mode: Set `DEBUG=True` in `.env`
3. Review Playwright traces for scraping issues
