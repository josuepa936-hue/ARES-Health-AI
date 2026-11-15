import { act, fireEvent, render, screen, waitFor, within } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { afterEach, beforeEach, expect, it, vi } from 'vitest';
import App from './App';
import { Overview } from './components/Overview';
import { TimelineView } from './components/TimelineView';
import { snapshotSchema, timelineSchema } from './contracts';
import * as downloads from './download';
import { fixtures, mockApi, respond } from './test/mockApi';
let fetchMock: ReturnType<typeof mockApi>;
beforeEach(() => {
  fetchMock = mockApi();
  vi.stubGlobal('fetch', fetchMock);
});
afterEach(() => vi.unstubAllGlobals());
async function ready() {
  render(<App />);
  await screen.findByRole('heading', { name: 'Mission overview' });
}
it('loads real API shapes, all scenario states, physiological charts and scientific links', async () => {
  const user = userEvent.setup();
  await ready();
  expect(screen.getByText('SYNTHETIC DATA / NOT A MEDICAL DEVICE')).toBeVisible();
  expect(
    screen.getAllByRole('button', {
      name: /^(Resting heart rate|Sleep duration|Daily activity)/,
    }),
  ).toHaveLength(3);
  await user.click(screen.getByRole('tab', { name: 'Research Sources' }));
  expect(screen.getByRole('link', { name: fixtures.evidence.references[0].title })).toHaveAttribute(
    'href',
    fixtures.evidence.references[0].url,
  );
  for (const id of ['heart_rate_shift', 'sleep_shift', 'incomplete', 'stable'] as const) {
    await user.selectOptions(screen.getByLabelText('Demo scenario'), id);
    await screen.findByRole('heading', { name: 'Mission overview' });
    expect(
      screen.getByText(fixtures[id].demo.assessment, { selector: '.assessment-chip strong' }),
    ).toBeVisible();
  }
  expect(
    fetchMock.mock.calls.some(([url]) =>
      String(url).includes('/api/timeline?scenario=sleep_shift'),
    ),
  ).toBe(true);
});
it('blocks trend findings and advanced metrics even with an inconsistent blocked payload', () => {
  const snapshot = snapshotSchema.parse({
    ...fixtures.stable.demo,
    assessment: 'DATA_QUALITY_BLOCKED',
    quality_issues: ['Missing fictional observation'],
    guidance: fixtures.incomplete.demo.guidance,
  });
  render(<Overview snapshot={snapshot} />);
  expect(screen.getByRole('alert')).toHaveTextContent('Missing fictional observation');
  expect(screen.queryByText('API descriptive statistics')).not.toBeInTheDocument();
  expect(screen.queryByText(/No demonstration rule triggered/)).not.toBeInTheDocument();
  expect(screen.queryByRole('region', { name: 'Explainable findings' })).not.toBeInTheDocument();
});
it('shows incomplete observations as missing values, not zero or reconstructed statistics', async () => {
  const user = userEvent.setup();
  await ready();
  await user.selectOptions(screen.getByLabelText('Demo scenario'), 'incomplete');
  await screen.findByText('Data quality blocks interpretation.');
  await user.click(screen.getByText('Observation values and UTC dates'));
  expect(screen.getAllByText('Missing')).toHaveLength(5);
  expect(screen.queryByText('API descriptive statistics')).not.toBeInTheDocument();
  await user.click(screen.getByRole('tab', { name: 'Mission Timeline' }));
  expect(screen.getAllByText(/All trend interpretations are withheld/)[0]).toBeVisible();
});
it('filters timeline types while retaining IDs and explains repeated windows', async () => {
  const user = userEvent.setup();
  render(
    <TimelineView
      timeline={timelineSchema.parse(fixtures.heart_rate_shift.timeline)}
      blocked={false}
    />,
  );
  expect(screen.getByText(/Repeated trends are overlapping/)).toBeVisible();
  expect(screen.getByText('event-000001')).toBeVisible();
  for (const type of ['observation', 'analysis_status', 'data_quality'])
    await user.click(screen.getByRole('checkbox', { name: type }));
  expect(screen.queryByText('event-000001')).not.toBeInTheDocument();
  expect(screen.getAllByText('trend_change', { selector: 'strong' }).length).toBeGreaterThan(0);
  await user.click(screen.getByRole('checkbox', { name: 'trend_change' }));
  expect(screen.getByText('No events match the selected filters.')).toBeVisible();
});
it('handles loading, empty scenario/evidence lists and API errors without fallback data', async () => {
  fetchMock.mockImplementation(async (input) =>
    String(input).includes('scenarios')
      ? respond({ ...fixtures.scenarios, scenarios: [] })
      : respond({ ...fixtures.evidence, references: [] }),
  );
  render(<App />);
  expect(screen.getByText('Loading scenarios…')).toBeVisible();
  expect(await screen.findByText('No scenarios available from the API.')).toBeVisible();
  await userEvent.setup().click(screen.getByRole('tab', { name: 'Research Sources' }));
  expect(screen.getByText('No references available.')).toBeVisible();
  expect(screen.queryByRole('heading', { name: 'Mission overview' })).not.toBeInTheDocument();
});
it('can retry a failed API connection', async () => {
  // The NASA risk explorer also fetches on mount. Fail the scenario
  // request by path rather than relying on incidental effect ordering.
  const normal = mockApi();
  let failedScenarioOnce = false;
  fetchMock.mockImplementation((input, init) => {
    if (!failedScenarioOnce && String(input).endsWith('/api/scenarios')) {
      failedScenarioOnce = true;
      return Promise.reject(new TypeError('Offline'));
    }
    return normal(input, init);
  });
  const user = userEvent.setup();
  render(<App />);
  expect(await screen.findByRole('alert')).toHaveTextContent('Cannot reach the local API');
  await user.click(screen.getByRole('button', { name: 'Retry API connection' }));
  await screen.findByRole('heading', { name: 'Mission overview' });
});
it('removes old results when a new mission request fails', async () => {
  const user = userEvent.setup();
  await ready();
  const normal = mockApi();
  fetchMock.mockImplementation((input, init) =>
    String(input).includes('heart_rate_shift')
      ? Promise.resolve(respond({ detail: 'Synthetic request rejected' }, 422))
      : normal(input, init),
  );
  await user.selectOptions(screen.getByLabelText('Demo scenario'), 'heart_rate_shift');
  expect(await screen.findByRole('alert')).toHaveTextContent('Synthetic request rejected');
  expect(screen.queryByRole('heading', { name: 'Mission overview' })).not.toBeInTheDocument();
});
it('aborts stale requests and ignores late responses on rapid scenario changes', async () => {
  const user = userEvent.setup();
  await ready();
  const normal = mockApi();
  const pending: { resolve: (response: Response) => void; signal: AbortSignal }[] = [];
  fetchMock.mockImplementation((input, init) => {
    if (String(input).includes('heart_rate_shift'))
      return new Promise((resolve) =>
        pending.push({ resolve, signal: init!.signal as AbortSignal }),
      );
    return normal(input, init);
  });
  await user.selectOptions(screen.getByLabelText('Demo scenario'), 'heart_rate_shift');
  expect(screen.getByText('Loading mission data…')).toBeVisible();
  await user.selectOptions(screen.getByLabelText('Demo scenario'), 'sleep_shift');
  await screen.findByRole('heading', { name: 'Mission overview' });
  expect(pending).toHaveLength(2);
  expect(pending.every((request) => request.signal.aborted)).toBe(true);
  await act(async () => {
    pending[0].resolve(respond(fixtures.heart_rate_shift.demo));
    pending[1].resolve(respond(fixtures.heart_rate_shift.timeline));
  });
  expect(screen.getByLabelText('Demo scenario')).toHaveValue('sleep_shift');
  expect(screen.getAllByText(/Sleep duration: recent/).length).toBeGreaterThan(0);
  expect(screen.queryByText(/Resting heart rate: recent/)).not.toBeInTheDocument();
});
it('requires CSV attestation, displays rejection errors, and clears stale mission output', async () => {
  const user = userEvent.setup();
  await ready();
  const file = new File(['invalid synthetic fixture'], 'fictional.csv', { type: 'text/csv' });
  await user.upload(screen.getByLabelText('Synthetic CSV file'), file);
  await user.click(screen.getByRole('button', { name: 'Upload synthetic CSV' }));
  expect(screen.getByRole('alert')).toHaveTextContent('Confirm fictional');
  const normal = mockApi();
  fetchMock.mockImplementation((input, init) =>
    String(input).endsWith('/synthetic-csv')
      ? Promise.resolve(
          respond({ detail: { errors: ['CSV_REJECTED: Missing required columns'] } }, 422),
        )
      : normal(input, init),
  );
  await user.click(screen.getByRole('checkbox', { name: /I attest/ }));
  await user.click(screen.getByRole('button', { name: 'Upload synthetic CSV' }));
  expect(await screen.findByRole('alert')).toHaveTextContent('Missing required columns');
  expect(screen.queryByRole('heading', { name: 'Mission overview' })).not.toBeInTheDocument();
});
it('uses the embedded CSV report for export without submitting a built-in review', async () => {
  const download = vi.spyOn(downloads, 'downloadReport').mockImplementation(() => {});
  const user = userEvent.setup();
  await ready();
  await user.upload(
    screen.getByLabelText('Synthetic CSV file'),
    new File(['synthetic template'], 'synthetic.csv', { type: 'text/csv' }),
  );
  await user.click(screen.getByRole('checkbox', { name: /I attest/ }));
  await user.click(screen.getByRole('button', { name: 'Upload synthetic CSV' }));
  await screen.findByText('Active data source: Uploaded synthetic CSV');
  await user.click(screen.getByRole('tab', { name: 'Mission Timeline' }));
  expect(screen.getByRole('heading', { name: 'Mission timeline' })).toBeVisible();
  expect(screen.getByText('event-000001')).toBeVisible();
  expect(screen.queryByRole('button', { name: 'Request review JSON' })).not.toBeInTheDocument();
  await user.click(screen.getByRole('tab', { name: 'Review & Export' }));
  await user.click(screen.getByRole('checkbox', { name: /I confirm these review actions/ }));
  await user.click(screen.getByRole('button', { name: 'Build comprehensive JSON report' }));
  await user.click(await screen.findByRole('button', { name: 'Download comprehensive JSON' }));
  expect(download).toHaveBeenCalledWith(
    expect.objectContaining({
      scenario: 'uploaded_synthetic_csv',
      copilot_schema_version: '1.5-demo',
    }),
  );
  expect(fetchMock.mock.calls.some(([url]) => String(url).endsWith('/review'))).toBe(false);
});
it('exports a manually documented comprehensive review and invalidates it after note edits', async () => {
  const download = vi.spyOn(downloads, 'downloadReport').mockImplementation(() => {});
  const user = userEvent.setup();
  await ready();
  await user.click(screen.getByRole('tab', { name: 'Review & Export' }));
  await user.selectOptions(screen.getByLabelText('Fictional review state'), 'DOCUMENTED');
  await user.type(screen.getByLabelText('Fictional review note'), 'Fictional review only.');
  expect(screen.getByLabelText('Fictional review note')).toHaveAttribute('maxlength', '500');
  await user.click(screen.getByRole('button', { name: 'Record fictional note' }));
  await user.click(screen.getByRole('checkbox', { name: /I confirm these review actions/ }));
  await user.click(screen.getByRole('button', { name: 'Build comprehensive JSON report' }));
  await user.click(await screen.findByRole('button', { name: 'Download comprehensive JSON' }));
  expect(download).toHaveBeenCalledWith(
    expect.objectContaining({
      copilot_schema_version: '1.5-demo',
      fictional_review: expect.objectContaining({
        review_state: 'DOCUMENTED',
        clinical_authorization: false,
      }),
    }),
  );
  const request = fetchMock.mock.calls.find(([url]) =>
    String(url).endsWith('/comprehensive-report'),
  );
  expect(JSON.parse(String(request![1]!.body)).audit_log).toContainEqual(
    expect.objectContaining({
      sequence: 2,
      action: 'note',
      note: 'Fictional review only.',
      // New Issue #21 provenance: UTC browser click-time is retained.
      recorded_at_utc: expect.stringMatching(
        /^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}\.\d{3}Z$/,
      ),
    }),
  );
  await user.type(screen.getByLabelText('Fictional review note'), ' Updated.');
  expect(screen.getByRole('button', { name: 'Download comprehensive JSON' })).toBeDisabled();
});
it('shows comprehensive report API failures without enabling an export', async () => {
  const user = userEvent.setup();
  await ready();
  const normal = mockApi();
  fetchMock.mockImplementation((input, init) =>
    String(input).endsWith('/comprehensive-report')
      ? Promise.resolve(respond({ detail: 'Review unavailable' }, 500))
      : normal(input, init),
  );
  await user.click(screen.getByRole('tab', { name: 'Review & Export' }));
  await user.click(screen.getByRole('checkbox', { name: /I confirm these review actions/ }));
  await user.click(screen.getByRole('button', { name: 'Build comprehensive JSON report' }));
  expect(await screen.findByRole('alert')).toHaveTextContent('Review unavailable');
  expect(
    screen.queryByRole('button', { name: 'Download comprehensive JSON' }),
  ).not.toBeInTheDocument();
});
it('cancels review requests when the mission changes', async () => {
  const user = userEvent.setup();
  await ready();
  const normal = mockApi();
  let signal: AbortSignal | undefined;
  fetchMock.mockImplementation((input, init) => {
    if (String(input).endsWith('/comprehensive-report')) {
      signal = init!.signal as AbortSignal;
      return new Promise(() => {});
    }
    return normal(input, init);
  });
  await user.click(screen.getByRole('tab', { name: 'Review & Export' }));
  await user.click(screen.getByRole('checkbox', { name: /I confirm these review actions/ }));
  await user.click(screen.getByRole('button', { name: 'Build comprehensive JSON report' }));
  await user.selectOptions(screen.getByLabelText('Demo scenario'), 'incomplete');
  await screen.findByText('Data quality blocks interpretation.');
  expect(signal?.aborted).toBe(true);
});
it('rejects oversized CSV before making an upload request and resets attestation on file changes', async () => {
  const user = userEvent.setup();
  await ready();
  const input = screen.getByLabelText('Synthetic CSV file');
  await user.upload(input, new File(['x'.repeat(1_000_001)], 'large.csv', { type: 'text/csv' }));
  await user.click(screen.getByRole('checkbox', { name: /I attest/ }));
  await user.click(screen.getByRole('button', { name: 'Upload synthetic CSV' }));
  expect(screen.getByRole('alert')).toHaveTextContent('1,000,000 bytes');
  expect(fetchMock.mock.calls.some(([url]) => String(url).endsWith('/synthetic-csv'))).toBe(false);
  await user.upload(input, new File(['x'], 'small.csv', { type: 'text/csv' }));
  expect(screen.getByRole('checkbox', { name: /I attest/ })).not.toBeChecked();
});
