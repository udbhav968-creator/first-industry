import os
import sys
import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "api")))

from crawl4ai_client import scrape_url

def test_crawl4ai_scrape_offline_fallback():
    # Test scraping with offline container returns structured result without raising exceptions
    res = scrape_url("https://example.com", crawl4ai_url="http://127.0.0.1:59999", timeout=0.5)
    assert isinstance(res, dict)
    assert "url" in res
    assert "markdown" in res
    assert "title" in res
    assert res["status"] in ["success", "fallback", "failed"]

def test_crawl4ai_invalid_target_handling():
    res = scrape_url("http://invalid-non-existent-domain-xyz.local", crawl4ai_url="http://127.0.0.1:59999", timeout=0.5)
    assert isinstance(res, dict)
    assert res["status"] in ["fallback", "failed"]
