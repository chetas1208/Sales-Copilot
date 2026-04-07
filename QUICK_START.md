# ⚡ Quick Start - Meetstream AI

## 🎉 Everything is Built and Ready!

### ✅ **What You Have:**

1. **Web Dashboard** - Beautiful React app for meeting prep
2. **AI Backend** - 5 specialized agents powered by OpenAI
3. **Chrome Extension** - Real-time insights in Google Meet
4. **Apify Integration** - Ready for LinkedIn scraping
5. **Scalekit Auth** - Ready for SSO

---

## 🚀 **Start in 30 Seconds**

### **Step 1: Add Your OpenAI API Key**

```bash
# Edit the .env file
nano backend/.env

# Make sure it has:
OPENAI_API_KEY=<your_openai_api_key_here>
```

⚠️ **Important:** You said you revoked the old key. Add your new one!

### **Step 2: Start Everything**

```bash
cd "/Users/jeetshah/Documents/Meetstream AI"
./start-all.sh
```

This opens tmux with 2 panes:
- **Left:** Backend (Python FastAPI)
- **Right:** Frontend (React/Vite)

### **Step 3: Open Dashboard**

**Browser:** http://localhost:5173

---

## 🎯 **First Time Usage**

### **1. Login**
- Use any placeholder credentials in local demo mode
- Click "Sign in"

### **2. Set Up Profile**
- Click "Profile"
- Fill your company info
- Save

### **3. Prepare Meeting**
- Click "Dashboard" → "Prepare New Meeting"
- Fill prospect details:
  ```
  Prospect: John Doe
  Role: VP of Sales
  Company: Stripe
  Website: https://stripe.com
  LinkedIn: https://linkedin.com/in/johndoe (optional)
  ```
- Click **"Start AI Research"**
- Wait 10-20 seconds
- ✅ AI generates insights!

### **4. View Insights**
Right panel shows:
- Company overview
- Key products
- Talking points
- LinkedIn profile (if URL provided)

### **5. Review Later**
- Click "Past Meetings"
- Select meeting
- View all insights

---

## 🎨 **Chrome Extension (Optional)**

1. Chrome → `chrome://extensions/`
2. Enable "Developer mode"
3. "Load unpacked" → Select `salesstream-extension/`
4. Join Google Meet
5. Enter company URL in extension
6. Get real-time insights!

---

## 🔗 **Ready to Integrate**

### **Scalekit (Enterprise SSO) - FULLY INTEGRATED! ✅**

Scalekit authentication is now fully implemented with backend and frontend code ready!

```bash
# 1. Sign up at https://www.scalekit.com/
# 2. Create a new environment
# 3. Go to Settings → Environment Details
# 4. Copy your credentials

# 5. Add to backend/.env:
SCALEKIT_ENVIRONMENT_URL=https://yourcompany.scalekit.com
SCALEKIT_CLIENT_ID=skc_test_xxxxxxxxxxxxx
SCALEKIT_CLIENT_SECRET=<your_scalekit_client_secret>

# 6. Install Scalekit SDK (if not already installed):
cd backend
source venv/bin/activate
pip install -r requirements.txt

# 7. Configure redirect URIs in Scalekit dashboard:
# - http://localhost:5173/auth/callback (development)
# - https://yourdomain.com/auth/callback (production)

# 8. Restart backend:
./start.sh

# 9. Test SSO:
# - Go to http://localhost:5173/login
# - Click "SSO with Scalekit" button
# - Complete authentication flow
# - Get redirected back to dashboard with user logged in!
```

**What's Implemented:**
- ✅ Backend: `scalekit_auth.py` service with all methods
- ✅ Backend: 4 authentication endpoints (login, callback, refresh, logout)
- ✅ Frontend: Login page with SSO button
- ✅ Frontend: OAuth callback handler page
- ✅ Frontend: Token storage and user session management

**Backend Endpoints:**
- `GET /auth/scalekit/login?redirect_uri=...` - Returns authorization URL
- `GET /auth/scalekit/callback?code=...` - Exchanges code for tokens
- `POST /auth/scalekit/refresh` - Refreshes access token
- `GET /auth/scalekit/logout` - Returns logout URL

### **Apify (LinkedIn Scraping)**
```bash
# 1. Sign up: https://apify.com/
# 2. Get API token from https://console.apify.com/account/integrations
# 3. Add to backend/.env:
APIFY_TOKEN=your_token_here

# 4. Install client:
cd backend
source venv/bin/activate
pip install apify-client

# 5. Restart backend
# LinkedIn scraping will now work in Meeting Prep page!
```

---

## 📝 **Key Files**

- `backend/.env` - Your OpenAI API key
- `start-all.sh` - Start everything
- `COMPLETE_SYSTEM_GUIDE.md` - Full documentation
- `FRONTEND_GUIDE.md` - Dashboard details
- `README.md` - System architecture

---

## 🐛 **Troubleshooting**

### **"OPENAI_API_KEY not found"**
```bash
# Add new key to backend/.env
echo "OPENAI_API_KEY=<your_openai_api_key_here>" >> backend/.env
```

### **Frontend not loading**
```bash
cd frontend
npm install
npm run dev
```

### **Backend not starting**
```bash
cd backend
./start.sh
# Check for errors in terminal
```

### **CORS errors**
```bash
# Make sure backend/.env has:
ALLOWED_ORIGINS=http://localhost:5173
```

---

## 💡 **What It Does**

### **Web Dashboard:**
- 📝 **Profile Setup** - Your company info
- 🎯 **Meeting Prep** - AI-powered research
- 📊 **Past Meetings** - Review insights
- 🔗 **LinkedIn Integration** - Profile scraping

### **AI Agents:**
- 🤖 **Research Agent** - Scrapes company websites
- 👥 **Social Intelligence** - LinkedIn analysis
- ⭐ **Review Analysis** - Customer sentiment
- 💬 **Conversation Agent** - Real-time transcript analysis
- 🎯 **Strategy Agent** - Synthesizes battle cards

### **Chrome Extension:**
- 🎨 Beautiful glassmorphism overlay
- 📡 WebSocket connection to backend
- ⚡ Real-time insights during calls

---

## 🎓 **Example Workflow**

```
1. Open http://localhost:5173
2. Login with any email
3. Go to "Prepare New Meeting"
4. Enter:
   - Prospect: John Doe
   - Company: https://stripe.com
   - Meeting goal: Discovery call
5. Click "Start AI Research"
6. Wait 15 seconds
7. Read AI insights
8. Use insights in your meeting!
```

---

## 🚨 **Current Status**

✅ **Working Now:**
- Web dashboard
- AI research agents
- OpenAI GPT-4 integration
- Company website scraping
- Meeting preparation
- Past meetings review

🟡 **Ready to Enable:**
- Apify LinkedIn scraping (add API token)
- Scalekit SSO (add credentials)
- Meetstream transcription (webhook ready)

---

## 📞 **Services Running**

When you run `./start-all.sh`:

- ✅ Backend API: http://localhost:8000
- ✅ Frontend Dashboard: http://localhost:5173
- ✅ Health Check: http://localhost:8000/health
- ✅ API Docs: http://localhost:8000/docs

---

## 🎉 **You're Ready!**

```bash
# Start everything:
./start-all.sh

# Then open:
http://localhost:5173
```

**Happy Selling! 🚀**
