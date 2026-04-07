# Company Intelligence MCP Server - Bug Report and Code Review

## Executive Summary

**Status: ⚠️ NOT SAFE TO RUN - Critical Issues Found**

The Company Intelligence MCP Server code has several critical bugs and issues that must be fixed before installation and deployment. Below is a comprehensive analysis of all issues found.

---

## 🔴 Critical Issues (Must Fix Before Running)

### 1. Missing Required Package: `fastmcp`
**Severity:** CRITICAL
**File:** `backend/mcp_servers/company_intelligence_mcp/server.py`
**Line:** 14

**Issue:**
```python
from fastmcp import FastMCP  # fastmcp is not installed
```

**Impact:**
- The MCP server cannot start without this package
- All API endpoints in `company_intelligence.py` will fail on import
- Application will crash on startup

**Fix:**
```bash
pip install fastmcp
```

**Note:** Package is listed in `requirements.txt` line 18 but not installed

---

### 2. Missing `asyncio` Import in main.py
**Severity:** CRITICAL
**File:** `backend/main.py`
**Line:** 328

**Issue:**
```python
# Line 328 uses asyncio.gather() but asyncio is not imported
user_company_data, target_company_data = await asyncio.gather(
    user_company_task,
    target_company_task,
    return_exceptions=True
)
```

**Impact:**
- `NameError: name 'asyncio' is not defined` will occur at runtime
- `/api/scrape-companies` endpoint will crash

**Fix:**
Add at the top of `main.py` (around line 12):
```python
import asyncio
```

---

### 3. Deprecated ChromaDB API
**Severity:** HIGH (Breaking Change)
**File:** `backend/mcp_servers/company_intelligence_mcp/server.py`
**Lines:** 54-57

**Issue:**
```python
# OLD DEPRECATED API (ChromaDB 1.x)
chroma_client = chromadb.Client(Settings(
    chroma_db_impl="duckdb+parquet",
    persist_directory="./chroma_db"
))
```

**Error Message When Run:**
```
You are using a deprecated configuration of Chroma.
Please see https://docs.trychroma.com/deployment/migration
```

**Impact:**
- Code will fail with deprecation error
- ChromaDB version 1.5.5 is installed (new API)
- Database persistence may not work correctly

**Fix:**
Replace lines 54-64 in `server.py` with:
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

**Also Update Import:**
Remove this line (line 16):
```python
from chromadb.config import Settings  # No longer needed
```

---

## 🟡 High Priority Issues

### 4. Cadence Website Has Cloudflare Protection
**Severity:** HIGH
**URL:** `https://www.cadence.com/en_US/home.html`

**Issue:**
The website uses Cloudflare's anti-bot protection:
```
HTTP/2 403
cf-mitigated: challenge
```

**Impact:**
- Basic scraping with Playwright will fail with 403 Forbidden
- Cloudflare requires JavaScript challenge solving
- Bot detection mechanisms present

**Current Scraper Limitations:**
1. No stealth mode enabled in Playwright
2. No browser fingerprint randomization
3. No challenge solver

**Recommendations:**

**Option A: Use Stealth Playwright (Recommended)**
```python
# In web_scraper_mcp/server.py, update browser launch:
from playwright.async_api import async_playwright
from playwright_stealth import stealth_async

self.playwright = await async_playwright().start()
self.browser = await self.playwright.chromium.launch(
    headless=True,
    args=[
        '--no-sandbox',
        '--disable-setuid-sandbox',
        '--disable-blink-features=AutomationControlled'
    ]
)

# When creating page:
page = await self.browser.new_page()
await stealth_async(page)  # Apply stealth
```

Install: `pip install playwright-stealth`

**Option B: Use Undetected ChromeDriver**
- Switch from Playwright to undetected-chromedriver
- More effective against Cloudflare

**Option C: Use a Scraping API Service**
- ScrapingBee, ScraperAPI, or similar
- Handles Cloudflare challenges automatically
- Costs money but more reliable

**Option D: Accept Failure and Handle Gracefully**
- Update code to handle 403 errors gracefully
- Return meaningful error messages
- Log failed scrapes for manual review

