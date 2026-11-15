#!/bin/sh
set -eu
# This entrypoint is solely for a prepared, network-isolated test container.
python - <<'PY'
from pathlib import Path
import socket,json,errno
assert {p.name for p in Path('/sys/class/net').iterdir()} == {'lo'}, 'Use docker run --network none.'
try:
    socket.create_connection(('198.51.100.1', 443), timeout=1)
except OSError as exc:
    assert exc.errno == errno.ENETUNREACH
    Path('/results/network-proof.json').write_text(json.dumps({'interfaces':['lo'],'outbound_errno':exc.errno,'route_table':Path('/proc/net/route').read_text()},indent=2))
    print('PASS: only loopback interface; outbound TCP blocked:', type(exc).__name__, exc.errno)
else:
    raise SystemExit('Outbound connectivity unexpectedly available')
PY
python -m uvicorn src.ares_health.api:app --host 127.0.0.1 --port 8000 --no-access-log > /results/server.log 2>&1 &
ARES_OFFLINE_PID=$!
trap 'kill "$ARES_OFFLINE_PID" 2>/dev/null || true' EXIT
python - <<'PY'
import time,httpx
for attempt in range(100):
    try:
        response=httpx.get('http://127.0.0.1:8000/api/status',timeout=1,trust_env=False)
        if response.status_code==200:
            assert response.json()['mode']=='local-development'
            break
    except httpx.HTTPError:
        pass
    time.sleep(.1)
else:
    raise SystemExit('Local server did not become ready')
PY
python -m pytest -q -p no:cacheprovider --basetemp=/results/pytest-tmp offline_checks/http_workflow.py > /results/http.log 2>&1
cat /results/http.log
cd /app/frontend
node node_modules/@playwright/test/cli.js test --config playwright.offline.config.ts > /results/browser.log 2>&1
cat /results/browser.log
