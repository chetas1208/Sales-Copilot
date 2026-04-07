# Scalekit SSO Setup Guide

## Overview

Scalekit is fully integrated into Meetstream AI! This guide will help you set up enterprise Single Sign-On (SSO) authentication using Scalekit.

## What's Already Built

✅ **Backend Implementation:**
- `backend/services/scalekit_auth.py` - Scalekit authentication service
- OAuth2 authorization code flow
- Token management (access + refresh)
- User session handling
- 4 authentication endpoints

✅ **Frontend Implementation:**
- `frontend/src/pages/Login.jsx` - SSO button with redirect
- `frontend/src/pages/AuthCallback.jsx` - OAuth callback handler
- Token storage in localStorage
- User session management
- Automatic redirect to dashboard after login

✅ **API Endpoints:**
- `GET /auth/scalekit/login` - Initiates SSO flow
- `GET /auth/scalekit/callback` - Handles OAuth callback
- `POST /auth/scalekit/refresh` - Refreshes access token
- `GET /auth/scalekit/logout` - Returns logout URL

---

## Setup Instructions

### Step 1: Create Scalekit Account

1. Go to https://www.scalekit.com/
2. Click "Sign Up" or "Get Started"
3. Complete registration
4. Verify your email

### Step 2: Create Environment

1. Log in to https://app.scalekit.com/
2. Click "Create New Environment"
3. Choose environment name (e.g., "meetstream-dev" or "meetstream-prod")
4. Select your preferred region

### Step 3: Get Credentials

1. In your Scalekit dashboard, go to **Settings → Environment Details**
2. Copy these three values:
   - **Environment URL** (e.g., `https://yourcompany.scalekit.com`)
   - **Client ID** (starts with `skc_test_` or `skc_live_`)
   - **Client Secret** (starts with `sks_test_` or `sks_live_`)

### Step 4: Configure Backend

1. Open `backend/.env` file
2. Add your Scalekit credentials:

```env
# Scalekit SSO Authentication
SCALEKIT_ENVIRONMENT_URL=https://yourcompany.scalekit.com
SCALEKIT_CLIENT_ID=skc_test_xxxxxxxxxxxxxxxxxxxxx
SCALEKIT_CLIENT_SECRET=<your_scalekit_client_secret>
```

3. Save the file

### Step 5: Install Scalekit SDK

```bash
cd backend
source venv/bin/activate  # Mac/Linux
# OR
venv\Scripts\activate  # Windows

pip install -r requirements.txt
```

This installs `scalekit-sdk-python==1.0.0`

### Step 6: Configure Redirect URIs

In your Scalekit dashboard:

1. Go to **Settings → OAuth → Redirect URIs**
2. Add these URLs:
   - **Development:** `http://localhost:5173/auth/callback`
   - **Production:** `https://yourdomain.com/auth/callback`
3. Save changes

### Step 7: Configure Logout URLs (Optional)

1. Go to **Settings → OAuth → Logout URIs**
2. Add:
   - **Development:** `http://localhost:5173/login`
   - **Production:** `https://yourdomain.com/login`

### Step 8: Restart Services

```bash
# Stop running services (Ctrl+C in terminals)

# Restart backend
cd backend
./start.sh

# Restart frontend (in another terminal)
cd frontend
npm run dev
```

### Step 9: Test SSO Flow

1. Open browser: http://localhost:5173/login
2. Click **"SSO with Scalekit"** button
3. You'll be redirected to Scalekit hosted login
4. Enter your credentials
5. Complete authentication
6. You'll be redirected back to: http://localhost:5173/auth/callback
7. Tokens are exchanged and stored
8. You're automatically redirected to dashboard
9. You're now logged in! ✅

---

## How It Works

### Authentication Flow

```
1. User clicks "SSO with Scalekit" button
   ↓
2. Frontend calls: GET /auth/scalekit/login?redirect_uri=...
   ↓
3. Backend returns authorization_url from Scalekit
   ↓
4. Frontend redirects to Scalekit hosted login
   ↓
5. User authenticates with their identity provider
   ↓
6. Scalekit redirects to: http://localhost:5173/auth/callback?code=...
   ↓
7. Frontend calls: GET /auth/scalekit/callback?code=...&redirect_uri=...
   ↓
8. Backend exchanges code for tokens via Scalekit SDK
   ↓
9. Backend returns: { user, access_token, refresh_token, expires_in }
   ↓
10. Frontend stores tokens in localStorage
    ↓
11. Frontend calls onLogin() with user data
    ↓
12. User is redirected to dashboard - logged in!
```

### Token Management

**Access Token:**
- Stored in `localStorage.getItem('access_token')`
- Used for API authentication
- Short-lived (typically 1 hour)

**Refresh Token:**
- Stored in `localStorage.getItem('refresh_token')`
- Used to get new access tokens
- Long-lived (typically 30 days)

**User Data:**
- Stored in `localStorage.getItem('user')`
- Contains: `{ id, email, name, organization_id, roles }`

### Security Notes

