# Meetstream AI - Complete Codebase Architecture Map

## Project Overview
Meetstream AI is a multi-agent AI-powered sales intelligence platform with three main components:
1. **Backend**: FastAPI + Multi-agent AI orchestrator (Python)
2. **Frontend**: React dashboard for meeting prep (TypeScript/JSX)
3. **Chrome Extension**: Real-time overlay during Google Meet calls (JavaScript)

---

## Directory Structure

```
/Users/jeetshah/Documents/Meetstream AI/
├── backend/                          # Python FastAPI backend
│   ├── main.py                      # FastAPI app (primary entry point)
│   ├── requirements.txt              # Python dependencies
│   ├── .env                          # Configuration (GITIGNORED)
│   ├── .env.example                  # Template for .env
│   │
│   ├── services/                    # Core service modules
│   │   ├── websocket_manager.py     # Manages WebSocket connections
│   │   ├── agent_orchestrator.py    # Coordinates multi-agent execution
│   │   ├── openai_client.py         # OpenAI/GPT-4o wrapper
│   │   ├── claude_client.py         # Claude API integration (placeholder)
│   │   ├── scalekit_auth.py         # OAuth2 SSO authentication
│   │   ├── meetstream_service.py    # Meetstream bot integration
│   │   └── assemblyai_service.py    # Real-time transcription service
│   │
│   ├── agents/                      # AI Agent modules
│   │   ├── research_agent.py        # Website scraping & analysis
│   │   ├── social_intelligence_agent.py  # LinkedIn insights
│   │   ├── review_analysis_agent.py     # Customer sentiment analysis
│   │   ├── conversation_agent.py    # Real-time transcript analysis
│   │   └── strategy_agent.py        # Synthesis & recommendations
│   │
│   ├── mcp_servers/                 # MCP (Model Context Protocol) implementations
│   │   └── web_scraper_mcp/
│   │       ├── server.py            # Web scraping MCP server
│   │       └── __init__.py
│   │
│   ├── start.sh                     # Backend startup script
│   ├── start.bat                    # Windows startup script
│   └── INTEGRATION_README.md         # Integration documentation
│
├── frontend/                         # React TypeScript dashboard
│   ├── src/
│   │   ├── App.jsx                  # Main app router (Auth + Routes)
│   │   ├── main.jsx                 # Vite entry point
│   │   │
│   │   ├── pages/                   # Page components
│   │   │   ├── Login.tsx            # Login page with Scalekit SSO
│   │   │   ├── AuthCallback.jsx     # OAuth callback handler
│   │   │   ├── Dashboard.jsx        # Main dashboard with quick actions
│   │   │   ├── ProfileSetup.jsx     # User profile configuration
│   │   │   ├── MeetingPrep.jsx      # Prospect research & prep
│   │   │   └── PastMeetings.jsx     # Meeting history & insights
│   │   │
│   │   ├── components/
│   │   │   ├── Navbar.jsx           # Navigation bar
│   │   │   └── ui/                  # UI components (shadcn-style)
│   │   │       ├── button.tsx
│   │   │       ├── input.tsx
│   │   │       ├── label.tsx
│   │   │       ├── login-card.tsx
│   │   │       └── gaming-login.tsx
│   │   │
│   │   ├── services/
│   │   │   └── api.js               # Axios client for backend APIs
│   │   │
│   │   ├── lib/
│   │   │   └── utils.ts             # Utility functions
│   │   │
│   │   └── styles/
│   │       ├── index.css
│   │       └── style.css
│   │
│   ├── public/                      # Static assets
│   │   ├── icons.svg
│   │   └── favicon.svg
│   │
│   ├── package.json                 # npm dependencies
│   ├── vite.config.ts               # Vite build config
│   ├── tsconfig.json                # TypeScript config
│   ├── tailwind.config.js           # Tailwind CSS config
│   └── postcss.config.js            # PostCSS config
│
├── salesstream-extension/           # Chrome Extension
│   ├── manifest.json                # Extension manifest (MV3)
│   ├── content.js                   # Content script injected into Google Meet
│   ├── popup.js                     # Popup script for extension UI
│   ├── popup.html                   # Popup HTML with input form
│   ├── styles.css                   # Popup styling
│   ├── README.md                    # Extension documentation
│   └── icons/                       # Extension icons
│       ├── icon16.png
│       ├── icon48.png
│       └── icon128.png
│
├── Documentation/
│   ├── README.md                    # Main documentation
│   ├── QUICK_START.md              # Setup & running instructions
│   ├── FRONTEND_GUIDE.md           # Frontend component docs
│   ├── COMPLETE_SYSTEM_GUIDE.md    # Full system architecture
│   ├── SCALEKIT_SETUP_GUIDE.md     # OAuth2 SSO setup
│   └── MIGRATION_TO_OPENAI.md      # Migration from Claude to OpenAI
│
├── start-all.sh                     # Master startup script (tmux)
├── .gitignore                       # Git exclusions
└── .git/                            # Git repository

```

