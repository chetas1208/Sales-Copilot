# Live Transcription Setup & Testing Guide

## ✅ What's Been Configured

1. **AssemblyAI API Key**: Configured in `backend/.env` (line 38)
2. **Backend WebSocket Broadcasting**: Transcripts broadcast to all connected clients
3. **Chrome Extension UI**: New "Live Transcription" section added to overlay
4. **Real-time Display**: Transcripts auto-scroll with timestamps

---

## 🎯 How to See Live Transcription

### Step 1: Start the Backend Server

```bash
cd backend
python main.py
```

The server will start on `http://localhost:8000`

### Step 2: Load the Chrome Extension

1. Open Chrome and go to `chrome://extensions/`
2. Enable "Developer mode" (top right)
3. Click "Load unpacked"
4. Select the `salesstream-extension` folder
5. Extension should now be active

### Step 3: Join a Google Meet

1. Open a Google Meet: `https://meet.google.com/new`
2. The SalesStream overlay should appear in the top-right corner
3. Check the status bar at the bottom - it should say "Connected to AI Backend"

### Step 4: Start the Meetstream Bot

**Option A: Using API (curl)**

```bash
curl -X POST http://localhost:8000/api/meetstream/start-bot \
  -H "Content-Type: application/json" \
  -d '{
    "meeting_url": "https://meet.google.com/YOUR-MEETING-CODE",
    "bot_name": "Meetstream AI Transcriber"
  }'
```

**Option B: Using Python**

```python
import requests

response = requests.post('http://localhost:8000/api/meetstream/start-bot', json={
    "meeting_url": "https://meet.google.com/YOUR-MEETING-CODE",
    "bot_name": "Meetstream AI Transcriber"
})

bot_id = response.json()['bot_id']
print(f"Bot started: {bot_id}")
```

### Step 5: Watch Live Transcripts Appear

- Transcripts will appear in the "🎙️ Live Transcription" section
- Partial transcripts (interim) appear in italic
- Complete sentences appear in normal text
- Auto-scrolls to show latest transcript
- Timestamps show when each line was spoken

---

## 📋 API Endpoints

### Start Bot & Transcription
```http
POST /api/meetstream/start-bot
Content-Type: application/json

{
  "meeting_url": "https://meet.google.com/xxx-xxxx-xxx",
  "bot_name": "Meetstream AI Assistant",
  "recording_mode": "audio_only"
}
```

**Response:**
```json
{
  "bot_id": "unique-bot-id",
  "meeting_url": "https://meet.google.com/xxx-xxxx-xxx",
  "status": "started",
  "transcription_enabled": true
}
```

### Stop Bot
```http
DELETE /api/meetstream/stop-bot/{bot_id}
```

**Response:**
```json
{
  "bot_id": "unique-bot-id",
  "meeting_url": "https://meet.google.com/xxx-xxxx-xxx",
  "started_at": "2026-03-28T...",
  "ended_at": "2026-03-28T...",
  "transcription": {
    "full_transcript": "Complete meeting transcript...",
    "transcript_count": 150,
    "audio_duration_seconds": 1800
  }
}
```

### Check Bot Status
```http
GET /api/meetstream/bot-status/{bot_id}
```

### List Active Bots
```http
GET /api/meetstream/active-bots
```

### List Transcription Sessions
```http
GET /api/transcription/sessions
```

### Get Specific Session
```http
GET /api/transcription/session/{session_id}
```

---

## 🔍 Troubleshooting

### Issue: Extension shows "Disconnected"

**Solution:**
1. Make sure backend is running: `curl http://localhost:8000/health`
2. Check browser console (F12) for WebSocket errors
3. Verify CORS settings in `backend/.env` allow `chrome-extension://*`

### Issue: No transcripts appearing

**Checklist:**
- [ ] AssemblyAI API key is valid (check line 38 in `backend/.env`)
- [ ] Bot successfully joined the meeting (check Meetstream dashboard)
- [ ] Audio is being streamed from Meetstream to backend
- [ ] WebSocket connection is active (check extension console)

**Debug Commands:**
```bash
# Check backend logs
tail -f backend/logs/app.log

# Check active sessions
curl http://localhost:8000/api/transcription/sessions

# Check bot status
curl http://localhost:8000/api/meetstream/active-bots
```

### Issue: "AssemblyAI not configured" error

**Solution:**
Replace the placeholder in `backend/.env`:
```env
ASSEMBLYAI_API_KEY=your_actual_key_here
```

Get your key from: https://www.assemblyai.com/app/api-keys

---

## 🎨 Extension UI Features

### Live Transcription Section
- **Location**: Top section of overlay
- **Icon**: 🎙️
- **Auto-scroll**: Newest transcripts always visible
- **History**: Keeps last 50 transcript lines
- **Styling**: Monospace font, glassmorphism background

### Transcript Line Types
1. **Partial** (italic, dim): Interim results while person is speaking
2. **Complete** (normal): Final transcript after end-of-turn detected

### Example Display
```
10:30:45 Hello, can you hear me?
10:30:48 Yes, loud and clear...
10:30:52 Great! Let's talk about your needs.
```

---

## 🚀 Testing Without Real Meeting

If you want to test without joining a real meeting, you can simulate transcripts:

```python
# test_transcript_simulator.py
import asyncio
import websockets
import json
from datetime import datetime

async def simulate_transcripts():
    uri = "ws://localhost:8000/ws"

    async with websockets.connect(uri) as websocket:
        # Wait for connection
        response = await websocket.recv()
        print(f"Connected: {response}")

        # Simulate transcript messages
        test_transcripts = [
            "Hello, can you hear me?",
            "Yes, I can hear you perfectly.",
            "Great! Let's discuss the project requirements.",
            "We need a scalable solution for our platform.",
            "That sounds interesting. Tell me more about your current setup."
        ]

        for i, text in enumerate(test_transcripts):
            message = {
                "type": "live_transcript",
                "bot_id": "test-bot-123",
                "transcript": text,
                "end_of_turn": True,
                "timestamp": datetime.now().isoformat()
            }

            await websocket.send(json.dumps(message))
            print(f"Sent: {text}")

            await asyncio.sleep(3)  # 3 seconds between messages

asyncio.run(simulate_transcripts())
```

Run with:
```bash
pip install websockets
python test_transcript_simulator.py
```

---

## 📊 Architecture Flow

```
Google Meet → Meetstream Bot → Captures Audio
                                     ↓
                              Audio Stream (PCM 16kHz)
                                     ↓
                              Backend receives audio
                                     ↓
                           AssemblyAI Service (transcribes)
                                     ↓
                           WebSocket Manager (broadcasts)
                                     ↓
                           Chrome Extension (displays)
```

---

## 🔐 Environment Variables Summary

```env
# Required for transcription
ASSEMBLYAI_API_KEY=<your_assemblyai_api_key_here>  ✅ Configured

# Required for bot control
MEETSTREAM_API_KEY=<your_meetstream_api_key_here>  ✅ Configured
MEETSTREAM_API_URL=https://api.meetstream.ai/api/v1

# Backend
HOST=0.0.0.0
PORT=8000
```

---

## ✨ Next Steps

1. **Test the flow**: Start backend → Load extension → Start bot → Watch transcripts
2. **Integration**: Connect transcripts to AI agents for real-time analysis
3. **Storage**: Add database to persist transcripts
4. **Features**: Add speaker diarization, sentiment analysis, keyword extraction

---

## 📞 Support

- Backend logs: Check console output from `python main.py`
- Extension logs: Right-click extension → Inspect → Console tab
- Network logs: Browser DevTools → Network tab → Filter "WS"

All components are ready to go! 🎉
