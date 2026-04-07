"""
Meetstream AI - Sales Intelligence Backend
Main FastAPI application with WebSocket support
"""

from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
from dotenv import load_dotenv
import os
import logging
import asyncio
from typing import Dict, Any, Optional
import json
from datetime import datetime

from services.websocket_manager import WebSocketManager
from services.agent_orchestrator import AgentOrchestrator
from services.scalekit_auth import get_scalekit_auth
from services.meetstream_service import get_meetstream_service, set_websocket_manager
from services.assemblyai_service import get_assemblyai_service

# Import enhanced company intelligence API
from api.company_intelligence import router as intelligence_router

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.DEBUG if os.getenv("DEBUG", "True") == "True" else logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize managers
ws_manager = WebSocketManager()
agent_orchestrator = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifecycle manager for startup and shutdown events"""
    # Startup
    logger.info("Starting Meetstream AI Backend...")

    # Connect WebSocket manager to meetstream service
    set_websocket_manager(ws_manager)
    logger.info("WebSocket manager connected")

    global agent_orchestrator
    agent_orchestrator = AgentOrchestrator()
    await agent_orchestrator.initialize()
    logger.info("Agent orchestrator initialized")

    yield

    # Shutdown
    logger.info("Shutting down Meetstream AI Backend...")
    if agent_orchestrator:
        await agent_orchestrator.cleanup()


# Create FastAPI app
app = FastAPI(
    title="Meetstream AI - Sales Intelligence API",
    description="Multi-agent system for real-time sales insights during Google Meet calls",
    version="1.0.0",
    lifespan=lifespan
)

# Configure CORS
allowed_origins = os.getenv("ALLOWED_ORIGINS", "chrome-extension://*,http://localhost:3000").split(",")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins (including Chrome extensions)
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include enhanced company intelligence router
app.include_router(intelligence_router)


# ============================================================================
# WebSocket Endpoints
# ============================================================================

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """
    Main WebSocket connection for Chrome extension
    Handles bidirectional communication for real-time insights
    """
    await ws_manager.connect(websocket)
    connection_id = ws_manager.get_connection_id(websocket)
    logger.info(f"WebSocket connected: {connection_id}")

    try:
        # Send welcome message
        await ws_manager.send_to_connection(websocket, {
            "type": "connection_established",
            "connection_id": connection_id,
            "message": "Connected to Meetstream AI Backend"
        })

        while True:
            # Receive message from Chrome extension
            data = await websocket.receive_text()
            message = json.loads(data)

            logger.info(f"Received message from {connection_id}: {message.get('type')}")

            # Route message to appropriate handler
            await handle_websocket_message(websocket, message)

    except WebSocketDisconnect:
        logger.info(f"WebSocket disconnected: {connection_id}")
        ws_manager.disconnect(websocket)
    except Exception as e:
        logger.error(f"WebSocket error for {connection_id}: {str(e)}")
        ws_manager.disconnect(websocket)


async def handle_websocket_message(websocket: WebSocket, message: Dict[str, Any]):
    """Route incoming WebSocket messages to appropriate handlers"""
    message_type = message.get("type")

    try:
        if message_type == "start_research":
            # Sales rep submitted company URLs for research
            await handle_start_research(websocket, message)

        elif message_type == "transcript_update":
            # Real-time transcript from Meetstream
            await handle_transcript_update(websocket, message)

        elif message_type == "ping":
            # Keep-alive ping
            await ws_manager.send_to_connection(websocket, {"type": "pong"})

        else:
            logger.warning(f"Unknown message type: {message_type}")
            await ws_manager.send_to_connection(websocket, {
                "type": "error",
                "message": f"Unknown message type: {message_type}"
            })

    except Exception as e:
        logger.error(f"Error handling message type {message_type}: {str(e)}")
        await ws_manager.send_to_connection(websocket, {
            "type": "error",
            "message": f"Error processing request: {str(e)}"
        })


async def handle_start_research(websocket: WebSocket, message: Dict[str, Any]):
    """
    Handle research request from Chrome extension
    Supports two modes:
    1. NEW: my_company_url + target_company_url (product-need matching)
    2. LEGACY: company_url + competitor_urls (competitive analysis)
    """
    # Check for new format (my company vs target company)
    my_company_url = message.get("my_company_url")
    target_company_url = message.get("target_company_url")

    # Check for legacy format
    company_url = message.get("company_url")
    competitor_urls = message.get("competitor_urls", [])

    # Validation
    if not (my_company_url or target_company_url or company_url):
        await ws_manager.send_to_connection(websocket, {
            "type": "error",
            "message": "At least one company URL is required"
        })
        return

    # Determine mode and log
    if my_company_url or target_company_url:
        logger.info(f"🎯 Product-need matching mode: My={my_company_url}, Target={target_company_url}")
        message_text = f"🚀 Web crawler activated! Analyzing your company and target prospect..."
    else:
        logger.info(f"📊 Competitive analysis mode: {company_url}, competitors: {competitor_urls}")
        message_text = f"Research agents activated for {company_url}"

    # Send acknowledgment
    await ws_manager.send_to_connection(websocket, {
        "type": "research_started",
        "message": message_text,
        "my_company_url": my_company_url,
        "target_company_url": target_company_url,
        "company_url": company_url,
        "competitor_urls": competitor_urls
    })

    # Trigger agent orchestrator with appropriate parameters
    await agent_orchestrator.start_research(
        websocket=websocket,
        my_company_url=my_company_url,
        target_company_url=target_company_url,
        company_url=company_url,
        competitor_urls=competitor_urls
    )


async def handle_transcript_update(websocket: WebSocket, message: Dict[str, Any]):
    """
    Handle real-time transcript update from Meetstream
    Triggers conversation analysis agent
    """
    transcript_text = message.get("transcript")
    speaker = message.get("speaker", "unknown")
    timestamp = message.get("timestamp")

    if not transcript_text:
        return

    logger.info(f"Transcript update: {speaker} - {transcript_text[:50]}...")

    # Trigger conversation agent
    await agent_orchestrator.process_transcript(
        websocket=websocket,
        transcript=transcript_text,
        speaker=speaker,
        timestamp=timestamp
    )


# ============================================================================
# REST API Endpoints
# ============================================================================

@app.get("/")
async def root():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "Meetstream AI - Sales Intelligence API",
        "version": "1.0.0"
    }


@app.get("/health")
async def health_check():
    """Detailed health check"""
    return {
        "status": "healthy",
        "active_connections": ws_manager.get_active_connections_count(),
        "agents_status": agent_orchestrator.get_status() if agent_orchestrator else "not_initialized"
    }


@app.post("/webhook/meetstream")
async def meetstream_webhook(payload: Dict[str, Any]):
    """
    Webhook endpoint for Meetstream transcription service
    Receives real-time transcripts and broadcasts to connected clients
    """
    # Verify webhook secret (optional but recommended)
    webhook_secret = os.getenv("MEETSTREAM_WEBHOOK_SECRET")
    # TODO: Implement webhook signature verification

    logger.info(f"Meetstream webhook received: {payload.get('event_type')}")

    # Extract transcript data
    transcript = payload.get("transcript", {})
    meeting_id = payload.get("meeting_id")

    # Broadcast to all connected websockets (or specific meeting room)
    await ws_manager.broadcast({
        "type": "transcript_update",
        "meeting_id": meeting_id,
        "transcript": transcript.get("text"),
        "speaker": transcript.get("speaker"),
        "timestamp": transcript.get("timestamp")
    })

    return {"status": "received"}


@app.post("/api/research")
async def trigger_research(request: Dict[str, Any]):
    """
    REST endpoint to trigger research (alternative to WebSocket)
    Useful for testing or batch processing
    """
    company_url = request.get("company_url")
    competitor_urls = request.get("competitor_urls", [])

    if not company_url:
        raise HTTPException(status_code=400, detail="company_url is required")

    # Create a research job
    job_id = await agent_orchestrator.create_research_job(
        company_url=company_url,
        competitor_urls=competitor_urls
    )

    return {
        "status": "started",
        "job_id": job_id,
        "message": "Research job created. Connect via WebSocket to receive real-time updates."
    }


@app.post("/api/scrape-companies")
async def scrape_companies(request: Dict[str, Any]):
    """
    Scrape both user company and target company websites
    Used by frontend when user submits company URLs for meeting prep

    Body:
        user_company_url: User's company website URL
        target_company_url: Target company website URL

    Returns:
        Structured company information for both companies
    """
    user_company_url = request.get("user_company_url")
    target_company_url = request.get("target_company_url")

    if not user_company_url or not target_company_url:
        raise HTTPException(
            status_code=400,
            detail="Both user_company_url and target_company_url are required"
        )

    try:
        # Import the research agent
        from agents.research_agent import ResearchAgent
        from services.openai_client import get_openai_client

        # Initialize research agent with OpenAI (can also use Claude)
        openai_client = get_openai_client()
        research_agent = ResearchAgent(openai_client)

        # Scrape both companies in parallel
        logger.info(f"Scraping companies: {user_company_url}, {target_company_url}")

        user_company_task = research_agent.analyze_website(user_company_url)
        target_company_task = research_agent.analyze_website(target_company_url)

        user_company_data, target_company_data = await asyncio.gather(
            user_company_task,
            target_company_task,
            return_exceptions=True
        )

        # Handle errors
        if isinstance(user_company_data, Exception):
            logger.error(f"Error scraping user company: {str(user_company_data)}")
            user_company_data = {
                "success": False,
                "error": str(user_company_data),
                "url": user_company_url
            }

        if isinstance(target_company_data, Exception):
            logger.error(f"Error scraping target company: {str(target_company_data)}")
            target_company_data = {
                "success": False,
                "error": str(target_company_data),
                "url": target_company_url
            }

        return {
            "status": "success",
            "user_company": user_company_data,
            "target_company": target_company_data,
            "scraped_at": datetime.now().isoformat()
        }

    except Exception as e:
        logger.error(f"Error scraping companies: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# Scalekit Authentication Endpoints
# ============================================================================

scalekit_auth = get_scalekit_auth()

@app.get("/auth/scalekit/login")
async def scalekit_login(
    redirect_uri: str = "http://localhost:5173/auth/callback",
    organization_id: Optional[str] = None,
    login_hint: Optional[str] = None
):
    """
    Initiate Scalekit SSO login

    Query Parameters:
        redirect_uri: Where to redirect after authentication
        organization_id: Optional organization ID
        login_hint: Optional email hint
    """
    if not scalekit_auth.is_configured():
        raise HTTPException(
            status_code=503,
            detail="Scalekit authentication is not configured. Please add SCALEKIT_* environment variables."
        )

    try:
        auth_url = scalekit_auth.get_authorization_url(
            redirect_uri=redirect_uri,
            organization_id=organization_id,
            login_hint=login_hint
        )
        return {"authorization_url": auth_url}

    except Exception as e:
        logger.error(f"Scalekit login error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/auth/scalekit/callback")
async def scalekit_callback(
    code: str,
    redirect_uri: str = "http://localhost:5173/auth/callback"
):
    """
    Handle Scalekit OAuth callback

    Query Parameters:
        code: Authorization code from Scalekit
        redirect_uri: Original redirect URI
    """
    if not scalekit_auth.is_configured():
        raise HTTPException(status_code=503, detail="Scalekit not configured")

    try:
        # Exchange code for tokens
        result = await scalekit_auth.handle_callback(code, redirect_uri)

        # Return user info and tokens
        # In production, set these as HttpOnly cookies
        return {
            "user": result["user"],
            "access_token": result["access_token"],
            "refresh_token": result["refresh_token"],
            "expires_in": result["expires_in"]
        }

    except Exception as e:
        logger.error(f"Scalekit callback error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/auth/scalekit/refresh")
async def scalekit_refresh(payload: Dict[str, Any]):
    """
    Refresh access token

    Body:
        refresh_token: Refresh token
    """
    if not scalekit_auth.is_configured():
        raise HTTPException(status_code=503, detail="Scalekit not configured")

    refresh_token = payload.get("refresh_token")
    if not refresh_token:
        raise HTTPException(status_code=400, detail="refresh_token required")

    try:
        result = await scalekit_auth.refresh_access_token(refresh_token)
        return result

    except Exception as e:
        logger.error(f"Token refresh error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/auth/scalekit/logout")
async def scalekit_logout(redirect_uri: str = "http://localhost:5173/login"):
    """
    Get Scalekit logout URL

    Query Parameters:
        redirect_uri: Where to redirect after logout
    """
    if not scalekit_auth.is_configured():
        raise HTTPException(status_code=503, detail="Scalekit not configured")

    try:
        logout_url = scalekit_auth.get_logout_url(redirect_uri)
        return {"logout_url": logout_url}

    except Exception as e:
        logger.error(f"Logout error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# Frontend API Endpoints
# ============================================================================

# In-memory storage (replace with database in production)
profiles = {}
meetings = {}
linkedin_cache = {}

@app.post("/api/profile")
async def save_profile(payload: Dict[str, Any]):
    """Save user profile"""
    user_id = payload.get("userId", "default")
    profiles[user_id] = payload
    return {"status": "success", "message": "Profile saved"}


@app.get("/api/profile/{user_id}")
async def get_profile(user_id: str):
    """Get user profile"""
    profile = profiles.get(user_id)
    if profile:
        return profile
    raise HTTPException(status_code=404, detail="Profile not found")


@app.post("/api/meeting-prep")
async def save_meeting_prep(payload: Dict[str, Any]):
    """Save meeting preparation data"""
    meeting_id = str(len(meetings) + 1)
    meetings[meeting_id] = {
        "id": meeting_id,
        **payload,
        "created_at": datetime.now().isoformat()
    }
    return {"status": "success", "meeting_id": meeting_id}


@app.get("/api/meeting-prep/{meeting_id}")
async def get_meeting_prep(meeting_id: str):
    """Get meeting preparation data"""
    meeting = meetings.get(meeting_id)
    if meeting:
        return meeting
    raise HTTPException(status_code=404, detail="Meeting not found")


@app.get("/api/meetings/{user_id}")
async def get_past_meetings(user_id: str):
    """Get all past meetings for a user"""
    user_meetings = [m for m in meetings.values() if m.get("userId") == user_id]
    return {"meetings": user_meetings}


@app.get("/api/meetings/{meeting_id}/insights")
async def get_meeting_insights(meeting_id: str):
    """Get insights for a specific meeting"""
    meeting = meetings.get(meeting_id)
    if meeting:
        return {"insights": meeting.get("insights", {})}
    raise HTTPException(status_code=404, detail="Meeting not found")


@app.post("/api/linkedin/profile")
async def fetch_linkedin_profile(payload: Dict[str, Any]):
    """
    Fetch LinkedIn profile via Apify

    For production: Integrate with Apify API
    apify_client = ApifyClient(os.getenv("APIFY_TOKEN"))
    run = apify_client.actor("apify/linkedin-profile-scraper").call(
        run_input={"startUrls": [{"url": payload["linkedin_url"]}]}
    )
    """
    linkedin_url = payload.get("linkedin_url")

    # Check cache first
    if linkedin_url in linkedin_cache:
        return linkedin_cache[linkedin_url]

    # TODO: Implement Apify integration
    # For now, return placeholder
    profile_data = {
        "name": "John Doe",
        "headline": "VP of Sales at Tech Company",
        "location": "San Francisco, CA",
        "summary": "Experienced sales leader...",
        "experience": [],
        "education": [],
        "scraped_at": datetime.now().isoformat()
    }

    linkedin_cache[linkedin_url] = profile_data
    return profile_data


@app.post("/api/linkedin/company")
async def fetch_linkedin_company(payload: Dict[str, Any]):
    """Fetch LinkedIn company page via Apify"""
    linkedin_url = payload.get("linkedin_url")

    if linkedin_url in linkedin_cache:
        return linkedin_cache[linkedin_url]

    # TODO: Implement Apify integration
    company_data = {
        "name": "Acme Inc",
        "description": "Leading SaaS company...",
        "industry": "Software",
        "size": "201-500 employees",
        "website": "https://acme.com",
        "scraped_at": datetime.now().isoformat()
    }

    linkedin_cache[linkedin_url] = company_data
    return company_data


# ============================================================================
# Meetstream Bot & Transcription Endpoints
# ============================================================================

meetstream_service = get_meetstream_service()
assemblyai_service = get_assemblyai_service()


@app.post("/api/meetstream/start-bot")
async def start_meetstream_bot(payload: Dict[str, Any]):
    """
    Start a Meetstream bot in a Google Meet meeting
    Automatically enables real-time transcription via AssemblyAI Streaming

    Body:
        meeting_url: Google Meet URL (required)
        bot_name: Bot display name (default: "Meetstream Agent")
        video_required: Enable video (default: true)
        webhook_url: Custom webhook URL for transcription (optional)

    Returns:
        Bot session info with live transcription enabled
    """
    if not meetstream_service.is_configured():
        raise HTTPException(
            status_code=503,
            detail="Meetstream not configured. Please add MEETSTREAM_API_KEY to environment variables."
        )

    meeting_url = payload.get("meeting_url")
    if not meeting_url:
        raise HTTPException(status_code=400, detail="meeting_url is required")

    bot_name = payload.get("bot_name", "Meetstream Agent")
    video_required = payload.get("video_required", True)
    webhook_url = payload.get("webhook_url")  # Optional custom webhook

    try:
        result = await meetstream_service.start_bot(
            meeting_url=meeting_url,
            bot_name=bot_name,
            video_required=video_required,
            webhook_url=webhook_url
        )

        logger.info(f"Bot started: {result['bot_id']} with live transcription")
        return result

    except Exception as e:
        logger.error(f"Error starting bot: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.delete("/api/meetstream/stop-bot/{bot_id}")
async def stop_meetstream_bot(bot_id: str):
    """
    Stop a Meetstream bot and end transcription
    Returns final transcription summary

    Path Parameters:
        bot_id: Bot session identifier
    """
    if not meetstream_service.is_configured():
        raise HTTPException(status_code=503, detail="Meetstream not configured")

    try:
        summary = await meetstream_service.stop_bot(bot_id)
        logger.info(f"Bot stopped: {bot_id}")
        return summary

    except Exception as e:
        logger.error(f"Error stopping bot: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/meetstream/bot-status/{bot_id}")
async def get_bot_status(bot_id: str):
    """
    Get current status of a Meetstream bot session

    Path Parameters:
        bot_id: Bot session identifier
    """
    status = meetstream_service.get_bot_status(bot_id)

    if status.get("status") == "not_found":
        raise HTTPException(status_code=404, detail="Bot session not found")

    return status


@app.get("/api/meetstream/active-bots")
async def get_active_bots():
    """Get list of all active Meetstream bot sessions"""
    bots = meetstream_service.get_active_bots()
    return {"active_bots": bots, "count": len(bots)}


@app.post("/webhook")
async def meetstream_live_transcription_webhook(payload: Dict[str, Any]):
    """
    Webhook endpoint for Meetstream LIVE TRANSCRIPTION (streaming)
    Receives real-time transcription updates from Meetstream's streaming transcription

    Body (example from Meetstream):
        {
          "bot_id": "...",
          "speakerName": "John Doe",
          "timestamp": "2026-01-24T17:00:30.354452",
          "new_text": "hello",
          "transcript": "hello world",
          "words": [...],
          "end_of_turn": false,
          "custom_attributes": {...}
        }
    """
    try:
        bot_id = payload.get("bot_id")
        speaker_name = payload.get("speakerName", "Unknown")
        transcript = payload.get("transcript", "")
        new_text = payload.get("new_text", "")
        end_of_turn = payload.get("end_of_turn", False)
        timestamp = payload.get("timestamp")
        words = payload.get("words", [])
        utterance = payload.get("utterance", "")
        turn_is_formatted = payload.get("turn_is_formatted", False)
        transcription_mode = payload.get("transcription_mode", "")
        custom_attributes = payload.get("custom_attributes", {})

        # Enhanced logging - log full webhook payload for debugging
        logger.info(f"[WEBHOOK] Received from bot {bot_id}")
        logger.debug(f"[WEBHOOK] Full payload: {json.dumps(payload, indent=2)}")
        logger.debug(f"[WEBHOOK] Fields - speaker: {speaker_name}, new_text: '{new_text}', "
                    f"end_of_turn: {end_of_turn}, words_count: {len(words)}, "
                    f"transcription_mode: {transcription_mode}, custom_attrs: {custom_attributes}")

        # Store transcript in database
        from services.transcript_storage import get_transcript_storage
        storage = get_transcript_storage()
        storage_result = storage.store_webhook_payload(payload)

        if storage_result.get("success"):
            logger.info(f"[STORAGE] Saved transcript_id={storage_result.get('transcript_id')}, words={storage_result.get('word_count')}")
        else:
            logger.error(f"[STORAGE] Failed to store: {storage_result.get('error')}")

        # Broadcast to all connected WebSocket clients (including full payload for inspector)
        await ws_manager.broadcast({
            "type": "live_transcript",
            "bot_id": bot_id,
            "speaker": speaker_name,
            "transcript": transcript,
            "new_text": new_text,
            "end_of_turn": end_of_turn,
            "timestamp": timestamp or datetime.now().isoformat(),
            "words": words,
            "utterance": utterance,
            "turn_is_formatted": turn_is_formatted,
            "transcription_mode": transcription_mode,
            "custom_attributes": custom_attributes,
            "raw_payload": payload  # Include full raw payload for webhook inspector
        })

        # Trigger real-time AI analysis when we have meaningful content
        # Only analyze complete turns with actual content (not partial words)
        if end_of_turn and transcript.strip() and len(transcript.split()) >= 3:
            logger.info(f"[AI ANALYSIS] Triggering conversation agent for: {speaker_name}: {transcript[:50]}...")

            # Get all active WebSocket connections
            active_connections = ws_manager.get_active_connections()

            # Trigger conversation agent for each connection (they share research context)
            for ws_connection in active_connections:
                try:
                    asyncio.create_task(
                        agent_orchestrator._run_conversation_agent(
                            websocket=ws_connection,
                            meeting_id=bot_id,  # Use bot_id as meeting_id
                            transcript=transcript,
                            speaker=speaker_name
                        )
                    )
                except Exception as agent_error:
                    logger.error(f"[AI ANALYSIS] Error starting conversation agent: {agent_error}")

        # Return 200 OK quickly (as recommended by Meetstream)
        return {"status": "received", "bot_id": bot_id, "stored": storage_result.get("success")}

    except Exception as e:
        logger.error(f"Error processing live transcription webhook: {str(e)}")
        # Still return 200 to avoid retries
        return {"status": "error", "message": str(e)}


@app.post("/webhooks/meetstream/audio")
async def meetstream_audio_webhook(bot_id: str, audio: bytes):
    """
    Legacy webhook endpoint for Meetstream audio streaming
    (Not used when using live_transcription_required with streaming providers)

    Query Parameters:
        bot_id: Bot session identifier

    Body:
        Raw audio bytes (PCM 16-bit, 16kHz, mono)
    """
    if not bot_id:
        raise HTTPException(status_code=400, detail="bot_id query parameter required")

    try:
        success = await meetstream_service.handle_audio_webhook(bot_id, audio)

        if not success:
            logger.warning(f"Failed to process audio for bot: {bot_id}")

        return {"status": "received"}

    except Exception as e:
        logger.error(f"Error processing audio webhook: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# Transcript Storage API Endpoints
# ============================================================================

@app.get("/api/transcripts/meetings")
async def get_all_meetings(limit: int = 50):
    """Get all stored meetings"""
    from services.transcript_storage import get_transcript_storage
    storage = get_transcript_storage()
    meetings = storage.get_all_meetings(limit=limit)
    return {"meetings": meetings, "count": len(meetings)}


@app.get("/api/transcripts/meeting/{bot_id}")
async def get_meeting_details(bot_id: str):
    """Get meeting details and statistics"""
    from services.transcript_storage import get_transcript_storage
    storage = get_transcript_storage()
    meeting = storage.get_meeting_by_bot_id(bot_id)
    if not meeting:
        raise HTTPException(status_code=404, detail="Meeting not found")

    stats = storage.get_meeting_statistics(bot_id)
    return {"meeting": meeting, "statistics": stats}


@app.get("/api/transcripts/meeting/{bot_id}/transcripts")
async def get_meeting_transcripts(bot_id: str, limit: int = 1000):
    """Get all transcript segments for a meeting"""
    from services.transcript_storage import get_transcript_storage
    storage = get_transcript_storage()
    transcripts = storage.get_transcripts_by_bot_id(bot_id, limit=limit)
    return {"transcripts": transcripts, "count": len(transcripts)}


@app.get("/api/transcripts/meeting/{bot_id}/text")
async def get_meeting_full_text(bot_id: str):
    """Get complete meeting transcript as formatted text"""
    from services.transcript_storage import get_transcript_storage
    storage = get_transcript_storage()
    text = storage.get_full_transcript_text(bot_id)
    return {"bot_id": bot_id, "transcript": text}


@app.get("/api/transcripts/transcript/{transcript_id}/words")
async def get_transcript_words(transcript_id: int):
    """Get word-level data for a specific transcript segment"""
    from services.transcript_storage import get_transcript_storage
    storage = get_transcript_storage()
    words = storage.get_words_for_transcript(transcript_id)
    return {"transcript_id": transcript_id, "words": words, "count": len(words)}


@app.get("/api/transcripts/search")
async def search_transcripts(q: str, bot_id: Optional[str] = None, limit: int = 50):
    """Search transcripts by text content"""
    from services.transcript_storage import get_transcript_storage
    storage = get_transcript_storage()
    results = storage.search_transcripts(q, bot_id=bot_id, limit=limit)
    return {"query": q, "results": results, "count": len(results)}


@app.delete("/api/transcripts/meeting/{bot_id}")
async def delete_meeting(bot_id: str):
    """Delete a meeting and all its transcripts"""
    from services.transcript_storage import get_transcript_storage
    storage = get_transcript_storage()
    success = storage.delete_meeting(bot_id)
    if not success:
        raise HTTPException(status_code=404, detail="Meeting not found")
    return {"success": True, "message": "Meeting deleted"}


@app.get("/api/transcription/sessions")
async def get_transcription_sessions():
    """Get list of all active transcription sessions"""
    sessions = assemblyai_service.get_active_sessions()
    return {"active_sessions": sessions, "count": len(sessions)}


@app.get("/api/transcription/session/{session_id}")
async def get_transcription_session(session_id: str):
    """Get status of a specific transcription session"""
    status = assemblyai_service.get_session_status(session_id)

    if status.get("status") == "not_found":
        raise HTTPException(status_code=404, detail="Transcription session not found")

    return status


# ============================================================================
# Error Handlers
# ============================================================================

@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """Global exception handler"""
    logger.error(f"Unhandled exception: {str(exc)}")
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error", "error": str(exc)}
    )


# ============================================================================
# Run Server
# ============================================================================

if __name__ == "__main__":
    import uvicorn

    host = os.getenv("HOST", "0.0.0.0")
    port = int(os.getenv("PORT", 8000))

    uvicorn.run(
        "main:app",
        host=host,
        port=port,
        reload=os.getenv("DEBUG", "True") == "True",
        log_level="debug" if os.getenv("DEBUG", "True") == "True" else "info"
    )
