# Meetstream AI - Component Summary & Implementation Status

## Quick Overview

**Meetstream AI** is a 3-tier AI-powered sales intelligence system:

1. **Chrome Extension** (Vanilla JavaScript) - Overlays on Google Meet
2. **FastAPI Backend** (Python) - Multi-agent orchestrator with WebSocket server
3. **React Frontend** (TypeScript) - Web dashboard for meeting prep

---

## Component Status Matrix

| Component | Status | Files | Lines | Notes |
|-----------|--------|-------|-------|-------|
| **Backend - Core** | DONE | 1 | 1000+ | main.py fully implemented |
| **WebSocket Manager** | DONE | 1 | 300+ | Complete connection/message handling |
| **Agent Orchestrator** | DONE | 1 | 500+ | Framework complete, agents pluggable |
| **Research Agent** | DONE | 1 | 200+ | Web scraping + GPT-4o analysis |
| **Conversation Agent** | PARTIAL | 1 | 217 | Detection framework ready |
| **Strategy Agent** | PARTIAL | 1 | 123 | Synthesis framework ready |
| **Social Intelligence Agent** | PLACEHOLDER | 1 | 123 | Needs Apify token |
| **Review Analysis Agent** | PLACEHOLDER | 1 | 200+ | Needs scraper enhancement |
| **Extension - Core** | DONE | 3 | 1000+ | Popup + content script complete |
| **Extension - Overlay UI** | DONE | 400+ lines | 400+ | Glassmorphism design implemented |
| **Extension - WebSocket** | DONE | 300+ lines | 300+ | Full client implementation |
| **Frontend - Core** | DONE | 1 | 100+ | App.jsx with routing |
| **Frontend - Login** | DONE | 2 | 100+ | Scalekit SSO integrated |
| **Frontend - Dashboard** | DONE | 1 | 200+ | Main page with quick actions |
| **Frontend - Profile** | DONE | 1 | 300+ | Form collection |
| **Frontend - Meeting Prep** | DONE | 1 | 400+ | Research form, local storage |
| **Frontend - Past Meetings** | DONE | 1 | 300+ | History view with placeholders |
| **Scalekit OAuth2** | DONE | 1 | 200+ | Full SSO integration |
| **MCP Web Scraper** | DONE | 1 | 200+ | Playwright-based scraping |
| **OpenAI Client** | DONE | 1 | 100+ | GPT-4o wrapper |

**Legend**: DONE (fully implemented) | PARTIAL (framework + core logic) | PLACEHOLDER (structure only)

---

## Key File Locations

### Backend
```
backend/
├── main.py                                    # FastAPI app + endpoints
├── services/
│   ├── websocket_manager.py                   # WebSocket management
│   ├── agent_orchestrator.py                  # Multi-agent coordination
│   ├── openai_client.py                       # GPT-4o wrapper
│   ├── scalekit_auth.py                       # OAuth2 SSO
│   ├── meetstream_service.py                  # Meetstream bot control
│   ├── assemblyai_service.py                  # Transcription service
│   └── claude_client.py                       # Claude integration (future)
├── agents/
│   ├── research_agent.py                      # Website analysis (DONE)
│   ├── conversation_agent.py                  # Real-time analysis (PARTIAL)
│   ├── social_intelligence_agent.py           # LinkedIn insights (PLACEHOLDER)
│   ├── review_analysis_agent.py               # Sentiment analysis (PLACEHOLDER)
│   └── strategy_agent.py                      # Synthesis (PLACEHOLDER)
├── mcp_servers/
│   └── web_scraper_mcp/server.py              # Web scraping
├── requirements.txt                           # Dependencies
├── .env.example                               # Config template
└── start.sh                                   # Startup script
```

### Frontend
```
frontend/
├── src/
│   ├── App.jsx                                # Main router
│   ├── main.jsx                               # Entry point
│   ├── pages/
│   │   ├── Login.tsx                          # Scalekit SSO
│   │   ├── AuthCallback.jsx                   # OAuth handler
│   │   ├── Dashboard.jsx                      # Main page
│   │   ├── ProfileSetup.jsx                   # User config
│   │   ├── MeetingPrep.jsx                    # Research form
│   │   └── PastMeetings.jsx                   # History
│   ├── components/
│   │   ├── Navbar.jsx                         # Navigation
│   │   └── ui/                                # UI primitives
│   └── services/
│       └── api.js                             # Axios client
├── package.json                               # Dependencies
├── vite.config.ts                             # Build config
├── tailwind.config.js                         # Styling config
└── postcss.config.js                          # PostCSS config
```

### Chrome Extension
```
salesstream-extension/
├── manifest.json                              # Extension manifest (MV3)
├── content.js                                 # Content script
├── popup.html                                 # Popup UI
├── popup.js                                   # Popup logic
├── styles.css                                 # Popup styles
├── README.md                                  # Extension docs
└── icons/                                     # Extension icons
    ├── icon16.png
    ├── icon48.png
    └── icon128.png
```

