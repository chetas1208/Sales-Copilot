# Slack PM Integration - Knowledge Gap Detection System

## Overview

The Meetstream AI backend now includes an intelligent **Knowledge Gap Detection Agent** that monitors live sales conversations and automatically alerts your PM team via Slack when critical unknowns are detected.

## How It Works

### Architecture Flow

```
Live Meeting Transcript
    ↓
Knowledge Gap Agent (AI-powered detection)
    ↓
Critical Unknown Detected?
    ↓ YES
Slack Message → PM Channel
    ↓
PM Responds in Thread
    ↓
Response Auto-Broadcast → Sales Rep Extension
    ↓
Knowledge Base Updated for Future
```

### What Gets Detected

The Knowledge Gap Agent uses GPT-4o to intelligently detect:

✅ **Critical Unknowns (PM Alert Triggered)**
- Product feature questions during deal discussions
- Technical capability inquiries that are deal-blockers
- Pricing/contracting questions with high buying intent
- Competitive comparison questions during evaluation

❌ **Non-Critical (No Alert)**
- General curiosity questions
- Questions the sales rep can answer
- Off-topic or casual conversation
- Previously answered questions

### Smart Detection Criteria

The agent evaluates:
1. **Is this about our product?** (vs. general chat)
2. **Does the sales rep know the answer?** (knowledge base check)
3. **Is this time-sensitive?** (buying intent detection)
4. **What's the urgency level?** (0-10 score)

Only questions scoring **7+ urgency** or marked as **high/critical** trigger PM alerts.

---

## Setup Instructions

### 1. Create Slack App

1. Go to https://api.slack.com/apps
2. Click **"Create New App"** → **"From scratch"**
3. Name: `Meetstream PM Assistant`
4. Choose your workspace

### 2. Configure Bot Permissions

In your Slack app settings:

**OAuth & Permissions** → **Scopes** → Add these Bot Token Scopes:
- `chat:write` - Send messages to channels
- `channels:read` - List channels
- `channels:history` - Read channel messages
- `conversations.connect:write` - Post in threads
- `groups:read` - List private channels (if needed)
- `groups:history` - Read private channel messages (if needed)

### 3. Install App to Workspace

1. Click **"Install to Workspace"**
2. Review permissions and click **"Allow"**
3. Copy the **Bot User OAuth Token** (starts with `xoxb-`)

### 4. Get Channel ID

1. Open Slack
2. Go to your PM channel
3. Right-click the channel name → **"View channel details"**
4. Scroll down, copy the **Channel ID** (starts with `C`)

### 5. Configure Environment Variables

Edit `/backend/.env`:

```bash
# Slack Integration
SLACK_BOT_TOKEN=your_slack_bot_token_here
SLACK_SIGNING_SECRET=your_slack_signing_secret_here
SLACK_PM_CHANNEL_ID=your_slack_channel_id_here
```

### 6. Install Dependencies

```bash
cd backend
pip install slack-sdk==3.33.4
```

### 7. Restart Backend

```bash
# Kill existing server
lsof -ti:8000 | xargs kill -9

# Start with new configuration
python3 -m uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### 8. Verify Installation

Check that the Knowledge Gap Agent is loaded:

```bash
curl http://localhost:8000/health
```

You should see:
```json
{
  "status": "healthy",
  "agents_status": {
    "loaded_agents": [
      "research",
      "social_intelligence",
      "review_analysis",
      "conversation",
      "strategy",
      "knowledge_gap"  ✅
    ]
  }
}
```

---

## Usage

### Automatic Operation

The Knowledge Gap Agent runs automatically during live meetings. No manual intervention needed.

**When a prospect asks:**
> "Can your platform integrate with Salesforce using custom objects?"

**If critical (high urgency + buying intent):**

1. 🤖 **Agent detects** knowledge gap
2. 📨 **Slack alert sent** to PM channel with:
   - Prospect's exact question
   - Meeting context (company, attendees)
   - AI-suggested answer
   - Urgency indicator (🔴 Critical / 🟡 Moderate / 🟢 Low)
3. 👤 **PM responds** in Slack thread
4. 📡 **Response auto-broadcasts** to sales rep's Chrome extension
5. 💾 **Answer stored** in knowledge base for future meetings

### Example Slack Message

```
🔴 Knowledge Gap Detected

