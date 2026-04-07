"""
Research Agent
Analyzes company websites and extracts key business information
"""

import logging
from typing import Dict, Any, Optional
from mcp_servers.web_scraper_mcp.server import get_web_scraper

logger = logging.getLogger(__name__)


class ResearchAgent:
    """AI agent for researching companies via web scraping"""

    def __init__(self, ai_client):
        """
        Initialize research agent

        Args:
            ai_client: AI API client instance (Claude or OpenAI)
        """
        self.ai_client = ai_client
        self.web_scraper = None

        self.system_prompt = """You are a sales research analyst specializing in quickly understanding companies from their websites.

Your goal is to analyze a company's website and extract key information that would be valuable for a sales professional about to have a conversation with them.

Focus on:
1. What does the company do? (products/services)
2. Who are their customers? (target market)
3. What are their main value propositions?
4. What problems do they solve?
5. What are their key differentiators?
6. Any recent news, funding, or significant developments?

Provide a concise, actionable summary that a salesperson can quickly scan before or during a call."""

        logger.info("Research agent initialized")

    async def analyze_website(self, url: str) -> Dict[str, Any]:
        """
        Analyze a company website and extract sales intelligence

        Args:
            url: Company website URL

        Returns:
            Dict with research findings
        """
        logger.info(f"Research agent analyzing: {url}")

        try:
            # Get web scraper instance
            if not self.web_scraper:
                self.web_scraper = await get_web_scraper()

            # Scrape the website
            scraped_data = await self.web_scraper.extract_company_info(url)

            if scraped_data.get("error"):
                return {
                    "success": False,
                    "error": scraped_data["error"],
                    "url": url
                }

            # Prepare context for Claude
            context_text = self._prepare_context(scraped_data)

            # Ask Claude to analyze
            user_prompt = f"""Analyze this company website data and provide a concise sales intelligence briefing:

Company Website: {url}
Company Name: {scraped_data.get('company_name', 'Unknown')}

--- Website Content ---
{context_text}
--- End Content ---

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

Keep it concise and actionable. Focus on what's most relevant for a sales conversation."""

            # Call AI client (Claude or OpenAI)
            analysis = await self.ai_client.simple_prompt(
                prompt=user_prompt,
                system=self.system_prompt,
                max_tokens=2000
            )

            # Structure the response
            result = {
                "success": True,
                "url": url,
                "company_name": scraped_data.get("company_name", "Unknown"),
                "summary": analysis,
                "raw_data": {
                    "description": scraped_data.get("description", ""),
                    "products": scraped_data.get("products", []),
                    "contact_info": scraped_data.get("contact_info", {}),
                },
                "metadata": scraped_data.get("metadata", {})
            }

            logger.info(f"Research agent completed analysis of {url}")

            return result

        except Exception as e:
            logger.error(f"Research agent error for {url}: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "url": url
            }

    def _prepare_context(self, scraped_data: Dict[str, Any]) -> str:
        """Prepare scraped data as context for Claude"""
        parts = []

        # Title
        if scraped_data.get("title"):
            parts.append(f"Page Title: {scraped_data['title']}")

        # Description
        if scraped_data.get("description"):
            parts.append(f"Description: {scraped_data['description']}")

        # Headings
        if scraped_data.get("headings"):
            headings_text = "\n".join([
                f"- {h.get('text', '')}"
                for h in scraped_data["headings"][:10]
            ])
            parts.append(f"Main Headings:\n{headings_text}")

        # About section
        if scraped_data.get("about_text"):
            parts.append(f"About Section: {scraped_data['about_text'][:500]}")

        # Products
        if scraped_data.get("products"):
            products_text = "\n".join([f"- {p}" for p in scraped_data["products"]])
            parts.append(f"Products/Services:\n{products_text}")

        # Contact info
        if scraped_data.get("contact_info"):
            contact = scraped_data["contact_info"]
            if contact:
                parts.append(f"Contact Info: {contact}")

        return "\n\n".join(parts)

    async def compare_competitors(
        self,
        company_url: str,
        competitor_urls: list[str]
    ) -> Dict[str, Any]:
        """
        Compare a company against competitors

        Args:
            company_url: Target company URL
            competitor_urls: List of competitor URLs

        Returns:
            Comparative analysis
        """
        logger.info(f"Comparing {company_url} against {len(competitor_urls)} competitors")

        try:
            # Analyze target company
            company_analysis = await self.analyze_website(company_url)

            # Analyze competitors
            competitor_analyses = []
            for comp_url in competitor_urls:
                comp_analysis = await self.analyze_website(comp_url)
                competitor_analyses.append(comp_analysis)

            # Ask Claude to compare
            comparison_prompt = f"""Compare this target company against its competitors and identify key differentiators and competitive advantages:

**TARGET COMPANY:**
{company_analysis.get('summary', 'No data')}

**COMPETITORS:**
{chr(10).join([f"{i+1}. {comp.get('company_name', 'Unknown')}: {comp.get('summary', 'No data')[:300]}" for i, comp in enumerate(competitor_analyses)])}

Provide:
1. **Competitive Positioning:** Where does the target company stand?
2. **Unique Differentiators:** What makes them different?
3. **Competitive Weaknesses:** Where might competitors have an edge?
4. **Sales Strategy:** How should the sales rep position against these competitors?

Keep it concise and actionable."""

            comparison = await self.ai_client.simple_prompt(
                prompt=comparison_prompt,
                system=self.system_prompt,
                max_tokens=1500
            )

            return {
                "success": True,
                "company": company_analysis,
                "competitors": competitor_analyses,
                "comparison": comparison
            }

        except Exception as e:
            logger.error(f"Competitor comparison error: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }
