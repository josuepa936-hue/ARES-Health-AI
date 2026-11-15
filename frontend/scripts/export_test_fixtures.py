"""Refresh fictional API fixtures from the canonical backend (run from repo root)."""
import json
from pathlib import Path

from fastapi.testclient import TestClient
from src.ares_health.api import app
from src.ares_health.synthetic import generate_scenario

client = TestClient(app)
fixtures = {"scenarios": client.get('/api/scenarios').json(), "evidence": client.get('/api/evidence').json()}
for scenario in ['stable', 'heart_rate_shift', 'sleep_shift', 'incomplete']:
    fixtures[scenario] = {
        'demo': client.get('/api/demo', params={'scenario': scenario}).json(),
        'timeline': client.get('/api/timeline', params={'scenario': scenario}).json(),
        'report': client.post('/api/review', json={'scenario': scenario}).json(),
    }
Path('frontend/src/test/fixtures.json').write_text(json.dumps(fixtures, indent=2, allow_nan=False) + '\n')
Path('frontend/public/synthetic-template.csv').write_text(generate_scenario('stable', seed=2026).to_csv(index=False))
