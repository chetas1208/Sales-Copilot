"""
Review Analysis Agent
Analyzes customer reviews from G2, Capterra, Reddit, etc.
"""

import logging
from typing import Dict, Any
from mcp_servers.web_scraper_mcp.server import get_web_scraper

logger = logging.getLogger(__name__)


class ReviewAnalysisAgent:
    """AI agent for analyzing customer reviews and complaints"""

    def __init__(self, claude_client):
        """Initialize review analysis agent"""
        self.claude_client = claude_client
        self.web_scraper = None

        self.system_prompt = """You are a customer sentiment analyst specializing in competitive intelligence from reviews.

Your goal is to analyze customer reviews to find:
1. **Common Complaints:** What frustrates their customers?
2. **Unmet Needs:** What are customers asking for?
3. **Competitor Weaknesses:** Where do they fall short?
4. **Positioning Opportunities:** How can our product address their pain points?

Focus on actionable insights that help sales reps position against competitors."""

        logger.info("Review analysis agent initialized")

    async def analyze_reviews(self, company_url: str) -> Dict[str, Any]:
        """
        Analyze customer reviews for a company

        Args:
            company_url: Company website URL

        Returns:
            Dict with review analysis
        """
        logger.info(f"Review analysis agent analyzing: {company_url}")

        try:
            # Extract company name
            if not self.web_scraper:
                self.web_scraper = await get_web_scraper()

            company_data = await self.web_scraper.scrape_url(company_url)
            company_name = company_data.get("title", "Unknown Company").split("-")[0].strip()

            # Search for reviews (in production, use review site APIs or scraping)
            # For MVP, we'll generate placeholder insights
            review_sources = [
                f"https://www.g2.com/search?utf8=%E2%9C%93&query={company_name}",
                f"https://www.capterra.com/software/{company_name.lower()}",
                f"https://www.reddit.com/search/?q={company_name}+review"
            ]

            analysis = await self._analyze_sentiment(company_name, review_sources)

            return {
                "success": True,
                "company_name": company_name,
                "company_url": company_url,
                "summary": analysis,
                "review_sources": review_sources,
                "note": "Review scraping requires API access or advanced scraping - placeholder analysis shown"
            }

        except Exception as e:
            logger.error(f"Review analysis error for {company_url}: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "company_url": company_url
            }

    async def _analyze_sentiment(
        self,
        company_name: str,
        review_sources: list[str]
    ) -> str:
        """Analyze sentiment from reviews"""

        prompt = f"""Provide a sales intelligence briefing on customer sentiment for: {company_name}

Since we don't have live review data yet, provide a framework for analyzing reviews:

**Where to Check:**
- G2: {review_sources[0]}
- Capterra: {review_sources[1]}
- Reddit: {review_sources[2]}

**What to Look For:**
1. **Most Common Complaints:** (3-5 patterns)
2. **Feature Gaps:** What do customers wish it had?
3. **Support/Service Issues:** Any red flags?
4. **Pricing Concerns:** Is it too expensive/cheap?
5. **Competitive Comparison:** What are customers switching from/to?

**Sales Action Items:**
- How to position against their weaknesses
- Questions to ask prospects about their experience
- Talking points if prospect uses this competitor

Provide this as a template analysis with placeholder insights."""

        try:
            analysis = await self.claude_client.simple_prompt(
                prompt=prompt,
                system=self.system_prompt,
                max_tokens=1200
            )
            return analysis

        except Exception as e:
            return f"Error analyzing reviews: {str(e)}"