Company: Acme Corp
Urgency: 9/10 🔴
Category: Integration
Attendees: John (CEO), Sarah (CTO)

Prospect's Question:
> "Can your platform integrate with Salesforce using custom objects?"

Why This Is Critical:
Prospect is evaluating against competitor. This is a potential deal-blocker
during technical evaluation phase.

AI-Suggested Response:
```
Yes, our platform supports Salesforce integration including custom objects
via our Enterprise API. We use OAuth 2.0 and support bi-directional sync
with field-level mapping.
```

[Join Meeting] button
```

**PM responds in thread:**
> "Yes confirmed! We support custom objects via our Enterprise API. Here's our integration doc: [link]. The sales team can also offer a demo of the Salesforce sync."

**Sales rep sees in extension overlay:**
> ✅ **PM Response Received**
> "Yes confirmed! We support custom objects via our Enterprise API..."

---

## Testing Without Slack

The system works in **mock mode** if Slack credentials are not configured:

```python
# Mock mode (no SLACK_BOT_TOKEN)
# - Logs Slack messages to console
# - Tracks "fake" threads
# - Doesn't actually send to Slack
# - Good for testing the detection logic
```

To test mock mode:
1. Don't set SLACK_BOT_TOKEN in .env
2. Restart backend
3. Trigger knowledge gap (see below)
4. Check logs for "MOCK SLACK MESSAGE"

---

## Testing the Integration

### Method 1: WebSocket Test (Recommended)

Create a test WebSocket client:

```python
import asyncio
import websockets
import json

async def test_knowledge_gap():
    uri = "ws://localhost:8000/ws"

    async with websockets.connect(uri) as websocket:
        # Simulate company research
        await websocket.send(json.dumps({
            "type": "start_research",
            "data": {
                "company_url": "https://stripe.com",
                "competitor_urls": []
            }
        }))

        # Wait for research to complete
        await asyncio.sleep(5)

        # Simulate prospect asking a critical question
        await websocket.send(json.dumps({
            "type": "live_transcript",
            "data": {
                "transcript": "Can you integrate with our SAP system using custom middleware?",
                "speaker": "prospect",
                "timestamp": "2026-03-28T12:00:00Z"
            }
        }))

        # Listen for responses
        for i in range(10):
            response = await websocket.recv()
            data = json.loads(response)
            print(f"Received: {data.get('type')}")

            if data.get('type') == 'knowledge_gap':
                print("✅ PM was notified!")
                print(f"Question: {data.get('metadata', {}).get('exact_question')}")
                break

        await asyncio.sleep(2)

asyncio.run(test_knowledge_gap())
```

### Method 2: Direct Agent Test

```python
from agents.knowledge_gap_agent import KnowledgeGapAgent
from services.openai_client import get_openai_client

async def test_agent():
    client = get_openai_client()
    agent = KnowledgeGapAgent(client)

    # Test transcript
    result = await agent.analyze_for_knowledge_gap(
        transcript="Does your product support real-time webhooks for order updates? We need this for our ERP integration.",
        speaker="prospect",
        company_info={"company_name": "Acme Corp"},
        conversation_context=[]
    )

    print(f"Is product question: {result.get('is_product_question')}")
    print(f"Is knowledge gap: {result.get('is_knowledge_gap')}")
    print(f"Criticality: {result.get('criticality')}")
    print(f"Urgency score: {result.get('urgency_score')}/10")
    print(f"Should notify PM: {agent.should_notify_pm(result)}")

