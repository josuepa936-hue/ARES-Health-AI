import { act, render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { afterEach, expect, it, vi } from 'vitest';
import ResearchLab from './ResearchLab';
import Workspace from '../Workspace';
import { mockApi, respond } from '../test/mockApi';
afterEach(() => vi.unstubAllGlobals());
const result = {
  schema_version: '1.2-research',
  record: '100',
  data_provenance: 'public_research_ecg',
  status: 'abstained',
  reasons: ['Missing finite input samples'],
  source: {
    dataset: 'MIT-BIH Arrhythmia Database',
    version: '1.0.0',
    url: 'https://physionet.org/content/mitdb/1.0.0/',
    doi: 'https://doi.org/10.13026/C2F305',
    context: 'Public terrestrial research',
  },
  protocol: {
    sampling_rate_hz: 360,
    tolerance_ms: 150,
    scoring_start_sample: 360,
    scoring_end_sample_exclusive: 21240,
    segment_end_sample_exclusive: 21600,
    display_stride: 12,
    matching: 'ordered one-to-one',
  },
  processing_versions: { wfdb: '4.3.1', neurokit2: '0.2.12' },
  quality: { status: 'failed', checks: [] },
  metrics: null,
  waveform: [],
  detected_peaks: [],
  reference_peaks: [],
  matches: [],
  discrepancies: [],
  annotation_counts: null,
  disclaimer: 'Not clinical validation or spaceflight qualification.',
};
it('shows abstention and public provenance without scores or synthetic labels', async () => {
  vi.stubGlobal('fetch', vi.fn().mockResolvedValue(respond(result)));
  render(<ResearchLab />);
  expect(await screen.findByText('Benchmark abstained')).toBeVisible();
  expect(screen.getByText('PUBLIC TERRESTRIAL RESEARCH ECG / NOT A MEDICAL DEVICE')).toBeVisible();
  expect(screen.queryByText('SYNTHETIC DATA / NOT A MEDICAL DEVICE')).not.toBeInTheDocument();
  expect(screen.queryByRole('img')).not.toBeInTheDocument();
  expect(
    screen.queryByRole('heading', { name: /Beat-detection benchmark/ }),
  ).not.toBeInTheDocument();
});
it('renders supplied benchmark metrics, waveform markers and discrepancies without recomputing', async () => {
  vi.stubGlobal(
    'fetch',
    vi.fn().mockResolvedValue(
      respond({
        ...result,
        status: 'benchmarked',
        reasons: [],
        quality: { status: 'engineering_gates_passed', checks: [] },
        metrics: {
          tp: 2,
          fp: 1,
          fn: 1,
          precision: 2 / 3,
          recall: 2 / 3,
          f1: 2 / 3,
          mean_absolute_timing_error_ms: 25,
        },
        waveform: [
          { sample: 0, mv: 0 },
          { sample: 600, mv: 1 },
        ],
        detected_peaks: [{ sample: 400, mv: 1 }],
        reference_peaks: [{ sample: 409, mv: 0.9 }],
        discrepancies: [{ type: 'FP', sample: 1000 }],
        annotation_counts: { excluded_nonbeat_annotations: 2 },
      }),
    ),
  );
  render(<ResearchLab />);
  expect(
    await screen.findByRole('heading', { name: 'Beat-detection benchmark (not medical accuracy)' }),
  ).toBeVisible();
  expect(screen.getByText('25')).toBeVisible();
  const chart = screen.getByRole('img');
  expect(chart.querySelectorAll('circle')).toHaveLength(1);
  expect(chart.querySelectorAll('rect')).toHaveLength(1);
  expect(screen.getByRole('cell', { name: '1000' })).toBeVisible();
  expect(screen.getByText(/Metrics use full-resolution/)).toBeVisible();
});
it('offers retry when research is disabled or unavailable', async () => {
  const fetch = vi
    .fn()
    .mockResolvedValueOnce(respond({ detail: 'Optional research mode is disabled.' }, 503))
    .mockResolvedValue(respond(result));
  vi.stubGlobal('fetch', fetch);
  const user = userEvent.setup();
  render(<ResearchLab />);
  expect(await screen.findByRole('alert')).toHaveTextContent('disabled');
  await user.click(screen.getByRole('button', { name: 'Reload research benchmark' }));
  expect(await screen.findByText('Benchmark abstained')).toBeVisible();
});
it('does not request research until selected and preserves the mission fallback', async () => {
  const normal = mockApi();
  const fetch = vi.fn((input: string | URL | Request, init?: RequestInit) =>
    String(input).includes('/research/') ? Promise.resolve(respond(result)) : normal(input, init),
  );
  vi.stubGlobal('fetch', fetch);
  const user = userEvent.setup();
  render(<Workspace />);
  await screen.findByRole('heading', { name: 'Mission overview' });
  expect(fetch.mock.calls.some(([url]) => String(url).includes('/research/'))).toBe(false);
  await user.click(screen.getByRole('button', { name: 'Optional research lab' }));
  expect(await screen.findByText('Benchmark abstained')).toBeVisible();
  expect(screen.getByText('SYNTHETIC DATA / NOT A MEDICAL DEVICE')).not.toBeVisible();
  await user.click(screen.getByRole('button', { name: 'Synthetic mission demo' }));
  expect(screen.getByRole('heading', { name: 'Mission overview' })).toBeVisible();
});
it('aborts research requests on unmount', () => {
  let signal: AbortSignal | undefined;
  vi.stubGlobal(
    'fetch',
    vi.fn((_input, init) => {
      signal = init.signal;
      return new Promise(() => {});
    }),
  );
  const view = render(<ResearchLab />);
  view.unmount();
  expect(signal?.aborted).toBe(true);
});
