# Words Array Data Structure - What You're Receiving

## Overview

Based on the ngrok inspector screenshot and Meetstream documentation, here's what the `words` array contains in each webhook payload.

---

## Real Example from Your ngrok Inspector

From the screenshot showing speaker "jeet shah" saying "maybe screenshot":

```json
{
  "bot_id": "29c35114-cefb-4f30-b7c8-3e1fc4828463",
  "speakerName": "jeet shah",
  "timestamp": "2026-03-28T22:50:24.538Z",
  "transcript": "maybe",
  "utterance": "Maybe screenshot.",
  "words": [
    {
      "word": "maybe",
      "start": 1025.44,
      "end": 1025.52,
      "confidence": 0.98253,
      "speaker": "jeet shah",
      "punctuated_word": "maybe",
      "speech_confidence": 0.98253,
      "word_is_final": true
    },
    {
      "word": "screenshot",
      "start": 1025.6,
      "end": 1026.16,
      "confidence": 0.742821,
      "speaker": "jeet shah",
      "punctuated_word": "screenshot",
      "speech_confidence": 0.742821,
      "word_is_final": false
    }
  ],
  "end_of_turn": false,
  "turn_is_formatted": false,
  "transcription_mode": "word_level"
}
```

---

## Words Array Structure

Each object in the `words[]` array contains:

### 1. **`word`** (string)
- The raw word as recognized by the speech recognition
- Example: `"maybe"`, `"screenshot"`
- **Use case:** Display raw transcription

### 2. **`start`** (number)
- Start time of the word in seconds from the beginning of audio
- Example: `1025.44` = 1025.44 seconds into the audio stream
- **Use case:**
  - Sync transcript with audio/video
  - Create karaoke-style highlighting
  - Jump to specific moments in conversation

### 3. **`end`** (number)
- End time of the word in seconds from the beginning of audio
- Example: `1025.52` = 1025.52 seconds into the audio stream
- **Duration:** `end - start` = word duration
  - "maybe": 1025.52 - 1025.44 = **0.08 seconds**
  - "screenshot": 1026.16 - 1025.6 = **0.56 seconds**
- **Use case:**
  - Calculate speaking rate
  - Detect pauses between words
  - Measure word emphasis

### 4. **`confidence`** (number, 0-1)
- Confidence score for the word recognition
- Range: 0.0 (low confidence) to 1.0 (high confidence)
- Examples from your data:
  - "maybe": **0.98253** (98.3% confident) ✅ High
  - "screenshot": **0.742821** (74.3% confident) ⚠️ Medium
- **Use case:**
  - Flag uncertain words for review
  - Color-code words by confidence
  - Filter out low-confidence words
  - Trigger clarification requests

### 5. **`speaker`** (string)
- Name of the person speaking
- Example: `"jeet shah"`
- **Use case:**
  - Speaker attribution
  - Multi-speaker conversation tracking
  - Per-speaker analytics

### 6. **`punctuated_word`** (string)
- The word with proper punctuation and capitalization
- Example: `"maybe"` → `"maybe"` (no change)
- Could be: `"hello"` → `"Hello"`, `"im"` → `"I'm"`
- **Use case:** Display formatted text to users

### 7. **`speech_confidence`** (number, 0-1)
- Alternative confidence metric (often same as `confidence`)
- Example: `0.98253`, `0.742821`
- **Use case:** Same as `confidence`

### 8. **`word_is_final`** (boolean)
- Indicates if this word is finalized or still being processed
- `true` = Final, won't change
- `false` = Interim, might be revised in next update
- Examples from your data:
  - "maybe": `true` ✅ Final
  - "screenshot": `false` ⚠️ Still being processed
- **Use case:**
  - Only display final words to reduce flickering
  - Show interim words in italic/gray
  - Commit only final words to database

---

## Analysis of Your Real Data

### Word 1: "maybe"
```json
{
  "word": "maybe",
  "start": 1025.44,
  "end": 1025.52,
  "confidence": 0.98253,
  "word_is_final": true
}
```

