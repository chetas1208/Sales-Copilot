"""
Enhanced Company Intelligence MCP Server
Uses FastMCP, ChromaDB for vector storage, and adaptive crawling
"""

import os
import asyncio
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime
import json
import hashlib

from fastmcp import FastMCP
import chromadb

# Import our existing services
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), '../..'))

from mcp_servers.web_scraper_mcp.server import get_web_scraper
from services.openai_client import get_openai_client

logger = logging.getLogger(__name__)

# Initialize FastMCP
mcp = FastMCP("Company Intelligence")

# Global instances
scraper = None
ai_client = None
chroma_client = None
collection = None

# In-memory cache
scrape_cache = {}


async def initialize():
    """Initialize all services"""
    global scraper, ai_client, chroma_client, collection

    if not scraper:
        scraper = await get_web_scraper()
        logger.info("Web scraper initialized")

    if not ai_client:
        ai_client = get_openai_client()
        logger.info("OpenAI client initialized")

    if not chroma_client:
        # Initialize ChromaDB (local storage) - using PersistentClient for v0.5+
        chroma_client = chromadb.PersistentClient(path="./chroma_db")

        # Get or create collection
        collection = chroma_client.get_or_create_collection(
            name="company_intelligence",
            metadata={"description": "Scraped company data with embeddings"}
        )
        logger.info("ChromaDB initialized")


@mcp.tool()
async def scrape_company(url: str, use_cache: bool = True) -> dict:
    """
    Scrape company website and extract basic information

    Args:
        url: Company website URL
        use_cache: Use cached results if available (default: True)

    Returns:
        Company information including name, description, products, contact info
    """
    await initialize()

    # Check cache
    if use_cache:
        cache_key = hashlib.md5(url.encode()).hexdigest()
        if cache_key in scrape_cache:
            cached_data, timestamp = scrape_cache[cache_key]
            age_minutes = (datetime.now() - timestamp).total_seconds() / 60
            if age_minutes < 60:  # Cache for 1 hour
                logger.info(f"Cache hit for {url} (age: {age_minutes:.1f}m)")
                return cached_data

    # Scrape
    logger.info(f"Scraping company: {url}")
    result = await scraper.extract_company_info(url)

    # Cache result
    if use_cache:
        cache_key = hashlib.md5(url.encode()).hexdigest()
        scrape_cache[cache_key] = (result, datetime.now())

    return result


@mcp.tool()
async def analyze_company_for_sales(url: str) -> dict:
    """
    Scrape company and generate AI-powered sales intelligence

    Args:
        url: Company website URL

    Returns:
        Complete sales brief with company overview, products, target market,
        value proposition, pain points, and sales talking points
    """
    await initialize()

    # Scrape company
    company_data = await scrape_company(url)

    if not company_data.get("success", True):
        return company_data  # Return error

    # Generate AI analysis
    logger.info(f"Analyzing company: {company_data.get('company_name', 'Unknown')}")

    prompt = f"""
Analyze this company for sales intelligence:

Company Name: {company_data.get('company_name', 'Unknown')}
URL: {url}
Description: {company_data.get('description', 'N/A')}
Title: {company_data.get('title', 'N/A')}

Main Headings:
{chr(10).join([h.get('text', '') for h in company_data.get('headings', [])[:10]])}

About Text:
{company_data.get('about_text', 'N/A')[:1000]}

Products/Services:
{chr(10).join([f"- {p}" for p in company_data.get('products', [])])}

Provide a structured analysis in this format:

**Company Overview:**
[2-3 sentences about what the company does]

**Products/Services:**
[Bullet points of main offerings]

**Target Market:**
[Who they serve]

**Value Proposition:**
[Key benefits/differentiators]

**Pain Points They Address:**
[What problems they solve]

**Sales Talking Points:**
[3-5 key insights for approaching this prospect]
"""

    analysis = await ai_client.simple_prompt(
        prompt=prompt,
        system="You are a sales research analyst specializing in quickly understanding companies from their websites.",
        max_tokens=2000
    )

    # Store in vector DB
    try:
        doc_id = hashlib.md5(url.encode()).hexdigest()
        collection.upsert(
            ids=[doc_id],
            documents=[f"{company_data.get('company_name', 'Unknown')}: {analysis}"],
            metadatas=[{
                "url": url,
                "company_name": company_data.get('company_name', 'Unknown'),
                "scraped_at": datetime.now().isoformat()
            }]
        )
        logger.info(f"Stored in ChromaDB: {doc_id}")
    except Exception as e:
        logger.warning(f"Failed to store in ChromaDB: {e}")

    return {
        "success": True,
        "url": url,
        "company_name": company_data.get('company_name', 'Unknown'),
        "raw_data": company_data,
        "ai_analysis": analysis,
        "scraped_at": datetime.now().isoformat()
    }


