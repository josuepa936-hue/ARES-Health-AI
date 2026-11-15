/** Real HTTP checks. Start loopback FastAPI and Vite before this suite. */
import { readFile } from 'node:fs/promises';
import { expect, it } from 'vitest';
import { createApi } from '../src/api';
const origin = 'http://127.0.0.1:5173';
const api = createApi(origin);
const signal = () => AbortSignal.timeout(10000);
it('serves the React entry point and API-backed catalog/evidence through Vite', async () => {
  const page = await fetch(origin);
  expect(page.status).toBe(200);
  expect(await page.text()).toContain('/src/main.tsx');
  expect((await api.scenarios(signal())).scenarios.map((item) => item.id)).toEqual([
    'stable',
    'heart_rate_shift',
    'sleep_shift',
    'incomplete',
  ]);
  const evidence = await api.evidence(signal());
  expect(
    evidence.references.some((item) => item.organization.includes('Canadian Space Agency')),
  ).toBe(true);
});
it.each(['stable', 'heart_rate_shift', 'sleep_shift', 'incomplete'] as const)(
  'loads %s through the proxy with canonical Python values and timeline',
  async (scenario) => {
    const [demo, timeline, direct] = await Promise.all([
      api.demo(scenario, signal()),
      api.timeline(scenario, signal()),
      fetch(`http://127.0.0.1:8000/api/demo?scenario=${scenario}&seed=2026&days=21`).then((res) =>
        res.json(),
      ),
    ]);
    expect(demo.summary).toEqual(direct.summary);
    expect(demo.observations).toEqual(direct.observations);
    expect(timeline.assessment).toBe(demo.assessment);
    expect(timeline.events.filter((event) => event.type === 'observation')).toHaveLength(21);
    if (scenario === 'incomplete') {
      expect(demo.assessment).toBe('DATA_QUALITY_BLOCKED');
      expect(demo.descriptive_signals).toEqual([]);
      expect(demo.observations.at(-1)?.sleep_hours).toBeNull();
      expect(timeline.events.some((event) => event.type === 'trend_change')).toBe(false);
    } else if (scenario !== 'stable') expect(demo.assessment).toBe('CHANGE_FOR_REVIEW');
  },
);
it('uploads the local synthetic template as raw bytes and exports its embedded report', async () => {
  const bytes = await readFile(new URL('../public/synthetic-template.csv', import.meta.url));
  const template = await fetch(`${origin}/synthetic-template.csv`);
  expect(await template.text()).toBe(bytes.toString());
  const snapshot = await api.upload(
    new File([new Uint8Array(bytes)], 'synthetic.csv', { type: 'text/csv' }),
    true,
    signal(),
  );
  expect(snapshot.scenario).toBe('uploaded_synthetic_csv');
  expect(snapshot.review_report.scenario).toBe('uploaded_synthetic_csv');
  expect(snapshot.review_report.assessment).toBe(snapshot.assessment);
  expect(snapshot.mission_timeline.assessment).toBe(snapshot.assessment);
  expect(snapshot.mission_timeline.scenario).toBe('uploaded_synthetic_csv');
  expect(
    snapshot.mission_timeline.events.filter((event) => event.type === 'observation'),
  ).toHaveLength(21);
  expect(JSON.parse(JSON.stringify(snapshot.review_report))).toEqual(snapshot.review_report);
});
it('surfaces strict CSV validation failures from the real backend', async () => {
  await expect(
    api.upload(new File(['timestamp_utc\ninvalid'], 'fictional-invalid.csv'), true, signal()),
  ).rejects.toThrow(/Missing|required|columns/i);
  const response = await fetch(`${origin}/api/synthetic-csv`, {
    method: 'POST',
    headers: { 'Content-Type': 'text/csv' },
    body: 'fictional',
  });
  expect(response.status).toBe(400);
});
it('submits a fictional review and preserves API report fields for JSON export', async () => {
  const report = await api.review(
    'heart_rate_shift',
    'Reviewed in demo',
    'Checked fictional records.',
    signal(),
  );
  expect(report.assessment).toBe('CHANGE_FOR_REVIEW');
  expect(report.reviewer_note).toBe('Checked fictional records.');
  expect(report.review_state).toBe('Reviewed in demo');
  expect(report).toHaveProperty('methodology');
});

it('keeps the optional research namespace separate from synthetic mission data', async () => {
  const response = await fetch(`${origin}/api/research/ecg/demo?record=100`);
  if (response.status === 503) {
    expect((await response.json()).detail).toMatch(/disabled|artifact/i);
  } else {
    expect(response.status).toBe(200);
    const { researchSchema } = await import('../src/research-contract');
    const research = researchSchema.parse(await response.json());
    expect(research.data_provenance).toBe('public_research_ecg');
    if (research.status === 'abstained') expect(research.metrics).toBeNull();
  }
  expect((await api.demo('stable', signal())).data_provenance).toBe('synthetic');
});