**Analysis:**
- ✅ **Duration:** 0.08 seconds (very quick)
- ✅ **Confidence:** 98.3% (very high)
- ✅ **Status:** Final (won't change)
- 💡 **Insight:** This is a confident, finalized word

### Word 2: "screenshot"
```json
{
  "word": "screenshot",
  "start": 1025.6,
  "end": 1026.16,
  "confidence": 0.742821,
  "word_is_final": false
}
```

**Analysis:**
- ⏱️ **Duration:** 0.56 seconds (7x longer than "maybe")
- ⚠️ **Confidence:** 74.3% (medium - might be uncertain)
- ⚠️ **Status:** Not final (could change in next update)
- 💡 **Insight:** System is still processing this word, might revise it

**Gap Between Words:**
- "maybe" ends at 1025.52
- "screenshot" starts at 1025.6
- **Pause:** 0.08 seconds between words

---

## Practical Use Cases

### 1. **Confidence-Based Color Coding**

You could color-code words in the transcript based on confidence:

```javascript
function getConfidenceColor(confidence) {
  if (confidence >= 0.95) return '#4ade80';      // Green - High
  if (confidence >= 0.85) return '#fbbf24';      // Yellow - Medium
  if (confidence >= 0.70) return '#fb923c';      // Orange - Low
  return '#f87171';                              // Red - Very Low
}

// Example:
// "maybe" (0.98253) → Green
// "screenshot" (0.742821) → Orange
```

### 2. **Filter Interim Words**

Show only final words to prevent flickering UI:

```javascript
function shouldDisplayWord(word) {
  return word.word_is_final === true;
}

// "maybe" → Display (final)
// "screenshot" → Hide or show in italic (interim)
```

### 3. **Karaoke-Style Highlighting**

Highlight words as they're spoken using timing:

```javascript
function highlightWordAtTime(currentTime, words) {
  return words.find(w =>
    currentTime >= w.start && currentTime <= w.end
  );
}

// At 1025.45 seconds → "maybe" is highlighted
// At 1025.8 seconds → "screenshot" is highlighted
```

### 4. **Speaking Rate Analysis**

Calculate words per minute:

```javascript
function calculateSpeakingRate(words) {
  const duration = words[words.length - 1].end - words[0].start;
  const wordsPerMinute = (words.length / duration) * 60;
  return wordsPerMinute;
}

// Your data: 2 words in 0.72 seconds
// Rate: (2 / 0.72) * 60 = 166 WPM (normal conversational pace)
```

### 5. **Low-Confidence Word Detection**

Flag words that might need clarification:

```javascript
function getLowConfidenceWords(words, threshold = 0.85) {
  return words.filter(w => w.confidence < threshold);
}

// In your data: "screenshot" (0.74) would be flagged
```

### 6. **Pause Detection**

Identify significant pauses in speech:

```javascript
function detectPauses(words, pauseThreshold = 0.3) {
  const pauses = [];
  for (let i = 1; i < words.length; i++) {
    const gap = words[i].start - words[i - 1].end;
    if (gap > pauseThreshold) {
      pauses.push({
        after_word: words[i - 1].word,
        before_word: words[i].word,
        duration: gap
      });
    }
  }
  return pauses;
}

// Your data: 0.08 second gap (no significant pause)
```

---

## What You Can Build With This Data

### 1. **Real-Time Transcript with Confidence Indicators**
```
[10:50:24] jeet shah:
  ✅ maybe (98%)
  ⚠️ screenshot (74%, interim)
```

### 2. **Word-by-Word Timeline**
```
1025.44s ──┬── maybe (0.08s, 98%) ──┬── 0.08s gap ──┬── screenshot (0.56s, 74%)
           │                        │               │
        [start]                  [end]           [end]
```

### 3. **Speaking Pace Visualization**
```
Fast    │█████░░░░░░│ Slow
        │  "maybe"  │

Fast    │░░░░░░█████│ Slow
        │"screenshot"│
```

### 4. **Confidence Heatmap**
```
Transcript: "maybe screenshot"
Confidence: █████████░░░░░░░
           (98%)    (74%)
```

### 5. **Smart Filtering for UI**
- Show only `word_is_final: true` in main transcript
- Show `word_is_final: false` in "Processing..." section
- Highlight low-confidence words for review

---

## Complete Field Reference

| Field | Type | Example | Description |
|-------|------|---------|-------------|
| `word` | string | `"maybe"` | Raw recognized word |
| `start` | number | `1025.44` | Start time (seconds) |
| `end` | number | `1025.52` | End time (seconds) |
| `confidence` | number | `0.98253` | Recognition confidence (0-1) |
| `speaker` | string | `"jeet shah"` | Speaker name |
| `punctuated_word` | string | `"maybe"` | Formatted word with punctuation |
| `speech_confidence` | number | `0.98253` | Alternative confidence score |
| `word_is_final` | boolean | `true` | Whether word is finalized |

---

## How to Access This Data

### In Your Backend (`main.py`):
```python
words = payload.get("words", [])
for word in words:
    print(f"Word: {word['word']}")
    print(f"  Time: {word['start']:.2f}s - {word['end']:.2f}s")
    print(f"  Duration: {word['end'] - word['start']:.2f}s")
    print(f"  Confidence: {word['confidence'] * 100:.1f}%")
    print(f"  Final: {word['word_is_final']}")
```

### In Your Chrome Extension (`content.js`):
```javascript
// Already available in webhook inspector!
message.words.forEach(word => {
  console.log(`${word.word}: ${word.confidence * 100}%`);
});
```

### In ngrok Inspector:
- Go to http://127.0.0.1:4040
- Click any POST /webhook request
- Look at the "Raw" tab to see full JSON
- Scroll to "words" array

---

## Summary

From your real webhook data, you're receiving **8 fields per word**:

1. ✅ Raw word text
2. ⏱️ Precise timing (start/end)
3. 📊 Confidence scores (2 metrics)
4. 🎙️ Speaker attribution
5. 📝 Punctuated version
6. ✓ Finalization status

This gives you everything needed to build:
- Karaoke-style highlighting
- Confidence-based filtering
- Speaking rate analysis
- Pause detection
- Multi-speaker tracking
- Quality assurance tools

**All of this data is now captured in your backend and available in the Webhook Inspector!**
