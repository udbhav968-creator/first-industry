#!/usr/bin/env bash
set -e

SEARXNG_URL="${SEARXNG_URL:-http://localhost:8080}"

echo "Testing SearXNG connectivity at $SEARXNG_URL..."
status_code=$(curl -s -o /dev/null -w "%{http_code}" "$SEARXNG_URL" || true)

if [ "$status_code" -eq 200 ] || [ "$status_code" -eq 302 ]; then
  echo "SearXNG is running and reachable (HTTP $status_code)."
  
  # Check JSON search capability
  json_status=$(curl -s -o /dev/null -w "%{http_code}" "$SEARXNG_URL/search?q=test&format=json" || true)
  if [ "$json_status" -eq 200 ]; then
    echo "SearXNG JSON search API is enabled and operational."
  fi
  exit 0
else
  echo "SearXNG failed with HTTP $status_code."
  exit 1
fi
