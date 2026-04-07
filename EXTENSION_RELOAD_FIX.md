# Extension Not Working - Quick Fix

## The Problem

When you click "Start Research", you see "Please open a Google Meet page first!" even though you ARE on a Google Meet page.

**Cause:** The content script (`content.js`) isn't loaded on the page yet, or needs to be reloaded after updates.

## The Solution

### Step 1: Reload the Extension

1. Open a new tab and go to: `chrome://extensions/`
2. Find **"SalesStream Overlook"**
3. Click the **reload icon** (circular arrow) on the extension card
4. You should see the extension reload

### Step 2: Refresh the Google Meet Page

1. Go back to your Google Meet tab
2. **Hard refresh** the page: `Cmd+Shift+R` (Mac) or `Ctrl+Shift+F5` (Windows)
3. Wait for the page to fully load

### Step 3: Verify the Overlay Appears

1. After the page loads, you should see the **glassmorphism overlay** appear in the top-right corner
2. If you see the overlay, the content script is loaded!

### Step 4: Try "Start Research" Again

1. Click the extension icon
2. Enter your company URLs
3. Click "Start Research"
4. Should work now!

## Debugging

### Check if Content Script is Loaded

1. On the Google Meet page, press `F12` to open DevTools
2. Go to the **Console** tab
3. Look for: `[SalesStream] Overlay initialized`
4. If you see it, content script is loaded ✅
5. If not, reload the extension and refresh the page

### Check for Errors

In the Console, look for:
- Red error messages
- `chrome.runtime.lastError`
- `Failed to load resource` errors

### Still Not Working?

**Try this:**

1. **Remove and re-add the extension:**
   ```
   chrome://extensions/
   → Remove "SalesStream Overlook"
   → Click "Load unpacked"
   → Select the salesstream-extension folder again
   ```

2. **Check manifest permissions:**
   - Extension should have permission for `meet.google.com/*`
   - Check if Chrome is blocking the extension

3. **Check backend is running:**
   ```bash
   curl http://localhost:8000/health
   ```
   Should return: `{"status": "healthy"}`

4. **Test the popup console:**
   - Right-click extension icon
   - Click "Inspect popup"
   - Check Console for errors when clicking "Start Research"

## Expected Behavior (When Working)

### 1. Extension Icon Clicked
Popup opens with two input fields

### 2. Enter URLs
```
Your Company: https://www.nvidia.com
Target Company: https://www.cadence.com/en_US/home/ai/overview.html
```

### 3. Click "Start Research"
- Button changes to "Researching..."
- Status message: "Starting web crawler and AI analysis..."

### 4. Content Script Receives Message
- Console log: "Sending START_RESEARCH message to content script"
- Content script responds: `{ success: true }`

### 5. WebSocket Sends to Backend
- Overlay status changes to: "Web crawler active - Researching companies..."

### 6. Backend Processes
- Backend logs show: "🎯 Product-need matching mode"
- Web crawler starts scraping both companies

### 7. Insights Appear
- After 15-20 seconds
- Overlay shows real-time insights
- "🎯 How to Help..." section appears

## Common Issues

### Issue: "Extension needs reload! Go to chrome://extensions/"

**Solution:**
- Go to `chrome://extensions/`
- Click reload on SalesStream Overlook
- Refresh Google Meet page

### Issue: "Please open a Google Meet page first!"

**Cause:** Not on a `meet.google.com/*` URL

**Solution:**
- Make sure you're on a URL like: `meet.google.com/abc-defg-hij`
- NOT just `meet.google.com` homepage

### Issue: Overlay not appearing

**Solution:**
1. Check DevTools Console for errors
2. Reload extension
3. Hard refresh page (Cmd+Shift+R)
4. Check if content.js file exists in extension folder

### Issue: "Failed to start research"

**Possible causes:**
- Backend not running
- WebSocket connection failed
- Invalid URLs

**Solution:**
```bash
# Check backend
curl http://localhost:8000/health

# Restart backend
cd backend
python3 -m uvicorn main:app --reload
```

## Quick Test

**To verify everything is working:**

1. **Test content script:**
   - Open Google Meet: `meet.google.com/test-abc-def`
   - Look for glassmorphism overlay
   - If you see it, content script ✅

2. **Test popup:**
   - Click extension icon
   - Popup should open
   - If it opens, popup ✅

3. **Test backend:**
   ```bash
   curl http://localhost:8000/health
   ```
   Should return healthy status
   If yes, backend ✅

4. **Test research:**
   - Enter: Your Company = `https://stripe.com`
   - Enter: Target = `https://anthropic.com`
   - Click "Start Research"
   - Wait 20 seconds
   - Check overlay for insights
   - If insights appear, everything ✅

## Still Having Issues?

**Debug checklist:**

- [ ] Extension reloaded via chrome://extensions/
- [ ] Google Meet page refreshed (hard refresh)
- [ ] Overlay appears on Meet page
- [ ] Backend running (curl health check)
- [ ] Console shows no errors
- [ ] WebSocket connected (check overlay status bar)
- [ ] Valid company URLs entered (https://)

**If all checked and still not working:**

1. Check browser console for specific errors
2. Check backend logs: `tail -f /tmp/backend.log`
3. Try a different Google Meet URL
4. Restart Chrome completely

## Updated Error Message

The popup now shows a more helpful message:
- Old: "Please open a Google Meet page first!"
- New: "Extension needs reload! Go to chrome://extensions/"

This tells you exactly what to do when the content script isn't responding.