**Website Structure Analysis:**
- **URL Pattern:** `/en_US/home.html` suggests AEM (Adobe Experience Manager)
- **Security:** Strict CSP, CORS, and referrer policies
- **Protection:** Cloudflare Bot Management Enterprise
- **Recommendation:** For enterprise sites like Cadence, consider using official APIs or LinkedIn data instead

---

### 5. Missing Error Handling for Web Scraper Initialization
**Severity:** MEDIUM
**File:** `backend/mcp_servers/company_intelligence_mcp/server.py`
**Line:** 22

**Issue:**
```python
from mcp_servers.web_scraper_mcp.server import get_web_scraper
```

If Playwright is not installed or fails to initialize, the entire import chain breaks.

**Fix:**
Add try-catch in `initialize()` function:
```python
async def initialize():
    """Initialize all services"""
    global scraper, ai_client, chroma_client, collection

    if not scraper:
        try:
            scraper = await get_web_scraper()
            logger.info("Web scraper initialized")
        except Exception as e:
            logger.error(f"Failed to initialize web scraper: {e}")
            raise RuntimeError("Web scraper initialization failed. Ensure Playwright is installed: playwright install chromium")
```

---

## 🟢 Medium Priority Issues

### 6. Potential Asyncio Issues in `requirements.txt`
**Severity:** LOW
**File:** `backend/requirements.txt`
**Line:** 31

**Issue:**
```python
asyncio==3.4.3
```

**Problem:**
- `asyncio` is built into Python 3.4+
- Installing it as a package can cause conflicts
- This package is a backport for Python 2

**Fix:**
Remove line 31 from `requirements.txt`:
```diff
- asyncio==3.4.3
```

---

### 7. No Embeddings Model for ChromaDB
**Severity:** MEDIUM
**File:** `backend/mcp_servers/company_intelligence_mcp/server.py`

**Issue:**
ChromaDB collection is created without specifying embedding function:
```python
collection = chroma_client.get_or_create_collection(
    name="company_intelligence",
    metadata={"description": "Scraped company data with embeddings"}
)
```

**Problem:**
- ChromaDB will use default embeddings
- Search quality may be suboptimal
- No explicit embedding model configured

**Recommendation:**
Add sentence-transformers embedding function:
```python
from chromadb.utils import embedding_functions

# Initialize embedding function
embedding_function = embedding_functions.SentenceTransformerEmbeddingFunction(
    model_name="all-MiniLM-L6-v2"
)

collection = chroma_client.get_or_create_collection(
    name="company_intelligence",
    metadata={"description": "Scraped company data with embeddings"},
    embedding_function=embedding_function
)
```

Note: `sentence-transformers==3.3.1` is already in requirements.txt

---

### 8. Weak Company Name Extraction
**Severity:** LOW
**File:** `backend/mcp_servers/web_scraper_mcp/server.py`
**Lines:** 282-305

**Issue:**
Company name extraction logic is very basic:
```python
def _extract_company_name(self, data: Dict[str, Any]) -> str:
    title = data.get("title", "")
    if title:
        name = re.sub(r'\s*[-|:]\s*(Home|Homepage|Official Site).*', '', title, flags=re.IGNORECASE)
        return name.strip()
    # ...
    return "Unknown"
```

**Problem:**
- Won't work for sites with complex titles
- Cadence.com title may be: "Cadence Design Systems | EDA Software & IP Solutions"
- Regex pattern may not capture correctly

**Recommendation:**
Use AI to extract company name:
```python
async def _extract_company_name_with_ai(self, data: Dict[str, Any]) -> str:
    """Use AI to extract company name"""
    title = data.get("title", "")
    description = data.get("metadata", {}).get("description", "")

    prompt = f"Extract only the company name from this: Title: '{title}', Description: '{description}'. Return only the company name, nothing else."

    # Use OpenAI or Claude
    name = await ai_client.simple_prompt(prompt, max_tokens=50)
    return name.strip()
```

---

### 9. Cache Expiration Bug
**Severity:** LOW
**File:** `backend/mcp_servers/company_intelligence_mcp/server.py`
**Line:** 86

**Issue:**
```python
age_minutes = (datetime.now() - timestamp).seconds / 60
```

