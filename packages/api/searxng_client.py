import os
import urllib.parse
import urllib.request
import json
from typing import List, Dict, Optional

DEFAULT_SEARXNG_URL = os.environ.get("SEARXNG_URL", "http://localhost:8080")

def search_searxng(
    query: str,
    searxng_url: Optional[str] = None,
    timeout: float = 0.8,
    max_results: int = 5,
) -> List[Dict]:
    """
    Search the public web using the local SearXNG service without any API key.
    Returns structured results: [{'title': ..., 'url': ..., 'content': ...}]
    Falls back gracefully if SearXNG is offline or unreachable.
    """
    base_url = (searxng_url or DEFAULT_SEARXNG_URL).rstrip("/")
    params = urllib.parse.urlencode({
        "q": query,
        "format": "json",
    })
    url = f"{base_url}/search?{params}"

    try:
        req = urllib.request.Request(
            url,
            headers={"User-Agent": "TechStackIssuesFinder/1.0"}
        )
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            if resp.status == 200:
                body = resp.read().decode("utf-8")
                data = json.loads(body)
                raw_results = data.get("results", [])
                formatted = []
                for item in raw_results[:max_results]:
                    formatted.append({
                        "title": item.get("title", ""),
                        "url": item.get("url", ""),
                        "content": item.get("content", ""),
                        "engine": item.get("engine", "searxng"),
                    })
                return formatted
    except Exception:
        pass

    # Resilient fallback: Return direct knowledge links for the query
    clean_query = urllib.parse.quote_plus(query)
    return [
        {
            "title": f"NVD Vulnerability Search: {query}",
            "url": f"https://nvd.nist.gov/vuln/search/results?query={clean_query}",
            "content": f"Public CVE database search for {query}",
            "engine": "fallback",
        },
        {
            "title": f"GitHub Advisory Database: {query}",
            "url": f"https://github.com/advisories?query={clean_query}",
            "content": f"Security advisories and CVEs for {query}",
            "engine": "fallback",
        }
    ]
