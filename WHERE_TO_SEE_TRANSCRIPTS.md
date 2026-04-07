# 📍 WHERE TO SEE LIVE TRANSCRIPTION (Step-by-Step)

## ✅ Backend Status: WORKING
- Webhook is receiving transcripts ✅
- Transcripts are being processed ✅
- Backend is ready to broadcast ✅

## ❌ Issue: Extension Not Connected
- **Problem**: Extension is not connecting to WebSocket
- **Result**: Transcripts are processed but have nowhere to display

---

## 🔧 STEP-BY-STEP FIX

### Step 1: Load the Chrome Extension

1. **Open Chrome**

2. **Go to**: `chrome://extensions/`

3. **Enable "Developer mode"** (toggle in top-right corner)

4. **Click "Load unpacked"**

5. **Navigate to and select**:
   ```
   /Users/jeetshah/Documents/Meetstream AI/salesstream-extension
   ```

6. **You should see**: "SalesStream Overlook" extension loaded with green checkmark

---

### Step 2: Open a Google Meet Tab

1. **Go to**: `https://meet.google.com/`

2. **Create or join ANY meeting** (can be a test meeting)

3. **The overlay MUST appear** in the top-right corner:
   ```
   ┌────────────────────────────────┐
   │ SS  SalesStream Overlook   [−][×]│
   └────────────────────────────────┘
   ```

4. **Scroll down in the overlay** to the bottom

5. **Check the status bar**:
   - ✅ Should say: "Connected to AI Backend" (green dot)
   - ❌ If says: "Disconnected" (red dot) → See troubleshooting below

---

### Step 3: Look for the Transcription Section

**The transcript section is at the TOP of the overlay:**

```
┌────────────────────────────────────────────┐
│ SalesStream Overlook              [−] [×]  │
├────────────────────────────────────────────┤
│                                            │
│ 🎙️ Live Transcription        ← HERE!     │
│ ┌────────────────────────────────────────┐│
│ │ 03:00:00 Jeet Shah: Hello everyone    ││
│ │ 03:00:03 Client: Hi Jeet, good to...  ││
│ │ 03:00:06 Jeet Shah: Let's discuss...  ││
│ └────────────────────────────────────────┘│
│                                            │
│ • Real-time Insights                       │
│ ┌────────────────────────────────────────┐│
│ │ Listening for conversation context...  ││
│ └────────────────────────────────────────┘│
└────────────────────────────────────────────┘
```

---

### Step 4: Send Test Transcripts

**While on Google Meet page with extension loaded:**

```bash
cd "/Users/jeetshah/Documents/Meetstream AI"
python3 test_transcript_simulation.py
```

**Within 2 seconds**, you should see transcripts appear in the "🎙️ Live Transcription" section!

---

## 🔍 Troubleshooting

### Issue: "Extension not showing on Google Meet"

**Solution:**
1. Make sure you're on `https://meet.google.com/` (not just google.com)
2. Refresh the page (Cmd+R)
3. Check Chrome DevTools (F12) → Console for errors
4. Extension only loads on `meet.google.com` pages

---

### Issue: "Overlay shows but says 'Disconnected'"

**Check if backend is running:**
```bash
curl http://localhost:8000/health
```

**Should return:**
```json
{"status":"healthy","active_connections":0,...}
```

**If not working:**
```bash
# Restart backend
pkill -9 python
cd backend
python main.py > /tmp/backend.log 2>&1 &
```

**Check WebSocket URL in extension:**
1. Open DevTools (F12)
2. Go to Console tab
3. Look for: "Connecting to backend: ws://localhost:8000/ws"
4. Should see: "[WebSocket] Connected to Meetstream AI backend"

---

### Issue: "Extension connected but no transcripts"

**Test the flow manually:**

1. **Make sure you're on a Google Meet page**
2. **Open DevTools** (F12) → Console tab
3. **Run test script**:
   ```bash
   python3 test_transcript_simulation.py
   ```
4. **In Console, you should see**:
   - "Received message: live_transcript"
   - Messages about transcript processing

**If you don't see messages:**
- Extension is not connected to WebSocket
- Reload the Google Meet page
- Check if overlay shows "Connected"

---

## 📸 Visual Guide

### What You're Looking For:

**1. Chrome Extensions Page:**
```
SalesStream Overlook
   ID: abc123...
   ✅ Enabled
```

**2. Google Meet Page:**
```
[Top-right corner of screen]
   ┌────────────────────┐
   │ SS SalesStream    │ ← Draggable overlay
   └────────────────────┘
```

**3. Inside Overlay (scroll to top):**
```
🎙️ Live Transcription    ← This section!
┌──────────────────────────┐
│ Waiting for meeting...   │ ← Before transcripts
└──────────────────────────┘

   OR after sending test:

┌──────────────────────────┐
│ 03:00:00 Jeet: Hello    │ ← After transcripts!
│ 03:00:03 Client: Hi...  │
└──────────────────────────┘
```

**4. Bottom of Overlay:**
```
● Connected to AI Backend  ← Green dot = good
```

---

## 🧪 Quick Test Checklist

Run through this checklist in order:

- [ ] Extension loaded in Chrome (`chrome://extensions/`)
- [ ] On a Google Meet page (`meet.google.com`)
- [ ] Overlay visible in top-right corner
- [ ] Status shows "Connected to AI Backend" (green)
- [ ] Ran: `python3 test_transcript_simulation.py`
- [ ] Checked "🎙️ Live Transcription" section at TOP of overlay

**If ALL checkboxes are checked and still not showing:**

Open Chrome DevTools (F12) → Console tab and send me:
1. Any error messages
2. Screenshot of the console
3. Screenshot of the overlay

---

## 💡 Common Mistakes

1. ❌ **Looking in wrong place**: Transcripts are at the TOP of overlay, not bottom
2. ❌ **Not on Google Meet**: Extension only works on `meet.google.com` pages
3. ❌ **Extension not loaded**: Check `chrome://extensions/`
4. ❌ **Page not refreshed**: After loading extension, refresh Google Meet page
5. ❌ **Wrong URL**: Must be `ws://localhost:8000/ws` for WebSocket

---

## 🎯 Expected Flow

1. Load extension
2. Go to Google Meet
3. See overlay (top-right)
4. Check status = "Connected"
5. Run test script
6. See transcripts appear in "🎙️ Live Transcription"

**If this doesn't work, open DevTools Console and look for errors!**
