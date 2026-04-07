"""
Agent Orchestrator
Coordinates multiple AI agents and manages their execution
"""

import logging
import asyncio
import uuid
from typing import Dict, Any, Optional, List
from fastapi import WebSocket
from datetime import datetime

from services.openai_client import get_openai_client
from services.websocket_manager import WebSocketManager
from services.slack_service import SlackService

logger = logging.getLogger(__name__)


class AgentOrchestrator:
    """Orchestrates multiple AI agents for sales intelligence"""

    def __init__(self):
        self.openai_client = None
        self.ws_manager = WebSocketManager()
        self.slack_service = None

        # Store active research jobs
        self.active_jobs: Dict[str, Dict[str, Any]] = {}

        # Store conversation context per meeting
        self.conversation_contexts: Dict[str, List[Dict[str, Any]]] = {}

        # Store company information per meeting (for knowledge gap detection)
        self.meeting_company_info: Dict[str, Dict[str, Any]] = {}

        # Agent modules (will be imported dynamically)
        self.agents = {}

        logger.info("Agent orchestrator initialized")

    async def initialize(self):
        """Initialize the orchestrator and load agents"""
        # Initialize OpenAI client
        self.openai_client = get_openai_client()

        # Initialize Slack service
        self.slack_service = SlackService(websocket_manager=self.ws_manager)

        # Import and initialize agents
        await self._load_agents()

        logger.info("Agent orchestrator ready")

    async def _load_agents(self):
        """Dynamically load all agent modules"""
        try:
            # Import agent modules
            from agents.research_agent import ResearchAgent
            from agents.social_intelligence_agent import SocialIntelligenceAgent
            from agents.review_analysis_agent import ReviewAnalysisAgent
            from agents.conversation_agent import ConversationAgent
            from agents.strategy_agent import StrategyAgent
            from agents.knowledge_gap_agent import KnowledgeGapAgent

            # Initialize agents
            self.agents = {
                "research": ResearchAgent(self.openai_client),
                "social_intelligence": SocialIntelligenceAgent(self.openai_client),
                "review_analysis": ReviewAnalysisAgent(self.openai_client),
                "conversation": ConversationAgent(self.openai_client),
                "strategy": StrategyAgent(self.openai_client),
                "knowledge_gap": KnowledgeGapAgent(self.openai_client)
            }

            logger.info(f"Loaded {len(self.agents)} agents")

        except ImportError as e:
            logger.warning(f"Some agents not yet implemented: {str(e)}")
            # Initialize with empty dict for now
            self.agents = {}

    async def cleanup(self):
        """Cleanup resources"""
        logger.info("Agent orchestrator shutting down")
        # Cancel any active jobs
        for job_id in list(self.active_jobs.keys()):
            await self._cancel_job(job_id)

    def get_status(self) -> Dict[str, Any]:
        """Get orchestrator status"""
        return {
            "loaded_agents": list(self.agents.keys()),
            "active_jobs": len(self.active_jobs),
            "conversation_contexts": len(self.conversation_contexts)
        }

    async def start_research(
        self,
        websocket: WebSocket,
        company_url: str = None,
        competitor_urls: List[str] = None,
        my_company_url: str = None,
        target_company_url: str = None
    ):
        """
        Start multi-agent research on companies

        Args:
            websocket: WebSocket to send updates to
            company_url: (Legacy) Target company website URL
            competitor_urls: (Legacy) List of competitor URLs
            my_company_url: YOUR company website URL (what you sell)
            target_company_url: TARGET/prospect company URL (who you're selling to)
        """
        job_id = str(uuid.uuid4())

        # Handle both new and legacy parameters
        if my_company_url or target_company_url:
            # New format: my company vs target company
            company_url = target_company_url
            competitor_urls = competitor_urls or []
        else:
            # Legacy format
            my_company_url = None
            competitor_urls = competitor_urls or []

        # Store job metadata
        self.active_jobs[job_id] = {
            "job_id": job_id,
            "company_url": company_url,
            "competitor_urls": competitor_urls,
            "my_company_url": my_company_url,
            "target_company_url": target_company_url,
            "started_at": datetime.utcnow().isoformat(),
            "status": "in_progress",
            "results": {}
        }

        logger.info(f"Starting research job {job_id} - My: {my_company_url}, Target: {target_company_url}")

        try:
            # Run agents in parallel
            tasks = []

            # NEW MODE: My Company vs Target Company (product-need matching)
            if my_company_url and target_company_url:
                logger.info("Running product-need matching mode")

                # Scrape YOUR company (to understand what you sell)
                if "research" in self.agents:
                    tasks.append(
                        self._run_research_agent(websocket, job_id, my_company_url, agent_key="my_company")
                    )

                # Scrape TARGET company (to understand their needs)
                if "research" in self.agents:
                    tasks.append(
                        self._run_research_agent(websocket, job_id, target_company_url, agent_key="target_company")
                    )

                # Execute both scrapes concurrently
                if tasks:
                    await asyncio.gather(*tasks, return_exceptions=True)

                # After both companies analyzed, generate matching insights
                await self._generate_product_need_matching(websocket, job_id)

            # LEGACY MODE: Single company research
            elif company_url:
                # Task 1: Research Agent - scrape company website
                if "research" in self.agents:
                    tasks.append(
                        self._run_research_agent(websocket, job_id, company_url)
                    )

                # Task 2: Social Intelligence Agent - LinkedIn research
                if "social_intelligence" in self.agents:
                    tasks.append(
                        self._run_social_intelligence_agent(websocket, job_id, company_url)
                    )

                # Task 3: Review Analysis Agent - find customer complaints
                if "review_analysis" in self.agents:
                    tasks.append(
                        self._run_review_analysis_agent(websocket, job_id, company_url)
                    )

                # Task 4: Competitor research (optional)
                for competitor_url in competitor_urls:
                    if "research" in self.agents:
                        tasks.append(
                            self._run_research_agent(websocket, job_id, competitor_url, is_competitor=True)
                        )

                # Execute all tasks concurrently
                if tasks:
                    results = await asyncio.gather(*tasks, return_exceptions=True)

                    # Process results
                    for i, result in enumerate(results):
                        if isinstance(result, Exception):
                            logger.error(f"Agent task {i} failed: {str(result)}")

                # After all agents complete, run Strategy Agent to synthesize
                if "strategy" in self.agents:
                    await self._run_strategy_agent(websocket, job_id)

            # Mark job as completed
            self.active_jobs[job_id]["status"] = "completed"
            self.active_jobs[job_id]["completed_at"] = datetime.utcnow().isoformat()

            # Send completion notification
            await self.ws_manager.send_to_connection(websocket, {
                "type": "research_completed",
                "job_id": job_id,
                "message": "All research agents completed"
            })

            logger.info(f"Research job {job_id} completed")

        except Exception as e:
            logger.error(f"Error in research job {job_id}: {str(e)}")

            self.active_jobs[job_id]["status"] = "failed"
            self.active_jobs[job_id]["error"] = str(e)

            await self.ws_manager.send_error(
                websocket,
                f"Research job failed: {str(e)}",
                error_code="RESEARCH_FAILED"
            )

    async def _run_research_agent(
        self,
        websocket: WebSocket,
        job_id: str,
        url: str,
        is_competitor: bool = False,
        agent_key: str = None
    ):
        """Run research agent on a URL"""
        if agent_key:
            # New mode: explicit agent key (my_company or target_company)
            agent_name = agent_key
            display_name = "Your Company" if agent_key == "my_company" else "Target Company"
        else:
            # Legacy mode
            agent_name = f"research_{'competitor' if is_competitor else 'company'}"
            display_name = "Competitor" if is_competitor else "Company"

        await self.ws_manager.send_agent_update(
            websocket,
            agent_name,
            "started",
            f"🔍 Web crawler analyzing {display_name}: {url}"
        )

        try:
            # Run the agent
            result = await self.agents["research"].analyze_website(url)

            # Store results
            if job_id in self.active_jobs:
                self.active_jobs[job_id]["results"][agent_name] = result

            # Send insights to extension
            await self.ws_manager.send_insight(
                websocket,
                insight_type="company_research" if not is_competitor else "competitor_research",
                title=f"✅ {display_name} Analysis: {result.get('company_name', 'Unknown')}",
                content=result.get("summary", "")[:500] + "..." if len(result.get("summary", "")) > 500 else result.get("summary", ""),
                source="Research Agent",
                priority="high",
                metadata=result
            )

            await self.ws_manager.send_agent_update(
                websocket,
                agent_name,
                "completed",
                "Analysis complete"
            )

        except Exception as e:
            logger.error(f"Research agent failed for {url}: {str(e)}")
            await self.ws_manager.send_agent_update(
                websocket,
                agent_name,
                "error",
                str(e)
            )

    async def _run_social_intelligence_agent(
        self,
        websocket: WebSocket,
        job_id: str,
        company_url: str
    ):
        """Run social intelligence agent"""
        agent_name = "social_intelligence"

        await self.ws_manager.send_agent_update(
            websocket,
            agent_name,
            "started",
            "Gathering social intelligence from LinkedIn"
        )

        try:
            result = await self.agents["social_intelligence"].analyze_company(company_url)

            if job_id in self.active_jobs:
                self.active_jobs[job_id]["results"][agent_name] = result

            await self.ws_manager.send_insight(
                websocket,
                insight_type="social_intelligence",
                title=f"LinkedIn Insights: {result.get('company_name', 'Company')}",
                content=result.get("summary", ""),
                source="LinkedIn Agent",
                priority="normal",
                metadata=result
            )

            await self.ws_manager.send_agent_update(
                websocket,
                agent_name,
                "completed",
                "Social intelligence gathered"
            )

        except Exception as e:
            logger.error(f"Social intelligence agent failed: {str(e)}")
            await self.ws_manager.send_agent_update(
                websocket,
                agent_name,
                "error",
                str(e)
            )

    async def _run_review_analysis_agent(
        self,
        websocket: WebSocket,
        job_id: str,
        company_url: str
    ):
        """Run review analysis agent"""
        agent_name = "review_analysis"

        await self.ws_manager.send_agent_update(
            websocket,
            agent_name,
            "started",
            "Analyzing customer reviews and complaints"
        )

        try:
            result = await self.agents["review_analysis"].analyze_reviews(company_url)

            if job_id in self.active_jobs:
                self.active_jobs[job_id]["results"][agent_name] = result

            await self.ws_manager.send_insight(
                websocket,
                insight_type="customer_sentiment",
                title=f"Customer Sentiment Analysis",
                content=result.get("summary", ""),
                source="Review Analysis Agent",
                priority="high",
                metadata=result
            )

            await self.ws_manager.send_agent_update(
                websocket,
                agent_name,
                "completed",
                "Review analysis complete"
            )

        except Exception as e:
            logger.error(f"Review analysis agent failed: {str(e)}")
            await self.ws_manager.send_agent_update(
                websocket,
                agent_name,
                "error",
                str(e)
            )

    async def _run_strategy_agent(
        self,
        websocket: WebSocket,
        job_id: str
    ):
        """Run strategy agent to synthesize all insights"""
        agent_name = "strategy"

        await self.ws_manager.send_agent_update(
            websocket,
            agent_name,
            "started",
            "Synthesizing insights into sales strategy"
        )

        try:
            # Get all results from this job
            job_data = self.active_jobs.get(job_id, {})
            all_results = job_data.get("results", {})

            result = await self.agents["strategy"].synthesize(all_results)

            # Send strategic recommendations
            await self.ws_manager.send_insight(
                websocket,
                insight_type="strategy",
                title="Sales Strategy Recommendations",
                content=result.get("summary", ""),
                source="Strategy Agent",
                priority="critical",
                metadata=result
            )

            await self.ws_manager.send_agent_update(
                websocket,
                agent_name,
                "completed",
                "Strategy generated"
            )

        except Exception as e:
            logger.error(f"Strategy agent failed: {str(e)}")
            await self.ws_manager.send_agent_update(
                websocket,
                agent_name,
                "error",
                str(e)
            )

    async def _generate_product_need_matching(
        self,
        websocket: WebSocket,
        job_id: str
    ):
        """
        Generate AI insights matching YOUR products to TARGET company's needs
        This is the KEY feature: "Here's how YOUR solution solves THEIR problem"
        """
        agent_name = "product_need_matcher"

        await self.ws_manager.send_agent_update(
            websocket,
            agent_name,
            "started",
            "🤖 AI analyzing product-need matching..."
        )

        try:
            # Get results for both companies
            job_data = self.active_jobs.get(job_id, {})
            results = job_data.get("results", {})

            my_company_data = results.get("my_company", {})
            target_company_data = results.get("target_company", {})

            if not my_company_data.get("success") or not target_company_data.get("success"):
                raise Exception("Failed to analyze one or both companies")

            # Prepare prompt for AI
            matching_prompt = f"""You are a sales AI assistant helping a sales rep understand how to help a prospect.

**YOUR COMPANY (What you sell):**
Company: {my_company_data.get('company_name', 'Unknown')}
{my_company_data.get('summary', 'No data available')}

**TARGET COMPANY (Your prospect):**
Company: {target_company_data.get('company_name', 'Unknown')}
{target_company_data.get('summary', 'No data available')}

**Your Task:**
Analyze how YOUR products/services can help the TARGET company. Provide actionable insights in this format:

**🎯 How You Can Help:**
[2-3 specific ways your products solve their problems]

**💡 Key Talking Points:**
[3-5 bullet points to mention in the sales call]

**🚨 Pain Points to Address:**
[Specific challenges they face that you can solve]

**📊 Value Proposition:**
[Why they should choose your solution]

**🎬 Opening Line:**
[A personalized opening sentence for the sales call]

Keep it concise, actionable, and focused on THEIR needs, not YOUR features."""

            # Call OpenAI to generate matching insights
            matching_analysis = await self.openai_client.simple_prompt(
                prompt=matching_prompt,
                system="You are an expert sales strategist specializing in consultative selling and value-based conversations.",
                max_tokens=1500
            )

            # Send the insights to the overlay
            await self.ws_manager.send_insight(
                websocket,
                insight_type="product_need_matching",
                title=f"🎯 How to Help {target_company_data.get('company_name', 'Target Company')}",
                content=matching_analysis,
                source="Product-Need Matching AI",
                priority="critical",
                metadata={
                    "my_company": my_company_data.get("company_name"),
                    "target_company": target_company_data.get("company_name")
                }
            )

            # Store the company research for use in real-time conversation analysis
            if job_id in self.active_jobs:
                self.active_jobs[job_id]["company_research"] = {
                    "my_company": my_company_data,
                    "target_company": target_company_data,
                    "matching_insights": matching_analysis
                }

            await self.ws_manager.send_agent_update(
                websocket,
                agent_name,
                "completed",
                "✅ Product-need matching complete! Real-time suggestions enabled."
            )

            logger.info(f"Product-need matching completed for job {job_id}")

        except Exception as e:
            logger.error(f"Product-need matching failed: {str(e)}")
            await self.ws_manager.send_agent_update(
                websocket,
                agent_name,
                "error",
                f"Failed to generate matching: {str(e)}"
            )

    async def process_transcript(
        self,
        websocket: WebSocket,
        transcript: str,
        speaker: str,
        timestamp: Optional[str] = None,
        meeting_id: Optional[str] = None
    ):
        """
        Process real-time transcript from Meetstream

        Args:
            websocket: WebSocket connection
            transcript: Transcript text
            speaker: Speaker identifier
            timestamp: Optional timestamp
            meeting_id: Optional meeting identifier
        """
        # Store in conversation context
        if meeting_id is None:
            meeting_id = "default"

        if meeting_id not in self.conversation_contexts:
            self.conversation_contexts[meeting_id] = []

        self.conversation_contexts[meeting_id].append({
            "speaker": speaker,
            "text": transcript,
            "timestamp": timestamp or datetime.utcnow().isoformat()
        })

        # Run conversation agent and knowledge gap agent in parallel
        tasks = []

        # Task 1: Conversation agent (objection detection, questions, etc.)
        if "conversation" in self.agents:
            tasks.append(
                self._run_conversation_agent(websocket, meeting_id, transcript, speaker)
            )

        # Task 2: Knowledge gap agent (detect unknowns, trigger PM alerts)
        if "knowledge_gap" in self.agents:
            tasks.append(
                self._run_knowledge_gap_agent(websocket, meeting_id, transcript, speaker)
            )

        # Execute agents concurrently
        if tasks:
            await asyncio.gather(*tasks, return_exceptions=True)

    async def _run_conversation_agent(
        self,
        websocket: WebSocket,
        meeting_id: str,
        transcript: str,
        speaker: str
    ):
        """Run conversation agent for objection detection and real-time suggestions"""
        try:
            # Get company research from stored jobs
            company_research = None
            for job_id, job_data in self.active_jobs.items():
                if job_data.get("status") == "completed" and job_data.get("company_research"):
                    company_research = job_data["company_research"]
                    break

            # Analyze transcript with company context
            result = await self.agents["conversation"].analyze_transcript(
                transcript=transcript,
                speaker=speaker,
                context=self.conversation_contexts[meeting_id],
                company_research=company_research
            )

            # If agent detected something important (objection, question, etc.)
            if result.get("action_required"):
                # Determine insight type based on what was detected
                insight_type = "objection_handling"
                if result.get("type") == "response_needed":
                    insight_type = "real_time_suggestion"
                elif result.get("type") == "opportunity":
                    insight_type = "opportunity"

                await self.ws_manager.send_insight(
                    websocket,
                    insight_type=insight_type,
                    title=result.get("title", f"💬 {speaker} says..."),
                    content=result.get("suggestion", ""),
                    source="Real-Time AI Coach",
                    priority=result.get("priority", "high"),
                    metadata=result
                )

                logger.info(f"Real-time suggestion generated for {speaker}: {result.get('summary', '')[:50]}")

        except Exception as e:
            logger.error(f"Conversation agent failed: {str(e)}")

    async def _run_knowledge_gap_agent(
        self,
        websocket: WebSocket,
        meeting_id: str,
        transcript: str,
        speaker: str
    ):
        """Run knowledge gap agent to detect unknowns and trigger PM alerts"""
        try:
            # Get company info for this meeting
            company_info = self.meeting_company_info.get(meeting_id)

            # Analyze for knowledge gaps
            result = await self.agents["knowledge_gap"].analyze_for_knowledge_gap(
                transcript=transcript,
                speaker=speaker,
                company_info=company_info,
                conversation_context=self.conversation_contexts[meeting_id]
            )

            # Check if we should notify PM
            if self.agents["knowledge_gap"].should_notify_pm(result):
                logger.warning(
                    f"Knowledge gap detected - notifying PM: "
                    f"{result.get('exact_question', 'Unknown')}"
                )

                # Format Slack message
                meeting_context = {
                    "meeting_id": meeting_id,
                    "company_name": company_info.get('company_name', 'Unknown') if company_info else 'Unknown',
                    "attendees": company_info.get('attendees', []) if company_info else [],
                    "meeting_url": company_info.get('meeting_url', '') if company_info else ''
                }

                slack_message = self.agents["knowledge_gap"].format_slack_message(
                    result,
                    meeting_context
                )

                # Send to Slack
                slack_response = await self.slack_service.send_pm_alert(
                    slack_message,
                    meeting_context
                )

                # Notify sales rep that PM was alerted
                if slack_response and slack_response.get('success'):
                    await self.ws_manager.send_insight(
                        websocket,
                        insight_type="knowledge_gap",
                        title="PM Team Notified",
                        content=f"The PM team has been notified about: \"{result.get('exact_question', 'this question')}\" "
                                f"and will provide guidance shortly.",
                        source="Knowledge Gap Agent",
                        priority="high",
                        metadata={
                            **result,
                            'slack_thread': slack_response.get('thread_ts'),
                            'pm_notified': True
                        }
                    )

            # If it's a product question but not critical, just show in UI
            elif result.get("is_product_question") and result.get("suggested_answer"):
                await self.ws_manager.send_insight(
                    websocket,
                    insight_type="product_question",
                    title="Product Question Detected",
                    content=result.get("suggested_answer", ""),
                    source="Knowledge Gap Agent",
                    priority="normal",
                    metadata=result
                )

        except Exception as e:
            logger.error(f"Knowledge gap agent failed: {str(e)}", exc_info=True)

    def set_meeting_company_info(
        self,
        meeting_id: str,
        company_info: Dict[str, Any]
    ):
        """
        Set company information for a meeting (used by knowledge gap agent)

        Args:
            meeting_id: Meeting identifier
            company_info: Company information dict
        """
        self.meeting_company_info[meeting_id] = company_info
        logger.info(f"Set company info for meeting {meeting_id}: {company_info.get('company_name', 'Unknown')}")

    async def create_research_job(
        self,
        company_url: str,
        competitor_urls: List[str]
    ) -> str:
        """
        Create a research job without WebSocket (REST API)

        Returns:
            job_id: Job identifier
        """
        job_id = str(uuid.uuid4())

        self.active_jobs[job_id] = {
            "job_id": job_id,
            "company_url": company_url,
            "competitor_urls": competitor_urls,
            "started_at": datetime.utcnow().isoformat(),
            "status": "pending",
            "results": {}
        }

        logger.info(f"Created research job {job_id}")

        return job_id

    async def _cancel_job(self, job_id: str):
        """Cancel an active job"""
        if job_id in self.active_jobs:
            self.active_jobs[job_id]["status"] = "cancelled"
            logger.info(f"Cancelled job {job_id}")