---

## Data Connections

### Extension ↔ Backend
```javascript
WebSocket: ws://localhost:8000/ws

MESSAGE FLOW:
Extension sends: {type: "start_research", company_url, competitor_urls}
Backend receives: route to handle_start_research()
Backend sends: {type: "insight", insight_type, title, content, ...}
Extension receives: render in overlay dynamically
```

### Frontend ↔ Backend
```javascript
REST API: http://localhost:8000/api/*

ENDPOINTS:
POST   /api/research              → Start research job
POST   /api/profile               → Save user profile
GET    /api/profile/{userId}      → Load user profile
POST   /api/meeting-prep          → Save meeting prep
GET    /api/meetings/{userId}     → Get past meetings
POST   /api/linkedin/profile      → Fetch LinkedIn (Apify)
GET    /auth/scalekit/login       → OAuth flow
```

### Agent Orchestration
```python
PARALLEL EXECUTION (asyncio.gather):
- ResearchAgent.analyze_website(company_url)
- SocialIntelligenceAgent.analyze_company()
- ReviewAnalysisAgent.analyze_reviews()
- ResearchAgent.analyze_website(competitor_urls)  # per competitor

THEN:
- StrategyAgent.synthesize(all_results)

RESULT:
Each agent sends insights via ws_manager.send_insight()
Extension displays in real-time as insights arrive
```

---

## What's Working Now

### FULLY FUNCTIONAL:
- [x] Chrome Extension injects overlay on Google Meet
- [x] Extension popup collects company URLs
- [x] Extension WebSocket connects to backend
- [x] Backend WebSocket server accepts connections
- [x] Research Agent scrapes websites + analyzes with GPT-4o
- [x] Real-time insights sent to extension via WebSocket
- [x] Extension overlay displays insights dynamically
- [x] Frontend dashboard loads (React + React Router)
- [x] Scalekit SSO login/logout implemented
- [x] Profile setup form collects user info
- [x] Meeting prep form collects prospect details
- [x] API endpoints for profile/meetings (in-memory storage)
- [x] Keep-alive ping mechanism (30-second heartbeat)
- [x] Connection status indicator in overlay
- [x] Draggable/minimizable overlay controls

### MOSTLY WORKING (requires tokens/config):
- [~] Conversation Agent (detection logic in place, needs transcript feed)
- [~] Strategy Agent (framework ready, needs orchestrator to call it)
- [~] Social Intelligence Agent (needs APIFY_TOKEN)
- [~] Review Analysis Agent (needs web scraper MCP enhancement)

### NOT IMPLEMENTED YET:
- [ ] Real Meetstream bot integration (API exists, needs testing)
- [ ] AssemblyAI transcription (service structure exists)
- [ ] Database persistence (using in-memory dicts)
- [ ] Frontend form validation
- [ ] Error handling & logging infrastructure
- [ ] Unit tests & integration tests
- [ ] Production deployment configs

---

## How to Use Each Component

### 1. Start Backend
```bash
cd backend
cp .env.example .env
# Edit .env and add: OPENAI_API_KEY=<your_openai_api_key_here>
python main.py
# Runs on http://localhost:8000
```

### 2. Start Frontend
```bash
cd frontend
npm install  # if needed
npm run dev
# Runs on http://localhost:5173
```

### 3. Install Extension
```
1. Go to chrome://extensions/
2. Enable "Developer mode"
3. Click "Load unpacked"
4. Select /salesstream-extension folder
5. Open Google Meet tab
6. Click extension icon to open popup
```

### 4. Use Extension
```
1. Enter company website: https://example.com
2. Enter competitors (optional)
3. Click "Start Research"
4. See overlay appear with insights in real-time
5. Insights update as agents complete
```

### 5. Use Frontend
```
1. Go to http://localhost:5173
2. Click "Login with Scalekit"
3. Authenticate with email
4. See Dashboard
5. Click "Start Meeting Prep" to research prospects
6. Click "Browse Meetings" to view history
```

---

## Important Dependencies

### Backend
- **FastAPI** - Web framework
- **Uvicorn** - ASGI server
- **WebSockets** - WebSocket support
- **OpenAI** - GPT-4o API client
- **Scalekit SDK** - OAuth2 SSO
- **Playwright** - Web scraping
- **Beautiful Soup** - HTML parsing

### Frontend
- **React** - UI library
- **React Router** - Routing
- **Axios** - HTTP client
- **Tailwind CSS** - Styling
- **Scalekit React SDK** - SSO
- **Vite** - Build tool

### Extension
- **Vanilla JavaScript** - No dependencies
- **Chrome APIs** - Native browser APIs

---

## Configuration Required

