# How Meetstream Bot Joining Works - Complete Explanation

**Your Question:** "How do I make sure the bot can join on its own with the same webhook?"

**Short Answer:** The webhook URL is configured ONCE when you create the bot. Every meeting you create, you just need to run the script with the new meeting URL, and Meetstream handles everything automatically.

---

## The Magic: How It Works

### Step 1: You Create a Google Meet Link
```
https://meet.google.com/abc-defg-hij
```

### Step 2: You Run the Bot Creation Command
```bash
./START_BOT_COMMAND.sh https://meet.google.com/abc-defg-hij
```

### Step 3: What Happens Behind the Scenes

```
You (Terminal)
    │
    │ 1. Run script with meeting URL
    │
    ▼
Meetstream API
    │
    │ 2. Creates a virtual bot participant
    │    with webhook: https://signe-untextual-cyrus.ngrok-free.dev/webhook
    │
    ▼
Google Meet
    │
    │ 3. Bot "joins" the meeting as a participant
    │    (appears as "Meetstream AI Transcriber")
    │
    │ 4. Bot starts capturing audio
    │
    ▼
AssemblyAI (Transcription Service)
    │
    │ 5. Transcribes audio in real-time
    │
    │ 6. Sends webhook to YOUR URL
    │    POST https://signe-untextual-cyrus.ngrok-free.dev/webhook
    │
    ▼
Your Backend (FastAPI)
    │
    │ 7. Receives webhook payload
    │
    │ 8. Logs to console
    │
    │ 9. Broadcasts via WebSocket
    │
    ▼
Chrome Extension
    │
    │ 10. Displays in overlay
    │     - Live Transcription
    │     - Webhook Inspector
```

---

## Key Configuration: The Webhook URL

In your `START_BOT_COMMAND.sh` script (line 30):

```json
{
  "live_transcription_required": {
    "webhook_url": "https://signe-untextual-cyrus.ngrok-free.dev/webhook"
  }
}
```

**This webhook URL is attached to EVERY bot you create with this script.**

### What This Means:

✅ **Same webhook for all meetings**
- Meeting 1: https://meet.google.com/aaa-bbbb-ccc → Uses your webhook
- Meeting 2: https://meet.google.com/xxx-yyyy-zzz → Uses your webhook
- Meeting 3: https://meet.google.com/mmm-nnnn-ooo → Uses your webhook

✅ **Bot automatically joins**
- You don't manually add it
- Meetstream API tells Google Meet to let the bot in
- Bot appears as a participant named "Meetstream AI Transcriber"

✅ **Transcription happens automatically**
- Once bot joins, it starts listening
- AssemblyAI processes audio
- Webhooks flow to your backend

---

## Why "Somehow It's Working" - The Full Picture

### 1. **ngrok Tunnel (Always Active)**
```
Internet Request
    │
    ▼
https://signe-untextual-cyrus.ngrok-free.dev/webhook
    │
    │ (ngrok tunnel)
    │
    ▼
http://localhost:8000/webhook
    │
    ▼
Your FastAPI Backend
```

**Why it works:**
- ngrok creates a public URL that tunnels to your localhost
- Meetstream can send webhooks to this public URL
- Your backend running on port 8000 receives them

### 2. **Bot Creation API (On Demand)**
Every time you run the script:

```bash
./START_BOT_COMMAND.sh https://meet.google.com/new-meeting-link
```

It sends this request:
```bash
curl -X POST https://api.meetstream.ai/api/v1/bots \
  -H "Authorization: Bearer <MEETSTREAM_API_KEY>" \
  -d '{
    "meeting_url": "https://meet.google.com/new-meeting-link",
    "live_transcription_required": {
      "webhook_url": "https://signe-untextual-cyrus.ngrok-free.dev/webhook"
    }
  }'
```

**What Meetstream does:**
1. Creates a virtual participant
2. Makes it join the Google Meet at that URL
3. Configures it to send transcriptions to your webhook
4. Returns a `bot_id` (you see this in webhook payloads)

### 3. **Webhook Flow (Automatic)**
Once bot joins:

```
[Audio from meeting]
    │
    ▼
[Meetstream Bot captures audio]
    │
    ▼
[AssemblyAI transcribes]
    │
    ▼
[Sends POST request with transcript]
    │
    ▼
POST https://signe-untextual-cyrus.ngrok-free.dev/webhook
{
  "bot_id": "29c35114-cefb-4f30-b7c8-3e1fc4828463",
  "speakerName": "jeet shah",
  "transcript": "maybe screenshot",
  "words": [...],
  ...
}
    │
    ▼
[Your backend receives it]
    │
    ▼
[Broadcast to Chrome Extension]
```

---

## For EVERY New Meeting, Here's What You Do

### Method 1: Using the Script (Easiest)
```bash
# 1. Create a new Google Meet
# Go to: https://meet.google.com/new
# Get URL: https://meet.google.com/xyz-abcd-123

# 2. Run the script
cd /Users/jeetshah/Documents/Meetstream\ AI
./START_BOT_COMMAND.sh https://meet.google.com/xyz-abcd-123

# 3. Bot joins automatically!
# Watch for "Meetstream AI Transcriber" in participants
```

