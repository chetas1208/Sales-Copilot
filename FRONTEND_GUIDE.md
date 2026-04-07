# Meetstream AI - Frontend Dashboard Guide

## Overview

A complete web dashboard for sales reps to prepare for meetings with AI-powered insights. Built with React, Tailwind CSS, and integrated with the FastAPI backend.

## Features

### ✅ **Completed**

1. **Authentication System**
   - Email/password login
   - Scalekit SSO integration placeholder
   - Session management

2. **Dashboard**
   - Quick actions for meeting prep
   - Statistics overview (total meetings, upcoming, research, LinkedIn profiles)
   - Recent activity feed

3. **Company Profile Setup**
   - Sales rep's company information
   - Products/services description
   - Value proposition
   - Target market
   - Competitors list

4. **Meeting Preparation**
   - Prospect information form (name, role, email, LinkedIn)
   - Company information (name, website, LinkedIn)
   - Meeting details (date, goal, notes)
   - AI research trigger
   - Real-time insights display
   - LinkedIn profile fetching via Apify (placeholder)

5. **Past Meetings**
   - List of all prepared meetings
   - Detailed view of each meeting
   - Insights review
   - LinkedIn data display

---

## Architecture

```
frontend/
├── src/
│   ├── components/
│   │   └── Navbar.jsx              # Navigation bar
│   ├── pages/
│   │   ├── Login.jsx               # Login page
│   │   ├── Dashboard.jsx           # Main dashboard
│   │   ├── ProfileSetup.jsx        # Company profile
│   │   ├── MeetingPrep.jsx         # Meeting preparation
│   │   └── PastMeetings.jsx        # Meeting history
│   ├── services/
│   │   └── api.js                  # API client (axios)
│   ├── App.jsx                     # Main app with routing
│   ├── main.jsx                    # Entry point
│   └── index.css                   # Tailwind styles
├── package.json
└── tailwind.config.js
```

---

## Getting Started

### Prerequisites

- Node.js 16+ and npm
- Backend running on `http://localhost:8000`

### Installation

```bash
cd frontend
npm install
```

### Running

```bash
npm run dev
```

Frontend will start on: `http://localhost:5173`

---

## Pages Overview

### 1. Login (`/login`)

**Features:**
- Email/password authentication
- Scalekit SSO button (placeholder)
- Session persistence

**How it works:**
- Credentials stored in localStorage
- After login, redirects to Dashboard
- Protected routes check authentication

### 2. Dashboard (`/`)

**Features:**
- Welcome message with user name
- Quick action cards:
  - "Prepare New Meeting" → `/meeting-prep`
  - "View Past Meetings" → `/past-meetings`
- Statistics cards:
  - Total Meetings
  - Upcoming Meetings
  - Active Research
  - LinkedIn Profiles
- Recent activity feed

**Data Source:**
- Stats: Currently hardcoded, can be fetched from `/api/meetings/{user_id}`
- Activity: Placeholder data

### 3. Profile Setup (`/profile`)

**Purpose:** Configure sales rep's company information for better AI insights

**Form Fields:**
- **Company Information:**
  - Company Name *
  - Company Website *
  - Industry *
  - Company Size (dropdown)
  - Your Role *

- **What You Offer:**
  - Products/Services * (textarea)
  - Value Proposition * (textarea)
  - Target Market * (textarea)
  - Main Competitors (textarea)

**Storage:**
- LocalStorage: `profile_{userId}`
- API: POST `/api/profile` (future)

**Usage:**
This data helps AI agents understand your company's context when analyzing prospects.

### 4. Meeting Prep (`/meeting-prep`)

**Purpose:** Research prospects and get AI insights before meetings

**Form Sections:**

**A. Prospect Information**
- Full Name *
- Email
- Role/Title *
- LinkedIn Profile URL

**B. Company Information**
- Company Name *
- Company Website *
- Company LinkedIn URL

**C. Meeting Details**
- Meeting Date & Time
- Meeting Goal * (discovery, demo, closing, etc.)
- Additional Notes

**AI Research Button:**
When clicked:
1. Fetches LinkedIn profile (via Apify placeholder)
2. Triggers backend research agents
3. Displays insights in real-time
4. Saves meeting to localStorage