⚠️ **Production Recommendations:**

1. **Use HttpOnly Cookies** instead of localStorage for tokens
2. **Enable HTTPS** for all environments
3. **Implement CSRF protection**
4. **Add rate limiting** on authentication endpoints
5. **Log authentication events** for audit trails
6. **Rotate secrets regularly**

---

## API Reference

### 1. Initiate SSO Login

**Endpoint:** `GET /auth/scalekit/login`

**Query Parameters:**
- `redirect_uri` (required) - Where to redirect after authentication
- `organization_id` (optional) - Direct SSO for specific organization
- `login_hint` (optional) - Email hint for login form

**Response:**
```json
{
  "authorization_url": "https://yourcompany.scalekit.com/oauth/authorize?..."
}
```

**Example:**
```bash
curl "http://localhost:8000/auth/scalekit/login?redirect_uri=http://localhost:5173/auth/callback"
```

### 2. Handle OAuth Callback

**Endpoint:** `GET /auth/scalekit/callback`

**Query Parameters:**
- `code` (required) - Authorization code from Scalekit
- `redirect_uri` (required) - Original redirect URI

**Response:**
```json
{
  "user": {
    "id": "user_123",
    "email": "john@company.com",
    "name": "John Doe",
    "organization_id": "org_456",
    "roles": ["admin", "sales"]
  },
  "access_token": "eyJhbGciOiJSUzI1NiIs...",
  "refresh_token": "eyJhbGciOiJSUzI1NiIs...",
  "expires_in": 3600
}
```

### 3. Refresh Access Token

**Endpoint:** `POST /auth/scalekit/refresh`

**Body:**
```json
{
  "refresh_token": "eyJhbGciOiJSUzI1NiIs..."
}
```

**Response:**
```json
{
  "access_token": "eyJhbGciOiJSUzI1NiIs...",
  "expires_in": 3600
}
```

### 4. Get Logout URL

**Endpoint:** `GET /auth/scalekit/logout`

**Query Parameters:**
- `redirect_uri` (required) - Where to redirect after logout

**Response:**
```json
{
  "logout_url": "https://yourcompany.scalekit.com/oauth/logout?..."
}
```

---

## Code Reference

### Backend Service

**File:** `backend/services/scalekit_auth.py`

```python
from scalekit import ScalekitClient

class ScalekitAuth:
    def __init__(self):
        self.client = ScalekitClient(
            environment_url=os.getenv("SCALEKIT_ENVIRONMENT_URL"),
            client_id=os.getenv("SCALEKIT_CLIENT_ID"),
            client_secret=os.getenv("SCALEKIT_CLIENT_SECRET")
        )

    def get_authorization_url(self, redirect_uri, organization_id=None):
        return self.client.get_authorization_url(
            redirect_uri=redirect_uri,
            scopes=["openid", "profile", "email", "offline_access"],
            organization_id=organization_id
        )

    async def handle_callback(self, code, redirect_uri):
        result = self.client.authenticate_with_code(
            code=code,
            redirect_uri=redirect_uri
        )
        return {
            "user": {
                "id": result.user.id,
                "email": result.user.email,
                "name": result.user.name,
                "organization_id": result.user.organization_id
            },
            "access_token": result.access_token,
            "refresh_token": result.refresh_token,
            "expires_in": result.expires_in
        }
```

### Frontend SSO Button

**File:** `frontend/src/pages/Login.jsx`

```javascript
const handleScalekitLogin = async () => {
  setIsLoading(true)

  try {
    const response = await fetch(
      'http://localhost:8000/auth/scalekit/login?redirect_uri=http://localhost:5173/auth/callback'
    )
    const data = await response.json()

    if (data.authorization_url) {
      // Redirect to Scalekit hosted login
      window.location.href = data.authorization_url
    }
  } catch (error) {
    console.error('Scalekit login error:', error)
    alert('SSO is not configured yet')
    setIsLoading(false)
  }
}
```

### Frontend Callback Handler

**File:** `frontend/src/pages/AuthCallback.jsx`

```javascript
useEffect(() => {
  const code = searchParams.get('code')

  const response = await fetch(
    `http://localhost:8000/auth/scalekit/callback?code=${code}&redirect_uri=http://localhost:5173/auth/callback`
  )
  const data = await response.json()

  // Store tokens
  localStorage.setItem('access_token', data.access_token)
  localStorage.setItem('refresh_token', data.refresh_token)

  // Login user
  onLogin({
    id: data.user.id,
    email: data.user.email,
    name: data.user.name,
    organization_id: data.user.organization_id,
    roles: data.user.roles || []
  })

  // Redirect to dashboard
  navigate('/')
}, [searchParams])
```

---

## Troubleshooting

### Error: "Scalekit not configured"

**Problem:** Backend can't find Scalekit credentials

**Solution:**
1. Check `backend/.env` has all three variables
2. Make sure there are no typos in variable names
3. Restart backend after adding credentials

### Error: "Invalid redirect_uri"

**Problem:** Redirect URI not registered in Scalekit dashboard

**Solution:**
1. Go to Scalekit dashboard → Settings → OAuth → Redirect URIs
2. Add exact URL: `http://localhost:5173/auth/callback`
3. Make sure there are no trailing slashes
4. Save and try again

