import os
import sys
import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "api")))

from searxng_client import search_searxng

def test_searxng_fallback_search():
    results = search_searxng("node 18.15.0", searxng_url="http://127.0.0.1:59999", timeout=0.5)
    assert len(results) > 0
    assert any("nvd.nist.gov" in r["url"] for r in results)
    assert results[0]["engine"] == "fallback"

def test_searxng_result_structure():
    results = search_searxng("react 17.0.2", searxng_url="http://127.0.0.1:59999", timeout=0.5)
    for r in results:
        assert "title" in r
        assert "url" in r
        assert "content" in r
        assert "engine" in r
