/** Issue #21: real UI event time and canonical comprehensive export contract. */
import { render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { afterEach, expect, it, vi } from 'vitest';
import App from '../App';
import { mockApi } from '../test/mockApi';

afterEach(() => vi.unstubAllGlobals());

it('stamps fictitious actions at click time and exports matching four-state review status', async () => {
  const fetch = mockApi();
  vi.stubGlobal('fetch', fetch);
  const user = userEvent.setup();
  render(<App />);
  await screen.findByRole('heading', { name: 'Mission overview' });
  await user.click(screen.getByRole('tab', { name: 'ARES Copilot' }));
  await screen.findByRole('region', { name: 'ARES mission copilot' });
  await user.click(screen.getByRole('tab', { name: 'Review & Export' }));

  const note = screen.getByLabelText('Fictional review note');
  await user.type(note, 'cardiovascular');
  await user.click(screen.getByRole('button', { name: 'Record fictional note' }));
  await user.click(screen.getByRole('checkbox', { name: /Inspected fictional source/ }));
  await user.selectOptions(screen.getByLabelText('Fictional review state'), 'IN_PROGRESS');

  expect(screen.getByText('#1 note')).toBeVisible();
  expect(screen.getByText('#2 source_units')).toBeVisible();
  expect(screen.getByText('#3 review_state')).toBeVisible();
  expect(screen.getAllByTitle('User-device UTC, not server verified')).toHaveLength(3);
  await user.click(screen.getByRole('checkbox', { name: /I confirm these review actions/ }));
  await user.click(screen.getByRole('button', { name: 'Build comprehensive JSON report' }));
  expect(await screen.findByText(/Report: NO_DEMO_RULE_TRIGGERED · review IN_PROGRESS/))
    .toBeVisible();
  const call = fetch.mock.calls.find(([url]) =>
    String(url).includes('/api/mission/comprehensive-report'),
  );
  expect(call).toBeDefined();
  const body = JSON.parse(String(call![1]?.body));
  expect(body.audit_log).toHaveLength(3);
  expect(body.audit_log.map((e: { sequence: number }) => e.sequence)).toEqual([1, 2, 3]);
  for (const event of body.audit_log) {
    expect(event.recorded_at_utc).toMatch(
      /^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}\.\d{3}Z$/,
    );
    expect(Number.isFinite(Date.parse(event.recorded_at_utc))).toBe(true);
  }
  expect(body.audit_log.map((e: { recorded_at_utc: string }) => e.recorded_at_utc))
    .toEqual([...body.audit_log.map((e: { recorded_at_utc: string }) => e.recorded_at_utc)].sort());
});