@mcp.tool()
async def compare_companies(
    user_company_url: str,
    target_company_url: str
) -> dict:
    """
    Scrape and compare two companies for sales preparation

    Args:
        user_company_url: Your company's website URL
        target_company_url: Target prospect's website URL

    Returns:
        Analysis of both companies plus positioning strategy
    """
    await initialize()

    logger.info(f"Comparing companies: {user_company_url} vs {target_company_url}")

    # Scrape both in parallel
    results = await asyncio.gather(
        analyze_company_for_sales(user_company_url),
        analyze_company_for_sales(target_company_url),
        return_exceptions=True
    )

    user_company = results[0] if not isinstance(results[0], Exception) else {
        "success": False, "error": str(results[0])
    }
    target_company = results[1] if not isinstance(results[1], Exception) else {
        "success": False, "error": str(results[1])
    }

    # Generate comparison and positioning
    if user_company.get("success") and target_company.get("success"):
        comparison_prompt = f"""
Compare these two companies and provide sales positioning strategy:

YOUR COMPANY ({user_company['company_name']}):
{user_company['ai_analysis']}

TARGET COMPANY ({target_company['company_name']}):
{target_company['ai_analysis']}

Provide:
1. **Competitive Positioning:** Where does your company stand?
2. **Key Differentiators:** What makes your company unique?
3. **Positioning Strategy:** How should the sales rep position your solution?
4. **Common Ground:** What do both companies have in common to build rapport?
5. **Objection Handling:** Potential objections and how to address them
"""

        positioning = await ai_client.simple_prompt(
            prompt=comparison_prompt,
            system="You are a sales strategist creating competitive positioning.",
            max_tokens=1500
        )
    else:
        positioning = "Unable to generate positioning due to scraping errors."

    return {
        "success": True,
        "user_company": user_company,
        "target_company": target_company,
        "positioning_strategy": positioning,
        "compared_at": datetime.now().isoformat()
    }


@mcp.tool()
async def extract_with_instruction(
    url: str,
    instruction: str
) -> dict:
    """
    Extract specific information using natural language instructions

    Args:
        url: Website URL to scrape
        instruction: Natural language extraction instruction

    Examples:
        - "List all products with their pricing"
        - "Find the names and titles of executives"
        - "Extract recent news or press releases"
        - "What are their customer testimonials?"

    Returns:
        Extracted information as structured data
    """
    await initialize()

    logger.info(f"Smart extraction from {url}: {instruction}")

    # Scrape page
    page_data = await scraper.scrape_url(url)

    if page_data.get("error"):
        return {"success": False, "error": page_data["error"]}

    # Extract with AI
    content = page_data.get("content", {})
    text = content.get("text", "")[:8000]  # Limit to 8k chars

    extraction_prompt = f"""
Extract information from this webpage based on the instruction.

Instruction: {instruction}

Webpage URL: {url}
Webpage Title: {page_data.get('title', 'Unknown')}

Webpage Content:
{text}

Extract the requested information and return it as structured JSON.
If the information is not found, return {{"found": false, "message": "Information not available"}}.
"""

    result = await ai_client.simple_prompt(
        prompt=extraction_prompt,
        system="You extract structured data from webpages based on natural language instructions.",
        max_tokens=1500
    )

    # Try to parse as JSON
    try:
        extracted_data = json.loads(result)
    except:
        extracted_data = {"raw_text": result}

    return {
        "success": True,
        "url": url,
        "instruction": instruction,
        "extracted_data": extracted_data,
        "extracted_at": datetime.now().isoformat()
    }