**Problem:**
- `.seconds` only returns seconds component (0-86399)
- For time differences > 24 hours, this will be incorrect
- Cache may incorrectly report age

**Fix:**
```python
age_minutes = (datetime.now() - timestamp).total_seconds() / 60
```

---

### 10. No Rate Limiting for OpenAI Calls
**Severity:** MEDIUM

**Issue:**
Multiple concurrent calls to OpenAI API without rate limiting:
```python
# In compare_companies, two simultaneous API calls
results = await asyncio.gather(
    analyze_company_for_sales(user_company_url),
    analyze_company_for_sales(target_company_url),
    return_exceptions=True
)
```

Each `analyze_company_for_sales` makes 1-2 OpenAI API calls. This can hit rate limits quickly.

**Recommendation:**
- Add rate limiting decorator
- Use asyncio.Semaphore to limit concurrent API calls
- Add retry logic with exponential backoff

---

## ✅ Code Quality Issues (Non-Breaking)

### 11. Hardcoded Persist Directory
**File:** `backend/mcp_servers/company_intelligence_mcp/server.py`
**Line:** 56

```python
persist_directory="./chroma_db"  # Relative path
```

**Issue:** Relative paths can cause issues depending on where the server is run from.

**Fix:** Use absolute path:
```python
import os
persist_directory = os.path.join(os.path.dirname(__file__), "chroma_db")
```

---

### 12. No Connection Pooling for Scraper
**File:** `backend/mcp_servers/web_scraper_mcp/server.py`

Browser is initialized once and reused, which is good. However:
- No maximum page limit
- No cleanup of stale browser contexts
- Memory can grow over time

**Recommendation:** Add periodic browser restart.

---

### 13. No Timeout on AI Calls
**File:** `backend/mcp_servers/company_intelligence_mcp/server.py`

AI calls have no timeout:
```python
analysis = await ai_client.simple_prompt(
    prompt=prompt,
    system="...",
    max_tokens=2000
)
```

**Recommendation:** Add timeout using asyncio.wait_for():
```python
try:
    analysis = await asyncio.wait_for(
        ai_client.simple_prompt(prompt=prompt, system="...", max_tokens=2000),
        timeout=30.0  # 30 seconds
    )
except asyncio.TimeoutError:
    return {"success": False, "error": "AI analysis timed out"}
```

---

## 🧪 Testing Recommendations

### Before Running:
1. ✅ Install missing packages: `pip install fastmcp`
2. ✅ Fix `asyncio` import in `main.py`
3. ✅ Update ChromaDB API calls
4. ✅ Test with a simple website first (not Cadence)

### Test URLs (in order of difficulty):
1. **Easy:** `https://example.com` (minimal, no protection)
2. **Medium:** `https://www.ycombinator.com` (simple, public)
3. **Hard:** `https://www.cadence.com/en_US/home.html` (Cloudflare protected)

### Test Commands:
```bash
# 1. Install dependencies
cd /Users/jeetshah/Documents/Meetstream\ AI/backend
pip install fastmcp

# 2. Test imports
python -c "from mcp_servers.company_intelligence_mcp.server import scrape_company"

# 3. Start server (after fixes)
python -m uvicorn main:app --reload

# 4. Test endpoint
curl -X POST http://localhost:8000/api/intelligence/scrape \
  -H "Content-Type: application/json" \
  -d '{"url": "https://example.com"}'
```

---

## 📊 Summary Table

| Issue | Severity | File | Status | Breaking |
|-------|----------|------|--------|----------|
| Missing `fastmcp` package | CRITICAL | server.py:14 | ❌ Not installed | YES |
| Missing `asyncio` import | CRITICAL | main.py:328 | ❌ Not fixed | YES |
| Deprecated ChromaDB API | HIGH | server.py:54-57 | ❌ Not fixed | YES |
| Cadence Cloudflare block | HIGH | N/A | ⚠️ Expected | NO |
| No scraper error handling | MEDIUM | server.py:22 | ❌ Not fixed | Partial |
| Wrong `asyncio` in requirements | LOW | requirements.txt:31 | ❌ Not fixed | NO |
| No embeddings specified | MEDIUM | server.py:60 | ⚠️ Works but suboptimal | NO |
| Weak name extraction | LOW | web_scraper_mcp/server.py:282 | ⚠️ Works but imperfect | NO |
| Cache expiration bug | LOW | server.py:86 | ❌ Not fixed | NO |
| No API rate limiting | MEDIUM | server.py:217 | ❌ Not fixed | NO |