asyncio.run(test_agent())
```

### Method 3: REST API Test

```bash
# Start a mock meeting
curl -X POST http://localhost:8000/api/mock/meeting-start \
  -H "Content-Type: application/json" \
  -d '{
    "company_name": "Test Corp",
    "meeting_url": "https://meet.google.com/abc-defg-hij"
  }'

# Simulate transcript with knowledge gap
curl -X POST http://localhost:8000/webhook \
  -H "Content-Type: application/json" \
  -d '{
    "transcript": "Can your API handle more than 100k requests per minute with SLA guarantees?",
    "speaker": "prospect",
    "bot_id": "test-bot-123"
  }'
```

---

## Configuration Options

### Urgency Thresholds

Edit `knowledge_gap_agent.py` to adjust sensitivity:

```python
def should_notify_pm(self, analysis: Dict[str, Any]) -> bool:
    criticality = analysis.get('criticality', 'none')
    urgency = analysis.get('urgency_score', 0)

    # Adjust these thresholds
    if criticality in ['high', 'critical']:  # Current: high/critical only
        return True

    if urgency >= 7:  # Current: 7+, adjust to 6 for more alerts
        return True

    return False
```

### Knowledge Base Integration

To connect ChromaDB for knowledge lookup:

```python
# In agent_orchestrator.py _load_agents()
from services.chromadb_service import ChromaDBService

chromadb = ChromaDBService()
self.agents["knowledge_gap"] = KnowledgeGapAgent(
    self.openai_client,
    knowledge_base_service=chromadb  # Enable KB lookup
)
```

### Slack Message Format

Customize the Slack message in `knowledge_gap_agent.py` → `format_slack_message()`:

```python
# Add custom fields
"fields": [
    {
        "type": "mrkdwn",
        "text": f"*Deal Size:*\n${deal_size}"  # Add custom data
    }
]
```

---

## Monitoring & Debugging

### Check Agent Status

```bash
curl http://localhost:8000/health | jq '.agents_status'
```

### View Active Slack Threads

```python
# In Python console
from services.slack_service import SlackService

slack = SlackService()
active_threads = slack.get_active_threads()
print(f"Active threads: {len(active_threads)}")

for thread_ts, info in active_threads.items():
    print(f"Thread: {thread_ts}")
    print(f"Status: {info['status']}")
    print(f"Question: {info['question'][:50]}")
```

### Backend Logs

```bash
# Watch logs for knowledge gaps
tail -f /tmp/backend_test.log | grep "CRITICAL KNOWLEDGE GAP"

# Watch logs for Slack messages
tail -f /tmp/backend_test.log | grep "Slack message sent"
```

### Test Slack Connection

```python
from services.slack_service import SlackService

slack = SlackService()

# Check if configured
print(f"Slack configured: {slack.is_configured()}")

# Send test message
await slack.send_test_message("Test from Meetstream AI")
```

---

## Troubleshooting

### Issue: Agent not loaded

**Symptom:** `loaded_agents` doesn't include `knowledge_gap`

**Solution:**
```bash
# Check for import errors
cd backend
python3 -c "from agents.knowledge_gap_agent import KnowledgeGapAgent; print('OK')"

# Restart backend
lsof -ti:8000 | xargs kill -9
python3 -m uvicorn main:app --reload
```

### Issue: Slack messages not sending

**Symptom:** Logs show "Slack client not initialized"

**Solution:**
1. Verify `.env` has correct `SLACK_BOT_TOKEN`
2. Ensure token starts with `xoxb-`
3. Check bot has permissions (see Setup step 2)
4. Restart backend after adding credentials

### Issue: PM responses not reaching sales rep

**Symptom:** PM replies in Slack but sales rep doesn't see it

**Solution:**
1. Check WebSocket connection is active
2. Verify `_monitor_thread()` is running (check logs)
3. Increase monitoring duration (default 30 min):
   ```python
   await self._monitor_thread(thread_ts, max_duration=3600)  # 1 hour
   ```

### Issue: Too many / too few alerts

**Symptom:** PM getting spammed OR missing important questions

**Solution: Adjust urgency threshold**
```python
# knowledge_gap_agent.py

