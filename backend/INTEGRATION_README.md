# AssemblyAI + Meetstream Bot Integration

This document explains the integration between AssemblyAI real-time transcription and Meetstream bot for your sales intelligence platform.

## Overview

The integration enables:
- **Real-time meeting transcription** using AssemblyAI's Streaming STT (Speech-to-Text)
- **Meetstream bot deployment** to join Google Meet meetings automatically
- **Live audio streaming** from Meetstream bot to AssemblyAI for transcription
- **Multi-agent processing** of transcripts for sales insights

## Architecture

```
Google Meet Meeting
       ↓
Meetstream Bot (joins meeting & streams audio)
       ↓
Backend API (receives audio stream)
       ↓
AssemblyAI Streaming API (transcribes in real-time)
       ↓
Agent Orchestrator (processes transcripts)
       ↓
WebSocket (broadcasts insights to frontend)
```

## Configuration

### 1. Environment Variables

Add to `/backend/.env`:

```bash
# Meetstream API Configuration
MEETSTREAM_API_KEY=<your_meetstream_api_key_here>
MEETSTREAM_API_URL=https://api.meetstream.ai/api/v1
MEETSTREAM_WEBHOOK_SECRET=your_webhook_secret_here

# AssemblyAI Real-time Transcription
# Get your API key from https://www.assemblyai.com/app/api-keys
ASSEMBLYAI_API_KEY=your_assemblyai_api_key_here
```

### 2. Get AssemblyAI API Key

1. Go to https://www.assemblyai.com/
2. Sign up or login
3. Navigate to https://www.assemblyai.com/app/api-keys
4. Copy your API key
5. Add it to your `.env` file

## API Endpoints

### Start Meetstream Bot

```http
POST /api/meetstream/start-bot
Content-Type: application/json

{
  "meeting_url": "https://meet.google.com/xxx-yyyy-zzz",
  "bot_name": "Meetstream AI Assistant",
  "recording_mode": "speaker_view"
}
```

**Response:**
```json
{
  "bot_id": "bot_12345",
  "meeting_url": "https://meet.google.com/xxx-yyyy-zzz",
  "status": "started",
  "transcription_enabled": true
}
```

### Stop Meetstream Bot

```http
DELETE /api/meetstream/stop-bot/{bot_id}
```

**Response:**
```json
{
  "bot_id": "bot_12345",
  "meeting_url": "https://meet.google.com/xxx-yyyy-zzz",
  "started_at": "2026-03-28T14:00:00Z",
  "ended_at": "2026-03-28T14:30:00Z",
  "transcription": {
    "session_id": "bot_12345",
    "transcript_count": 247,
    "full_transcript": "Complete meeting transcript...",
    "audio_duration_seconds": 1800
  }
}
```

### Get Bot Status

```http
GET /api/meetstream/bot-status/{bot_id}
```

**Response:**
```json
{
  "bot_id": "bot_12345",
  "meeting_url": "https://meet.google.com/xxx-yyyy-zzz",
  "started_at": "2026-03-28T14:00:00Z",
  "status": "active",
  "transcription": {
    "status": "active",
    "session_id": "bot_12345",
    "transcript_count": 42,
    "latest_transcript": {
      "transcript": "So the key features are...",
      "end_of_turn": true,
      "timestamp": "2026-03-28T14:05:30Z"
    }
  }
}
```

### List Active Bots

```http
GET /api/meetstream/active-bots
```

**Response:**
```json
{
  "active_bots": [
    {
      "bot_id": "bot_12345",
      "meeting_url": "https://meet.google.com/xxx-yyyy-zzz",
      "started_at": "2026-03-28T14:00:00Z",
      "status": "active"
    }
  ],
  "count": 1
}
```

### List Transcription Sessions

```http
GET /api/transcription/sessions
```

**Response:**
```json
{
  "active_sessions": [
    {
      "session_id": "bot_12345",
      "started_at": "2026-03-28T14:00:00Z",
      "transcript_count": 42
    }
  ],
  "count": 1
}
```

## Service Components

### 1. AssemblyAI Service (`services/assemblyai_service.py`)

Handles real-time transcription using AssemblyAI Streaming STT v3:

- **Speech Model**: Universal-3 Pro Streaming (`u3-rt-pro`)
- **Sample Rate**: 16 kHz
- **Latency**: Sub-300ms
- **Features**: Multilingual code switching, advanced prompting

**Key Methods:**
- `start_transcription_session()` - Initialize streaming session
- `send_audio()` - Send audio chunks for transcription
- `end_transcription_session()` - Close session and get summary
- `get_session_status()` - Get current session status

### 2. Meetstream Service (`services/meetstream_service.py`)

Manages Meetstream bot deployment and audio streaming:

**Key Methods:**
- `start_bot()` - Deploy bot to Google Meet
- `stop_bot()` - Remove bot from meeting
- `handle_audio_webhook()` - Process audio from Meetstream
- `get_bot_status()` - Get bot session status