**Insights Panel (Right Side):**
- LinkedIn Profile Summary
- Company Overview
- Key Products
- Talking Points
- Objection Handlers

**Storage:**
- LocalStorage: `meeting_{timestamp}`
- Contains all form data + AI insights

### 5. Past Meetings (`/past-meetings`)

**Purpose:** Review previous meeting preparations and insights

**Layout:**
- **Left Panel:** List of all meetings (chronological)
- **Right Panel:** Selected meeting details

**Meeting Card Shows:**
- Company name
- Prospect name & role
- Creation timestamp
- Meeting scheduled time

**Detail View:**
- Prospect information
- Company information
- Meeting goal & notes
- LinkedIn profile data
- AI insights (company overview, products, talking points)

---

## API Integration

### Endpoints Used

```javascript
// Profile
POST /api/profile              // Save profile
GET  /api/profile/{userId}     // Get profile

// Meeting Prep
POST /api/meeting-prep         // Save meeting
GET  /api/meeting-prep/{meetingId}  // Get meeting

// Research
POST /api/research             // Trigger AI research

// LinkedIn via Apify
POST /api/linkedin/profile     // Fetch LinkedIn profile
POST /api/linkedin/company     // Fetch company page

// Past Meetings
GET  /api/meetings/{userId}              // All meetings
GET  /api/meetings/{meetingId}/insights  // Meeting insights
```

### API Client (`src/services/api.js`)

```javascript
import { apiService } from './services/api'

// Example usage
const insights = await apiService.startResearch(
  'https://stripe.com',
  ['https://competitor.com']
)
```

---

## Integrations

### 1. Apify (LinkedIn Scraping)

**Current Status:** Placeholder implementation

**To Integrate:**

```javascript
// backend/main.py
from apify_client import ApifyClient

@app.post("/api/linkedin/profile")
async def fetch_linkedin_profile(payload: Dict[str, Any]):
    apify_token = os.getenv("APIFY_TOKEN")
    client = ApifyClient(apify_token)

    # Run LinkedIn Profile Scraper
    run = client.actor("apify/linkedin-profile-scraper").call(
        run_input={
            "startUrls": [{"url": payload["linkedin_url"]}],
            "proxyConfiguration": {"useApifyProxy": True}
        }
    )

    # Get results
    items = client.dataset(run["defaultDatasetId"]).list_items().items
    return items[0] if items else {}
```

**Setup:**
1. Sign up at https://apify.com/
2. Get API token
3. Add to `backend/.env`: `APIFY_TOKEN=your_token`
4. Install: `pip install apify-client`

**Recommended Actors:**
- `apify/linkedin-profile-scraper` - $0.40/1000 profiles
- `apify/linkedin-company-scraper` - $0.40/1000 companies

### 2. Scalekit (SSO Authentication)

**Current Status:** Button placeholder in Login page

**To Integrate:**

```javascript
// frontend/src/pages/Login.jsx
import { ScalekitProvider, useScalekit } from '@scalekit-sdk/react'

function App() {
  return (
    <ScalekitProvider
      clientId={process.env.VITE_SCALEKIT_CLIENT_ID}
      environment={process.env.VITE_SCALEKIT_ENVIRONMENT_URL}
    >
      <Login />
    </ScalekitProvider>
  )
}

function Login() {
  const { loginWithRedirect } = useScalekit()

  const handleScalekitLogin = () => {
    loginWithRedirect({
      connection: 'google',  // or 'microsoft', 'okta', etc.
      redirectUri: window.location.origin + '/callback'
    })
  }
}
```

**Setup:**
1. Sign up at https://www.scalekit.com/
2. Create environment
3. Get Client ID and Environment URL
4. Add to `frontend/.env`:
   ```
   VITE_SCALEKIT_CLIENT_ID=your_client_id
   VITE_SCALEKIT_ENVIRONMENT_URL=https://your-env.scalekit.io
   ```

---

## Customization

### Styling

Using Tailwind CSS with custom theme:

```javascript
// tailwind.config.js
theme: {
  extend: {
    colors: {
      primary: {
        500: '#0ea5e9',  // Main brand color
        600: '#0284c7',
        // ... customize here
      },
    },
  },
}
```

