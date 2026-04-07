# Codebase Exploration - Complete Index

This document is your complete guide to understanding the Meetstream AI codebase structure and architecture.

## Generated Documentation

Three comprehensive documents have been created to help you navigate the codebase:

### 1. CODEBASE_MAP.md (DETAILED ARCHITECTURE)
**Purpose**: Deep dive into every component with code flow
**Best for**: Understanding how things work
**Length**: ~1500 lines
**Contains**:
- Complete directory structure
- Component connections & data flow
- Detailed WebSocket communication layer
- FastAPI endpoints & routes
- Agent system architecture
- Frontend React structure
- Chrome extension implementation
- Technology stack
- Implementation status checklist
- API communication contracts
- Environment configuration
- Key files by responsibility
- Debugging tips

**Start here if you want to**: Modify code, add features, fix bugs

---

### 2. ARCHITECTURE_VISUAL.txt (ASCII DIAGRAMS)
**Purpose**: Visual representation of system architecture
**Best for**: Quick understanding of data flow
**Length**: ~350 lines
**Contains**:
- System architecture overview (ASCII art)
- Data flow sequences
- File dependency map
- Implementation checklist
- Quick reference guide
- Troubleshooting guide

**Start here if you want to**: Get a quick visual overview, understand connections

---

### 3. COMPONENT_SUMMARY.md (STATUS & QUICK REFERENCE)
**Purpose**: Implementation status and common tasks
**Best for**: Quick lookups, getting started
**Length**: ~400 lines
**Contains**:
- Component status matrix
- Key file locations
- Data connections
- What's working now
- How to use each component
- Configuration required
- Common tasks (add endpoint, add agent, modify UI)
- Testing procedures
- Performance notes
- Next steps to complete

**Start here if you want to**: See what's done, how to run it, add basic features

---

## Quick Navigation

### I want to...

**...understand the overall architecture**
- Read: ARCHITECTURE_VISUAL.txt (System Architecture Overview)
- Then: CODEBASE_MAP.md (Component Connections section)

**...start the system**
- Read: COMPONENT_SUMMARY.md (How to Use Each Component)
- Run: `./start-all.sh` or read step-by-step instructions

**...modify the Chrome Extension**
- Read: CODEBASE_MAP.md (Chrome Extension Architecture section)
- Edit: `/salesstream-extension/content.js`
- Reference: WebSocketManager class and message handlers

**...add a new API endpoint**
- Read: COMPONENT_SUMMARY.md (Common Tasks section)
- Edit: `/backend/main.py` (add route)
- Edit: `/frontend/src/services/api.js` (add client method)

**...understand agent execution**
- Read: CODEBASE_MAP.md (Agent Orchestrator section)
- Read: CODEBASE_MAP.md (AI Agents section)
- Look at: `/backend/agents/research_agent.py` (example)

**...debug a problem**
- Read: ARCHITECTURE_VISUAL.txt (Troubleshooting Guide)
- Read: CODEBASE_MAP.md (Quick Debugging Tips)

**...check implementation status**
- Read: COMPONENT_SUMMARY.md (Component Status Matrix)
- Read: CODEBASE_MAP.md (Implementation Status section)

---

## Key Files by Purpose

### WebSocket & Real-time Communication
- `/backend/services/websocket_manager.py` - Connection management
- `/salesstream-extension/content.js` - WebSocket client (WebSocketManager class)
- `/backend/main.py` - WebSocket endpoint handler

### Agent Execution
- `/backend/services/agent_orchestrator.py` - Coordinates agents
- `/backend/agents/research_agent.py` - Website scraping (IMPLEMENTED)
- `/backend/agents/conversation_agent.py` - Transcript analysis (PARTIAL)
- `/backend/agents/strategy_agent.py` - Synthesis (PARTIAL)
- `/backend/agents/social_intelligence_agent.py` - LinkedIn (PLACEHOLDER)
- `/backend/agents/review_analysis_agent.py` - Sentiment (PLACEHOLDER)

### Frontend Routes
- `/frontend/src/App.jsx` - Main router
- `/frontend/src/pages/Login.tsx` - Authentication
- `/frontend/src/pages/Dashboard.jsx` - Main page
- `/frontend/src/pages/MeetingPrep.jsx` - Research form
- `/frontend/src/pages/PastMeetings.jsx` - History
- `/frontend/src/services/api.js` - API client

### Chrome Extension
- `/salesstream-extension/manifest.json` - Extension metadata
- `/salesstream-extension/content.js` - Injected script (MAIN FILE)
- `/salesstream-extension/popup.html` - UI form
- `/salesstream-extension/popup.js` - Form logic

### Configuration & Setup
- `/backend/.env.example` - Environment template
- `/backend/requirements.txt` - Python dependencies
- `/frontend/package.json` - JavaScript dependencies
- `/start-all.sh` - Master startup script

---

## Architecture at a Glance

```
Google Meet (meet.google.com)
    ↓
Chrome Extension (content.js)
    ↓
WebSocket: ws://localhost:8000/ws
    ↓
FastAPI Backend (main.py)
    ├─ WebSocketManager
    ├─ AgentOrchestrator
    │  ├─ ResearchAgent
    │  ├─ ConversationAgent
    │  ├─ StrategyAgent
    │  ├─ SocialIntelligenceAgent
    │  └─ ReviewAnalysisAgent
    └─ External APIs (OpenAI, Apify, etc.)

React Frontend (localhost:5173)
    ├─ Login (Scalekit SSO)
    ├─ Dashboard
    ├─ Profile Setup
    ├─ Meeting Prep
    └─ Past Meetings
         ↓
    REST API (http://localhost:8000/api/*)
```

---

