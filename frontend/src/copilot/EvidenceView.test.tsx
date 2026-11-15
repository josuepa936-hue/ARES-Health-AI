import { render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { afterEach, expect, it, vi } from 'vitest';
import { EvidenceView } from './EvidenceView';
import { responseSchema } from '../copilot-contract';
import { snapshotSchema } from '../contracts';
import responses from '../test/copilot-fixtures.json';
import snapshots from '../test/fixtures.json';
import App from '../App';
import { mockApi } from '../test/mockApi';
afterEach(() => vi.unstubAllGlobals());
it('shows a collapsed digest with canonical means, dates and progressive original references', async () => {
  const user = userEvent.setup();
  const response = responseSchema.parse(responses.heart_rate_shift.answers['What changed?']);
  const snapshot = snapshotSchema.parse(snapshots.heart_rate_shift.demo);
  render(<EvidenceView response={response} snapshot={snapshot} />);
  expect(screen.queryByText('Evidence summary')).not.toBeVisible();
  await user.click(screen.getByText(/View evidence/));
  const heart = snapshot.descriptive_signals.find((row) => row.metric === 'resting_hr_bpm')!;
  expect(screen.getByTestId('evidence-baseline-resting_hr_bpm')).toHaveTextContent(
    heart.baseline_mean.toFixed(3),
  );
  expect(screen.getByTestId('evidence-recent-resting_hr_bpm')).toHaveTextContent(
    heart.recent_mean.toFixed(3),
  );
  expect(screen.getByTestId('evidence-delta-resting_hr_bpm')).toHaveTextContent(
    `+${heart.delta.toFixed(3)}`,
  );
  expect(
    screen.getByText(/2026-11-01T00:00:00Z/, { selector: '.evidence-windows dd' }),
  ).toBeVisible();
  expect(screen.getByText('observation:20:resting_hr_bpm')).not.toBeVisible();
  await user.click(screen.getByText(/Detailed observations, UTC dates and timeline IDs/));
  expect(screen.getByText('observation:20:resting_hr_bpm')).toBeVisible();
  expect(screen.getAllByText(/Timeline:/).length).toBe(33);
});
it('withholds averages for blocked input even when supplied a snapshot with descriptive values', async () => {
  const user = userEvent.setup();
  const snapshot = snapshotSchema.parse(snapshots.stable.demo);
  render(
    <EvidenceView
      response={responseSchema.parse(responses.incomplete.answers['What changed?'])}
      snapshot={snapshot}
    />,
  );
  await user.click(screen.getByText(/View evidence/));
  expect(screen.getByText(/No numerical averages/)).toBeVisible();
  expect(screen.queryByLabelText('Canonical Python comparisons')).not.toBeInTheDocument();
  expect(screen.getByText(/Missing or nonnumeric resting_hr_bpm/)).toBeVisible();
});
it('preserves direct official source links and response limitations without deriving values', async () => {
  const user = userEvent.setup();
  render(
    <EvidenceView
      response={responseSchema.parse(
        responses.stable.answers['What is the relevant NASA hazard background?'],
      )}
    />,
  );
  await user.click(screen.getByText(/View evidence/));
  expect(screen.getByRole('link', { name: 'Space radiation' })).toHaveAttribute(
    'href',
    'https://www.nasa.gov/hrp/hazards/',
  );
  await user.click(screen.getByText('Medical limitations and context reference'));
  expect(screen.getByText(responses.stable.briefing.context_ref)).toBeVisible();
});
it('expands and restores the same conversation draft without new data requests', async () => {
  const fetch = mockApi();
  vi.stubGlobal('fetch', fetch);
  const user = userEvent.setup();
  render(<App />);
  await screen.findByRole('heading', { name: 'Mission overview' });
  await user.click(screen.getByRole('tab', { name: 'ARES Copilot' }));
  await screen.findByText(responses.stable.briefing.answer);
  await user.type(screen.getByLabelText('Fictional mission question'), 'What changed?');
  const count = fetch.mock.calls.length;
  await user.click(screen.getByRole('button', { name: 'Focus / expand conversation' }));
  expect(screen.getByRole('dialog', { name: 'Expanded ARES Copilot conversation' })).toBeVisible();
  expect(document.body.style.overflow).toBe('hidden');
  expect(screen.getByLabelText('Fictional mission question')).toHaveValue('What changed?');
  await user.click(screen.getByRole('button', { name: 'Restore docked conversation' }));
  expect(screen.getByLabelText('Fictional mission question')).toHaveValue('What changed?');
  await waitFor(() =>
    expect(screen.getByRole('button', { name: 'Focus / expand conversation' })).toHaveFocus(),
  );
  expect(fetch.mock.calls).toHaveLength(count);
  expect(document.body.style.overflow).not.toBe('hidden');
});

it('returns to the full cockpit and reopens the draft without changing mission facts or requesting data', async () => {
  const fetch = mockApi();
  vi.stubGlobal('fetch', fetch);
  const scroll = vi.spyOn(window, 'scrollTo').mockImplementation(() => {});
  const user = userEvent.setup();
  render(<App />);
  await screen.findByRole('heading', { name: 'Mission overview' });
  await user.selectOptions(screen.getByLabelText('Demo scenario'), 'heart_rate_shift');
  await screen.findByText(snapshots.heart_rate_shift.demo.assessment, {
    selector: '.assessment-chip strong',
  });
  await user.click(screen.getByRole('tab', { name: 'ARES Copilot' }));
  await screen.findByText(responses.heart_rate_shift.briefing.answer);
  const originalValue = screen.getByTestId('latest-resting_hr_bpm').textContent;
  await user.type(screen.getByLabelText('Fictional mission question'), 'What changed?');
  const calls = fetch.mock.calls.length;
  await user.click(screen.getByRole('button', { name: /Full cockpit/ }));
  await waitFor(() =>
    expect(screen.getByRole('button', { name: /ARES Copilot · briefing ready/ })).toHaveFocus(),
  );
  expect(scroll).toHaveBeenCalledWith({ top: 0, behavior: 'instant' });
  expect(screen.getByLabelText('Demo scenario')).toHaveValue('heart_rate_shift');
  await user.click(screen.getByRole('button', { name: /Open workspace/ }));
  expect(screen.getByLabelText('Fictional mission question')).toHaveValue('What changed?');
  expect(screen.getByTestId('latest-resting_hr_bpm')).toHaveTextContent(originalValue!);
  expect(fetch.mock.calls).toHaveLength(calls);
});
