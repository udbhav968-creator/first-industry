#!/bin/bash
set -e

SEARXNG_URL="${SEARXNG_URL:-http://localhost:8080}"

status=$(curl -s -o /dev/null -w "%{http_code}" "$SEARXNG_URL" || true)

if [ "$status" = "200" ] || [ "$status" = "302" ]; then
    echo "searxng: ok ($status)"
    exit 0
fi

echo "searxng: failed ($status)"
exit 1
