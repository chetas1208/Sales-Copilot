# MCP Web Scraping with OpenAI: GitHub Examples & Best Practices

## Overview
I researched GitHub repositories implementing MCP (Model Context Protocol) servers for web scraping with AI/LLM integration. Here are the best examples and how they can improve our implementation.

---

## 🏆 Top GitHub Examples

### 1. **MaitreyaM/WEB-SCRAPING-MCP**
**Repository:** https://github.com/MaitreyaM/WEB-SCRAPING-MCP

**Tech Stack:**
- FastMCP (MCP server framework)
- crawl4ai (web scraping)
- Google Gemini API (LLM analysis)
- SSE (Server-Sent Events) transport

**Key Features:**
```python
# Three MCP tools exposed:

1. scrape_url(url: str) -> str
   - Converts entire webpage to Markdown
   - Returns clean, structured text

2. extract_text_by_query(url: str, query: str, context_window: int = 300)
   - Searches for specific text on page
   - Returns up to 5 matching snippets with context

3. smart_extract(url: str, instruction: str) -> dict
   - Uses LLM (Gemini) for intelligent extraction
   - Natural language instructions: "List all products mentioned"
   - Returns structured JSON
```

**Why It's Good:**
- Combines dumb scraping (fast) with smart extraction (accurate)
- FastMCP makes it easy to create MCP tools
- SSE transport for real-time streaming

**Limitations:**
- Uses Gemini instead of OpenAI
- No RAG or vector storage
- Single-page focused

---

### 2. **sadiuysal/crawl4ai-mcp-server**
**Repository:** https://github.com/sadiuysal/crawl4ai-mcp-server

**Tech Stack:**
- Crawl4AI (advanced web crawling)
- MCP stdio protocol
- OpenAI Agents SDK compatible
- Playwright for JS-heavy sites

**Key Features:**
```python
# Four powerful tools:

1. scrape(url: str) -> markdown
   - Single page scraping
   - Markdown output optimized for LLMs

2. crawl(seed_url: str, max_pages: int = 10, adaptive: bool = True)
   - Multi-page breadth-first traversal
   - Adaptive stopping when enough content gathered
   - Smart depth control

3. crawl_site(seed_url: str, output_dir: str)
   - Full site crawling with persistence
   - Saves to disk (handles large sites)

4. crawl_sitemap(sitemap_url: str)
   - Sitemap-based crawling
   - Structured results
```

**Integration with OpenAI Agents SDK:**
```python
from agents import Agent, Runner
from agents.mcp.server import MCPServerStdio

async with MCPServerStdio(
    params={
        "command": "python",
        "args": ["-m", "crawler_agent.mcp_server"]
    }
) as server:
    agent = Agent(
        name="Research Assistant",
        instructions="Use crawl tools to research companies",
        mcp_servers=[server]
    )

    result = await Runner.run(
        agent,
        "Research https://acme.com - what do they sell?"
    )
```

**Why It's Excellent:**
- Production-ready with safety mechanisms
- Blocks internal networks/private IPs
- Adaptive crawling saves time and cost
- Docker deployment included
- Native OpenAI Agents SDK integration

**Best Use Case:**
- Multi-page company research
- Documentation crawling
- Competitive analysis

---

### 3. **coleam00/mcp-crawl4ai-rag**
**Repository:** https://github.com/coleam00/mcp-crawl4ai-rag

**Tech Stack:**
- Crawl4AI (scraping)
- OpenAI API (embeddings + completions)
- Supabase (vector database)
- pgvector (similarity search)

**Key Features:**
```python
# RAG-Enhanced Scraping

1. Crawl website + auto-embed content
   - Chunks pages into semantic segments
   - Generates OpenAI embeddings
   - Stores in Supabase pgvector

2. Contextual embeddings (optional)
   - Uses GPT-4.1-nano to enrich context
   - Better semantic understanding
   - Higher quality retrieval

3. Agentic RAG (optional)
   - Extracts code blocks
   - Generates summaries with LLM
   - Targeted code retrieval

4. Hybrid search
   - Semantic (vector similarity)
   - Keyword (full-text search)
   - Reranking with cross-encoder
```

