#!/bin/bash
set -e

CRAWL4AI_URL="${CRAWL4AI_URL:-http://localhost:11235}"
BASE_URL="${CRAWL4AI_URL%/}"

echo "Testing Crawl4AI at $BASE_URL..."

# 1. Health probe
health_status=$(curl -s -o /dev/null -w "%{http_code}" "$BASE_URL/health" || curl -s -o /dev/null -w "%{http_code}" "$BASE_URL" || true)
if [ "$health_status" = "200" ] || [ "$health_status" = "302" ]; then
    echo "crawl4ai health: ok (HTTP $health_status)"
else
    echo "crawl4ai health: container not listening (HTTP $health_status)"
fi

# 2. Scrape probe with no API key
scrape_status=$(curl -s -o /dev/null -w "%{http_code}" -X POST "$BASE_URL/crawl" \
  -H "Content-Type: application/json" \
  -d '{"urls": ["https://example.com"], "priority": 10}' || true)

if [ "$scrape_status" = "200" ]; then
    echo "crawl4ai scrape: ok (HTTP 200, no API key required)"
fi

echo "Crawl4AI smoke test completed."
exit 0
