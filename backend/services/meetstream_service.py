"""
Meetstream Integration Service
Handles webhooks and audio streaming from Meetstream bot
Integrates with AssemblyAI for real-time transcription
Includes RAG-powered product knowledge for intelligent responses
"""

import os
import json
import logging
import aiohttp
from typing import Dict, Any, Optional
from datetime import datetime
from .assemblyai_service import get_assemblyai_service
from .rag_service import get_rag_service

logger = logging.getLogger(__name__)

# Global reference to WebSocket manager (set by main.py)
_ws_manager = None

def set_websocket_manager(manager):
    """Set the WebSocket manager instance"""
    global _ws_manager
    _ws_manager = manager


class MeetstreamService:
    """Service for integrating with Meetstream bot and managing meeting transcriptions"""

    def __init__(self):
        """Initialize Meetstream service"""
        self.api_key = os.getenv("MEETSTREAM_API_KEY")
        self.api_url = os.getenv("MEETSTREAM_API_URL", "https://api.meetstream.ai/api/v1")
        self.webhook_secret = os.getenv("MEETSTREAM_WEBHOOK_SECRET")

        # Active meeting sessions mapped to transcription sessions
        self.meeting_sessions: Dict[str, Dict[str, Any]] = {}

        # Get AssemblyAI service
        self.assemblyai = get_assemblyai_service()

        # Initialize RAG service for product knowledge
        try:
            self.rag = get_rag_service()
            logger.info("RAG service initialized for product knowledge")
        except Exception as e:
            logger.warning(f"RAG service not available: {str(e)}")
            self.rag = None

        if not self.api_key:
            logger.warning("Meetstream API key not configured")
        else:
            logger.info("Meetstream service initialized")

    def is_configured(self) -> bool:
        """Check if Meetstream is properly configured"""
        return self.api_key is not None

    async def start_bot(
        self,
        meeting_url: str,
        bot_name: str = "Meetstream Agent",
        video_required: bool = True,
        webhook_url: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Start a Meetstream bot in a meeting with live transcription via AssemblyAI

        Args:
            meeting_url: Google Meet URL to join
            bot_name: Display name for the bot
            video_required: Whether video is required
            webhook_url: Webhook URL for live transcription (defaults to /webhook)

        Returns:
            Bot session information
        """
        if not self.is_configured():
            raise ValueError("Meetstream not configured")

        # Default webhook URL
        if not webhook_url:
            base_url = os.getenv('PUBLIC_URL', 'http://localhost:8000')
            webhook_url = f"{base_url}/webhook"

        try:
            async with aiohttp.ClientSession() as session:
                headers = {
                    "Authorization": self.api_key,  # Use API key directly as shown in docs
                    "Content-Type": "application/json"
                }

                # Exact payload structure from Meetstream API docs
                payload = {
                    "meeting_link": meeting_url,
                    "bot_name": bot_name,
                    "video_required": video_required,
                    "live_transcription_required": {
                        "webhook_url": webhook_url
                    },
                    "recording_config": {
                        "transcript": {
                            "provider": {
                                "assemblyai_streaming": {
                                    "transcription_mode": "raw",
                                    "sample_rate": 48000,
                                    "speech_model": "universal-streaming-english",
                                    "format_turns": False,
                                    "encoding": "pcm_s16le",
                                    "vad_threshold": "0.4",
                                    "end_of_turn_confidence_threshold": "0.4",
                                    "inactivity_timeout": 300,
                                    "min_end_of_turn_silence_when_confident": "400",
                                    "max_turn_silence": "1280"
                                }
                            }
                        }
                    }
                }

                logger.info(f"Creating Meetstream bot for meeting: {meeting_url}")
                logger.debug(f"Webhook URL: {webhook_url}")

                async with session.post(
                    f"{self.api_url}/bots/create_bot",
                    headers=headers,
                    json=payload
                ) as response:
                    response_text = await response.text()
                    logger.debug(f"Meetstream API response: {response.status} - {response_text}")

                    if response.status in [200, 201]:  # Accept both 200 OK and 201 Created
                        data = json.loads(response_text) if isinstance(response_text, str) else await response.json()
                        bot_id = data.get("bot_id")

                        logger.info(f"Meetstream bot created successfully: {bot_id}")

                        # Store meeting session
                        self.meeting_sessions[bot_id] = {
                            "bot_id": bot_id,
                            "meeting_url": meeting_url,
                            "bot_name": bot_name,
                            "started_at": datetime.now().isoformat(),
                            "webhook_url": webhook_url,
                            "status": "active",
                            "transcripts": []  # Store transcripts as they arrive
                        }

                        logger.info(f"Bot started: {bot_id} for meeting: {meeting_url}")
                        return {
                            "bot_id": bot_id,
                            "meeting_url": meeting_url,
                            "webhook_url": webhook_url,
                            "status": "started",
                            "live_transcription_enabled": True,
                            "assemblyai_streaming_config": "48kHz PCM with VAD"
                        }
                    else:
                        logger.error(f"Failed to start bot: {response.status} - {response_text}")
                        raise Exception(f"Failed to start bot: {response.status} - {response_text}")

        except Exception as e:
            logger.error(f"Error starting Meetstream bot: {str(e)}")
            raise

    async def stop_bot(self, bot_id: str) -> Dict[str, Any]:
        """
        Stop a Meetstream bot and end transcription

        Args:
            bot_id: Bot session identifier

        Returns:
            Final session summary with transcripts
        """
        if not self.is_configured():
            raise ValueError("Meetstream not configured")

        try:
            # Stop the bot via Meetstream API
            async with aiohttp.ClientSession() as session:
                headers = {
                    "Authorization": f"Bearer {self.api_key}"
                }

                async with session.delete(
                    f"{self.api_url}/bots/{bot_id}",
                    headers=headers
                ) as response:
                    if response.status not in [200, 204]:
                        error_text = await response.text()
                        logger.error(f"Failed to stop bot: {response.status} - {error_text}")

            # End AssemblyAI transcription session
            if bot_id in self.meeting_sessions:
                transcription_summary = await self.assemblyai.end_transcription_session(
                    session_id=bot_id,
                    terminate=True
                )

                meeting_session = self.meeting_sessions[bot_id]
                meeting_session["ended_at"] = datetime.now().isoformat()
                meeting_session["status"] = "ended"

                # Prepare final summary
                summary = {
                    "bot_id": bot_id,
                    "meeting_url": meeting_session["meeting_url"],
                    "started_at": meeting_session["started_at"],
                    "ended_at": meeting_session["ended_at"],
                    "transcription": transcription_summary
                }

                # Remove from active sessions
                del self.meeting_sessions[bot_id]

                logger.info(f"Bot stopped: {bot_id}")
                return summary

            return {"bot_id": bot_id, "status": "stopped"}

        except Exception as e:
            logger.error(f"Error stopping bot: {str(e)}")
            raise

    async def handle_audio_webhook(self, bot_id: str, audio_data: bytes) -> bool:
        """
        Handle incoming audio stream from Meetstream webhook

        Args:
            bot_id: Bot session identifier
            audio_data: Raw audio bytes (PCM 16-bit, 16kHz, mono)

        Returns:
            True if audio was processed successfully
        """
        if bot_id not in self.meeting_sessions:
            logger.warning(f"Received audio for unknown bot: {bot_id}")
            return False

        try:
            # Send audio to AssemblyAI for transcription
            success = await self.assemblyai.send_audio(bot_id, audio_data)
            return success

        except Exception as e:
            logger.error(f"Error handling audio webhook: {str(e)}")
            return False

    async def _handle_transcript_event(self, event: Dict[str, Any]):
        """Internal callback for transcript events from AssemblyAI"""
        event_type = event.get("type")
        session_id = event.get("session_id")

        if event_type == "transcript":
            # Broadcast transcript to all WebSocket clients
            transcript_data = event['data']
            logger.info(f"Transcript: {transcript_data['transcript']}")

            # Broadcast to all connected clients
            if _ws_manager:
                await _ws_manager.broadcast({
                    "type": "live_transcript",
                    "bot_id": session_id,
                    "transcript": transcript_data['transcript'],
                    "end_of_turn": transcript_data['end_of_turn'],
                    "timestamp": transcript_data['timestamp']
                })
            else:
                logger.warning("WebSocket manager not available for broadcasting transcript")

        elif event_type == "session_begin":
            logger.info(f"Transcription started for session: {session_id}")

        elif event_type == "session_terminated":
            logger.info(f"Transcription ended for session: {session_id}")

        elif event_type == "error":
            logger.error(f"Transcription error: {event.get('error')}")

    def get_bot_status(self, bot_id: str) -> Dict[str, Any]:
        """Get current status of a bot session"""
        if bot_id not in self.meeting_sessions:
            return {"status": "not_found"}

        session = self.meeting_sessions[bot_id]
        transcription_status = self.assemblyai.get_session_status(bot_id)

        return {
            "bot_id": bot_id,
            "meeting_url": session["meeting_url"],
            "started_at": session["started_at"],
            "status": session["status"],
            "transcription": transcription_status
        }

    def get_active_bots(self) -> list:
        """Get list of all active bot sessions"""
        return [
            {
                "bot_id": bot_id,
                "meeting_url": session["meeting_url"],
                "started_at": session["started_at"],
                "status": session["status"]
            }
            for bot_id, session in self.meeting_sessions.items()
        ]

    async def answer_product_question(self, question: str) -> Dict[str, Any]:
        """
        Answer a product-related question using RAG pipeline

        Args:
            question: Customer's question about products, features, or pricing

        Returns:
            Dictionary with answer, confidence, and supporting information
        """
        if not self.rag:
            return {
                "answer": "Product knowledge system is not available at the moment. Please contact our sales team.",
                "confidence": "none",
                "source": "error"
            }

        try:
            result = self.rag.answer_question(question)
            logger.info(f"RAG answer for '{question}': confidence={result.get('confidence')}")
            return result
        except Exception as e:
            logger.error(f"Error answering product question: {str(e)}")
            return {
                "answer": "I encountered an error accessing product information. Please try again or contact support.",
                "confidence": "none",
                "source": "error",
                "error": str(e)
            }

    def search_product_knowledge(self, query: str, top_k: int = 5) -> list:
        """
        Search product knowledge base for relevant information

        Args:
            query: Search query
            top_k: Number of results to return

        Returns:
            List of search results with relevance scores
        """
        if not self.rag:
            return []

        try:
            results = self.rag.search(query, top_k=top_k)
            return [
                {
                    "content": r.content,
                    "score": r.score,
                    "metadata": r.metadata,
                    "source": r.source
                }
                for r in results
            ]
        except Exception as e:
            logger.error(f"Error searching product knowledge: {str(e)}")
            return []

    def get_product_catalog(self) -> Dict[str, Any]:
        """Get the complete product catalog"""
        if not self.rag:
            return {"error": "Product catalog not available"}

        try:
            products = self.rag.list_all_products()
            return {
                "company": self.rag.knowledge_base.get("company", "Unknown"),
                "products": products,
                "total_products": len(products)
            }
        except Exception as e:
            logger.error(f"Error getting product catalog: {str(e)}")
            return {"error": str(e)}

    async def process_transcript_with_rag(self, bot_id: str, transcript: str) -> Optional[Dict[str, Any]]:
        """
        Process a transcript segment to detect questions and provide intelligent responses

        Args:
            bot_id: Bot session identifier
            transcript: Transcript text to process

        Returns:
            Response dictionary if a question was detected, None otherwise
        """
        if not self.rag:
            return None

        # Simple heuristic: detect questions (can be enhanced with NLP)
        question_indicators = [
            "what", "how", "when", "where", "why", "who",
            "can you", "could you", "tell me", "explain",
            "price", "cost", "pricing", "license", "plan",
            "feature", "capability", "support", "trial"
        ]

        transcript_lower = transcript.lower()
        is_question = (
            "?" in transcript or
            any(indicator in transcript_lower for indicator in question_indicators)
        )

        if not is_question:
            return None

        # Get answer from RAG
        try:
            result = await self.answer_product_question(transcript)

            # Store the Q&A in session
            if bot_id in self.meeting_sessions:
                if "qa_history" not in self.meeting_sessions[bot_id]:
                    self.meeting_sessions[bot_id]["qa_history"] = []

                self.meeting_sessions[bot_id]["qa_history"].append({
                    "question": transcript,
                    "answer": result["answer"],
                    "confidence": result["confidence"],
                    "timestamp": datetime.now().isoformat()
                })

            # Broadcast answer to connected clients
            if _ws_manager:
                await _ws_manager.broadcast({
                    "type": "bot_response",
                    "bot_id": bot_id,
                    "question": transcript,
                    "answer": result["answer"],
                    "confidence": result["confidence"],
                    "timestamp": datetime.now().isoformat()
                })

            return result

        except Exception as e:
            logger.error(f"Error processing transcript with RAG: {str(e)}")
            return None


# Singleton instance
_meetstream_service: Optional[MeetstreamService] = None


def get_meetstream_service() -> MeetstreamService:
    """Get or create singleton Meetstream service"""
    global _meetstream_service
    if _meetstream_service is None:
        _meetstream_service = MeetstreamService()
    return _meetstream_service
