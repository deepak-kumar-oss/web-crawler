import asyncio
import aiohttp
import time
import json
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urldefrag, urlparse

import sys, os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

import redis
from python_backend.config.settings import SEED_URL, MAX_PAGES, REQUEST_DELAY, USER_AGENT
from python_backend.services.utils import make_doc_id

# Redis
r = redis.Redis(host="localhost", port=6379, decode_responses=True)

# Domain restriction
ALLOWED_DOMAIN = urlparse(SEED_URL).netloc


def normalize(url, base):
    """Normalize URLs and keep them inside the same domain."""
    full = urljoin(base, url)
    clean, _ = urldefrag(full)  # remove #hash
    parsed = urlparse(clean)
    if parsed.scheme.startswith("http") and parsed.netloc == ALLOWED_DOMAIN:
        return clean
    return None


def save_page(url, title, text, outlinks, images):
    """Save crawled page to Redis."""
    doc_id = make_doc_id(url)
    page = {
        "doc_id": doc_id,
        "url": url,
        "title": title,
        "text": text,
        "outlinks": outlinks,
        "images": images,
        "timestamp": time.time(),
    }
    r.set(f"page:{doc_id}", json.dumps(page))
    return doc_id


async def fetch(session, url):
    """Fetch a URL using aiohttp."""
    try:
        async with session.get(url, timeout=10) as resp:
            if resp.status != 200:
                print(f" [{resp.status}] {url}")
                return None
            return await resp.text()
    except Exception as e:
        print(f"Error fetching {url}: {e}")
        return None


async def crawl_page(session, url):
    """Crawl a single page: fetch, parse, extract."""
    html = await fetch(session, url)
    if not html:
        return None

    soup = BeautifulSoup(html, "html.parser")
    title = soup.title.string.strip() if soup.title else ""
    text = " ".join(p.get_text(" ", strip=True) for p in soup.find_all("p"))

    # Extract links
    outlinks = []
    for a in soup.find_all("a", href=True):
        norm = normalize(a["href"], url)
        if norm:
            outlinks.append(norm)

    # Extract images
    images = []
    for img in soup.find_all("img"):
        src = img.get("src")
        if src:
            full = normalize(src, url)
            if full:
                images.append({
                    "src": full,
                    "alt": img.get("alt", "")
                })

    save_page(url, title, text, outlinks, images)
    return outlinks


async def spider():
    print(f" FAST SPIDER STARTED — Seed: {SEED_URL}")

    queue = asyncio.Queue()
    visited = set()

    await queue.put(SEED_URL)
    visited.add(SEED_URL)

    async with aiohttp.ClientSession(headers={"User-Agent": USER_AGENT}) as session:

        count = 0
        while not queue.empty() and count < MAX_PAGES:

            url = await queue.get()
            print(f"[{count+1}/{MAX_PAGES}] Crawling: {url}")

            outlinks = await crawl_page(session, url)
            count += 1

            if outlinks:
                for link in outlinks:
                    if link not in visited:
                        visited.add(link)
                        await queue.put(link)

            await asyncio.sleep(REQUEST_DELAY)

    print(f"\nTotal Crawled: {count}")


if __name__ == "__main__":
    asyncio.run(spider())
