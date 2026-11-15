#!/bin/sh
set -eu
if [ "${ARES_PUBLIC_DEMO:-}" != "1" ]; then
  echo "The deployment image requires ARES_PUBLIC_DEMO=1." >&2
  exit 1
fi
test -f /app/frontend/dist/index.html
test -d /app/frontend/dist/assets
# One process: rate/concurrency budgets are per process. Never trust client XFF.
exec python -m uvicorn src.ares_health.api:app --host 0.0.0.0 --port "${PORT:-10000}" --workers 1 --no-proxy-headers --no-access-log --log-config /app/deploy/logging.json --limit-concurrency 32 --timeout-keep-alive 5