## Data Flow Overview

### Extension Research Request
```
User enters URL in popup
    ↓
popup.js sends chrome.runtime.onMessage
    ↓
content.js receives and sends WebSocket message
    ↓
Backend receives at ws://localhost:8000/ws
    ↓
AgentOrchestrator launches agents in parallel
    ↓
Agents send insights via WebSocket
    ↓
Extension overlay updates in real-time
```

### Frontend Research Request
```
User fills form and clicks "Start Research"
    ↓
MeetingPrep.jsx calls apiService.startResearch()
    ↓
POST /api/research to backend
    ↓
Backend creates research job (returns job_id)
    ↓
Frontend can poll for results (or use WebSocket)
```

---

## Implementation Status Summary

### Complete (100%)
- FastAPI backend structure
- WebSocket communication
- Research Agent with web scraping
- React frontend with routing
- Scalekit SSO
- Chrome Extension with overlay
- Agent orchestrator framework
- API endpoints

### Partial (50-70%)
- Conversation Agent
- Strategy Agent
- Social Intelligence Agent
- Review Analysis Agent

### Not Started (0%)
- Meetstream bot integration
- AssemblyAI transcription
- Database persistence
- Unit tests
- Production deployment

---

## Technology Stack Quick Reference

**Backend**: Python 3.9+ with FastAPI, WebSockets, OpenAI, Scalekit, Playwright
**Frontend**: React, TypeScript, Tailwind CSS, Axios, Vite
**Extension**: Vanilla JavaScript, Chrome APIs
**Database**: In-memory dicts (needs migration to PostgreSQL/MongoDB)
**Authentication**: Scalekit OAuth2 SSO

---

## Getting Started Roadmap

1. **Read Documentation** (15 minutes)
   - Start with ARCHITECTURE_VISUAL.txt
   - Skim COMPONENT_SUMMARY.md

2. **Start Services** (5 minutes)
   - Run `./start-all.sh` or start backend/frontend individually

3. **Install Extension** (2 minutes)
   - Load unpacked extension from `/salesstream-extension`

4. **Test Functionality** (10 minutes)
   - Open Google Meet
   - Test extension popup
   - Test frontend dashboard

5. **Explore Code** (ongoing)
   - Reference CODEBASE_MAP.md as needed
   - Modify components from COMPONENT_SUMMARY.md

---

## For Developers

### To Add a Feature
1. Check CODEBASE_MAP.md for similar implementations
2. Use COMPONENT_SUMMARY.md for common tasks
3. Follow existing patterns in the codebase
4. Test with curl/Postman for APIs
5. Test in browser console for extension

### To Debug an Issue
1. Check ARCHITECTURE_VISUAL.txt troubleshooting section
2. Verify environment variables: `cat backend/.env`
3. Check service health: `curl localhost:8000/health`
4. Review backend logs for errors
5. Check browser console for extension errors

### To Understand a Component
1. Find the file in CODEBASE_MAP.md
2. Read the description and nearby sections
3. Look at how it's called from other files
4. Trace the data flow in CODEBASE_MAP.md
5. Test with sample requests

---

## File Locations Summary

```
/Users/jeetshah/Documents/Meetstream AI/
├── backend/                                 # Python FastAPI
│   ├── main.py                             # START HERE for backend
│   ├── services/
│   │   ├── websocket_manager.py
│   │   ├── agent_orchestrator.py
│   │   └── openai_client.py
│   └── agents/
│       ├── research_agent.py               # Fully implemented
│       └── [other agents]
│
├── frontend/                                # React TypeScript
│   ├── src/
│   │   ├── App.jsx                         # START HERE for frontend
│   │   ├── pages/
│   │   └── services/api.js
│   └── package.json
│
├── salesstream-extension/                   # Chrome Extension
│   ├── content.js                          # START HERE for extension
│   ├── popup.html
│   ├── popup.js
│   └── manifest.json
│
└── Documentation/
    ├── CODEBASE_MAP.md                     # Read this (detailed)
    ├── ARCHITECTURE_VISUAL.txt             # Read this (overview)
    ├── COMPONENT_SUMMARY.md                # Read this (quick ref)
    └── [other docs]
```

---

## Quick Commands

```bash
# Start everything
./start-all.sh

# Start just backend
cd backend && python main.py

# Start just frontend
cd frontend && npm run dev

# Check backend health
curl http://localhost:8000/health

# Test research API
curl -X POST http://localhost:8000/api/research \
  -H "Content-Type: application/json" \
  -d '{"company_url":"https://example.com","competitor_urls":[]}'

# View backend logs
tail -f backend/nohup.out

# Check extension WebSocket state
# (In Google Meet console) console.log(wsManager.ws.readyState)
```

---

## Next Actions

Based on your codebase exploration:

1. **If you want to add features**: Read CODEBASE_MAP.md, COMPONENT_SUMMARY.md
2. **If you want to understand flow**: Read ARCHITECTURE_VISUAL.txt
3. **If you want to deploy**: Check CODEBASE_MAP.md (none implemented yet)
4. **If you want to test**: Follow COMPONENT_SUMMARY.md testing section
5. **If you have questions**: Check troubleshooting in ARCHITECTURE_VISUAL.txt

---

## Document Cross-References

- **CODEBASE_MAP.md** → For detailed technical implementation
- **ARCHITECTURE_VISUAL.txt** → For system overview and diagrams
- **COMPONENT_SUMMARY.md** → For quick reference and common tasks
- **README.md** → Project overview and features
- **QUICK_START.md** → Setup instructions

---

Last updated: March 28, 2026
Codebase explored: Meetstream AI (3 components, 50+ files)
Status: ~70% implemented, ready for extension/deployment