**Configuration:**
```bash
OPENAI_API_KEY=<your_openai_api_key_here>
MODEL_CHOICE=gpt-4.1-nano

# Feature flags
USE_CONTEXTUAL_EMBEDDINGS=true   # Better retrieval, more API cost
USE_AGENTIC_RAG=true             # Code-focused extraction
USE_RERANKING=true               # Local model, no API cost
```

**Why It's Advanced:**
- Full RAG pipeline for scraped content
- Enables "chat with website" features
- Persistent knowledge base
- Hybrid search for best results

**Cost Trade-offs:**
- Basic RAG: Only embeddings (cheap)
- Contextual: Extra LLM calls per chunk (moderate)
- Agentic: Code summarization (higher)

**Best Use Case:**
- Building knowledge base from docs
- Multi-session research
- Question answering over scraped content

---

## 🎯 Key Learnings for Our Implementation

### 1. **Use FastMCP for Easy Tool Creation**
Instead of manually implementing MCP protocol, use FastMCP:

```python
from fastmcp import FastMCP

mcp = FastMCP("Company Scraper")

@mcp.tool()
async def scrape_company(url: str) -> dict:
    """Scrape company website and extract business info"""
    # Use our existing web_scraper_mcp
    result = await web_scraper.extract_company_info(url)

    # Analyze with OpenAI
    analysis = await openai_client.simple_prompt(
        prompt=f"Analyze this company: {result}",
        system="You are a sales analyst..."
    )

    return {"company": result, "analysis": analysis}

@mcp.tool()
async def compare_companies(
    user_company: str,
    target_company: str
) -> dict:
    """Scrape and compare two companies"""
    # Scrape both in parallel
    results = await asyncio.gather(
        scrape_company(user_company),
        scrape_company(target_company)
    )

    return {
        "user_company": results[0],
        "target_company": results[1]
    }
```

### 2. **Add Adaptive Crawling**
Don't scrape entire sites - stop when you have enough:

```python
async def adaptive_crawl(seed_url: str, max_pages: int = 10):
    """Crawl until sufficient content gathered"""
    pages = []
    queue = [seed_url]
    visited = set()

    while queue and len(pages) < max_pages:
        url = queue.pop(0)
        if url in visited:
            continue

        # Scrape page
        page_data = await scrape_url(url)
        pages.append(page_data)
        visited.add(url)

        # Check if we have enough content
        total_words = sum(p['word_count'] for p in pages)
        if total_words > 5000:  # Enough for analysis
            break

        # Add links to queue
        queue.extend(page_data['links'][:5])  # Only top 5 links

    return pages
```

### 3. **Implement Smart Extraction**
Add LLM-based extraction for specific needs:

```python
@mcp.tool()
async def extract_with_instruction(
    url: str,
    instruction: str
) -> dict:
    """
    Extract specific information using natural language

    Example:
        extract_with_instruction(
            "https://acme.com",
            "List all products with their pricing"
        )
    """
    # Scrape page
    page_content = await web_scraper.scrape_url(url)

    # Use OpenAI for extraction
    prompt = f"""
Extract information from this webpage based on the instruction.

Instruction: {instruction}

Webpage content:
{page_content['content']['text'][:5000]}

Return the result as structured JSON.
"""

    result = await openai_client.simple_prompt(
        prompt=prompt,
        system="You extract structured data from webpages.",
        max_tokens=1000
    )

    return json.loads(result)
```

### 4. **Add Caching to Reduce Costs**
Cache scraped data to avoid re-scraping:

