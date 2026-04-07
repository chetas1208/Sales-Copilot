# Meetstream Bot Integration Guide

## 🤖 Overview

The backend now supports **Meetstream bot creation** with **AssemblyAI live streaming transcription** using the exact API structure from Meetstream docs.

---

## 🎯 API Configuration

### Meetstream Bot API Endpoint

The bot creation uses the official Meetstream API structure:

```
POST https://api.meetstream.ai/api/v1/bots/create_bot
```

### Configuration in Code

**Location:** `backend/services/meetstream_service.py:49`

The service now sends:
- ✅ `meeting_link` (not `meeting_url`)
- ✅ `video_required: true`
- ✅ `live_transcription_required` with webhook
- ✅ Full AssemblyAI streaming config:
  - 48kHz sample rate
  - PCM S16LE encoding
  - VAD (Voice Activity Detection) threshold: 0.4
  - End-of-turn confidence: 0.4
  - Inactivity timeout: 300s
  - Universal streaming English model

---

## 🚀 How to Use

### 1. Start a Bot

```bash
curl -X POST http://localhost:8000/api/meetstream/start-bot \
  -H "Content-Type: application/json" \
  -d '{
    "meeting_url": "https://meet.google.com/abc-defg-hij",
    "bot_name": "Sales Assistant",
    "video_required": true,
    "webhook_url": "https://your-server.com/webhook"
  }'
```

**Response:**
```json
{
  "bot_id": "bot_123abc",
  "meeting_url": "https://meet.google.com/abc-defg-hij",
  "webhook_url": "https://your-server.com/webhook",
  "status": "started",
  "live_transcription_enabled": true,
  "assemblyai_streaming_config": "48kHz PCM with VAD"
}
```

### 2. Receive Live Transcriptions

Transcriptions arrive at your webhook:

```
POST https://your-server.com/webhook
```

**Payload from Meetstream:**
```json
{
  "bot_id": "bot_123abc",
  "speakerName": "John Doe",
  "timestamp": "2026-03-28T17:00:30.354452",
  "new_text": "hello",
  "transcript": "hello world",
  "words": [...],
  "end_of_turn": false,
  "custom_attributes": {}
}
```

### 3. Stop the Bot

```bash
curl -X DELETE http://localhost:8000/api/meetstream/stop-bot/bot_123abc
```

---

## 📝 Request Parameters

### Start Bot Endpoint

**`POST /api/meetstream/start-bot`**

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `meeting_url` | string | ✅ Yes | - | Google Meet URL |
| `bot_name` | string | ❌ No | "Meetstream Agent" | Bot display name |
| `video_required` | boolean | ❌ No | `true` | Enable video |
| `webhook_url` | string | ❌ No | `http://localhost:8000/webhook` | Custom webhook URL |

---

## 🎙️ AssemblyAI Streaming Config

The bot automatically configures AssemblyAI with these settings:

```json
{
  "transcription_mode": "raw",
  "sample_rate": 48000,
  "speech_model": "universal-streaming-english",
  "format_turns": false,
  "encoding": "pcm_s16le",
  "vad_threshold": "0.4",
  "end_of_turn_confidence_threshold": "0.4",
  "inactivity_timeout": 300,
  "min_end_of_turn_silence_when_confident": "400",
  "max_turn_silence": "1280"
}
```

### What These Mean:

- **`sample_rate: 48000`** - High quality audio (48kHz)
- **`vad_threshold: 0.4`** - Voice Activity Detection sensitivity
- **`end_of_turn_confidence: 0.4`** - When to detect end of speaking turn
- **`inactivity_timeout: 300`** - 5 minutes of silence before timeout
- **`min_end_of_turn_silence: 400ms`** - Minimum silence to end turn
- **`max_turn_silence: 1280ms`** - Maximum silence within turn

---

## 🔌 Webhook Integration

### Your Webhook Endpoint

The webhook at `POST /webhook` receives live transcription updates.

**Already implemented in:** `backend/main.py:689`

```python
@app.post("/webhook")
async def meetstream_live_transcription_webhook(payload: Dict[str, Any]):
    """
    Webhook for Meetstream LIVE TRANSCRIPTION
    Receives real-time updates from AssemblyAI streaming
    """
    bot_id = payload.get("bot_id")
    speaker_name = payload.get("speakerName", "Unknown")
    transcript = payload.get("transcript", "")
    new_text = payload.get("new_text", "")
    end_of_turn = payload.get("end_of_turn", False)

    # Broadcast to WebSocket clients
    await ws_manager.broadcast({
        "type": "live_transcript",
        "bot_id": bot_id,
        "speaker": speaker_name,
        "transcript": transcript,
        "new_text": new_text,
        "end_of_turn": end_of_turn
    })

    return {"status": "received", "bot_id": bot_id}
```

