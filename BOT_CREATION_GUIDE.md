# Meetstream Bot Creation - Complete Guide

## Overview

Your Chrome extension now has **one-click bot creation** functionality! When you're on a Google Meet call, you can instantly create a Meetstream bot that joins the meeting and provides real-time transcription.

## How It Works

### 1. **User Flow**
```
User joins Google Meet
  → Opens Chrome Extension Popup
  → Clicks "Start Recording Bot"
  → Extension fetches current Meet URL
  → API call to backend creates bot
  → Bot joins meeting with live transcription
  → Transcripts appear in overlay
```

### 2. **Architecture**

```
Chrome Extension (popup.js)
  ↓ (fetches current tab URL)
  ↓ (POST request)
Backend API (/api/meetstream/start-bot)
  ↓ (calls Meetstream API)
Meetstream Service (meetstream_service.py)
  ↓ (creates bot session)
Meetstream API
  ↓ (bot joins Google Meet)
Google Meet
  ↓ (sends audio/transcripts via webhook)
Backend Webhook (/webhook)
  ↓ (broadcasts via WebSocket)
Chrome Extension Overlay (content.js)
  ↓ (displays live transcripts)
```

## Files Modified

### 1. **salesstream-extension/popup.html**
- Added new "Bot Control" section
- Added "Start Recording Bot" button
- Added bot status message display area

### 2. **salesstream-extension/popup.js**
- Added `startBotBtn` click handler
- Implemented automatic Google Meet URL detection
- Added API call to `/api/meetstream/start-bot`
- Added error handling and status messages
- Notifies content script when bot starts

### 3. **salesstream-extension/content.js**
- Added `BOT_STARTED` message handler
- Updates overlay status when bot is created
- Shows bot ID in the connection status

### 4. **salesstream-extension/manifest.json**
- Added `"tabs"` permission for URL access
- Added `"http://localhost:8000/*"` to host_permissions for API calls

## Usage Instructions

### Step 1: Start Your Backend
```bash
cd backend
python3 -m uvicorn main:app --reload
```

Make sure your `.env` file has:
```
MEETSTREAM_API_KEY=your_api_key_here
```

### Step 2: Load the Extension
1. Open Chrome and go to `chrome://extensions/`
2. Enable "Developer mode"
3. Click "Load unpacked"
4. Select the `salesstream-extension` folder

### Step 3: Join a Google Meet
1. Go to any Google Meet call (or create a test meeting)
2. Make sure you're on a URL like: `https://meet.google.com/abc-defg-hij`

### Step 4: Start the Bot
1. Click the extension icon (puzzle piece in Chrome toolbar)
2. Click the **"Start Recording Bot"** button
3. Wait for confirmation message: "Bot started! ID: xxxxxxxx..."
4. The bot will join your meeting within ~10 seconds

### Step 5: View Live Transcripts
- Open the glassmorphism overlay on your Meet page
- Watch live transcripts appear in real-time
- Check the "Webhook Inspector" to see raw webhook data

## API Endpoint Details

### POST `/api/meetstream/start-bot`

**Request Body:**
```json
{
  "meeting_url": "https://meet.google.com/abc-defg-hij",
  "bot_name": "Meetstream AI Transcriber",
  "video_required": true
}
```

**Response (Success):**
```json
{
  "bot_id": "bot_xxxxxxxxxxxxxxxxxx",
  "meeting_url": "https://meet.google.com/abc-defg-hij",
  "webhook_url": "http://localhost:8000/webhook",
  "status": "started",
  "live_transcription_enabled": true,
  "assemblyai_streaming_config": "48kHz PCM with VAD"
}
```

**Response (Error):**
```json
{
  "detail": "Meetstream not configured. Please add MEETSTREAM_API_KEY to environment variables."
}
```

## Backend Service Layer

The bot creation is handled by `MeetstreamService.start_bot()` located at:
- **File:** `backend/services/meetstream_service.py`
- **Line:** 50-155

**What it does:**
1. Validates Meetstream API configuration
2. Constructs payload with AssemblyAI streaming config
3. Calls Meetstream API `/bots/create_bot`
4. Stores bot session in memory
5. Returns bot details including bot_id and webhook URL

## Troubleshooting

### "Please open a Google Meet page first!"
- Make sure you're on an actual meeting page, not just meet.google.com homepage
- URL must match pattern: `meet.google.com/[meeting-code]`

### "Failed to start bot. Check backend!"
- Ensure backend is running at `http://localhost:8000`
- Check backend console for error logs
- Verify `MEETSTREAM_API_KEY` is set in `.env`

### "Meetstream not configured"
- Add `MEETSTREAM_API_KEY=ms_xxxxxx` to your `.env` file
- Restart the backend server

### Bot doesn't join the meeting
- Check if the meeting link is valid and active
- Verify bot was created by checking backend logs
- Look for bot creation response with valid `bot_id`
- Meeting might require approval - check Google Meet for join requests

### No transcripts appearing
- Verify webhook URL is accessible (use ngrok if testing remotely)
- Check WebSocket connection in overlay status bar
- Open browser DevTools Console to see WebSocket messages
- Check backend logs for incoming webhook requests

## Testing Without a Real Meeting

You can test bot creation on the Google Meet homepage:
1. Go to `https://meet.google.com/abc-test-meeting` (fake URL)
2. The extension will try to create a bot
3. It may fail to join, but you can verify the API call works

## Next Steps

### Enhancement Ideas:
1. **Add Stop Bot Button** - Allow users to stop the bot from the extension
2. **Bot Status Indicator** - Show if bot is active, joining, or disconnected
3. **Multiple Meeting Support** - Track multiple bots across different meetings
4. **Bot Configuration** - Allow users to customize bot name and settings
5. **Recording Download** - Add option to download meeting transcripts

### Code Locations for Enhancements:

**Add Stop Bot Button:**
- Modify: `salesstream-extension/popup.html` (add button)
- Modify: `salesstream-extension/popup.js` (add click handler calling `/api/meetstream/stop-bot/{bot_id}`)

**Bot Status Tracking:**
- Modify: `salesstream-extension/popup.js` (poll `/api/meetstream/bot-status/{bot_id}`)
- Display status in popup UI

## Code Snippets

### Manual Bot Creation (Alternative to Extension)

**Using curl:**
```bash
curl -X POST http://localhost:8000/api/meetstream/start-bot \
  -H "Content-Type: application/json" \
  -d '{
    "meeting_url": "https://meet.google.com/YOUR-MEETING-CODE",
    "bot_name": "Meetstream AI Transcriber"
  }'
```

**Using Python:**
```python
import requests

response = requests.post(
    "http://localhost:8000/api/meetstream/start-bot",
    json={
        "meeting_url": "https://meet.google.com/abc-defg-hij",
        "bot_name": "My Custom Bot"
    }
)
print(response.json())
```

## Summary

✅ **What's Working:**
- One-click bot creation from Chrome extension
- Automatic Google Meet URL detection
- Bot joins meeting with live transcription
- Real-time transcript display in overlay
- Webhook inspector for debugging

🎉 **You can now create bots easily without manually calling APIs or using shell scripts!**