it('performs the complete fictional crew input-to-evaluation-to-report flow through real FastAPI', async () => {
  const result = await api.fictionalCheckIn(
    {
      fictional_attestation: true,
      scenario: 'stable',
      seed: 2026,
      days: 21,
      resting_hr_bpm: 140,
      sleep_hours: 7,
      activity_minutes: 45,
      concerns: ['fatigue'],
    },
    signal(),
  );
  expect(result.data_provenance).toBe('synthetic');
  expect(result.assessment).toBe('CHANGE_FOR_REVIEW');
  expect(result.mission_timeline.assessment).toBe(result.assessment);
  expect(result.review_report.assessment).toBe(result.assessment);
  expect(result.observations.at(-1)?.resting_hr_bpm).toBe(140);
  expect(result.check_in.reported_concerns).toEqual(['fatigue']);
  expect(result.decision_support.clinical_decision_support).toBe(false);
  const unchanged = await api.demo('stable', signal());
  expect(unchanged.assessment).toBe('NO_DEMO_RULE_TRIGGERED');
});

it('serves the five spaceflight hazards as documented context, not risk scores', async () => {
  const guide = await api.riskGuide(signal());
  expect(guide.risks).toHaveLength(5);
  expect(guide.reference_url).toContain('nasa.gov');
  expect(guide.risks.every((risk) => risk.ares_current_coverage.length > 0)).toBe(true);
  expect(JSON.stringify(guide)).not.toMatch(/"risk_score"/);
});

it('refuses a fictional check-in without a true attestation', async () => {
  const response = await fetch(origin + '/api/mission/fictional-check-in', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      scenario: 'stable',
      days: 21,
      resting_hr_bpm: 64,
      sleep_hours: 7,
      activity_minutes: 45,
    }),
  });
  expect(response.status).toBe(422);
});

it.each(['stable', 'heart_rate_shift', 'sleep_shift', 'incomplete'] as const)(
  'recalculates an offline copilot briefing for %s',
  async (scenario) => {
    const source = { kind: 'scenario' as const, scenario, seed: 2026, days: 21 };
    const [brief, demo] = await Promise.all([
      api.copilot(source, '', 0, undefined, signal()),
      api.demo(scenario, signal()),
    ]);
    expect(brief.assessment).toBe(demo.assessment);
    expect(brief.engine).toBe('deterministic-offline');
    expect(brief.generative_model).toBe(false);
    const reply = await api.copilot(source, 'What changed?', 1, brief.context_ref, signal());
    expect(reply.context_ref).toBe(brief.context_ref);
    if (scenario === 'incomplete')
      expect(reply.evidence_refs.every((ref) => ref.kind === 'quality')).toBe(true);
  },
);
it('exports canonical check-in values and manual documented state without clinical authorization', async () => {
  const source = {
    kind: 'scenario' as const,
    scenario: 'stable' as const,
    seed: 2026,
    days: 21,
    check_in: {
      fictional_attestation: true as const,
      resting_hr_bpm: 140,
      sleep_hours: 7,
      activity_minutes: 45,
      concerns: [],
    },
  };
  const briefing = await api.copilot(source, '', 0, undefined, signal());
  const report = await api.comprehensiveReport(
    source,
    briefing.context_ref,
    [{ turn: 1, question: 'What changed?' }],
    [
      {
        sequence: 1, action: 'review_state', review_state: 'DOCUMENTED',
        recorded_at_utc: '2026-11-15T07:00:00.000Z',
      },
      {
        sequence: 2, action: 'source_units', checked: true,
        recorded_at_utc: '2026-11-15T07:00:01.000Z',
      },
    ],
    signal(),
  );
  expect(report.fictional_review.review_state).toBe('DOCUMENTED');
  expect(report.review_state).toBe('DOCUMENTED');
  expect(report.application_version).toBe('1.5');
  expect(report.copilot_application_version).toBe(report.application_version);
  expect(report.mission_timeline.application_version).toBe(report.application_version);
  expect(report.fictional_review.audit_timestamps_complete).toBe(true);
  expect(report.fictional_review.audit_log.map((entry) => entry.recorded_at_utc)).toEqual([
    '2026-11-15T07:00:00.000Z', '2026-11-15T07:00:01.000Z',
  ]);
  expect(report.fictional_review.clinical_authorization).toBe(false);
  expect(report.assessment).toBe(briefing.assessment);
  expect(report.copilot.transcript[0].response.context_ref).toBe(report.context_ref);
  expect(report.evaluated_observations).toEqual(
    expect.arrayContaining([
      expect.objectContaining({ resting_hr_bpm: 140, sleep_hours: 7, activity_minutes: 45 }),
    ]),
  );
});
it('refuses stale context and unsafe medical questions over real HTTP', async () => {
  const stable = { kind: 'scenario' as const, scenario: 'stable' as const, seed: 2026, days: 21 };
  const brief = await api.copilot(stable, '', 0, undefined, signal());
  const unsafe = await api.copilot(stable, 'Give a treatment', 1, brief.context_ref, signal());
  expect(unsafe.intent).toBe('refusal');
  await expect(
    api.copilot(
      { ...stable, scenario: 'sleep_shift' },
      'What changed?',
      1,
      brief.context_ref,
      signal(),
    ),
  ).rejects.toThrow('Mission context changed');
});
