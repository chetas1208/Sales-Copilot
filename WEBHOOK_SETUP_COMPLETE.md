# 🎯 Complete Webhook Setup for Meetstream Live Transcription

## ✅ What I've Done

1. **Created webhook endpoint** at `/webhook` in your backend
2. **Updated extension** to display transcripts with speaker names
3. **Started backend server** (running on `http://localhost:8000`)
4. **Backend is READY** to receive Meetstream transcriptions

---

## 🚀 Current Status

### ✅ Backend Running
```
URL: http://localhost:8000
Health: http://localhost:8000/health
Webhook: http://localhost:8000/webhook
```

### ✅ Webhook Endpoint Ready
The endpoint at `POST /webhook` will:
- Receive Meetstream's live transcription JSON
- Extract: `bot_id`, `speakerName`, `transcript`, `new_text`, `end_of_turn`
- Broadcast to all connected WebSocket clients
- Display in Chrome Extension overlay

---

## 🔧 Next Steps for YOU

### Option 1: Deploy Backend to Public URL (RECOMMENDED)

You need to deploy your backend to get a public URL that Meetstream can reach.

**Quick Deploy Options:**

#### A. Railway.app (5 minutes)
```bash
# Install Railway CLI
brew install railwayapp/railway/railway

# Login
railway login

# Initialize and deploy
cd backend
railway init
railway up
```

You'll get a URL like: `https://your-app.railway.app`

#### B. Render.com (Free tier)
1. Go to https://render.com
2. Connect your GitHub repo
3. Create new Web Service
4. Deploy `backend` directory
5. Get URL: `https://your-backend.onrender.com`

#### C. Fly.io
```bash
# Install flyctl
brew install flyctl

# Deploy
cd backend
fly launch
fly deploy
```

### Option 2: Use ngrok with Valid Token

Get a valid ngrok auth token from: https://dashboard.ngrok.com/get-started/your-authtoken

```bash
# Configure ngrok with valid token
ngrok config add-authtoken YOUR_VALID_TOKEN_HERE

# Start tunnel
ngrok http 8000
```

You'll get a URL like: `https://abc123.ngrok-free.app`

---

## 📝 Meetstream Bot Configuration

Once you have your PUBLIC URL, use this payload:

### For AssemblyAI Streaming:

```json
{
  "meeting_url": "https://meet.google.com/your-meeting-code",
  "bot_name": "Meetstream AI Transcriber",
  "live_transcription_required": {
    "webhook_url": "YOUR_PUBLIC_URL/webhook"
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

### For Deepgram Streaming:

```json
{
  "meeting_url": "https://meet.google.com/your-meeting-code",
  "bot_name": "Meetstream AI Transcriber",
  "live_transcription_required": {
    "webhook_url": "YOUR_PUBLIC_URL/webhook"
  },
  "recording_config": {
    "transcript": {
      "provider": {
        "deepgram_streaming": {
          "transcription_mode": "sentence",
          "model": "nova-2",
          "language": "en",
          "punctuate": true,
          "smart_format": true,
          "endpointing": 300,
          "vad_events": true,
          "utterance_end_ms": 1000,
          "encoding": "linear16",
          "channels": 1
        }
      }
    }
  }
}
```

---

## 🧪 Test Locally First

Before deploying, you can test the webhook endpoint:

```bash
# Start backend (if not running)
cd backend
python main.py

# In another terminal, simulate Meetstream webhook:
curl -X POST http://localhost:8000/webhook \
  -H "Content-Type: application/json" \
  -d '{
    "bot_id": "test-123",
    "speakerName": "John Doe",
    "timestamp": "2026-03-28T15:00:00",
    "new_text": "Hello everyone",
    "transcript": "Hello everyone, welcome to the meeting",
    "end_of_turn": false,
    "words": []
  }'