---

## Component Connections & Data Flow

### 1. WebSocket Communication Layer
**File**: `/backend/services/websocket_manager.py`

Manages bidirectional communication between Chrome Extension and Backend:

```
Chrome Extension (content.js)
    ↓
WebSocket Connection: ws://localhost:8000/ws
    ↓
FastAPI WebSocket Endpoint (@app.websocket("/ws"))
    ↓
WebSocketManager
    ├── Connect: Tracks connection with unique ID
    ├── Send: send_to_connection(websocket, message)
    ├── Send: broadcast(message) - to all clients
    ├── Send: send_insight() - custom insight format
    ├── Send: send_agent_update() - agent status updates
    └── Send: send_error() - error notifications
```

**Message Types**:
- `connection_established`: Initial handshake
- `start_research`: Chrome Extension → Backend
- `research_started`: Backend → Extension (acknowledgment)
- `agent_update`: Backend → Extension (agent progress)
- `insight`: Backend → Extension (AI findings)
- `transcript_update`: Real-time from Meetstream
- `ping/pong`: Keep-alive mechanism

---

### 2. FastAPI Backend Architecture
**File**: `/backend/main.py`

#### Startup/Lifecycle
```python
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Initialize agent_orchestrator
    agent_orchestrator = AgentOrchestrator()
    await agent_orchestrator.initialize()
    
    yield
    
    # Shutdown: Cleanup resources
    await agent_orchestrator.cleanup()
```

#### API Endpoints

**WebSocket Endpoint**:
- `GET /ws` - Main WebSocket for Chrome Extension

**REST API - Research & Company Data**:
```
POST   /api/research                      # Trigger research job
GET    /api/meetings/{user_id}            # Get past meetings
GET    /api/meetings/{meeting_id}/insights # Get meeting insights
POST   /api/linkedin/profile              # Fetch LinkedIn profile (Apify)
POST   /api/linkedin/company              # Fetch company LinkedIn page
```

**Meetstream Integration**:
```
POST   /api/meetstream/start-bot/{meeting_url}      # Start Meetstream bot
DELETE /api/meetstream/stop-bot/{bot_id}            # Stop recording
GET    /api/meetstream/bot-status/{bot_id}          # Get bot status
GET    /api/meetstream/active-bots                  # List all active bots
POST   /webhooks/meetstream/audio                   # Audio webhook
```

**Authentication (Scalekit SSO)**:
```
GET    /auth/scalekit/login                         # Initiate SSO
GET    /auth/scalekit/callback                      # OAuth callback
POST   /auth/scalekit/refresh                       # Refresh token
GET    /auth/scalekit/logout                        # Get logout URL
```

**Health & Profile**:
```
GET    /                                  # Health check
GET    /health                            # Detailed health
POST   /api/profile                       # Save user profile
GET    /api/profile/{user_id}             # Get user profile
POST   /api/meeting-prep                  # Save meeting prep
GET    /api/meeting-prep/{meeting_id}     # Get meeting prep
```

---

### 3. Agent Orchestrator
**File**: `/backend/services/agent_orchestrator.py`

Coordinates multi-agent execution with parallel task processing:

```
Research Request (Chrome Extension or Frontend)
    ↓
AgentOrchestrator.start_research()
    ↓
Parallel Agent Execution (asyncio.gather):
    ├─→ ResearchAgent.analyze_website(company_url)
    │   └─→ [IMPLEMENTED] Scrapes website, extracts info
    │
    ├─→ SocialIntelligenceAgent.analyze_company()
    │   └─→ [PLACEHOLDER] LinkedIn insights
    │
    ├─→ ReviewAnalysisAgent.analyze_reviews()
    │   └─→ [PLACEHOLDER] Customer sentiment from G2, Capterra
    │
    └─→ ResearchAgent.analyze_website(competitor_urls)
        └─→ [IMPLEMENTED] Competitor analysis
    
    ↓
StrategyAgent.synthesize(all_results)
    └─→ [PLACEHOLDER] Synthesizes insights into recommendations
    
    ↓
WebSocket broadcast to Chrome Extension
    └─→ Each agent sends updates → Extension displays in overlay
```

