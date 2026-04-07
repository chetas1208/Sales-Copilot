"""
Conversation Agent
Analyzes real-time meeting transcripts to detect questions, objections, and opportunities
"""

import logging
from typing import Dict, Any, List, Optional

logger = logging.getLogger(__name__)


class ConversationAgent:
    """AI agent for analyzing real-time conversation transcripts"""

    def __init__(self, claude_client):
        """Initialize conversation agent"""
        self.claude_client = claude_client

        self.system_prompt = """You are a real-time sales conversation analyst. Your job is to listen to meeting transcripts and identify:

1. **Questions** from the prospect that need answering
2. **Objections** or concerns raised
3. **Buying signals** or positive indicators
4. **Topics** being discussed
5. **Recommended responses** for the sales rep

Be concise and actionable. Only flag important moments that require sales rep action or awareness.

If nothing significant is detected, respond with: {"action_required": false}"""

        logger.info("Conversation agent initialized")

    async def analyze_transcript(
        self,
        transcript: str,
        speaker: str,
        context: Optional[List[Dict[str, Any]]] = None,
        company_research: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Analyze a transcript snippet in real-time with company context

        Args:
            transcript: Latest transcript text
            speaker: Who said it
            context: Previous conversation context
            company_research: Research data from web crawler (YOUR company + TARGET company)

        Returns:
            Dict with analysis and suggestions
        """
        logger.debug(f"Analyzing transcript from {speaker}: {transcript[:50]}...")

        try:
            # Build context window (last 5 messages)
            context_text = ""
            if context:
                recent_context = context[-5:]
                context_text = "\n".join([
                    f"{msg['speaker']}: {msg['text']}"
                    for msg in recent_context[:-1]  # Exclude current message
                ])

            # Build company research context
            research_context = ""
            if company_research:
                my_company = company_research.get("my_company", {})
                target_company = company_research.get("target_company", {})

                research_context = f"""
**YOUR COMPANY (Jeet's company):**
{my_company.get('company_name', 'Unknown')}: {my_company.get('summary', 'No data')[:300]}...

**TARGET COMPANY (Chetas's company):**
{target_company.get('company_name', 'Unknown')}: {target_company.get('summary', 'No data')[:300]}...

**PRODUCT-NEED MATCHING:**
{company_research.get('matching_insights', 'No matching data available')[:400]}...
"""

            # Analyze current statement
            user_prompt = f"""You are helping Jeet (the sales rep) respond to Chetas (the prospect) in REAL-TIME.

{research_context if research_context else "[No company research data available]"}

**Previous Conversation:**
{context_text if context_text else "[No previous context]"}

**Current Statement:**
{speaker}: {transcript}

🎯 **Your Task:**
If Chetas (prospect) said something, suggest what Jeet (sales rep) should say next based on:
1. What Chetas just said
2. YOUR company's products that can help
3. TARGET company's needs and pain points

If Jeet (sales rep) is speaking, analyze if he's on the right track.

Provide ACTIONABLE, SPECIFIC suggestions using the company research context above.

Respond in JSON format:
{{
    "action_required": true/false,
    "type": "question/objection/opportunity/concern/response_needed",
    "summary": "One-sentence summary of what was said",
    "suggestion": "SPECIFIC suggestion for Jeet based on research context",
    "priority": "low/normal/high/critical",
    "title": "Title for the suggestion card"
}}

If Chetas asked a question or expressed concern, suggestion should reference YOUR products.
If nothing important, return: {{"action_required": false}}"""

            # Call Claude
            response = await self.claude_client.simple_prompt(
                prompt=user_prompt,
                system=self.system_prompt,
                max_tokens=500
            )

            # Parse response (simple approach - in production, use structured output)
            try:
                import json
                # Extract JSON from response (it might be wrapped in markdown)
                response_clean = response.strip()
                if response_clean.startswith("```"):
                    # Remove markdown code blocks
                    lines = response_clean.split("\n")
                    response_clean = "\n".join([l for l in lines if not l.startswith("```")])

                result = json.loads(response_clean)

                # Add metadata
                result["speaker"] = speaker
                result["transcript"] = transcript

                return result

            except json.JSONDecodeError:
                # Fallback if JSON parsing fails
                logger.warning("Failed to parse JSON response, returning raw text")
                return {
                    "action_required": True,
                    "type": "analysis",
                    "summary": response[:200],
                    "suggestion": response,
                    "priority": "normal",
                    "title": f"Analysis of {speaker}'s statement",
                    "speaker": speaker,
                    "transcript": transcript
                }

        except Exception as e:
            logger.error(f"Conversation agent error: {str(e)}")
            return {
                "action_required": False,
                "error": str(e)
            }

    async def detect_objection(self, transcript: str) -> Dict[str, Any]:
        """
        Specifically detect if a statement is an objection

        Args:
            transcript: Transcript text to analyze

        Returns:
            Dict with objection detection results
        """
        user_prompt = f"""Is this statement an objection or concern?

Statement: "{transcript}"

If yes, provide:
- Objection category (price, timing, competition, fit, authority, need)
- Severity (low/medium/high)
- Recommended response

Return JSON format."""

        try:
            response = await self.claude_client.simple_prompt(
                prompt=user_prompt,
                system="You are an expert at detecting sales objections.",
                max_tokens=300
            )

            return {"objection_detected": True, "analysis": response}

        except Exception as e:
            logger.error(f"Objection detection error: {str(e)}")
            return {"objection_detected": False, "error": str(e)}

    async def summarize_conversation(self, context: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Summarize entire conversation so far

        Args:
            context: Full conversation history

        Returns:
            Dict with summary
        """
        logger.info(f"Summarizing conversation ({len(context)} messages)")

        try:
            # Build full context
            conversation_text = "\n".join([
                f"{msg['speaker']}: {msg['text']}"
                for msg in context
            ])

            user_prompt = f"""Summarize this sales call conversation:

{conversation_text}

Provide:
1. **Key Topics Discussed**
2. **Prospect's Main Concerns**
3. **Buying Signals / Interest Level**
4. **Recommended Next Steps**

Keep it concise."""

            summary = await self.claude_client.simple_prompt(
                prompt=user_prompt,
                system=self.system_prompt,
                max_tokens=800
            )

            return {
                "success": True,
                "summary": summary,
                "message_count": len(context)
            }

        except Exception as e:
            logger.error(f"Conversation summary error: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }
