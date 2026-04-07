# 🚀 Meetstream AI - Complete System Guide

## ✅ **Everything is Built and Ready!**

You now have a complete AI-powered sales intelligence platform with 3 components:

### **1. Web Dashboard** (`frontend/`)
Beautiful React app for preparing meetings with AI

### **2. AI Backend** (`backend/`)
FastAPI server with 5 specialized AI agents powered by OpenAI GPT-4

### **3. Chrome Extension** (`salesstream-extension/`)
Real-time insights overlay for Google Meet

---

## 🎯 **Quick Start**

### **Option 1: Start Everything (Recommended)**

```bash
cd "/Users/jeetshah/Documents/Meetstream AI"
./start-all.sh
```

This starts:
- ✅ Backend on `http://localhost:8000`
- ✅ Frontend on `http://localhost:5173`

**Then open browser:** `http://localhost:5173`

---

### **Option 2: Start Individually**

**Terminal 1 - Backend:**
```bash
cd backend
./start.sh
```

**Terminal 2 - Frontend:**
```bash
cd frontend
npm run dev
```

---

## 📱 **Using the Web Dashboard**

### **1. Login**
- Open: `http://localhost:5173`
- Use any placeholder credentials in local demo mode
- Click "Sign in"

### **2. Set Up Your Profile**
- Click "Profile" in navigation
- Fill in your company details:
  - Company name, website, industry
  - Your role
  - Products/services
  - Value proposition
  - Target market
  - Competitors
- Click "Save Profile"

### **3. Prepare for a Meeting**
- Click "Dashboard" → "Prepare New Meeting"
- Fill in prospect information:
  - **Prospect:** Name, email, role, LinkedIn URL
  - **Company:** Name, website, LinkedIn page
  - **Meeting:** Date, goal, notes
- Click **"Start AI Research"**

**What happens:**
1. ✅ Fetches LinkedIn profile (if URL provided)
2. ✅ AI agents scrape company website
3. ✅ Generates insights:
   - Company overview
   - Key products
   - Talking points
   - Objection handlers
4. ✅ Saves meeting to "Past Meetings"

### **4. View Insights**
Insights appear in the right panel:
- 📊 LinkedIn profile summary
- 🏢 Company overview
- 📦 Key products/services
- 💡 Talking points for the call
- 🎯 How to handle objections

### **5. Review Past Meetings**
- Click "Past Meetings"
- Select any meeting from the list
- View all insights, LinkedIn data, notes

---

## 🎨 **Chrome Extension Usage**

### **Setup:**
1. Open Chrome → `chrome://extensions/`
2. Enable "Developer mode"
3. Click "Load unpacked"
4. Select folder: `salesstream-extension/`

### **During a Meeting:**
1. Join any Google Meet call
2. Extension overlay appears automatically
3. Click extension icon → Enter company URL
4. Click "Start Research"
5. Insights appear in overlay in real-time!

---

## 🤖 **AI Agents Overview**

Your system includes 5 specialized AI agents:

### **1. Research Agent**
- **What it does:** Scrapes company websites, extracts info
- **Output:** Company description, products, pain points
- **Uses:** Playwright web scraping + OpenAI GPT-4

### **2. Social Intelligence Agent**
- **What it does:** Analyzes LinkedIn profiles & company pages
- **Output:** Employee info, company culture, recent hires
- **Integration:** Apify (placeholder ready)

### **3. Review Analysis Agent**
- **What it does:** Scrapes G2, Capterra, Reddit for reviews
- **Output:** Customer complaints, common pain points
- **Use case:** Find competitor weaknesses

### **4. Conversation Agent**
- **What it does:** Analyzes real-time meeting transcripts
- **Output:** Detects objections, questions, buying signals
- **Integration:** Meetstream (ready for webhook)

### **5. Strategy Agent**
- **What it does:** Synthesizes all insights into battle card
- **Output:** Complete sales strategy, talking points, next steps

---

## 🔗 **Integrations**

### **1. OpenAI GPT-4** ✅ ACTIVE
- **Status:** Configured and working
- **API Key:** In `backend/.env`
- **Model:** GPT-4o (optimized)
- **Cost:** ~$0.015-0.03 per company research

### **2. Apify (LinkedIn)** 🟡 READY
- **Status:** Placeholder implemented
- **To activate:**
  1. Sign up: https://apify.com/
  2. Get API token
  3. Add to `backend/.env`: `APIFY_TOKEN=your_token`
  4. Install: `pip install apify-client`
- **Cost:** $0.40 per 1000 profiles

**Implementation:**
```python
# backend/main.py - already has placeholder
from apify_client import ApifyClient

client = ApifyClient(os.getenv("APIFY_TOKEN"))
run = client.actor("apify/linkedin-profile-scraper").call(
    run_input={"startUrls": [{"url": linkedin_url}]}
)
```

### **3. Scalekit (SSO)** 🟡 READY
- **Status:** Button in Login page
- **To activate:**
  1. Sign up: https://www.scalekit.com/
  2. Get Client ID & Environment URL
  3. Add to `frontend/.env`:
     ```
     VITE_SCALEKIT_CLIENT_ID=your_id
     VITE_SCALEKIT_ENVIRONMENT_URL=https://your-env.scalekit.io
     ```
  4. Uncomment Scalekit code in `frontend/src/pages/Login.jsx`

### **4. Meetstream (Transcription)** 🟡 READY
- **Status:** Webhook endpoint ready in backend
- **Endpoint:** `POST /webhook/meetstream`
- **To activate:** Configure Meetstream to send webhooks to your backend

---

## 📊 **API Endpoints**

Your backend provides these endpoints:

### **Health & Status**
```
GET  /                  # Health check
GET  /health            # Detailed status
```

### **Research**
```
POST /api/research      # Trigger AI research
```

### **Profile Management**
```
POST /api/profile                # Save user profile
GET  /api/profile/{userId}       # Get profile
```

### **Meeting Management**
```
POST /api/meeting-prep           # Save meeting prep
GET  /api/meeting-prep/{meetingId}  # Get meeting
GET  /api/meetings/{userId}      # List all meetings
GET  /api/meetings/{meetingId}/insights  # Get insights
```

### **LinkedIn Integration**
```
POST /api/linkedin/profile       # Fetch LinkedIn profile
POST /api/linkedin/company       # Fetch company page
```

### **WebSocket**
```
WS   /ws                        # Real-time updates
```

---

## 🗂️ **File Structure**

```
Meetstream AI/
├── backend/                     # FastAPI backend
│   ├── agents/                  # 5 AI agents
│   │   ├── research_agent.py
│   │   ├── conversation_agent.py
│   │   ├── social_intelligence_agent.py
│   │   ├── review_analysis_agent.py
│   │   └── strategy_agent.py
│   ├── mcp_servers/             # Web scraping
│   │   └── web_scraper_mcp/
│   ├── services/
│   │   ├── openai_client.py     # OpenAI wrapper
│   │   ├── websocket_manager.py
│   │   └── agent_orchestrator.py
│   ├── main.py                  # FastAPI app
│   ├── requirements.txt
│   ├── .env                     # Your API keys
│   └── start.sh
│
├── frontend/                    # React dashboard
│   ├── src/
│   │   ├── pages/
│   │   │   ├── Login.jsx
│   │   │   ├── Dashboard.jsx
│   │   │   ├── ProfileSetup.jsx
│   │   │   ├── MeetingPrep.jsx
│   │   │   └── PastMeetings.jsx
│   │   ├── components/
│   │   │   └── Navbar.jsx
│   │   ├── services/
│   │   │   └── api.js           # API client
│   │   ├── App.jsx
│   │   └── main.jsx
│   ├── package.json
│   └── tailwind.config.js
│
├── salesstream-extension/       # Chrome extension
│   ├── manifest.json
│   ├── content.js               # Overlay + WebSocket
│   ├── popup.html
│   ├── popup.js
│   └── icons/
│
├── start-all.sh                 # Start everything
├── README.md
├── FRONTEND_GUIDE.md
└── COMPLETE_SYSTEM_GUIDE.md     # This file
```

---

## 🎓 **Workflow Example**

### **Scenario:** You have a meeting with Stripe tomorrow

**Step 1: Login**
- Open `http://localhost:5173`
- Login with your email

**Step 2: Prepare**
- Go to "Prepare New Meeting"
- Fill in:
  - Prospect: John Doe, VP of Sales
  - Company: Stripe, https://stripe.com
  - LinkedIn: https://linkedin.com/in/johndoe
  - Goal: Discovery call

**Step 3: Research**
- Click "Start AI Research"
- Wait 10-30 seconds
- AI generates:
  - ✅ Company overview
  - ✅ Product analysis
  - ✅ Talking points
  - ✅ LinkedIn profile summary

**Step 4: Review**
- Read insights in right panel
- Note key talking points
- Review prospect's background

**Step 5: During Meeting**
- Join Google Meet
- Extension overlay shows real-time insights
- Reference talking points
- AI suggests responses (if transcript connected)

**Step 6: After Meeting**
- Go to "Past Meetings"
- Review notes and insights
- Plan follow-up actions

---

## 💡 **Tips & Best Practices**

### **For Best AI Insights:**
1. ✅ Complete your Profile first (helps AI understand your company)
2. ✅ Provide LinkedIn URLs (more context = better insights)
3. ✅ Add meeting goals (AI tailors insights to your objective)
4. ✅ Review insights before the call

### **Cost Optimization:**
- Switch to GPT-4o-mini in `openai_client.py` for 15x cheaper
- Enable caching for repeated research (coming soon)
- Use Apify selectively (costs per profile)

### **Security:**
- Never commit `.env` files
- Rotate API keys regularly
- Use Scalekit SSO for team access
- Add authentication to backend in production

---

## 🚨 **Troubleshooting**

### **Frontend won't start**
```bash
cd frontend
rm -rf node_modules package-lock.json
npm install
npm run dev
```

### **Backend won't start**
```bash
cd backend
source venv/bin/activate
pip install -r requirements.txt
python main.py
```

### **"OPENAI_API_KEY not found"**
```bash
# Check if key is in .env
cat backend/.env | grep OPENAI_API_KEY

# If missing, add it
echo "OPENAI_API_KEY=<your_openai_api_key_here>" >> backend/.env
```

### **CORS errors in browser**
Check `backend/.env`:
```
ALLOWED_ORIGINS=http://localhost:5173
```

### **AI research fails**
1. Check backend logs (terminal)
2. Verify OpenAI API key is valid
3. Check API quota: https://platform.openai.com/usage

---

## 📈 **Next Steps**

### **Immediate (Works Now):**
1. ✅ Use web dashboard for meeting prep
2. ✅ Get AI-powered company insights
3. ✅ Review past meetings
4. ✅ Use Chrome extension in Google Meet

### **Integrate (Ready to Add):**
1. 🔗 Add Apify for real LinkedIn data
2. 🔗 Add Scalekit for SSO authentication
3. 🔗 Connect Meetstream for real-time transcripts
4. 🗄️ Add PostgreSQL database (replace localStorage)

### **Future Enhancements:**
- Email reminders for meetings
- Calendar integration (Google, Outlook)
- CRM sync (Salesforce, HubSpot)
- Team collaboration features
- Mobile app
- Slack integration

---

## 🎉 **You're All Set!**

Your complete AI sales intelligence platform is ready:

1. **Start services:** `./start-all.sh`
2. **Open dashboard:** `http://localhost:5173`
3. **Login and explore!**

**Questions?**
- Check `FRONTEND_GUIDE.md` for frontend details
- Check `README.md` for system architecture
- Check backend logs for errors
- Review browser console (F12) for frontend issues

---

**Built with ❤️ using OpenAI GPT-4, FastAPI, React, and Chrome Extensions**

**Happy Selling! 🚀**
