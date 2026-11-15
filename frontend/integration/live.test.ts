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