**Agent Methods**:
- `start_research(websocket, company_url, competitor_urls)`
- `process_transcript(websocket, transcript, speaker)` - Real-time
- `_run_research_agent()` - Execute research agent
- `_run_social_intelligence_agent()` - Execute LinkedIn agent
- `_run_review_analysis_agent()` - Execute sentiment agent
- `_run_strategy_agent()` - Synthesize insights
- `create_research_job()` - REST API variant (no WebSocket)

---

### 4. AI Agents (Claude/OpenAI Powered)

**Agent Files** (in `/backend/agents/`):

#### a) ResearchAgent (IMPLEMENTED)
```
analyze_website(url: str)
    ├─ Web Scraper MCP → Get website content
    ├─ OpenAI GPT-4o → Analyze content with system prompt
    └─ Returns: {company_name, summary, products, market, differentiators}
```

**System Prompt Focus**: Extract business intelligence for sales reps
- What does company do?
- Target market?
- Key value props?
- Main differentiators?
- Recent developments?

#### b) SocialIntelligenceAgent (PLACEHOLDER)
```
analyze_company(company_url: str)
    ├─ Extract company name from URL
    ├─ Apify LinkedIn API → Fetch company page
    └─ Returns: {company_name, employees, industry, description, ...}
```

**Status**: Template created, needs Apify token + implementation

#### c) ReviewAnalysisAgent (PLACEHOLDER)
```
analyze_reviews(company_url: str)
    ├─ Web Scraper MCP → Scrape review sites (G2, Capterra, Reddit)
    ├─ OpenAI GPT-4o → Sentiment analysis
    └─ Returns: {sentiment_score, key_complaints, strengths, summary}
```

**Status**: Template created, needs web scraper MCP enhancement

#### d) ConversationAgent (PARTIAL)
```
analyze_transcript(transcript: str, speaker: str, context: List)
    ├─ Detect objections, questions, buying signals
    ├─ OpenAI GPT-4o → Generate suggestions
    └─ Returns: {action_required, title, suggestion, priority}
```

**Status**: Framework in place (217 lines), detection logic ready
**Integration**: Triggered on each transcript update from Meetstream

#### e) StrategyAgent (PLACEHOLDER)
```
synthesize(all_results: Dict) → Combines all agent outputs
    ├─ Takes research + social + review + conversation insights
    ├─ OpenAI GPT-4o → Creates battle cards + sales strategy
    └─ Returns: {summary, talking_points, objection_handlers, next_steps}
```

**Status**: Template created (123 lines)

---

### 5. Frontend - React Dashboard
**File**: `/frontend/src/App.jsx`

#### Authentication Flow
```
User visits http://localhost:5173
    ↓
/login page (Login.tsx)
    ├─ Email input
    └─ "Login with Scalekit" button
        ↓
    Backend: GET /auth/scalekit/login
        ↓
    Scalekit OAuth consent screen
        ↓
    Backend: GET /auth/scalekit/callback?code=...
        ↓
    Exchange code for tokens (access + refresh)
        ↓
    Frontend stores user in localStorage
        ↓
    Redirect to Dashboard (/pages/Dashboard.jsx)
```

#### Pages & Components

**1. Login (Login.tsx)**
- Scalekit SSO integration [IMPLEMENTED]
- Email/password fallback [PLACEHOLDER]

**2. Dashboard (Dashboard.jsx)**
- Quick stats (meetings this month, insights generated)
- Recent meetings list
- Quick actions (Start meeting prep, Browse past meetings)
- [IMPLEMENTED] Layout & navigation

**3. Profile Setup (ProfileSetup.jsx)**
- User company info
- Sales role/title
- Industry
- [IMPLEMENTED] Form collection

**4. Meeting Prep (MeetingPrep.jsx)**
- Prospect name/email/LinkedIn
- Company info
- Meeting goals
- AI research trigger
- [PARTIAL] API integration for LinkedIn
- [IMPLEMENTED] Form & local storage

