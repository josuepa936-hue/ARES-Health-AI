"""Explicit pytest target for a prepared --network none container, not mocked HTTP."""
import json
from pathlib import Path
import socket
import errno
import httpx
import pytest


@pytest.fixture(scope='module')
def client():
    assert {p.name for p in Path('/sys/class/net').iterdir()} == {'lo'}
    with httpx.Client(base_url='http://127.0.0.1:8000', timeout=15, trust_env=False) as c:
        yield c


def test_no_external_connectivity():
    assert {p.name for p in Path('/sys/class/net').iterdir()} == {'lo'}
    with pytest.raises(OSError) as exc:
        socket.create_connection(('198.51.100.1',443),timeout=1)
    assert exc.value.errno == errno.ENETUNREACH


def test_local_assets_and_no_remote_required_resources(client):
    import re
    r=client.get('/'); r.raise_for_status()
    assert 'data-public-demo="1"' not in r.text
    refs=re.findall(r'(?:src|href)="([^"]+)"',r.text)
    resources=[ref for ref in refs if ref.startswith('/assets/')]
    assert resources
    assert all(not ref.startswith(('http:', 'https:', '//')) for ref in refs)
    for resource in resources:
        asset=client.get(resource); asset.raise_for_status()
        if resource.endswith('.css'):
            assert '@import' not in asset.text
            assert not re.search(r'url\([\s\"\x27]*https?://',asset.text)


@pytest.mark.parametrize('scenario,state',[
    ('stable','NO_DEMO_RULE_TRIGGERED'),('heart_rate_shift','CHANGE_FOR_REVIEW'),
    ('sleep_shift','CHANGE_FOR_REVIEW'),('incomplete','DATA_QUALITY_BLOCKED')])
def test_scenarios_and_timeline_offline(client,scenario,state):
    snapshot=client.get('/api/demo',params={'scenario':scenario}); snapshot.raise_for_status()
    timeline=client.get('/api/timeline',params={'scenario':scenario}); timeline.raise_for_status()
    assert snapshot.json()['assessment']==timeline.json()['assessment']==state
    assert len(snapshot.json()['observations'])==21
    if scenario=='incomplete':
        assert snapshot.json()['descriptive_signals']==[]
        assert not any(e['type']=='trend_change' for e in timeline.json()['events'])


def test_checkin_copilot_wellness_and_report(client):
    values={'fictional_attestation':True,'resting_hr_bpm':140,'sleep_hours':7,
            'activity_minutes':45,'concerns':[]}
    checkin=client.post('/api/mission/fictional-check-in',json=values);checkin.raise_for_status()
    assert checkin.json()['observations'][-1]['resting_hr_bpm']==140
    context={'kind':'scenario','scenario':'stable','days':21,'seed':2026,'check_in':values}
    briefing=client.post('/api/mission/copilot',json={'context':context}); briefing.raise_for_status()
    ref=briefing.json()['context_ref']
    question={'turn':1,'question':'What changed?'}
    answer=client.post('/api/mission/copilot',json={'context':context,'expected_context_ref':ref,**question})
    answer.raise_for_status()
    wellness=client.post('/api/mission/wellness',json={'context':context,'expected_context_ref':ref})
    wellness.raise_for_status()
    assert len(wellness.json()['topics'])==3
    assert all(t['source_url'].startswith('https://www.nasa.gov/') for t in wellness.json()['topics'])
    report=client.post('/api/mission/comprehensive-report',json={'context':context,
        'expected_context_ref':ref,'fictional_attestation':True,'questions':[question],
        'audit_log':[{'sequence':1,'action':'review_state','review_state':'DOCUMENTED'}]})
    report.raise_for_status()
    result=report.json()
    assert result['fictional_review']['clinical_authorization'] is False
    assert result['fictional_review']['review_state']=='DOCUMENTED'
    assert len(result['evaluated_observations'])==21
    Path('/results/fictional-http-report.json').write_text(json.dumps(result,indent=2))


def test_research_unavailable_without_blocking_mission(client):
    # Local research is enabled deliberately: actual outbound NASA failure,
    # not just the disabled flag. No prepared MIT artifact is bundled.
    for path in ['/api/research/nasa/study','/api/research/nasa/sample-table','/api/research/ecg/demo?record=100']:
        r=client.get(path)
        assert r.status_code==503,r.text
        assert set(r.json())=={'detail'}
    assert client.get('/api/demo').json()['assessment']=='NO_DEMO_RULE_TRIGGERED'