### Error: "Authorization code expired"

**Problem:** Took too long to complete flow (>5 minutes)

**Solution:**
- Restart the login process from beginning
- Authorization codes expire quickly for security

### Error: "Invalid client_id or client_secret"

**Problem:** Credentials are incorrect

**Solution:**
1. Go back to Scalekit dashboard
2. Verify Client ID and Client Secret
3. Copy them again carefully
4. Update `backend/.env`
5. Restart backend

### User redirected but not logged in

**Problem:** Frontend didn't handle callback properly

**Solution:**
1. Check browser console (F12) for errors
2. Verify `/auth/callback` route exists in App.jsx
3. Check that `onLogin` function is passed to AuthCallback
4. Verify localStorage has tokens

### SSO button doesn't work

**Problem:** Backend not running or wrong URL

**Solution:**
1. Check backend is running: `curl http://localhost:8000/health`
2. Check browser console for network errors
3. Verify fetch URL matches backend URL
4. Check CORS settings in backend `.env`

---

## Multi-Organization Support

Scalekit supports multi-tenant organizations. To use this:

### 1. Create Organizations in Scalekit

1. Go to Scalekit dashboard
2. Navigate to **Organizations**
3. Create organization for each tenant
4. Configure their SSO provider (SAML, OIDC, etc.)
5. Get `organization_id` for each

### 2. Direct SSO for Specific Organization

```javascript
// Frontend: Pass organization_id
const handleCompanySSO = async (organizationId) => {
  const response = await fetch(
    `http://localhost:8000/auth/scalekit/login?redirect_uri=http://localhost:5173/auth/callback&organization_id=${organizationId}`
  )
  const data = await response.json()
  window.location.href = data.authorization_url
}
```

### 3. Email Domain Detection

```javascript
// Frontend: Use login_hint for auto-org detection
const handleEmailSSO = async (email) => {
  const response = await fetch(
    `http://localhost:8000/auth/scalekit/login?redirect_uri=http://localhost:5173/auth/callback&login_hint=${email}`
  )
  const data = await response.json()
  window.location.href = data.authorization_url
}
```

Scalekit will automatically detect organization from email domain.

---

## Testing

### Manual Testing

1. Start services
2. Go to http://localhost:5173/login
3. Click "SSO with Scalekit"
4. Complete authentication
5. Verify:
   - ✅ Redirected to dashboard
   - ✅ User name shown in navbar
   - ✅ localStorage has `access_token`, `refresh_token`, `user`
   - ✅ Can navigate to Profile, Meeting Prep, etc.
   - ✅ Logout works

### Test with Multiple Users

1. Login with User A
2. Verify dashboard shows User A's data
3. Logout
4. Login with User B
5. Verify dashboard shows User B's data

### Test Token Refresh

```javascript
// Call refresh endpoint after access token expires
const refreshToken = localStorage.getItem('refresh_token')

const response = await fetch('http://localhost:8000/auth/scalekit/refresh', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({ refresh_token: refreshToken })
})

const data = await response.json()
localStorage.setItem('access_token', data.access_token)
```

---

## Production Deployment

### Backend Configuration

```env
# Production .env
SCALEKIT_ENVIRONMENT_URL=https://yourcompany.scalekit.com
SCALEKIT_CLIENT_ID=skc_live_xxxxxxxxxxxxx
SCALEKIT_CLIENT_SECRET=<your_scalekit_client_secret>
ALLOWED_ORIGINS=https://yourdomain.com
```

### Frontend Configuration

Update redirect URIs in:
- Login.jsx: `https://yourdomain.com/auth/callback`
- AuthCallback.jsx: `https://yourdomain.com/auth/callback`

### Scalekit Dashboard

Add production redirect URIs:
- `https://yourdomain.com/auth/callback`
- `https://yourdomain.com/login` (logout)

### Security Checklist

- [ ] Use HTTPS everywhere
- [ ] Switch from localStorage to HttpOnly cookies
- [ ] Enable CSRF protection
- [ ] Add rate limiting
- [ ] Implement token rotation
- [ ] Log authentication events
- [ ] Set up monitoring and alerts
- [ ] Use live credentials (not test)
- [ ] Rotate secrets regularly
- [ ] Review CORS settings

---

## Support

**Scalekit Documentation:**
- Main docs: https://docs.scalekit.com/
- Quickstart: https://docs.scalekit.com/quickstart
- Python SDK: https://docs.scalekit.com/sdks/python

**Meetstream AI:**
- General setup: See `QUICK_START.md`
- Frontend guide: See `FRONTEND_GUIDE.md`
- Backend guide: See `COMPLETE_SYSTEM_GUIDE.md`

---

**Built with Scalekit for enterprise-grade SSO authentication!** 🔐