**5. Past Meetings (PastMeetings.jsx)**
- View historical meetings
- Insights & action items
- Follow-up tracking
- [IMPLEMENTED] UI layout
- [PLACEHOLDER] Backend persistence

**6. Auth Callback (AuthCallback.jsx)**
- Handles OAuth callback from Scalekit
- Extracts tokens
- Redirects to dashboard

#### API Service Layer
**File**: `/frontend/src/services/api.js`

```javascript
const apiService = {
    health: () => api.get('/health'),
    saveProfile: (data) => api.post('/api/profile', data),
    getProfile: (userId) => api.get(`/api/profile/${userId}`),
    saveMeetingPrep: (data) => api.post('/api/meeting-prep', data),
    getMeetingPrep: (meetingId) => api.get(`/api/meeting-prep/${meetingId}`),
    startResearch: (url, competitors) => api.post('/api/research', {...}),
    fetchLinkedInProfile: (url) => api.post('/api/linkedin/profile', {...}),
    fetchLinkedInCompany: (url) => api.post('/api/linkedin/company', {...}),
    getPastMeetings: (userId) => api.get(`/api/meetings/${userId}`),
    getMeetingInsights: (meetingId) => api.get(`/api/meetings/{meetingId}/insights`),
}
```

**Base URL**: `http://localhost:8000`

---

### 6. Chrome Extension Architecture
**Files**: `/salesstream-extension/`

#### Manifest & Permissions
```json
{
  "manifest_version": 3,
  "name": "SalesStream Overlook",
  "permissions": ["activeTab", "storage"],
  "host_permissions": ["https://meet.google.com/*"],
  "content_scripts": [{
    "matches": ["https://meet.google.com/*"],
    "js": ["content.js"],
    "css": ["styles.css"]
  }],
  "action": {
    "default_popup": "popup.html"
  }
}
```

#### Components

**1. Popup (popup.html + popup.js)**
- Input form for company website
- Competitor URLs (multi-line)
- "Start Research" button
- Status message display
- Chrome storage persistence

**Flow**:
```
User opens extension popup
    ↓
Enters company URL + competitors
    ↓
Clicks "Start Research"
    ↓
popup.js sends message to content.js
    ↓
content.js receives via chrome.runtime.onMessage
    ↓
WebSocketManager.startResearch()
    ↓
Sends to backend: {type: "start_research", company_url, competitor_urls}
```

**2. Content Script (content.js)**
- Injects glassmorphism overlay into Google Meet
- Creates Shadow DOM for style isolation
- WebSocket client initialization
- Real-time insight display

**WebSocket Manager Class**:
```javascript
class WebSocketManager {
    constructor() {
        this.ws = null  // WebSocket connection
        this.backendUrl = 'ws://localhost:8000/ws'
        this.reconnectAttempts = 0
        this.maxReconnectAttempts = 5
    }
    
    connect()              // Establish connection
    send(message)          // Send to backend
    handleMessage(msg)     // Route incoming messages
    addRealtimeInsight()   // Update overlay UI
    addInsightToSection()  // Add to specific section
    addSuggestedResponse() // Add to suggestions
    addNextSteps()         // Add to next steps section
}
```

**Message Handlers** (from backend):
```javascript
switch (message.type) {
    case 'connection_established':     // WebSocket connected
    case 'research_started':           // Research beginning
    case 'agent_update':               // Agent progress
    case 'insight':                    // Company/competitor data
    case 'research_completed':         // All done
    case 'error':                      // Error notification
    case 'pong':                       // Keep-alive
}
```

**3. Overlay UI (Glassmorphism Design)**
```html
├─ Header
│  ├─ Logo "SS"
│  ├─ Title "SalesStream Overlook"
│  ├─ Minimize button
│  └─ Close button
│
├─ Content (scrollable)
│  ├─ Real-time Insights section
│  │  └─ Dynamically populated insight cards
│  │
│  ├─ Suggested Responses section
│  │  └─ AI-generated talking points
│  │
│  ├─ Next Steps section
│  │  └─ Action items & follow-ups
│  │
│  └─ Status bar
│     └─ Connection indicator (●) + text
│
└─ Dragging: Header is draggable to move overlay
   Minimize: Collapses content, shows header only
   Close: Removes overlay from page
```

