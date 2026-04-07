"""
Knowledge Gap Detection Agent
Monitors conversations to detect when prospects ask about products/services not in the knowledge base.
Triggers Slack alerts to PM group for critical unknowns.
"""

import logging
from typing import Dict, Any, List, Optional
import json

logger = logging.getLogger(__name__)


class KnowledgeGapAgent:
    """AI agent for detecting knowledge gaps and triggering PM support"""

    def __init__(self, openai_client, knowledge_base_service=None):
        """
        Initialize knowledge gap agent

        Args:
            openai_client: OpenAI client for AI analysis
            knowledge_base_service: Service to search company knowledge base (e.g., ChromaDB)
        """
        self.openai_client = openai_client
        self.knowledge_base = knowledge_base_service

        self.system_prompt = """You are a knowledge gap detection specialist for sales conversations.

Your job is to:
1. Identify when a prospect asks about products, services, features, or capabilities
2. Assess if this is something the sales rep should know about their own company
3. Determine the criticality and urgency of getting an answer
4. Detect buying signals that make this question time-sensitive

CRITICAL UNKNOWNS (require immediate Slack alert):
- Questions with high buying intent ("Can you do X? We need it for our deal")
- Feature inquiries during pricing/contracting discussions
- Technical capability questions that are deal-blockers
- Competitive comparison questions during evaluation

NON-CRITICAL (no alert needed):
- General curiosity questions with no buying intent
- Questions the sales rep can handle with existing knowledge
- Off-topic or casual questions
- Questions already answered in the conversation

Output JSON format:
{
    "is_product_question": true/false,
    "is_knowledge_gap": true/false,
    "criticality": "none/low/moderate/high/critical",
    "urgency_score": 0-10,
    "question_category": "feature/pricing/integration/capability/other",
    "has_buying_intent": true/false,
    "exact_question": "verbatim prospect question",
    "context_summary": "brief meeting context",
    "suggested_answer": "best-guess answer from general knowledge",
    "why_critical": "explanation of why this needs PM attention",
    "recommended_action": "wait/notify_pm/escalate_urgent"
}"""

        logger.info("Knowledge Gap Detection Agent initialized")

    async def analyze_for_knowledge_gap(
        self,
        transcript: str,
        speaker: str,
        company_info: Optional[Dict[str, Any]] = None,
        conversation_context: Optional[List[Dict[str, Any]]] = None
    ) -> Dict[str, Any]:
        """
        Analyze transcript to detect knowledge gaps

        Args:
            transcript: Latest transcript text
            speaker: Who said it (should be prospect/customer)
            company_info: Known information about the sales rep's company
            conversation_context: Previous conversation messages

        Returns:
            Dict with knowledge gap analysis and recommended actions
        """
        logger.debug(f"Analyzing for knowledge gaps: {speaker}: {transcript[:100]}...")

        # Only analyze prospect/customer questions, not sales rep statements
        if speaker.lower() in ['you', 'sales rep', 'rep', 'agent']:
            logger.debug("Skipping - this is from the sales rep, not prospect")
            return {
                "is_product_question": False,
                "is_knowledge_gap": False,
                "criticality": "none",
                "recommended_action": "wait"
            }

        try:
            # Step 1: Check if we have this information in the knowledge base
            knowledge_available = False
            if self.knowledge_base and company_info:
                # Search vector database for relevant information
                knowledge_available = await self._check_knowledge_base(
                    transcript,
                    company_info
                )

            # Step 2: Build conversation context
            context_text = self._build_context(conversation_context)

            # Step 3: Build company knowledge context
            company_context = "No company information available"
            if company_info:
                company_context = f"""
Company Name: {company_info.get('company_name', 'Unknown')}
Products/Services: {company_info.get('products', 'Unknown')}
Key Features: {company_info.get('features', 'Unknown')}
"""

            # Step 4: Analyze with AI
            user_prompt = f"""Analyze this sales conversation for knowledge gaps:

**Sales Rep's Company Information:**
{company_context}

**Conversation History:**
{context_text}

**Latest Statement from Prospect:**
{speaker}: {transcript}

**Knowledge Base Status:** {"Information found in knowledge base" if knowledge_available else "Information NOT found in knowledge base"}

Determine:
1. Is this a question about the sales rep's company/product?
2. If yes, is it something the sales rep should be able to answer from their knowledge?
3. If it's a knowledge gap, how critical is it to get an answer RIGHT NOW?
4. Does the prospect show buying intent that makes this time-sensitive?

Output ONLY valid JSON (no markdown, no code blocks):"""

            # Call OpenAI
            response = await self.openai_client.simple_prompt(
                prompt=user_prompt,
                system=self.system_prompt,
                max_tokens=600
            )

            # Parse JSON response
            result = self._parse_json_response(response)

            # Add metadata
            result['transcript'] = transcript
            result['speaker'] = speaker
            result['knowledge_base_hit'] = knowledge_available
            result['timestamp'] = self._get_timestamp()

            # Log critical gaps
            if result.get('criticality') in ['high', 'critical']:
                logger.warning(
                    f"CRITICAL KNOWLEDGE GAP DETECTED: {result.get('exact_question')}"
                    f" | Urgency: {result.get('urgency_score')}/10"
                )

            return result

        except Exception as e:
            logger.error(f"Error analyzing knowledge gap: {str(e)}", exc_info=True)
            return {
                "is_product_question": False,
                "is_knowledge_gap": False,
                "criticality": "none",
                "recommended_action": "wait",
                "error": str(e)
            }

    async def _check_knowledge_base(
        self,
        query: str,
        company_info: Dict[str, Any]
    ) -> bool:
        """
        Check if we have relevant information in the knowledge base

        Args:
            query: The question/query to search for
            company_info: Company information context

        Returns:
            True if relevant information found, False otherwise
        """
        try:
            if not self.knowledge_base:
                return False

            # Search vector database
            results = await self.knowledge_base.search(
                query=query,
                filters={"company": company_info.get('company_name')},
                top_k=3
            )

            # Consider knowledge available if we have high-confidence matches
            if results and len(results) > 0:
                top_score = results[0].get('score', 0)
                if top_score > 0.7:  # High similarity threshold
                    logger.debug(f"Knowledge base hit: {results[0].get('text')[:100]}")
                    return True

            return False

        except Exception as e:
            logger.error(f"Error checking knowledge base: {str(e)}")
            return False

    def _build_context(self, conversation_context: Optional[List[Dict[str, Any]]]) -> str:
        """Build conversation context from previous messages"""
        if not conversation_context:
            return "[Start of conversation]"

        # Get last 8 messages for context
        recent = conversation_context[-8:]
        context_lines = []

        for msg in recent:
            speaker = msg.get('speaker', 'Unknown')
            text = msg.get('text', '')
            context_lines.append(f"{speaker}: {text}")

        return "\n".join(context_lines)

    def _parse_json_response(self, response: str) -> Dict[str, Any]:
        """Parse JSON from AI response, handling markdown code blocks"""
        try:
            # Remove markdown code blocks if present
            response_clean = response.strip()
            if response_clean.startswith('```'):
                # Extract content between ```json and ```
                lines = response_clean.split('\n')
                json_lines = []
                in_code_block = False

                for line in lines:
                    if line.startswith('```'):
                        in_code_block = not in_code_block
                        continue
                    if in_code_block:
                        json_lines.append(line)

                response_clean = '\n'.join(json_lines)

            # Parse JSON
            result = json.loads(response_clean)
            return result

        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse JSON response: {response[:200]}")
            # Return default safe response
            return {
                "is_product_question": False,
                "is_knowledge_gap": False,
                "criticality": "none",
                "recommended_action": "wait",
                "error": "JSON parse error"
            }

    def _get_timestamp(self) -> str:
        """Get current timestamp in ISO format"""
        from datetime import datetime
        return datetime.utcnow().isoformat() + "Z"

    def should_notify_pm(self, analysis: Dict[str, Any]) -> bool:
        """
        Determine if PM should be notified based on analysis

        Args:
            analysis: Knowledge gap analysis result

        Returns:
            True if PM notification should be sent
        """
        # Only notify for critical unknowns
        criticality = analysis.get('criticality', 'none')
        urgency = analysis.get('urgency_score', 0)
        action = analysis.get('recommended_action', 'wait')

        # Critical cases that need PM attention
        if criticality in ['high', 'critical']:
            return True

        if urgency >= 7:  # High urgency score
            return True

        if action in ['notify_pm', 'escalate_urgent']:
            return True

        return False

    def format_slack_message(
        self,
        analysis: Dict[str, Any],
        meeting_context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Format knowledge gap analysis into Slack message payload

        Args:
            analysis: Knowledge gap analysis result
            meeting_context: Additional meeting metadata

        Returns:
            Dict formatted for Slack API
        """
        # Extract key information
        question = analysis.get('exact_question', 'Unknown question')
        category = analysis.get('question_category', 'general')
        urgency = analysis.get('urgency_score', 5)
        suggested_answer = analysis.get('suggested_answer', 'No suggestion available')
        why_critical = analysis.get('why_critical', 'Prospect needs answer')

        # Urgency emoji
        urgency_emoji = "🔴" if urgency >= 8 else "🟡" if urgency >= 5 else "🟢"

        # Meeting context
        company_name = meeting_context.get('company_name', 'Unknown Company') if meeting_context else 'Unknown Company'
        attendees = meeting_context.get('attendees', []) if meeting_context else []
        meeting_url = meeting_context.get('meeting_url', '') if meeting_context else ''

        # Build Slack message with blocks
        message = {
            "text": f"{urgency_emoji} Knowledge Gap Alert: {category.upper()} question from {company_name}",
            "blocks": [
                {
                    "type": "header",
                    "text": {
                        "type": "plain_text",
                        "text": f"{urgency_emoji} Knowledge Gap Detected"
                    }
                },
                {
                    "type": "section",
                    "fields": [
                        {
                            "type": "mrkdwn",
                            "text": f"*Company:*\n{company_name}"
                        },
                        {
                            "type": "mrkdwn",
                            "text": f"*Urgency:*\n{urgency}/10 {urgency_emoji}"
                        },
                        {
                            "type": "mrkdwn",
                            "text": f"*Category:*\n{category.title()}"
                        },
                        {
                            "type": "mrkdwn",
                            "text": f"*Attendees:*\n{', '.join(attendees) if attendees else 'N/A'}"
                        }
                    ]
                },
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": f"*Prospect's Question:*\n> {question}"
                    }
                },
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": f"*Why This Is Critical:*\n{why_critical}"
                    }
                },
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": f"*AI-Suggested Response:*\n```{suggested_answer}```"
                    }
                },
                {
                    "type": "context",
                    "elements": [
                        {
                            "type": "mrkdwn",
                            "text": f"Meeting context provided to help you craft the best response"
                        }
                    ]
                }
            ]
        }

        # Add meeting link if available
        if meeting_url:
            message["blocks"].append({
                "type": "actions",
                "elements": [
                    {
                        "type": "button",
                        "text": {
                            "type": "plain_text",
                            "text": "Join Meeting"
                        },
                        "url": meeting_url,
                        "style": "primary"
                    }
                ]
            })

        return message