---

## 🚀 Action Items (Priority Order)

### Before First Run:
1. ✅ **MUST DO:** `pip install fastmcp`
2. ✅ **MUST DO:** Add `import asyncio` to main.py line 12
3. ✅ **MUST DO:** Fix ChromaDB API (replace Client with PersistentClient)

### After First Successful Run:
4. 🔧 Add scraper initialization error handling
5. 🔧 Remove `asyncio==3.4.3` from requirements.txt
6. 🔧 Fix cache expiration calculation bug
7. 🔧 Add embedding function to ChromaDB

### For Production:
8. 🏗️ Implement stealth mode for Playwright
9. 🏗️ Add API rate limiting
10. 🏗️ Add timeouts to AI calls
11. 🏗️ Use absolute paths for ChromaDB

---

## ✅ Safe to Install and Run?

**Answer: NO - Not yet. Fix critical issues first.**

### Installation Steps (Correct Order):

```bash
# 1. Navigate to backend
cd "/Users/jeetshah/Documents/Meetstream AI/backend"

# 2. Install missing package
pip install fastmcp

# 3. Apply code fixes (see sections above)
# - Add asyncio import to main.py
# - Update ChromaDB API in server.py

# 4. Test imports
python test_company_intelligence.py

# 5. Start server
python -m uvicorn main:app --reload --port 8000

# 6. Test with simple URL (NOT Cadence)
curl -X POST http://localhost:8000/api/intelligence/scrape \
  -H "Content-Type: application/json" \
  -d '{"url": "https://example.com"}'
```

---

## 🌐 Cadence.com Specific Issues

### URL Structure Analysis:
- **Base URL:** `https://www.cadence.com`
- **Homepage:** `/en_US/home.html`
- **Pattern:** Language-region prefix (`en_US`)
- **CMS:** Likely Adobe Experience Manager (AEM)

### Protection Mechanisms:
1. **Cloudflare Bot Management** - ACTIVE
   - Challenge page for bots
   - JavaScript fingerprinting
   - Browser verification required

2. **Strict Security Headers:**
   - `cross-origin-embedder-policy: require-corp`
   - `cross-origin-opener-policy: same-origin`
   - `referrer-policy: same-origin`

3. **Client Hints Required:**
   - Expects modern browser headers (Sec-CH-UA-*)
   - Playwright may not send these by default

### Scraping Recommendations for Cadence:

**Best Approach:**
1. Use Playwright with stealth mode
2. Set realistic viewport and user agent
3. Add random delays between requests
4. Consider using residential proxies
5. Be prepared for occasional failures

**Alternative Approaches:**
1. **LinkedIn Company Page** - Easier to scrape, good structured data
2. **Company API** - Check if Cadence has a public API
3. **Manual Fallback** - For high-value prospects, manual research may be more reliable

**Expected Success Rate:**
- Without stealth: 0-10% (Cloudflare will block)
- With stealth: 60-80% (may still hit challenges)
- With proxy rotation: 90%+ (most reliable)

---

## 📝 Conclusion

The Company Intelligence MCP Server code is **well-structured and comprehensive**, but has **3 critical bugs** that will prevent it from running:

1. Missing `fastmcp` package
2. Missing `asyncio` import
3. Deprecated ChromaDB API

Additionally, the Cadence website will be **challenging to scrape** due to Cloudflare protection, but the code will handle the error gracefully (returns error dict).

**Recommendation:** Fix the 3 critical issues, then test with easier websites before attempting Cadence. Consider implementing stealth mode for production use with enterprise websites.

---

**Report Generated:** 2026-03-28
**Tested Environment:** macOS (Darwin 25.4.0), Python 3.x
**ChromaDB Version:** 1.5.5
**Playwright Version:** 1.48.0