**Styling**: CSS-in-JS with:
- `backdrop-filter: blur(20px) saturate(180%)`
- `border: 1px solid rgba(255, 255, 255, 0.25)`
- Smooth animations & transitions

**Keep-Alive**:
```javascript
// Ping every 30 seconds
setInterval(() => {
    if (wsManager.ws?.readyState === WebSocket.OPEN) {
        wsManager.send({ type: 'ping' })
    }
}, 30000)
```

---

## Data Flow Diagrams

### 1. Chrome Extension → Backend Flow
```
Google Meet Page (meet.google.com)
    ↓
content.js initializes
    ├─ Creates glassmorphism overlay (Shadow DOM)
    ├─ Initializes WebSocketManager
    └─ Connects to ws://localhost:8000/ws
        ↓
    WebSocket established
        ↓
    User enters company URL in popup
        ↓
    popup.js sends chrome.runtime.onMessage
        ↓
    content.js receives via onMessage listener
        ↓
    wsManager.send({type: 'start_research', company_url, competitor_urls})
        ↓
    Backend receives at WebSocket endpoint
        ↓
    handle_websocket_message routes to handle_start_research()
        ↓
    agent_orchestrator.start_research() launched
```

### 2. Multi-Agent Research Execution
```
Agent Orchestrator receives research request
    ↓
Launches parallel tasks via asyncio.gather():
    │
    ├─ ResearchAgent.analyze_website(company_url)
    │   ├─ Web Scraper MCP → Extract HTML/text
    │   ├─ GPT-4o analysis with system prompt
    │   ├─ sends insight via ws_manager.send_insight()
    │   └─ sends update via ws_manager.send_agent_update()
    │        ↓
    │        WebSocket to Extension
    │
    ├─ SocialIntelligenceAgent.analyze_company()
    │   ├─ Apify LinkedIn API (configured but needs token)
    │   ├─ returns company insights
    │   └─ sends to extension
    │
    ├─ ReviewAnalysisAgent.analyze_reviews()
    │   ├─ Web Scraper → G2, Capterra, Reddit
    │   ├─ Sentiment analysis
    │   └─ sends to extension
    │
    └─ ResearchAgent.analyze_website(competitor_urls)
        ├─ Repeat for each competitor
        └─ sends to extension
    
    ↓ All agents complete
    
StrategyAgent.synthesize(all_results)
    ├─ Combines insights
    ├─ Generates battle cards
    └─ Sends final recommendations to extension
    
    ↓
Extension displays in overlay in real-time
```

### 3. Frontend Dashboard Flow
```
User visits http://localhost:5173/
    ↓
App.jsx checks localStorage for 'user'
    ├─ If exists → Shows Dashboard (authenticated)
    └─ If not exists → Shows Login page
    
If login required:
    ↓
Login.tsx presents Scalekit button
    ↓
User clicks "Login with Scalekit"
    ↓
Redirects to: /auth/scalekit/login
    ↓
Backend: GET /auth/scalekit/login
    ├─ Calls scalekit_auth.get_authorization_url()
    └─ Returns Scalekit OAuth URL
    
    ↓
Frontend redirects to Scalekit login
    ↓
User authenticates at Scalekit
    ↓
Scalekit redirects back to: /auth/scalekit/callback?code=xxx
    ↓
Backend: GET /auth/scalekit/callback
    ├─ Exchanges code for tokens (access + refresh)
    └─ Returns user info + tokens
    
    ↓
Frontend stores in localStorage
    ↓
Sets user state
    ↓
Redirects to Dashboard (/pages/Dashboard.jsx)

From Dashboard:
    ├─ Click "Start Meeting Prep" → MeetingPrep page
    │   ├─ Input prospect details
    │   ├─ Click "Start Research"
    │   ├─ Frontend: apiService.startResearch(url, competitors)
    │   └─ Backend: POST /api/research → creates job
    │
    └─ Click "Browse Meetings" → PastMeetings page
        ├─ Fetch: apiService.getPastMeetings(userId)
        └─ Display historical data
```

---

## Technology Stack