```

**Expected Response:**
```json
{
  "status": "received",
  "bot_id": "test-123"
}
```

**Check Extension:**
- Open Chrome Extension on a Google Meet page
- You should see "Hello everyone" in the "🎙️ Live Transcription" section

---

## 📊 Complete Flow Diagram

```
┌─────────────────────────────────────────────────────────┐
│ 1. You/Client speak in Google Meet                     │
└────────────────┬────────────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────────────────┐
│ 2. Meetstream Bot (joined meeting)                     │
│    - Captures audio                                     │
│    - Uses AssemblyAI/Deepgram streaming transcription  │
└────────────────┬────────────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────────────────┐
│ 3. Meetstream POSTs to YOUR_PUBLIC_URL/webhook          │
│    Payload:                                             │
│    {                                                    │
│      "bot_id": "...",                                   │
│      "speakerName": "John Doe",                         │
│      "transcript": "hello world",                       │
│      "new_text": "world",                               │
│      "end_of_turn": false                               │
│    }                                                    │
└────────────────┬────────────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────────────────┐
│ 4. Your Backend (/webhook endpoint)                    │
│    - Receives JSON                                      │
│    - Extracts transcript data                           │
│    - Broadcasts via WebSocket                           │
└────────────────┬────────────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────────────────┐
│ 5. WebSocket Manager (ws_manager.broadcast)            │
│    Sends to all connected clients:                      │
│    {                                                    │
│      "type": "live_transcript",                         │
│      "speaker": "John Doe",                             │
│      "transcript": "hello world",                       │
│      "new_text": "world",                               │
│      "end_of_turn": false,                              │
│      "timestamp": "..."                                 │
│    }                                                    │
└────────────────┬────────────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────────────────┐
│ 6. Chrome Extension (content.js)                       │
│    - Receives WebSocket message                         │
│    - Calls handleLiveTranscript()                       │
│    - Updates "🎙️ Live Transcription" section           │
│    - Displays: "10:30:45 John Doe: world"              │
└─────────────────────────────────────────────────────────┘
```

---

## 🎨 What You'll See in Extension

```
┌──────────────────────────────────────────────┐
│ SalesStream Overlook              [−] [×]   │
├──────────────────────────────────────────────┤
│                                              │
│ 🎙️ Live Transcription                       │
│ ┌──────────────────────────────────────────┐│
│ │ 10:30:45 John Doe: Hello everyone        ││
│ │ 10:30:48 Jane Smith: Hi John, good...    ││
│ │ 10:30:52 John Doe: Let's discuss the...  ││
│ │ 10:30:55 Jane Smith: Sounds great        ││
│ └──────────────────────────────────────────┘│
│                                              │
│ • Real-time Insights                         │
│ ┌──────────────────────────────────────────┐│
│ │ Listening for conversation context...    ││
│ └──────────────────────────────────────────┘│
│                                              │
│ ● Connected to AI Backend                   │
└──────────────────────────────────────────────┘
```

---

## 🔍 Debugging Checklist

### If no transcripts appear:

1. **Check backend is running:**
   ```bash
   curl http://localhost:8000/health
   ```

2. **Check webhook is accessible (if deployed):**
   ```bash
   curl YOUR_PUBLIC_URL/webhook
   ```

3. **Check backend logs:**
   ```bash
   tail -f /tmp/backend.log
   # Look for: "Received live transcription from bot..."
   ```

4. **Check extension WebSocket connection:**
   - Open Chrome DevTools (F12)
   - Go to Console
   - Look for: "[WebSocket] Connected to Meetstream AI backend"

5. **Check Meetstream bot status:**
   - Visit Meetstream dashboard
   - Verify bot joined the meeting
   - Check if transcription is enabled

6. **Test webhook manually:**
   ```bash
   curl -X POST YOUR_PUBLIC_URL/webhook \
     -H "Content-Type: application/json" \
     -d '{"bot_id":"test","speakerName":"Test","transcript":"test"}'
   ```

---

## 📋 What I Need from You

1. **Deploy backend** to get a public URL (Railway, Render, Fly, or ngrok)
2. **Share the public URL** with me (e.g., `https://your-app.railway.app`)
3. **Or** tell me which deployment method you prefer and I'll help

Once you have the public URL, the webhook URL for Meetstream will be:

```
YOUR_PUBLIC_URL/webhook
```

For example:
- If Railway: `https://your-app.railway.app/webhook`
- If Render: `https://your-backend.onrender.com/webhook`
- If ngrok: `https://abc123.ngrok-free.app/webhook`

---

## 🚀 Quick Start Commands

```bash
# Backend is already running!
# Just need to deploy or expose it

# Option 1: Railway
cd backend && railway init && railway up

# Option 2: Get valid ngrok token from dashboard.ngrok.com
ngrok config add-authtoken YOUR_TOKEN
ngrok http 8000

# Option 3: Deploy to Render.com
# Use web interface: render.com → New Web Service
```

**Once deployed, give me the URL and I'll create the final Meetstream bot configuration for you!** 🎉

---

## 📞 Current Backend Status

```
✅ Backend Server: RUNNING (localhost:8000)
✅ Webhook Endpoint: /webhook (READY)
✅ Extension: READY to display
✅ WebSocket Broadcasting: CONFIGURED

❌ Public URL: NOT YET (need deployment)
```

**Everything is ready except the public URL!** Let me know how you want to proceed. 🚀