# For MORE alerts (lower bar)
if urgency >= 5:  # Changed from 7
    return True

# For FEWER alerts (higher bar)
if urgency >= 9 and criticality == 'critical':  # Stricter
    return True
```

---

## API Reference

### New WebSocket Message Types

#### `knowledge_gap_detected`

Sent when PM is notified of critical unknown.

```json
{
  "type": "knowledge_gap_detected",
  "data": {
    "question": "Can you integrate with SAP?",
    "status": "notified",
    "slack_thread": "1234567890.123456",
    "timestamp": "2026-03-28T12:00:00Z"
  }
}
```

#### `pm_response_received`

Sent when PM responds in Slack thread.

```json
{
  "type": "pm_response_received",
  "data": {
    "original_question": "Can you integrate with SAP?",
    "response_text": "Yes, we have native SAP integration...",
    "pm_user": "U01234567",
    "timestamp": "2026-03-28T12:05:00Z"
  },
  "metadata": {
    "thread_ts": "1234567890.123456",
    "answered_at": "2026-03-28T12:05:00Z"
  }
}
```

#### `product_question`

Sent for non-critical product questions (no PM alert).

```json
{
  "type": "insight",
  "insight_type": "product_question",
  "title": "Product Question Detected",
  "content": "AI-suggested answer here...",
  "source": "Knowledge Gap Agent",
  "priority": "normal"
}
```

---

## Architecture Details

### Files Created/Modified

**New Files:**
- `backend/agents/knowledge_gap_agent.py` (460 lines) - Core detection logic
- `backend/services/slack_service.py` (380 lines) - Slack integration
- `SLACK_PM_INTEGRATION_README.md` (this file) - Documentation

**Modified Files:**
- `backend/services/agent_orchestrator.py` - Added knowledge gap agent integration
- `backend/services/websocket_manager.py` - Added PM communication methods
- `backend/.env.example` - Added Slack configuration
- `backend/requirements.txt` - Added slack-sdk dependency

### Agent Orchestrator Integration

The Knowledge Gap Agent runs in parallel with the Conversation Agent:

```python
# In process_transcript()
tasks = [
    _run_conversation_agent(...),    # Objection detection
    _run_knowledge_gap_agent(...)    # Knowledge gap detection
]
await asyncio.gather(*tasks)  # Run concurrently
```

### Slack Thread Monitoring

The Slack service automatically monitors threads for PM responses:

1. Send Slack message → Get `thread_ts`
2. Start background monitoring task
3. Poll every 5 seconds for new replies
4. When PM responds → Broadcast to WebSocket
5. Store answer in knowledge base (TODO)
6. Stop monitoring after 30 minutes

---

## Roadmap

### ✅ Implemented (v1.0)
- Knowledge gap detection with GPT-4o
- Slack integration with formatted messages
- PM response monitoring and broadcast
- WebSocket integration with Chrome extension
- Mock mode for testing without Slack
- Urgency scoring and criticality assessment

### 🚧 Planned (v1.1)
- [ ] Store PM responses in ChromaDB knowledge base
- [ ] Auto-answer future questions from KB
- [ ] Analytics dashboard for knowledge gaps
- [ ] Slack slash commands for KB search
- [ ] Multi-language support
- [ ] Integration with CRM for deal context

### 💡 Future Ideas
- Custom PM routing rules (technical questions → tech PM, pricing → revenue PM)
- Slack threads → Battle cards generator
- Auto-generate product docs from PM responses
- Knowledge gap trends and reporting

---

## Support

For issues or questions:
1. Check logs: `tail -f /tmp/backend_test.log`
2. Test agent: `python3 -c "from agents.knowledge_gap_agent import KnowledgeGapAgent; print('OK')"`
3. Verify Slack: `curl http://localhost:8000/health`
4. Open GitHub issue with logs and error details

---

## License

Part of Meetstream AI - Internal documentation