### Method 2: Using curl Manually
```bash
MEETING_URL="https://meet.google.com/your-meeting-link"

curl -X POST https://api.meetstream.ai/api/v1/bots \
  -H "Authorization: Bearer <MEETSTREAM_API_KEY>" \
  -H "Content-Type: application/json" \
  -d "{
    \"meeting_url\": \"$MEETING_URL\",
    \"bot_name\": \"Meetstream AI Transcriber\",
    \"live_transcription_required\": {
      \"webhook_url\": \"https://signe-untextual-cyrus.ngrok-free.dev/webhook\"
    }
  }"
```

### Method 3: From Your Backend (Future Enhancement)
You could create an API endpoint:

```python
@app.post("/api/meetstream/create-bot")
async def create_bot_for_meeting(meeting_url: str):
    """Create a Meetstream bot for a new meeting"""
    response = await meetstream_service.create_bot(
        meeting_url=meeting_url,
        webhook_url="https://signe-untextual-cyrus.ngrok-free.dev/webhook"
    )
    return response
```

---

## What You See When Bot Joins

### In Google Meet:
1. A new participant appears: **"Meetstream AI Transcriber"**
2. It has a camera icon (but no video/audio output)
3. It silently listens to the meeting

### In Your Backend Logs:
```
INFO - [WEBHOOK] Received from bot 29c35114-cefb-4f30-b7c8-3e1fc4828463
DEBUG - [WEBHOOK] Full payload: {
  "bot_id": "29c35114-cefb-4f30-b7c8-3e1fc4828463",
  "speakerName": "jeet shah",
  "transcript": "hello everyone",
  ...
}
```

### In Chrome Extension:
- Live Transcription section updates in real-time
- Webhook Inspector shows each payload
- Insights appear as AI processes the conversation

### In ngrok Inspector (http://127.0.0.1:4040):
- You see POST requests coming in
- Full webhook payloads visible
- Response status (200 OK)

---

## The Key: Webhook URL is Configured Per Bot

Each time you create a bot, you specify the webhook URL:

```json
{
  "meeting_url": "https://meet.google.com/DIFFERENT-EACH-TIME",
  "live_transcription_required": {
    "webhook_url": "https://signe-untextual-cyrus.ngrok-free.dev/webhook"  // ← SAME EVERY TIME
  }
}
```

### Analogy:
Think of it like a phone number:

- **Webhook URL** = Your phone number (always the same)
- **Meeting URL** = Different events you're attending
- **Bot** = A reporter you send to each event
- **Reporter calls your number** to report what's happening

Every reporter (bot) knows to call the same number (webhook), but they're at different events (meetings).

---

## What Happens to Old Bots?

When you create a NEW bot for a NEW meeting:

✅ **Old bot stays in old meeting** (if it's still active)
✅ **New bot joins new meeting**
✅ **Both send to same webhook**

Your backend can handle multiple bots simultaneously because each webhook includes `bot_id`:

```json
{
  "bot_id": "bot-1-for-meeting-abc",  // Old meeting
  ...
}

{
  "bot_id": "bot-2-for-meeting-xyz",  // New meeting
  ...
}
```

You can differentiate them in your code:
```python
bot_id = payload.get("bot_id")
if bot_id == "bot-1-for-meeting-abc":
    # Handle meeting 1 transcript
elif bot_id == "bot-2-for-meeting-xyz":
    # Handle meeting 2 transcript
```

---

## Common Questions

### Q: Do I need to create a new webhook for each meeting?
**A:** No! Same webhook URL for all meetings.

### Q: What if my ngrok URL changes?
**A:** You'll need to:
1. Update `START_BOT_COMMAND.sh` with the new ngrok URL
2. Create new bots with the updated URL
3. Old bots will still use the old URL (won't work if ngrok restarted)

### Q: Can I have multiple meetings at once?
**A:** Yes! Each bot sends to the same webhook with different `bot_id`

### Q: How do I stop a bot?
**A:** Call the Meetstream API to delete the bot:
```bash
curl -X DELETE https://api.meetstream.ai/api/v1/bots/{bot_id} \
     -H "Authorization: Bearer <MEETSTREAM_API_KEY>"
```

### Q: What if the meeting ends?
**A:** The bot automatically leaves and stops sending webhooks.

---

## Summary: The "Magic" Explained

1. **You create a Google Meet link** → New meeting URL
2. **You run the bot script** → Tells Meetstream to create a bot
3. **Meetstream creates a virtual participant** → Bot joins the meeting
4. **Bot captures audio** → Sends to AssemblyAI for transcription
5. **AssemblyAI sends webhooks** → To your configured webhook URL
6. **Your backend receives webhooks** → Processes and broadcasts
7. **Chrome extension displays** → Real-time transcripts

**The webhook URL is like your mailbox address - it doesn't change, but different senders (bots) can send mail (webhooks) to it!**

---

## Quick Reference: Creating a Bot for New Meeting

```bash
# Step 1: Get your meeting URL
MEETING_URL="https://meet.google.com/abc-defg-hij"

# Step 2: Create bot
./START_BOT_COMMAND.sh $MEETING_URL

# Step 3: Join the meeting
# Bot will appear as participant

# Step 4: Start talking
# Transcripts flow automatically to your webhook!

# Step 5: View transcripts
# - Chrome Extension overlay
# - Backend logs
# - ngrok inspector (http://127.0.0.1:4040)
```

---

Now that you understand how it works, let's tackle **storing the transcript data** so you can analyze it later!