```python
import hashlib
import json
from datetime import datetime, timedelta

# In-memory cache (use Redis in production)
scrape_cache = {}

async def scrape_with_cache(url: str, ttl_hours: int = 24):
    """Scrape with caching"""
    cache_key = hashlib.md5(url.encode()).hexdigest()

    # Check cache
    if cache_key in scrape_cache:
        cached_data, timestamp = scrape_cache[cache_key]
        age = datetime.now() - timestamp

        if age < timedelta(hours=ttl_hours):
            logger.info(f"Cache hit for {url}")
            return cached_data

    # Scrape if not cached
    logger.info(f"Scraping {url}")
    result = await web_scraper.scrape_url(url)

    # Cache result
    scrape_cache[cache_key] = (result, datetime.now())

    return result
```

---

## 🚀 Recommended Implementation for Meetstream AI

### Enhanced MCP Server Structure

```
backend/
├── mcp_servers/
│   ├── web_scraper_mcp/
│   │   ├── __init__.py
│   │   ├── server.py           # Existing Playwright scraper
│   │   └── tools.py            # NEW: MCP tool definitions
│   └── company_intelligence_mcp/   # NEW: Dedicated MCP server
│       ├── __init__.py
│       ├── server.py           # FastMCP-based server
│       ├── tools.py            # MCP tools for company research
│       └── cache.py            # Caching layer
```

### Tool Implementations

**tools.py:**
```python
from fastmcp import FastMCP
from mcp_servers.web_scraper_mcp.server import get_web_scraper
from services.openai_client import get_openai_client
import asyncio

mcp = FastMCP("Company Intelligence")
scraper = None
ai_client = None

@mcp.tool()
async def scrape_company_basic(url: str) -> dict:
    """Quick scrape: just extract company info"""
    global scraper
    if not scraper:
        scraper = await get_web_scraper()

    return await scraper.extract_company_info(url)

@mcp.tool()
async def scrape_company_analysis(url: str) -> dict:
    """Full scrape + AI analysis for sales intelligence"""
    global scraper, ai_client
    if not scraper:
        scraper = await get_web_scraper()
    if not ai_client:
        ai_client = get_openai_client()

    # Scrape
    company_data = await scraper.extract_company_info(url)

    # Analyze with AI
    prompt = f"""
Analyze this company for sales intelligence:

Company: {company_data['company_name']}
Description: {company_data['description']}
About: {company_data['about_text']}

Provide:
1. What they sell
2. Target market
3. Pain points they address
4. Sales talking points
"""

    analysis = await ai_client.simple_prompt(
        prompt=prompt,
        system="Sales analyst extracting key insights",
        max_tokens=1500
    )

    return {
        **company_data,
        "ai_analysis": analysis
    }

@mcp.tool()
async def compare_companies(
    user_company_url: str,
    target_company_url: str
) -> dict:
    """Scrape and compare two companies for sales prep"""
    # Scrape both in parallel
    results = await asyncio.gather(
        scrape_company_analysis(user_company_url),
        scrape_company_analysis(target_company_url),
        return_exceptions=True
    )

    user_company = results[0]
    target_company = results[1]

    # Generate comparison
    comparison = await ai_client.simple_prompt(
        prompt=f"""
Compare these two companies:

YOUR COMPANY:
{user_company.get('ai_analysis', 'N/A')}

TARGET COMPANY:
{target_company.get('ai_analysis', 'N/A')}

How should the sales rep position your company's solution?
""",
        system="Sales strategist creating positioning",
        max_tokens=1000
    )

    return {
        "user_company": user_company,
        "target_company": target_company,
        "positioning": comparison
    }

@mcp.tool()
async def extract_specific_info(
    url: str,
    extraction_query: str
) -> dict:
    """
    Extract specific information using natural language

    Example queries:
    - "List all products with pricing"
    - "What are their recent news items?"
    - "Who are the key executives?"
    """
    global scraper, ai_client
    if not scraper:
        scraper = await get_web_scraper()
    if not ai_client:
        ai_client = get_openai_client()

    # Scrape
    page_data = await scraper.scrape_url(url)

    # Extract with AI
    result = await ai_client.simple_prompt(
        prompt=f"""
Extract: {extraction_query}

From this webpage:
{page_data['content']['text'][:6000]}

Return as JSON.
""",
        system="Information extraction specialist",
        max_tokens=1000
    )

    return {"url": url, "query": extraction_query, "result": result}
```