@mcp.tool()
async def crawl_website_adaptive(
    seed_url: str,
    max_pages: int = 5,
    target_words: int = 5000
) -> dict:
    """
    Adaptively crawl multiple pages from a website
    Stops when enough content is gathered or max_pages reached

    Args:
        seed_url: Starting URL
        max_pages: Maximum pages to crawl (default: 5)
        target_words: Stop when this many words collected (default: 5000)

    Returns:
        Aggregated content from multiple pages with AI summary
    """
    await initialize()

    logger.info(f"Adaptive crawl starting: {seed_url} (max {max_pages} pages, target {target_words} words)")

    pages = []
    queue = [seed_url]
    visited = set()
    total_words = 0

    while queue and len(pages) < max_pages and total_words < target_words:
        url = queue.pop(0)

        if url in visited:
            continue

        visited.add(url)

        try:
            # Scrape page
            page_data = await scraper.scrape_url(url)

            if page_data.get("error"):
                logger.warning(f"Failed to scrape {url}: {page_data['error']}")
                continue

            content = page_data.get("content", {})
            word_count = content.get("word_count", 0)

            pages.append({
                "url": url,
                "title": page_data.get("title", ""),
                "word_count": word_count,
                "headings": content.get("headings", [])[:5],
                "text_preview": content.get("text", "")[:500]
            })

            total_words += word_count
            logger.info(f"Crawled {url} ({word_count} words, total: {total_words})")

            # Check if we have enough content
            if total_words >= target_words:
                logger.info(f"Target word count reached: {total_words} >= {target_words}")
                break

            # Add internal links to queue
            links = page_data.get("links", [])
            internal_links = [
                link["url"] for link in links
                if link.get("is_internal") and link["url"] not in visited
            ][:3]  # Only top 3 internal links

            queue.extend(internal_links)

        except Exception as e:
            logger.error(f"Error crawling {url}: {e}")
            continue

    # Generate summary of all crawled content
    crawl_summary = f"""
Crawled {len(pages)} pages from {seed_url}
Total words: {total_words}

Pages:
{chr(10).join([f"- {p['title']} ({p['word_count']} words)" for p in pages])}
"""

    summary_prompt = f"""
Summarize the key information from this website crawl:

{crawl_summary}

Provide:
1. **Main Topics:** What does this website cover?
2. **Key Sections:** What are the main areas/pages?
3. **Notable Information:** Any standout details or insights
"""

    ai_summary = await ai_client.simple_prompt(
        prompt=summary_prompt,
        system="You summarize website content.",
        max_tokens=800
    )

    return {
        "success": True,
        "seed_url": seed_url,
        "pages_crawled": len(pages),
        "total_words": total_words,
        "pages": pages,
        "ai_summary": ai_summary,
        "crawled_at": datetime.now().isoformat()
    }


@mcp.tool()
async def search_knowledge_base(query: str, top_k: int = 3) -> dict:
    """
    Search previously scraped companies in the local vector database

    Args:
        query: Search query (e.g., "companies that sell SaaS products")
        top_k: Number of results to return (default: 3)

    Returns:
        Relevant company information from ChromaDB
    """
    await initialize()

    logger.info(f"Searching knowledge base: {query}")

    try:
        results = collection.query(
            query_texts=[query],
            n_results=top_k
        )

        companies = []
        for i, doc in enumerate(results["documents"][0]):
            metadata = results["metadatas"][0][i]
            distance = results["distances"][0][i] if "distances" in results else None

            companies.append({
                "company_name": metadata.get("company_name", "Unknown"),
                "url": metadata.get("url", ""),
                "scraped_at": metadata.get("scraped_at", ""),
                "summary": doc[:500],  # First 500 chars
                "relevance_score": 1 - distance if distance else None
            })

        return {
            "success": True,
            "query": query,
            "results_found": len(companies),
            "companies": companies
        }

    except Exception as e:
        logger.error(f"Search failed: {e}")
        return {
            "success": False,
            "error": str(e),
            "message": "No companies in knowledge base yet. Scrape some companies first!"
        }


def start_server():
    """Start the FastMCP server"""
    logger.info("Starting Company Intelligence MCP Server...")
    mcp.run()


if __name__ == "__main__":
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

    start_server()