### Adding New Pages

1. Create component in `src/pages/`
2. Add route in `src/App.jsx`:
   ```javascript
   <Route path="/new-page" element={<NewPage user={user} />} />
   ```
3. Add navigation link in `src/components/Navbar.jsx`

### Adding API Endpoints

1. Add function to `src/services/api.js`:
   ```javascript
   export const apiService = {
     newEndpoint: (data) => api.post('/api/new-endpoint', data),
   }
   ```
2. Implement backend endpoint in `backend/main.py`

---

## Development Workflow

### Running Both Services

```bash
# Option 1: Separate terminals
# Terminal 1
cd backend && ./start.sh

# Terminal 2
cd frontend && npm run dev

# Option 2: Use tmux (recommended)
./start-all.sh
```

### Hot Reload

Both backend and frontend support hot reload:
- **Backend:** Uvicorn auto-reload on file changes
- **Frontend:** Vite HMR (Hot Module Replacement)

### Testing Flow

1. Start services: `./start-all.sh`
2. Open browser: `http://localhost:5173`
3. Login with any email
4. Go to Profile → Fill company info
5. Go to Meeting Prep → Fill form
6. Click "Start AI Research"
7. View insights in real-time
8. Check Past Meetings

---

## Deployment

### Frontend (Vercel/Netlify)

```bash
# Build production bundle
npm run build

# Preview production build
npm run preview

# Deploy to Vercel
vercel deploy
```

Update `src/services/api.js` with production backend URL:
```javascript
const API_BASE_URL = process.env.VITE_API_URL || 'http://localhost:8000'
```

### Environment Variables

Create `frontend/.env.production`:
```
VITE_API_URL=https://your-backend.com
VITE_SCALEKIT_CLIENT_ID=prod_client_id
VITE_SCALEKIT_ENVIRONMENT_URL=https://prod-env.scalekit.io
```

---

## Troubleshooting

### CORS Errors

**Problem:** `Access to fetch blocked by CORS policy`

**Solution:** Add frontend URL to backend `.env`:
```
ALLOWED_ORIGINS=http://localhost:5173,https://your-frontend.com
```

### API Connection Failed

**Check:**
1. Backend running: `curl http://localhost:8000/health`
2. CORS configured correctly
3. API base URL in `api.js` matches backend

### LinkedIn Data Not Loading

**Issue:** Apify integration not set up

**Quick Fix:** Currently returns placeholder data. Integrate Apify for real data (see Integrations section).

### Insights Not Appearing

**Check:**
1. OpenAI API key in `backend/.env`
2. Backend agents running (check terminal logs)
3. WebSocket connection (check browser console)

---

## Future Enhancements

### Phase 1 (Current)
✅ Basic CRUD for profiles & meetings
✅ AI research trigger
✅ LinkedIn placeholder

### Phase 2 (Next)
- [ ] Real Apify LinkedIn integration
- [ ] Scalekit SSO implementation
- [ ] Database (PostgreSQL) instead of localStorage
- [ ] Real-time WebSocket updates in dashboard

### Phase 3
- [ ] Email notifications for meeting reminders
- [ ] Calendar integration (Google Calendar, Outlook)
- [ ] CRM sync (Salesforce, HubSpot)
- [ ] Team collaboration features

### Phase 4
- [ ] Mobile app (React Native)
- [ ] Slack integration
- [ ] Advanced analytics dashboard
- [ ] Custom battle cards library

---

## Tech Stack

- **Framework:** React 18 + Vite
- **Routing:** React Router v6
- **Styling:** Tailwind CSS
- **HTTP Client:** Axios
- **Icons:** Heroicons
- **Auth:** Scalekit (planned)
- **State:** React Hooks (local state)

---

## Resources

- **React Docs:** https://react.dev/
- **Tailwind CSS:** https://tailwindcss.com/docs
- **Apify:** https://apify.com/
- **Scalekit:** https://www.scalekit.com/docs
- **Backend API Docs:** http://localhost:8000/docs (when running)

---

## Support

For issues:
1. Check browser console (F12)
2. Check backend logs (terminal)
3. Verify API connections
4. Review this guide

**Dashboard is ready to use! 🚀**
