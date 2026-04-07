# SalesStream Overlook - Chrome Extension

Real-time AI sales assistant overlay for Google Meet.

## 📦 Installation

### Step 1: Load the Extension in Chrome

1. Open **Chrome** and navigate to `chrome://extensions/`
2. Enable **Developer mode** (toggle in top-right corner)
3. Click **"Load unpacked"**
4. Select the `salesstream-extension` folder
5. The extension should now appear in your extensions list

### Step 2: Test It

1. Go to [Google Meet](https://meet.google.com/)
2. Join or start a meeting
3. You should see the **SalesStream Overlook** glassmorphism overlay appear in the top-right corner

## ✨ Features

- **Glassmorphism Design**: Beautiful frosted-glass overlay
- **Draggable**: Click and drag the header to reposition
- **Minimizable**: Click the `-` button to minimize
- **Shadow DOM**: Isolated styling that won't conflict with Google Meet
- **Bot Creation**: One-click bot creation for Google Meet transcription
- **Live Transcription**: Real-time transcript display from Meetstream API
- **Webhook Inspector**: Debug and view incoming webhook payloads
- **AI Integration Ready**: Sections for insights, suggestions, and next steps

## 🎮 Controls

- **Drag**: Click and hold the header to move the overlay
- **Minimize**: Click the `−` button
- **Close**: Click the `×` button

## 🤖 How to Start a Recording Bot

1. **Join a Google Meet** call (e.g., `https://meet.google.com/abc-defg-hij`)
2. **Click the extension icon** (puzzle piece in Chrome toolbar)
3. **Click "Start Recording Bot"** button
4. The bot will automatically:
   - Fetch the current Google Meet URL
   - Create a Meetstream bot for that meeting
   - Join the call with transcription enabled
   - Start sending live transcripts to your overlay

**Requirements:**
- Backend must be running at `http://localhost:8000`
- `MEETSTREAM_API_KEY` must be configured in your `.env` file
- You must be on an active Google Meet page when clicking the button

**Bot Features:**
- Real-time transcription via AssemblyAI Streaming
- Automatic webhook integration
- Live transcript display in the overlay
- Word-level timing and speaker identification

## 🔧 Troubleshooting

### Overlay doesn't appear:
- Make sure you're on a `meet.google.com` URL (not just the homepage)
- Check the extension is enabled in `chrome://extensions/`
- Open DevTools (F12) and check for console errors
- Try refreshing the Google Meet page

### Overlay conflicts with Meet UI:
- The overlay uses Shadow DOM to prevent style conflicts
- Try dragging it to a different position

## 📁 Project Structure

```
salesstream-extension/
├── manifest.json       # Extension configuration
├── content.js          # Main script that injects the overlay
├── styles.css          # Global styles (minimal)
├── popup.html          # Extension popup UI
├── icon16.png          # Extension icon (16x16)
├── icon48.png          # Extension icon (48x48)
├── icon128.png         # Extension icon (128x128)
└── README.md           # This file
```

## 🚀 Next Steps

**Phase 2**: FastAPI backend with WebSocket support
**Phase 3**: MeetStream integration for real-time transcription
**Phase 4**: AI-powered battle cards and suggestions
**Phase 5**: ScaleKit CRM authentication

## 🐛 Known Issues

- None yet! This is the MVP version.

## 📝 Notes

- The overlay currently shows placeholder content
- Real-time AI features will be added in Phase 4
- CRM integration coming in Phase 5