---

## 📊 Comparison Matrix

| Feature | Our Current | MaitreyaM | sadiuysal | coleam00 | Recommended |
|---------|-------------|-----------|-----------|----------|-------------|
| Single page scrape | ✅ | ✅ | ✅ | ✅ | ✅ Keep |
| Multi-page crawl | ❌ | ❌ | ✅ | ✅ | 🎯 Add |
| AI analysis | ✅ OpenAI | ✅ Gemini | ❌ | ✅ OpenAI | ✅ Keep |
| MCP protocol | ✅ Custom | ✅ FastMCP | ✅ stdio | ✅ Custom | 🎯 Add FastMCP |
| RAG/Vector DB | ❌ | ❌ | ❌ | ✅ Supabase | ⏭️ Future |
| Caching | ❌ | ❌ | ❌ | ❌ | 🎯 Add |
| Adaptive crawl | ❌ | ❌ | ✅ | ✅ | 🎯 Add |
| Company comparison | ✅ | ❌ | ❌ | ❌ | ✅ Keep |
| Smart extraction | ❌ | ✅ | ❌ | ✅ | 🎯 Add |

---

## 🎬 Next Steps

### Phase 1: Immediate Improvements (1-2 hours)
1. ✅ Create FastMCP-based tool wrapper (easier than custom MCP)
2. ✅ Add smart extraction tool with natural language queries
3. ✅ Implement basic caching to reduce API costs

### Phase 2: Enhanced Features (2-4 hours)
1. Add multi-page crawling with adaptive stopping
2. Implement company comparison matrix generation
3. Add product/pricing extraction tools

### Phase 3: Advanced (Future)
1. Add RAG with Supabase for persistent knowledge
2. Real-time streaming of scraping progress
3. Batch processing for multiple companies

---

## 💡 Code Example: Quick Win

Here's a 5-minute improvement using FastMCP:

```bash
# Install FastMCP
pip install fastmcp
```

```python
# backend/mcp_servers/company_intelligence_mcp/quick_server.py
from fastmcp import FastMCP
from mcp_servers.web_scraper_mcp.server import get_web_scraper
from services.openai_client import get_openai_client
import asyncio

mcp = FastMCP("Company Intelligence")

@mcp.tool()
async def analyze_for_sales(url: str) -> str:
    """One-shot: scrape company and return sales brief"""
    scraper = await get_web_scraper()
    ai = get_openai_client()

    # Scrape
    data = await scraper.extract_company_info(url)

    # Analyze
    brief = await ai.simple_prompt(
        f"Sales brief for {data['company_name']}: {data}",
        system="Sales analyst"
    )

    return brief

if __name__ == "__main__":
    mcp.run()
```

Run with:
```bash
python quick_server.py
```

Now any MCP client can call `analyze_for_sales("https://acme.com")`!

---

## 📚 Resources

- **FastMCP Docs:** https://github.com/jlowin/fastmcp
- **Crawl4AI:** https://github.com/unclecode/crawl4ai
- **MCP Protocol:** https://modelcontextprotocol.io
- **OpenAI Agents SDK:** https://openai.github.io/openai-agents-python

---

## Summary

The best implementations combine:
1. **Playwright/Crawl4AI** for robust scraping (handles JS sites)
2. **FastMCP** for easy tool creation
3. **OpenAI/Gemini** for intelligent extraction
4. **Adaptive crawling** to save time and money
5. **Caching** to avoid re-scraping

Our current implementation is solid! The main improvements would be:
- Add FastMCP wrapper for easier MCP tool creation
- Implement adaptive multi-page crawling
- Add smart extraction with natural language queries
- Implement caching layer