## Audio Pipeline

### Audio Format Requirements

- **Format**: PCM 16-bit
- **Sample Rate**: 16000 Hz (16 kHz)
- **Channels**: Mono (1 channel)
- **Encoding**: Little-endian

### Webhook Integration

Meetstream sends audio chunks to:
```
POST /webhooks/meetstream/audio?bot_id={bot_id}
Content-Type: application/octet-stream
Body: Raw audio bytes
```

## Real-time Transcription Flow

1. **Bot Joins Meeting**
   - User calls `POST /api/meetstream/start-bot`
   - Meetstream bot joins Google Meet
   - AssemblyAI session is initialized

2. **Audio Streaming**
   - Bot captures meeting audio
   - Audio streamed to backend via webhook
   - Backend forwards to AssemblyAI

3. **Transcription Events**
   - AssemblyAI sends turn events with transcripts
   - Backend receives and processes transcripts
   - Transcripts trigger agent analysis

4. **Meeting End**
   - User calls `DELETE /api/meetstream/stop-bot/{bot_id}`
   - Bot leaves meeting
   - Final transcript summary returned

## Transcript Event Types

### 1. Session Begin
```json
{
  "type": "session_begin",
  "session_id": "bot_12345",
  "assemblyai_session_id": "aai_abc123",
  "expires_at": 1743182400
}
```

### 2. Transcript Turn
```json
{
  "type": "transcript",
  "session_id": "bot_12345",
  "data": {
    "transcript": "So the key features are...",
    "end_of_turn": true,
    "timestamp": "2026-03-28T14:05:30Z"
  }
}
```

### 3. Session Terminated
```json
{
  "type": "session_terminated",
  "session_id": "bot_12345",
  "audio_duration_seconds": 1800
}
```

### 4. Error
```json
{
  "type": "error",
  "session_id": "bot_12345",
  "error": "Error message"
}
```

## Testing

### 1. Test Configuration

```bash
# Check services are configured
curl http://localhost:8000/health

# Should show:
# - meetstream_service: configured
# - assemblyai_service: configured
```

### 2. Start a Test Bot

```bash
curl -X POST http://localhost:8000/api/meetstream/start-bot \
  -H "Content-Type: application/json" \
  -d '{
    "meeting_url": "https://meet.google.com/test-meeting",
    "bot_name": "Test Bot"
  }'
```

### 3. Check Bot Status

```bash
curl http://localhost:8000/api/meetstream/bot-status/bot_12345
```

### 4. Stop Bot

```bash
curl -X DELETE http://localhost:8000/api/meetstream/stop-bot/bot_12345
```

## Error Handling

### Common Errors

1. **503 Service Unavailable**
   - Missing API keys in `.env`
   - Solution: Add `MEETSTREAM_API_KEY` and `ASSEMBLYAI_API_KEY`

2. **400 Bad Request**
   - Invalid meeting URL
   - Missing required parameters
   - Solution: Check request body format

3. **404 Not Found**
   - Bot session doesn't exist
   - Solution: Verify bot_id is correct

4. **500 Internal Server Error**
   - Meetstream API error
   - AssemblyAI connection error
   - Solution: Check logs for detailed error message

## Monitoring

### Backend Logs

```bash
# View real-time logs
tail -f /path/to/backend/logs/app.log

# Key log patterns:
2026-03-28 14:00:00 - services.meetstream_service - INFO - Bot started: bot_12345
2026-03-28 14:00:01 - services.assemblyai_service - INFO - Transcription session started: bot_12345
2026-03-28 14:00:05 - services.assemblyai_service - DEBUG - Transcript turn: So the key features are...
```

### Health Check

```bash
curl http://localhost:8000/health
```

## Integration with Agents

Transcripts automatically trigger agent processing:

1. **Conversation Agent** - Analyzes dialogue patterns
2. **Strategy Agent** - Identifies sales opportunities
3. **Review Analysis Agent** - Extracts key topics
4. **Social Intelligence Agent** - Detects sentiment
5. **Research Agent** - Enriches with company data

## Next Steps

1. **Get AssemblyAI API Key** - Required for transcription
2. **Test Bot Deployment** - Start with a test meeting
3. **Monitor Transcripts** - Check WebSocket for real-time data
4. **Configure Agents** - Customize agent behavior for your use case
5. **Add Database Storage** - Store transcripts and insights

## Resources

- [AssemblyAI Documentation](https://www.assemblyai.com/docs)
- [Meetstream API Documentation](https://api.meetstream.ai/docs)
- [Universal-3 Pro Streaming Model](https://www.assemblyai.com/docs/streaming/universal-3-pro)
- [AssemblyAI API Keys](https://www.assemblyai.com/app/api-keys)

## Support

For issues or questions:
- Backend: Check `backend/main.py` logs
- Services: Review `services/assemblyai_service.py` and `services/meetstream_service.py`
- Configuration: Verify `.env` file has all required keys