---

## 🌐 Environment Variables

Add to `backend/.env`:

```bash
# Meetstream Configuration
MEETSTREAM_API_KEY=<your_meetstream_api_key_here>
MEETSTREAM_API_URL=https://api.meetstream.ai/api/v1

# Public URL for webhooks (important for live transcription!)
PUBLIC_URL=https://your-ngrok-url.ngrok.io
```

**Important:** If testing locally, use ngrok or similar to expose your webhook:

```bash
ngrok http 8000
# Use the ngrok URL as PUBLIC_URL
```

---

## 🧪 Testing

### 1. Start the Server

```bash
cd backend
python main.py
```

### 2. Create a Test Meeting

Go to https://meet.google.com/new and create a test meeting.

### 3. Start the Bot

```bash
curl -X POST http://localhost:8000/api/meetstream/start-bot \
  -H "Content-Type: application/json" \
  -d '{
    "meeting_url": "https://meet.google.com/YOUR-MEETING-CODE"
  }'
```

### 4. Watch Transcriptions Arrive

The bot will join the meeting and start sending live transcriptions to your webhook.

---

## 📊 Data Flow

```
1. User clicks "Start Bot" in frontend
   ↓
2. Frontend calls POST /api/meetstream/start-bot
   ↓
3. Backend creates bot via Meetstream API
   {
     meeting_link: "meet.google.com/...",
     live_transcription_required: { webhook_url: "..." },
     recording_config: { assemblyai_streaming: {...} }
   }
   ↓
4. Meetstream bot joins Google Meet
   ↓
5. AssemblyAI streams transcription to webhook
   ↓
6. Backend receives POST /webhook with live transcripts
   ↓
7. Backend broadcasts to WebSocket clients
   ↓
8. Frontend displays real-time transcriptions
```

---

## 🎯 Frontend Integration

### Example: Start Bot from React

```typescript
const startBot = async (meetingUrl: string) => {
  const response = await fetch('http://localhost:8000/api/meetstream/start-bot', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      meeting_url: meetingUrl,
      bot_name: 'Sales Assistant',
      video_required: true
    })
  });

  const data = await response.json();
  console.log('Bot started:', data.bot_id);

  return data;
};
```

### Example: Receive Live Transcriptions via WebSocket

```typescript
const ws = new WebSocket('ws://localhost:8000/ws');

ws.onmessage = (event) => {
  const data = JSON.parse(event.data);

  if (data.type === 'live_transcript') {
    console.log(`${data.speaker}: ${data.new_text}`);

    // Update UI with real-time transcript
    updateTranscript({
      speaker: data.speaker,
      text: data.transcript,
      endOfTurn: data.end_of_turn
    });
  }
};
```

---

## 🔧 Configuration Details

### Meetstream API Call

**Exact structure sent to Meetstream:**

```json
{
  "meeting_link": "https://meet.google.com/abc-defg-hij",
  "bot_name": "Meetstream Agent",
  "video_required": true,
  "live_transcription_required": {
    "webhook_url": "https://your-server.com/webhook"
  },
  "recording_config": {
    "transcript": {
      "provider": {
        "assemblyai_streaming": {
          "transcription_mode": "raw",
          "sample_rate": 48000,
          "speech_model": "universal-streaming-english",
          "format_turns": false,
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
```

---

## ⚙️ Advanced Configuration

### Custom Webhook URL

If you want to use a different webhook:

```bash
curl -X POST http://localhost:8000/api/meetstream/start-bot \
  -H "Content-Type: application/json" \
  -d '{
    "meeting_url": "https://meet.google.com/abc-defg-hij",
    "webhook_url": "https://my-custom-server.com/custom-webhook"
  }'
```

### No Video Mode

Start bot without video:

```bash
curl -X POST http://localhost:8000/api/meetstream/start-bot \
  -H "Content-Type: application/json" \
  -d '{
    "meeting_url": "https://meet.google.com/abc-defg-hij",
    "video_required": false
  }'
```

---

## 📚 Related Documentation

- **Meetstream API Docs:** https://docs.meetstream.ai
- **AssemblyAI Streaming:** https://www.assemblyai.com/docs/api-reference/streaming
- **Backend Integration:** `backend/INTEGRATION_README.md`

---

## 🎊 Summary

✅ **Meetstream bot creation** - Exact API structure implemented
✅ **AssemblyAI streaming** - 48kHz with VAD enabled
✅ **Live webhook** - Real-time transcription delivery
✅ **WebSocket broadcast** - Push to connected clients
✅ **Frontend ready** - Easy integration with React/Vue/etc

**The bot system is fully configured and ready to use!** 🚀
