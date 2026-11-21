import os
import urllib.request
import urllib.parse
import json
import re
from typing import Dict, Optional

DEFAULT_CRAWL4AI_URL = os.environ.get("CRAWL4AI_URL", "http://localhost:11235")

def scrape_url(
    target_url: str,
    crawl4ai_url: Optional[str] = None,
    timeout: float = 10.0,
) -> Dict[str, str]:
    """
    Scrape text / markdown from a URL using local Crawl4AI without an API key.
    Falls back gracefully if Crawl4AI container is not active.
    """
    base_url = (crawl4ai_url or DEFAULT_CRAWL4AI_URL).rstrip("/")
    endpoint = f"{base_url}/crawl"

    payload = {
        "urls": [target_url],
        "priority": 10,
    }

    try:
        req = urllib.request.Request(
            endpoint,
            data=json.dumps(payload).encode("utf-8"),
            headers={
                "Content-Type": "application/json",
                "User-Agent": "TechStackIssuesFinder/1.0"
            },
            method="POST"
        )
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            if resp.status == 200:
                body = resp.read().decode("utf-8")
                data = json.loads(body)
                # Crawl4AI typically returns results array
                results = data.get("results", [])
                if results and len(results) > 0:
                    first = results[0]
                    return {
                        "url": target_url,
                        "markdown": first.get("markdown", ""),
                        "title": first.get("metadata", {}).get("title", ""),
                        "status": "success",
                        "engine": "crawl4ai"
                    }
    except Exception:
        pass

    # Resilient fallback: Basic fetch without heavy headless browser
    try:
        fallback_req = urllib.request.Request(
            target_url,
            headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
        )
        with urllib.request.urlopen(fallback_req, timeout=5.0) as f_resp:
            raw_html = f_resp.read().decode("utf-8", errors="ignore")
            # Strip simple tags for mock markdown
            cleaned_text = re.sub(r'<[^>]+>', ' ', raw_html)
            cleaned_text = ' '.join(cleaned_text.split())[:1500]
            title_match = re.search(r'<title>(.*?)</title>', raw_html, re.IGNORECASE)
            title = title_match.group(1).strip() if title_match else target_url
            return {
                "url": target_url,
                "markdown": cleaned_text,
                "title": title,
                "status": "fallback",
                "engine": "basic_fetch"
            }
    except Exception as e:
        return {
            "url": target_url,
            "markdown": f"Failed to retrieve content: {str(e)}",
            "title": target_url,
            "status": "failed",
            "engine": "none"
        }