### Backend
```
Python 3.9+
├─ FastAPI 0.115.0          # Web framework
├─ Uvicorn 0.32.0           # ASGI server
├─ WebSockets 13.1          # WebSocket support
├─ OpenAI 1.54.3            # GPT-4o API client
├─ Scalekit SDK 1.0.0       # OAuth2 SSO
├─ MCP 1.1.2                # Model Context Protocol
├─ Playwright 1.48.0        # Web scraping
├─ Beautiful Soup 4.12.3    # HTML parsing
├─ Requests 2.32.3          # HTTP client
├─ Pydantic 2.10.1          # Data validation
├─ Redis 5.2.0              # Caching (optional)
└─ Python-dotenv 1.0.1      # Environment management
```

### Frontend
```
React/TypeScript/Vite
├─ React (Latest)           # UI library
├─ React Router DOM 7.13.2  # Routing
├─ Axios 1.14.0             # HTTP client
├─ Tailwind CSS 4.2.2       # Styling
├─ Framer Motion 12.38.0    # Animations
├─ TypeScript ~5.9.3        # Type safety
├─ Vite 8.0.1               # Build tool
├─ Scalekit React SDK       # SSO integration
├─ Heroicons 2.2.0          # Icons
└─ Shadcn UI components     # UI primitives
```

### Chrome Extension
```
Vanilla JavaScript
├─ Manifest V3             # Latest extension standard
├─ WebSocket API           # Real-time communication
├─ Chrome Storage API      # Local persistence
├─ Shadow DOM              # Style isolation
└─ CSS3                    # Glassmorphism effects
```

---

## Implementation Status

### COMPLETED (100%)
- [x] FastAPI backend structure
- [x] WebSocket communication layer
- [x] Research Agent with web scraping
- [x] React frontend with routing
- [x] Scalekit SSO integration (OAuth2)
- [x] Chrome Extension with overlay
- [x] Extension ↔ Backend WebSocket
- [x] Agent orchestrator framework
- [x] OpenAI GPT-4o client wrapper
- [x] Profile & meeting prep forms
- [x] Health check & API endpoints

### PARTIAL IMPLEMENTATION (50-70%)
- [~] Conversation Agent (framework ready, detection logic in place)
- [~] Strategy Agent (framework ready, synthesis logic stubbed)
- [~] Review Analysis Agent (framework ready, needs scraper enhancement)
- [~] Social Intelligence Agent (framework ready, needs Apify token)
- [~] Frontend UI/UX polish

### NOT IMPLEMENTED (0%)
- [ ] Meetstream bot integration (API endpoints created)
- [ ] AssemblyAI transcription (service structure ready)
- [ ] Real-time transcript processing
- [ ] Post-meeting summaries
- [ ] CRM integrations (Salesforce, HubSpot)
- [ ] Database persistence (using in-memory for now)
- [ ] Unit tests & integration tests
- [ ] Production deployment configs
- [ ] Error tracking (Sentry)
- [ ] Monitoring & logging infrastructure

---

## API Communication Contract

### WebSocket Message Format

**Client → Server (Chrome Extension)**
```json
{
  "type": "start_research",
  "company_url": "https://example.com",
  "competitor_urls": ["https://competitor1.com", "https://competitor2.com"]
}
```

```json
{
  "type": "transcript_update",
  "transcript": "tell me about your pricing",
  "speaker": "prospect",
  "timestamp": "2024-03-28T14:30:00Z"
}
```

**Server → Client (Backend)**
```json
{
  "type": "connection_established",
  "connection_id": "uuid-here",
  "message": "Connected to Meetstream AI Backend"
}
```

```json
{
  "type": "agent_update",
  "agent_name": "research",
  "status": "completed",
  "message": "Analysis complete",
  "timestamp": "2024-03-28T14:30:00Z"
}
```

```json
{
  "type": "insight",
  "insight_type": "company_research",
  "title": "Company Analysis: Acme Inc",
  "content": "Key products: SaaS platform for...",
  "source": "Research Agent",
  "priority": "high",
  "metadata": {...},
  "timestamp": "2024-03-28T14:30:00Z"
}
```

### REST API Endpoints

**Start Research**
```
POST /api/research
Content-Type: application/json

{
  "company_url": "https://example.com",
  "competitor_urls": []
}

Response:
{
  "status": "started",
  "job_id": "uuid-here",
  "message": "Research job created..."
}
```

**Scalekit Login**
```
GET /auth/scalekit/login?redirect_uri=http://localhost:5173/auth/callback

Response:
{
  "authorization_url": "https://scalekit.com/oauth/authorize?..."
}
```

---

## Environment Configuration