### Required (Backend)
```env
OPENAI_API_KEY=<your_openai_api_key_here>  # Get from OpenAI
SCALEKIT_CLIENT_ID=...                  # Get from Scalekit
SCALEKIT_CLIENT_SECRET=...              # Get from Scalekit
SCALEKIT_ENVIRONMENT_URL=...            # Get from Scalekit
```

### Optional (Backend)
```env
APIFY_TOKEN=...                         # For LinkedIn scraping
DEBUG=True                              # Enable debug logging
PORT=8000                               # Server port
HOST=0.0.0.0                           # Server host
```

### Frontend (Auto-configured)
```
API_BASE_URL=http://localhost:8000      # Backend URL
```

### Extension (Hard-coded)
```javascript
backendUrl = 'ws://localhost:8000/ws'   # WebSocket URL
```

---

## Common Tasks

### Add a New API Endpoint
```python
# In backend/main.py
@app.post("/api/new-endpoint")
async def new_endpoint(payload: Dict[str, Any]):
    # Process request
    return {"status": "success", "data": result}

# In frontend/src/services/api.js
newEndpoint: (data) => api.post('/api/new-endpoint', data)

# In component
const response = await apiService.newEndpoint(data)
```

### Add a New Agent
```python
# Create backend/agents/my_agent.py
class MyAgent:
    async def execute(self, input_data):
        # Process with GPT-4o
        result = await self.openai_client.create_message(...)
        return result

# Register in backend/services/agent_orchestrator.py
self.agents = {
    "my_agent": MyAgent(self.openai_client),
    ...
}

# Call from orchestrator
await self._run_my_agent(websocket, job_id)
```

### Modify Overlay UI
```javascript
// In salesstream-extension/content.js

// 1. Modify HTML in createOverlayElement()
overlay.innerHTML = `
  <div class="new-section">...</div>
`

// 2. Add CSS in getOverlayStyles()
.new-section {
  /* styles */
}

// 3. Add handler for new message type
case 'new_insight':
  this.handleNewInsight(message)
  break

// 4. Implement handler
handleNewInsight(message) {
  // Update overlay
}
```

---

## Testing the System

### Test Extension Connection
```javascript
// In browser console on Google Meet
console.log('WebSocket state:', wsManager.ws.readyState)
// 0 = connecting, 1 = open, 2 = closing, 3 = closed
```

### Test Backend API
```bash
curl http://localhost:8000/health
# Should return: {"status": "healthy", ...}
```

### Test Frontend Auth
```javascript
// In browser console
localStorage.getItem('user')
// Should show user object if logged in
```

### Test Research Job
```bash
curl -X POST http://localhost:8000/api/research \
  -H "Content-Type: application/json" \
  -d '{
    "company_url": "https://example.com",
    "competitor_urls": []
  }'
```

---

## Performance Notes

### Parallel Execution
- Agents run in **parallel** with `asyncio.gather()`
- Typical research job: 30-60 seconds (depends on website size)
- Multiple jobs can run simultaneously

### WebSocket Broadcasting
- Messages are sent **immediately** as agents complete
- No queuing or batching
- Real-time updates to extension overlay

### Memory Usage
- **In-memory storage** for profiles/meetings (no database)
- ~100MB RAM for backend with typical load
- Extension uses <5MB RAM

---

## Next Steps to Complete

### Critical (For production):
1. [ ] Add database (PostgreSQL/MongoDB)
2. [ ] Implement error handling (Sentry)
3. [ ] Add authentication token refresh
4. [ ] Unit tests for agents
5. [ ] Rate limiting for APIs

### Important (For better UX):
1. [ ] Form validation (frontend)
2. [ ] Loading states & spinners
3. [ ] Error notifications
4. [ ] User profile persistence
5. [ ] Meeting history with search

### Nice-to-have (For features):
1. [ ] Meetstream real-time transcription
2. [ ] Post-call summaries
3. [ ] CRM integrations (Salesforce)
4. [ ] Battle card builder
5. [ ] Team collaboration

---

## Documentation Files

- **README.md** - Project overview
- **QUICK_START.md** - Setup instructions
- **FRONTEND_GUIDE.md** - Frontend architecture
- **COMPLETE_SYSTEM_GUIDE.md** - Full system docs
- **SCALEKIT_SETUP_GUIDE.md** - SSO configuration
- **CODEBASE_MAP.md** - This file (detailed architecture)
- **ARCHITECTURE_VISUAL.txt** - ASCII diagrams

---

## Support

For issues:
1. Check backend logs: `tail -f backend/nohup.out`
2. Check extension console: Right-click on Google Meet tab → Inspect → Console
3. Check frontend console: Browser dev tools → Console
4. Verify environment variables: `cat backend/.env | grep -v "#"`
5. Test health endpoint: `curl http://localhost:8000/health`
