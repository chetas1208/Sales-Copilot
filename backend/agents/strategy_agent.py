"""
Strategy Agent
Synthesizes all insights into actionable sales strategy
"""

import logging
from typing import Dict, Any

logger = logging.getLogger(__name__)


class StrategyAgent:
    """AI agent for synthesizing insights into sales strategy"""

    def __init__(self, claude_client):
        """Initialize strategy agent"""
        self.claude_client = claude_client

        self.system_prompt = """You are a senior sales strategist. Your job is to synthesize multiple sources of intelligence into a clear, actionable sales strategy.

You'll receive:
- Company research (what they do, products, value prop)
- Social intelligence (LinkedIn, team info)
- Review analysis (customer complaints, competitor weaknesses)
- Conversation context (if available)

Your output should be a concise battle card that includes:
1. **Quick Summary:** 2-3 sentences on who they are
2. **Key Talking Points:** 3-5 bullet points for the sales rep
3. **Objection Handlers:** Anticipated objections and responses
4. **Discovery Questions:** Smart questions to ask
5. **Next Steps:** Recommended follow-up actions

Make it scannable and immediately actionable during a live sales call."""

        logger.info("Strategy agent initialized")

    async def synthesize(self, all_insights: Dict[str, Any]) -> Dict[str, Any]:
        """
        Synthesize all agent insights into sales strategy

        Args:
            all_insights: Dict containing results from all other agents

        Returns:
            Dict with strategic recommendations
        """
        logger.info(f"Strategy agent synthesizing {len(all_insights)} insight sources")

        try:
            # Extract insights from each agent
            research = all_insights.get("research_company", {})
            social = all_insights.get("social_intelligence", {})
            reviews = all_insights.get("review_analysis", {})
            competitors = [v for k, v in all_insights.items() if k.startswith("research_competitor")]

            # Build comprehensive context
            context = self._build_context(research, social, reviews, competitors)

            # Ask Claude to synthesize
            user_prompt = f"""Synthesize these sales intelligence sources into a battle card:

{context}

Create a concise, actionable sales battle card following the format specified in your system prompt."""

            strategy = await self.claude_client.simple_prompt(
                prompt=user_prompt,
                system=self.system_prompt,
                max_tokens=2000
            )

            return {
                "success": True,
                "summary": strategy,
                "sources_synthesized": len(all_insights),
                "insights": {
                    "research_available": bool(research),
                    "social_available": bool(social),
                    "reviews_available": bool(reviews),
                    "competitors_analyzed": len(competitors)
                }
            }

        except Exception as e:
            logger.error(f"Strategy synthesis error: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }

    def _build_context(
        self,
        research: Dict[str, Any],
        social: Dict[str, Any],
        reviews: Dict[str, Any],
        competitors: list[Dict[str, Any]]
    ) -> str:
        """Build context string from all insights"""
        parts = []

        # Research insights
        if research and research.get("success"):
            parts.append(f"**COMPANY RESEARCH:**\n{research.get('summary', 'No data')}")

        # Social intelligence
        if social and social.get("success"):
            parts.append(f"\n**SOCIAL INTELLIGENCE:**\n{social.get('summary', 'No data')}")

        # Review analysis
        if reviews and reviews.get("success"):
            parts.append(f"\n**CUSTOMER REVIEWS & SENTIMENT:**\n{reviews.get('summary', 'No data')}")

        # Competitors
        if competitors:
            comp_text = "\n".join([
                f"- {comp.get('company_name', 'Unknown')}: {comp.get('summary', 'No data')[:200]}"
                for comp in competitors if comp.get("success")
            ])
            if comp_text:
                parts.append(f"\n**COMPETITORS:**\n{comp_text}")

        return "\n\n".join(parts) if parts else "No insights available yet."