**Required Variables** (in `/backend/.env`):
```
OPENAI_API_KEY=<your_openai_api_key_here>
ALLOWED_ORIGINS=chrome-extension://*,http://localhost:3000,http://localhost:5173
SCALEKIT_CLIENT_ID=...
SCALEKIT_CLIENT_SECRET=...
SCALEKIT_ENVIRONMENT_URL=...
```

**Optional Variables**:
```
APIFY_TOKEN=...  (for LinkedIn scraping)
DEBUG=True
HOST=0.0.0.0
PORT=8000
```

---

## How Components Connect

### Extension → Backend
1. Extension opens WebSocket to backend
2. User enters company URL in popup
3. Extension sends `{type: "start_research", company_url, competitor_urls}`
4. Backend runs agents in parallel
5. Agents send insights via WebSocket
6. Extension receives and displays in overlay

### Frontend → Backend
1. User logs in via Scalekit
2. Frontend stores auth tokens
3. Dashboard makes API calls for profile/meetings
4. Meeting Prep page can trigger research via REST API
5. Backend returns job_id (can be tracked separately)

### Agents → Extension
1. Agent runs research
2. Extracts key insights
3. Sends via `ws_manager.send_insight()`
4. Extension receives in `handleInsight()` message handler
5. Dynamically updates overlay UI

### Database Flow
- **Current**: In-memory dicts in main.py
- **Todo**: Move to database (PostgreSQL, MongoDB)
- **User data**: localStorage on frontend (should migrate to backend session)

---

## Common Modifications & Extensions

### To Add a New Agent
1. Create `/backend/agents/new_agent.py`
2. Implement `class NewAgent` with async method
3. Register in `AgentOrchestrator._load_agents()`
4. Call from orchestrator task list

### To Add a New API Endpoint
1. Add route in `/backend/main.py`
2. Create service method if complex logic
3. Return JSON response
4. Update frontend api.js service

### To Modify Overlay UI
1. Edit `/salesstream-extension/content.js`
2. Modify `createOverlayElement()` HTML
3. Modify `getOverlayStyles()` CSS
4. Message handlers in `WebSocketManager.handleMessage()`

### To Add Frontend Page
1. Create component in `/frontend/src/pages/`
2. Add route in `App.jsx`
3. Create API calls in `/frontend/src/services/api.js`
4. Add navigation link in `Navbar.jsx`

---

## Key Files by Responsibility

| Responsibility | File |
|---|---|
| Main entry point | `/backend/main.py` |
| Agent coordination | `/backend/services/agent_orchestrator.py` |
| WebSocket management | `/backend/services/websocket_manager.py` |
| Research execution | `/backend/agents/research_agent.py` |
| Web scraping | `/backend/mcp_servers/web_scraper_mcp/server.py` |
| OAuth2 SSO | `/backend/services/scalekit_auth.py` |
| Frontend routing | `/frontend/src/App.jsx` |
| Frontend API client | `/frontend/src/services/api.js` |
| Extension overlay | `/salesstream-extension/content.js` |
| Extension WebSocket | `/salesstream-extension/content.js` (WebSocketManager class) |

---

## Quick Debugging Tips

**Backend not responding**: 
- Check `python backend/main.py` is running
- Verify `OPENAI_API_KEY` in `.env`
- Check logs for agent initialization errors

**Extension not connecting**:
- Verify backend is running on port 8000
- Check browser console in Google Meet tab
- Confirm WebSocket URL matches (`ws://localhost:8000/ws`)

**Frontend showing blank page**:
- Check React router in App.jsx
- Verify localStorage auth state
- Browser dev tools → Network tab for API errors

**Agents not executing**:
- Check `agent_orchestrator.initialize()` completed
- Verify agents imported successfully in `_load_agents()`
- Check asyncio.gather() for exceptions

---

## Summary

This is a **3-tier architecture**:

1. **Backend (Python FastAPI)**: Orchestrates 5 AI agents, manages WebSocket connections, handles authentication
2. **Frontend (React)**: Dashboard for meeting prep, prospect research, uses SSO
3. **Extension (JavaScript)**: Injects overlay during Google Meet, receives real-time insights via WebSocket

The system is **messaging-driven** with WebSockets for real-time communication and REST APIs for configuration/history. Agents run **in parallel** with asyncio and send updates via WebSocket as they complete. All UI is **dynamically updated** as insights arrive.
