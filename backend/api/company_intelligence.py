"""
API endpoints for enhanced company intelligence with MCP server
"""

from fastapi import APIRouter, HTTPException
from typing import Dict, Any, Optional
import logging

router = APIRouter(prefix="/api/intelligence", tags=["Company Intelligence"])
logger = logging.getLogger(__name__)

# Import MCP server tools
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from mcp_servers.company_intelligence_mcp.server import (
    scrape_company,
    analyze_company_for_sales,
    compare_companies,
    extract_with_instruction,
    crawl_website_adaptive,
    search_knowledge_base
)


@router.post("/scrape")
async def scrape_company_endpoint(request: Dict[str, Any]):
    """
    Scrape company website and extract basic information

    Body:
        url: Company website URL
        use_cache: Use cached results (optional, default: true)
    """
    url = request.get("url")
    if not url:
        raise HTTPException(status_code=400, detail="url is required")

    use_cache = request.get("use_cache", True)

    try:
        result = await scrape_company(url, use_cache)
        return result
    except Exception as e:
        logger.error(f"Scraping failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/analyze")
async def analyze_company_endpoint(request: Dict[str, Any]):
    """
    Scrape company and generate AI-powered sales intelligence

    Body:
        url: Company website URL
    """
    url = request.get("url")
    if not url:
        raise HTTPException(status_code=400, detail="url is required")

    try:
        result = await analyze_company_for_sales(url)
        return result
    except Exception as e:
        logger.error(f"Analysis failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/compare")
async def compare_companies_endpoint(request: Dict[str, Any]):
    """
    Compare two companies for sales preparation

    Body:
        user_company_url: Your company's website URL
        target_company_url: Target prospect's website URL
    """
    user_company_url = request.get("user_company_url")
    target_company_url = request.get("target_company_url")

    if not user_company_url or not target_company_url:
        raise HTTPException(
            status_code=400,
            detail="Both user_company_url and target_company_url are required"
        )

    try:
        result = await compare_companies(user_company_url, target_company_url)
        return result
    except Exception as e:
        logger.error(f"Comparison failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/extract")
async def extract_with_instruction_endpoint(request: Dict[str, Any]):
    """
    Extract specific information using natural language

    Body:
        url: Website URL
        instruction: Natural language instruction

    Examples:
        {"url": "https://acme.com", "instruction": "List all products with pricing"}
        {"url": "https://acme.com", "instruction": "Find executive names and titles"}
    """
    url = request.get("url")
    instruction = request.get("instruction")

    if not url or not instruction:
        raise HTTPException(
            status_code=400,
            detail="Both url and instruction are required"
        )

    try:
        result = await extract_with_instruction(url, instruction)
        return result
    except Exception as e:
        logger.error(f"Extraction failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/crawl")
async def crawl_website_endpoint(request: Dict[str, Any]):
    """
    Adaptively crawl multiple pages from a website

    Body:
        seed_url: Starting URL
        max_pages: Maximum pages to crawl (optional, default: 5)
        target_words: Stop when this many words collected (optional, default: 5000)
    """
    seed_url = request.get("seed_url")
    if not seed_url:
        raise HTTPException(status_code=400, detail="seed_url is required")

    max_pages = request.get("max_pages", 5)
    target_words = request.get("target_words", 5000)

    try:
        result = await crawl_website_adaptive(seed_url, max_pages, target_words)
        return result
    except Exception as e:
        logger.error(f"Crawling failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/search")
async def search_knowledge_base_endpoint(request: Dict[str, Any]):
    """
    Search previously scraped companies in local vector database

    Body:
        query: Search query
        top_k: Number of results (optional, default: 3)

    Example:
        {"query": "companies that sell SaaS products", "top_k": 5}
    """
    query = request.get("query")
    if not query:
        raise HTTPException(status_code=400, detail="query is required")

    top_k = request.get("top_k", 3)

    try:
        result = await search_knowledge_base(query, top_k)
        return result
    except Exception as e:
        logger.error(f"Search failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))
