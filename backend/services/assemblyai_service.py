"""
AssemblyAI Streaming Transcription Service
Handles real-time audio transcription using AssemblyAI Streaming STT
Integrates with Meetstream bot for meeting transcriptions
"""

import os
import logging
import asyncio
import json
from typing import Dict, Any, Optional, Callable
from datetime import datetime
import assemblyai as aai
from assemblyai.streaming.v3 import (
    BeginEvent,
    StreamingClient,
    StreamingClientOptions,
    StreamingError,
    StreamingEvents,
    StreamingParameters,
    TerminationEvent,
    TurnEvent,
)

logger = logging.getLogger(__name__)


class AssemblyAIService:
    """AssemblyAI streaming transcription service for real-time audio"""

    def __init__(self):
        """Initialize AssemblyAI service"""
        self.api_key = os.getenv("ASSEMBLYAI_API_KEY")

        if not self.api_key:
            logger.warning("AssemblyAI API key not configured. Transcription will not be available.")
            self.client = None
            return

        # Initialize AssemblyAI
        aai.settings.api_key = self.api_key

        # Active transcription sessions
        self.active_sessions: Dict[str, Dict[str, Any]] = {}

        logger.info("AssemblyAI service initialized")

    def is_configured(self) -> bool:
        """Check if AssemblyAI is properly configured"""
        return self.api_key is not None

    async def start_transcription_session(
        self,
        session_id: str,
        callback: Optional[Callable] = None,
        speech_model: str = "u3-rt-pro",
        sample_rate: int = 16000,
        enable_extra_session_information: bool = True
    ) -> Dict[str, Any]:
        """
        Start a new real-time transcription session

        Args:
            session_id: Unique identifier for this transcription session
            callback: Optional callback function for transcript events
            speech_model: AssemblyAI speech model to use
            sample_rate: Audio sample rate in Hz
            enable_extra_session_information: Enable detailed session info

        Returns:
            Dict with session information
        """
        if not self.is_configured():
            raise ValueError("AssemblyAI not configured")

        if session_id in self.active_sessions:
            raise ValueError(f"Session {session_id} already exists")

        try:
            # Create streaming client
            client = StreamingClient(
                StreamingClientOptions(
                    api_key=self.api_key,
                    api_host="streaming.assemblyai.com",
                )
            )

            # Store session data
            session_data = {
                "client": client,
                "session_id": session_id,
                "started_at": datetime.now().isoformat(),
                "transcripts": [],
                "callback": callback,
                "assemblyai_session_id": None,
                "speech_model": speech_model,
                "sample_rate": sample_rate
            }

            # Set up event handlers
            def on_begin(streaming_client, event: BeginEvent):
                session_data["assemblyai_session_id"] = event.id
                logger.info(f"Transcription session started: {event.id} (session: {session_id})")
                if callback:
                    asyncio.create_task(callback({
                        "type": "session_begin",
                        "session_id": session_id,
                        "assemblyai_session_id": event.id,
                        "expires_at": event.expires_at
                    }))

            def on_turn(streaming_client, event: TurnEvent):
                transcript_data = {
                    "transcript": event.transcript,
                    "end_of_turn": event.end_of_turn,
                    "timestamp": datetime.now().isoformat()
                }

                session_data["transcripts"].append(transcript_data)
                logger.debug(f"Transcript turn: {event.transcript} (EOT: {event.end_of_turn})")

                if callback:
                    asyncio.create_task(callback({
                        "type": "transcript",
                        "session_id": session_id,
                        "data": transcript_data
                    }))

            def on_terminated(streaming_client, event: TerminationEvent):
                logger.info(f"Session terminated: {session_id}, Audio duration: {event.audio_duration_seconds}s")
                session_data["terminated_at"] = datetime.now().isoformat()
                session_data["audio_duration_seconds"] = event.audio_duration_seconds

                if callback:
                    asyncio.create_task(callback({
                        "type": "session_terminated",
                        "session_id": session_id,
                        "audio_duration_seconds": event.audio_duration_seconds
                    }))

            def on_error(streaming_client, error: StreamingError):
                logger.error(f"Transcription error in session {session_id}: {error}")
                if callback:
                    asyncio.create_task(callback({
                        "type": "error",
                        "session_id": session_id,
                        "error": str(error)
                    }))

            # Register event handlers
            client.on(StreamingEvents.Begin, on_begin)
            client.on(StreamingEvents.Turn, on_turn)
            client.on(StreamingEvents.Termination, on_terminated)
            client.on(StreamingEvents.Error, on_error)

            # Connect to AssemblyAI
            client.connect(
                StreamingParameters(
                    speech_model=speech_model,
                    sample_rate=sample_rate,
                    enable_extra_session_information=enable_extra_session_information
                )
            )

            # Store session
            self.active_sessions[session_id] = session_data

            return {
                "session_id": session_id,
                "started_at": session_data["started_at"],
                "speech_model": speech_model,
                "sample_rate": sample_rate,
                "status": "connected"
            }

        except Exception as e:
            logger.error(f"Error starting transcription session: {str(e)}")
            raise

    async def send_audio(self, session_id: str, audio_data: bytes) -> bool:
        """
        Send audio data to an active transcription session

        Args:
            session_id: Session identifier
            audio_data: Raw audio bytes (PCM 16-bit, mono, matching sample_rate)

        Returns:
            True if audio was sent successfully
        """
        if session_id not in self.active_sessions:
            raise ValueError(f"Session {session_id} not found")

        session = self.active_sessions[session_id]
        client = session["client"]

        try:
            # Send audio to AssemblyAI
            client.send(audio_data)
            return True
        except Exception as e:
            logger.error(f"Error sending audio to session {session_id}: {str(e)}")
            return False

    async def end_transcription_session(self, session_id: str, terminate: bool = True) -> Dict[str, Any]:
        """
        End a transcription session

        Args:
            session_id: Session identifier
            terminate: Whether to send terminate message to AssemblyAI

        Returns:
            Final session summary
        """
        if session_id not in self.active_sessions:
            raise ValueError(f"Session {session_id} not found")

        session = self.active_sessions[session_id]
        client = session["client"]

        try:
            # Disconnect from AssemblyAI
            if terminate:
                client.disconnect(terminate=True)
            else:
                client.disconnect()

            # Prepare session summary
            summary = {
                "session_id": session_id,
                "assemblyai_session_id": session.get("assemblyai_session_id"),
                "started_at": session["started_at"],
                "ended_at": datetime.now().isoformat(),
                "transcript_count": len(session["transcripts"]),
                "full_transcript": " ".join([t["transcript"] for t in session["transcripts"] if t["end_of_turn"]]),
                "audio_duration_seconds": session.get("audio_duration_seconds")
            }

            # Remove from active sessions
            del self.active_sessions[session_id]

            logger.info(f"Transcription session ended: {session_id}")
            return summary

        except Exception as e:
            logger.error(f"Error ending transcription session: {str(e)}")
            raise

    def get_session_status(self, session_id: str) -> Dict[str, Any]:
        """Get current status of a transcription session"""
        if session_id not in self.active_sessions:
            return {"status": "not_found"}

        session = self.active_sessions[session_id]
        return {
            "status": "active",
            "session_id": session_id,
            "assemblyai_session_id": session.get("assemblyai_session_id"),
            "started_at": session["started_at"],
            "transcript_count": len(session["transcripts"]),
            "latest_transcript": session["transcripts"][-1] if session["transcripts"] else None
        }

    def get_active_sessions(self) -> list:
        """Get list of all active transcription sessions"""
        return [
            {
                "session_id": sid,
                "started_at": session["started_at"],
                "transcript_count": len(session["transcripts"])
            }
            for sid, session in self.active_sessions.items()
        ]


# Singleton instance
_assemblyai_service: Optional[AssemblyAIService] = None


def get_assemblyai_service() -> AssemblyAIService:
    """Get or create singleton AssemblyAI service"""
    global _assemblyai_service
    if _assemblyai_service is None:
        _assemblyai_service = AssemblyAIService()
    return _assemblyai_service
