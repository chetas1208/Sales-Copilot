"""
Web Scraper MCP Server Implementation
Uses Playwright for web scraping with MCP protocol
"""

import logging
import asyncio
from typing import Dict, Any, Optional, List
from playwright.async_api import async_playwright, Browser, Page
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
import re

logger = logging.getLogger(__name__)


class WebScraperMCP:
    """Web scraper using Playwright with MCP interface"""

    def __init__(self):
        self.browser: Optional[Browser] = None
        self.playwright = None
        self.initialized = False

    async def initialize(self):
        """Initialize Playwright browser"""
        if self.initialized:
            return

        try:
            self.playwright = await async_playwright().start()
            self.browser = await self.playwright.chromium.launch(
                headless=True,
                args=['--no-sandbox', '--disable-setuid-sandbox']
            )
            self.initialized = True
            logger.info("Web scraper MCP server initialized")
        except Exception as e:
            logger.error(f"Failed to initialize web scraper: {str(e)}")
            raise

    async def cleanup(self):
        """Cleanup resources"""
        if self.browser:
            await self.browser.close()
        if self.playwright:
            await self.playwright.stop()
        self.initialized = False
        logger.info("Web scraper MCP server cleaned up")

    async def scrape_url(
        self,
        url: str,
        timeout: int = 30000,
        wait_for_selector: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Scrape a single URL and extract structured data

        Args:
            url: URL to scrape
            timeout: Page load timeout in milliseconds
            wait_for_selector: Optional CSS selector to wait for

        Returns:
            Dict with scraped data
        """
        if not self.initialized:
            await self.initialize()

        logger.info(f"Scraping URL: {url}")

        page = None
        try:
            page = await self.browser.new_page()
            await page.set_viewport_size({"width": 1920, "height": 1080})

            # Navigate to URL
            response = await page.goto(url, timeout=timeout, wait_until="domcontentloaded")

            # Wait for specific selector if provided
            if wait_for_selector:
                await page.wait_for_selector(wait_for_selector, timeout=5000)
            else:
                # Wait a bit for dynamic content
                await page.wait_for_timeout(2000)

            # Get page content
            html = await page.content()
            title = await page.title()

            # Parse with BeautifulSoup
            soup = BeautifulSoup(html, 'lxml')

            # Extract structured data
            result = {
                "url": url,
                "title": title,
                "status_code": response.status if response else None,
                "content": self._extract_content(soup),
                "metadata": self._extract_metadata(soup, url),
                "links": self._extract_links(soup, url),
                "images": self._extract_images(soup, url)
            }

            logger.info(f"Successfully scraped: {url}")

            return result

        except Exception as e:
            logger.error(f"Error scraping {url}: {str(e)}")
            return {
                "url": url,
                "error": str(e),
                "success": False
            }

        finally:
            if page:
                await page.close()

    def _extract_content(self, soup: BeautifulSoup) -> Dict[str, Any]:
        """Extract main content from page"""
        # Remove script and style elements
        for script in soup(["script", "style", "nav", "footer", "header"]):
            script.decompose()

        # Extract text
        text = soup.get_text(separator=' ', strip=True)
        text = re.sub(r'\s+', ' ', text)  # Clean up whitespace

        # Extract headings
        headings = []
        for tag in ['h1', 'h2', 'h3']:
            for heading in soup.find_all(tag):
                headings.append({
                    "level": tag,
                    "text": heading.get_text(strip=True)
                })

        # Extract paragraphs
        paragraphs = [p.get_text(strip=True) for p in soup.find_all('p') if p.get_text(strip=True)]

        return {
            "text": text[:10000],  # Limit to first 10k chars
            "headings": headings[:20],  # First 20 headings
            "paragraphs": paragraphs[:30],  # First 30 paragraphs
            "word_count": len(text.split())
        }

    def _extract_metadata(self, soup: BeautifulSoup, url: str) -> Dict[str, Any]:
        """Extract metadata from page"""
        metadata = {
            "url": url,
            "domain": urlparse(url).netloc
        }

        # Meta tags
        for meta in soup.find_all('meta'):
            name = meta.get('name') or meta.get('property')
            content = meta.get('content')
            if name and content:
                metadata[name] = content

        # Common metadata fields
        description = soup.find('meta', attrs={'name': 'description'})
        if description:
            metadata['description'] = description.get('content', '')

        keywords = soup.find('meta', attrs={'name': 'keywords'})
        if keywords:
            metadata['keywords'] = keywords.get('content', '')

        # Open Graph data
        og_title = soup.find('meta', attrs={'property': 'og:title'})
        if og_title:
            metadata['og_title'] = og_title.get('content', '')

        og_description = soup.find('meta', attrs={'property': 'og:description'})
        if og_description:
            metadata['og_description'] = og_description.get('content', '')

        return metadata

    def _extract_links(self, soup: BeautifulSoup, base_url: str) -> List[Dict[str, str]]:
        """Extract links from page"""
        links = []
        for a in soup.find_all('a', href=True):
            href = a['href']
            absolute_url = urljoin(base_url, href)
            text = a.get_text(strip=True)

            if absolute_url and not absolute_url.startswith(('mailto:', 'tel:', 'javascript:')):
                links.append({
                    "url": absolute_url,
                    "text": text,
                    "is_internal": urlparse(absolute_url).netloc == urlparse(base_url).netloc
                })

        return links[:50]  # Limit to 50 links

    def _extract_images(self, soup: BeautifulSoup, base_url: str) -> List[Dict[str, str]]:
        """Extract images from page"""
        images = []
        for img in soup.find_all('img', src=True):
            src = img['src']
            absolute_url = urljoin(base_url, src)
            alt = img.get('alt', '')

            images.append({
                "url": absolute_url,
                "alt": alt
            })

        return images[:20]  # Limit to 20 images

    async def scrape_multiple(
        self,
        urls: List[str],
        max_concurrent: int = 3
    ) -> List[Dict[str, Any]]:
        """
        Scrape multiple URLs concurrently

        Args:
            urls: List of URLs to scrape
            max_concurrent: Maximum concurrent scraping tasks

        Returns:
            List of scraping results
        """
        if not self.initialized:
            await self.initialize()

        logger.info(f"Scraping {len(urls)} URLs (max concurrent: {max_concurrent})")

        semaphore = asyncio.Semaphore(max_concurrent)

        async def scrape_with_semaphore(url):
            async with semaphore:
                return await self.scrape_url(url)

        results = await asyncio.gather(
            *[scrape_with_semaphore(url) for url in urls],
            return_exceptions=True
        )

        return [r if not isinstance(r, Exception) else {"error": str(r)} for r in results]

    async def extract_company_info(self, url: str) -> Dict[str, Any]:
        """
        Extract company-specific information from website

        Args:
            url: Company website URL

        Returns:
            Dict with company information
        """
        data = await self.scrape_url(url)

        if data.get("error"):
            return data

        # Extract company-specific data
        content = data.get("content", {})
        metadata = data.get("metadata", {})

        company_info = {
            "url": url,
            "company_name": self._extract_company_name(data),
            "description": metadata.get("description") or metadata.get("og_description", ""),
            "title": data.get("title", ""),
            "headings": content.get("headings", []),
            "about_text": self._find_about_section(content),
            "products": self._find_products(content),
            "contact_info": self._find_contact_info(data),
        }

        return company_info

    def _extract_company_name(self, data: Dict[str, Any]) -> str:
        """Try to extract company name from various sources"""
        # Try title first
        title = data.get("title", "")
        if title:
            # Remove common suffixes
            name = re.sub(r'\s*[-|:]\s*(Home|Homepage|Official Site).*', '', title, flags=re.IGNORECASE)
            return name.strip()

        # Try Open Graph title
        metadata = data.get("metadata", {})
        og_title = metadata.get("og_title", "")
        if og_title:
            return og_title.strip()

        # Try domain name as fallback
        domain = metadata.get("domain", "")
        if domain:
            # Extract main part of domain
            parts = domain.split('.')
            if len(parts) >= 2:
                return parts[-2].capitalize()

        return "Unknown"

    def _find_about_section(self, content: Dict[str, Any]) -> str:
        """Find 'About' section text"""
        paragraphs = content.get("paragraphs", [])

        # Look for paragraphs near "about" headings
        # Simple heuristic: return first few paragraphs
        if paragraphs:
            return " ".join(paragraphs[:3])

        return ""

    def _find_products(self, content: Dict[str, Any]) -> List[str]:
        """Try to identify products/services mentioned"""
        # Simple heuristic: look for headings that might be products
        headings = content.get("headings", [])

        products = []
        product_keywords = ['product', 'service', 'solution', 'feature']

        for heading in headings:
            text_lower = heading.get("text", "").lower()
            if any(keyword in text_lower for keyword in product_keywords):
                products.append(heading.get("text", ""))

        return products[:5]

    def _find_contact_info(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Extract contact information"""
        content = data.get("content", {})
        text = content.get("text", "")

        contact_info = {}

        # Find email (basic regex)
        emails = re.findall(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', text)
        if emails:
            contact_info["emails"] = list(set(emails))[:3]

        # Find phone numbers (basic regex for US format)
        phones = re.findall(r'\b\d{3}[-.]?\d{3}[-.]?\d{4}\b', text)
        if phones:
            contact_info["phones"] = list(set(phones))[:3]

        return contact_info


# Singleton instance
_web_scraper: Optional[WebScraperMCP] = None


async def get_web_scraper() -> WebScraperMCP:
    """Get or create singleton web scraper instance"""
    global _web_scraper
    if _web_scraper is None:
        _web_scraper = WebScraperMCP()
        await _web_scraper.initialize()
    return _web_scraper


def create_web_scraper_server() -> WebScraperMCP:
    """Factory function to create web scraper server"""
    return WebScraperMCP()
