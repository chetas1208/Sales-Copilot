# Quick Fix Guide - Company Intelligence MCP Server

## 🚨 3 Critical Fixes Required Before Running

### Fix #1: Install Missing Package (1 minute)

```bash
cd "/Users/jeetshah/Documents/Meetstream AI/backend"
pip install fastmcp
```

---

### Fix #2: Add Missing Import to main.py (1 minute)

**File:** `/Users/jeetshah/Documents/Meetstream AI/backend/main.py`

**Location:** After line 11 (after other imports)

**Add this line:**
```python
import asyncio
```

**Your imports section should look like:**
```python
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
from dotenv import load_dotenv
import os
import logging
from typing import Dict, Any, Optional
import json
import asyncio  # ← ADD THIS LINE
from datetime import datetime
```

---

### Fix #3: Update ChromaDB API (3 minutes)

**File:** `/Users/jeetshah/Documents/Meetstream AI/backend/mcp_servers/company_intelligence_mcp/server.py`

**Step 3.1:** Remove deprecated import (line 16)

Delete or comment out:
```python
from chromadb.config import Settings  # DELETE THIS LINE
```

**Step 3.2:** Replace ChromaDB initialization (lines 52-64)

**FIND:**
```python
if not chroma_client:
    # Initialize ChromaDB (local storage)
    chroma_client = chromadb.Client(Settings(
        chroma_db_impl="duckdb+parquet",
        persist_directory="./chroma_db"
    ))

    # Get or create collection
    collection = chroma_client.get_or_create_collection(
        name="company_intelligence",
        metadata={"description": "Scraped company data with embeddings"}
    )
    logger.info("ChromaDB initialized")
```

**REPLACE WITH:**
```python
if not chroma_client:
    # Initialize ChromaDB with new API (ChromaDB 1.x+)
    chroma_client = chromadb.PersistentClient(path="./chroma_db")

    # Get or create collection
    collection = chroma_client.get_or_create_collection(
        name="company_intelligence",
        metadata={"description": "Scraped company data with embeddings"}
    )
    logger.info("ChromaDB initialized")
```

---

## ✅ Verify Fixes

Run this command to verify all fixes:

```bash
cd "/Users/jeetshah/Documents/Meetstream AI/backend"

# Test imports
python -c "
import sys
sys.path.insert(0, '.')
print('Testing imports...')

# Test 1: fastmcp
try:
    import fastmcp
    print('✓ fastmcp imported')
except ImportError:
    print('✗ fastmcp FAILED - run: pip install fastmcp')

# Test 2: asyncio in main.py
with open('main.py', 'r') as f:
    if 'import asyncio' in f.read():
        print('✓ asyncio import found in main.py')
    else:
        print('✗ asyncio import MISSING in main.py')

# Test 3: ChromaDB
with open('mcp_servers/company_intelligence_mcp/server.py', 'r') as f:
    content = f.read()
    if 'PersistentClient' in content:
        print('✓ ChromaDB PersistentClient found')
    elif 'Client(Settings' in content:
        print('✗ ChromaDB still uses OLD API')
    else:
        print('⚠ ChromaDB API unclear')

print('\\nAll checks complete!')
"
```

---

## 🧪 Test the Server

After applying all fixes:

```bash
# Start the server
cd "/Users/jeetshah/Documents/Meetstream AI/backend"
python -m uvicorn main:app --reload --port 8000
```

In another terminal, test the API:

```bash
# Test with a simple website (NOT Cadence.com yet)
curl -X POST http://localhost:8000/api/intelligence/scrape \
  -H "Content-Type: application/json" \
  -d '{"url": "https://example.com"}'
```

Expected output (should work):
```json
{
  "url": "https://example.com",
  "company_name": "Example Domain",
  "title": "Example Domain",
  "description": "...",
  ...
}
```

---

## ⚠️ About Cadence.com

**The Cadence website uses Cloudflare Bot Protection and will return 403 Forbidden.**

To test Cadence scraping:
```bash
curl -X POST http://localhost:8000/api/intelligence/scrape \
  -H "Content-Type: application/json" \
  -d '{"url": "https://www.cadence.com/en_US/home.html"}'
```

Expected result:
```json
{
  "url": "https://www.cadence.com/en_US/home.html",
  "error": "...",
  "success": false
}
```

**This is expected behavior** - Cloudflare blocks automated bots. See the main bug report for solutions (stealth mode, proxies, etc.).

---

## 📋 Checklist

- [ ] Installed `fastmcp` package
- [ ] Added `import asyncio` to main.py
- [ ] Updated ChromaDB to `PersistentClient`
- [ ] Ran verification script (all checks pass)
- [ ] Started server successfully
- [ ] Tested with simple website (example.com)
- [ ] Reviewed Cadence.com limitations

---

## 🆘 Troubleshooting

### Error: "ModuleNotFoundError: No module named 'fastmcp'"
```bash
pip install fastmcp
```

### Error: "name 'asyncio' is not defined"
Add `import asyncio` after line 11 in main.py

### Error: "deprecated configuration of Chroma"
Update ChromaDB code to use `PersistentClient` (see Fix #3)

### Error: "Failed to initialize web scraper"
```bash
playwright install chromium
```

### Cadence.com returns 403
This is expected - see COMPANY_INTELLIGENCE_BUG_REPORT.md for solutions

---

**Total Fix Time: ~5 minutes**
**Files Modified: 2**
**Packages Installed: 1**
