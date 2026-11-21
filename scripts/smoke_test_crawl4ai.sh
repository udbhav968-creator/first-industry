#!/bin/bash
set -e

CRAWL4AI_URL="${CRAWL4AI_URL:-http://localhost:11235}"

status=$(curl -s -o /dev/null -w "%{http_code}" "$CRAWL4AI_URL/health" || curl -s -o /dev/null -w "%{http_code}" "$CRAWL4AI_URL" || true)

if [ "$status" = "200" ] || [ "$status" = "302" ]; then
    echo "crawl4ai: ok ($status)"
    exit 0
fi

echo "crawl4ai: failed ($status)"
exit 1
