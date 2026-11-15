import { render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { afterEach, expect, it, vi } from 'vitest';
import App from './App';
import { mockApi } from './test/mockApi';
import { FictionalCheckIn } from './components/FictionalCheckIn';

afterEach(() => vi.unstubAllGlobals());

it('lets a fictional astronaut submit one check-in and see backend report plus timeline', async () => {
  const fetch = mockApi();
  vi.stubGlobal('fetch', fetch);
  const user = userEvent.setup();
  render(<App />);
  await screen.findByRole('heading', { name: 'Mission overview' });

  const send = screen.getByRole('button', { name: 'Analyze fictional check-in' });
  expect(send).toBeDisabled();
  const hr = screen.getByRole('spinbutton', { name: 'Fictional resting heart rate' });
  await user.clear(hr);
  await user.type(hr, '140');
  await user.click(screen.getByRole('checkbox', { name: 'Fatigue (hypothetical)' }));
  await user.click(
    screen.getByRole('checkbox', { name: /I confirm this check-in contains fictional/ }),
  );
  await user.click(send);

  expect(
    await screen.findByText('Active data source: Attested fictional crew check-in'),
  ).toBeVisible();
  expect(
    screen.getByRole('heading', { name: 'Check-in applied to fictional mission' }),
  ).toBeVisible();
  expect(screen.getByText('Only the latest fictional observation was replaced.')).toBeVisible();
  await user.click(screen.getByRole('tab', { name: 'Mission Timeline' }));
  expect(screen.getByRole('heading', { name: 'Mission timeline' })).toBeVisible();
  expect(screen.getByText('event-000001')).toBeVisible();
  expect(screen.queryByRole('button', { name: 'Request review JSON' })).not.toBeInTheDocument();
  await user.click(screen.getByRole('tab', { name: 'Review & Export' }));
  await user.click(screen.getByRole('checkbox', { name: /I confirm these review actions/ }));
  await user.click(screen.getByRole('button', { name: 'Build comprehensive JSON report' }));
  expect(await screen.findByRole('button', { name: 'Download comprehensive JSON' })).toBeVisible();

  const entry = fetch.mock.calls.find(([url]) =>
    String(url).includes('/mission/fictional-check-in'),
  );
  expect(entry).toBeTruthy();
  const input = JSON.parse(String(entry![1]?.body));
  expect(input).toEqual({
    fictional_attestation: true,
    scenario: 'stable',
    seed: 2026,
    days: 21,
    resting_hr_bpm: 140,
    sleep_hours: 7.5,
    activity_minutes: 42,
    concerns: ['fatigue'],
  });
});

it('blocks unsanctioned or invalid fictional entry in the client', async () => {
  const onSubmit = vi.fn();
  const user = userEvent.setup();
  render(<FictionalCheckIn scenario="stable" busy={false} onSubmit={onSubmit} />);
  expect(screen.getByRole('button', { name: 'Analyze fictional check-in' })).toBeDisabled();
  await user.click(screen.getByRole('checkbox', { name: /I confirm this check-in/ }));
  await user.clear(screen.getByRole('spinbutton', { name: 'Fictional resting heart rate' }));
  await user.type(screen.getByRole('spinbutton', { name: 'Fictional resting heart rate' }), '260');
  await user.click(screen.getByRole('button', { name: 'Analyze fictional check-in' }));
  expect(onSubmit).not.toHaveBeenCalled();
});

it('loads official NASA hazard context and lets users explore each category', async () => {
  const fetch = mockApi();
  vi.stubGlobal('fetch', fetch);
  const user = userEvent.setup();
  render(<App />);
  await user.click(screen.getByRole('tab', { name: 'Spaceflight Risks' }));
  expect(
    await screen.findByRole('heading', { name: 'Five hazards of human spaceflight' }),
  ).toBeVisible();
  const risk = screen.getByRole('region', { name: 'NASA spaceflight risk explorer' });
  const radiation = screen.getByRole('button', { name: 'Space radiation' });
  expect(radiation).toHaveAttribute('aria-pressed', 'false');
  await user.click(radiation);
  expect(radiation).toHaveAttribute('aria-pressed', 'true');
  expect(risk).toHaveTextContent('Fictional or unavailable');
  expect(risk).toHaveTextContent('Read NASA Human Research Program source');
  expect(fetch.mock.calls.some(([url]) => String(url).endsWith('/mission/risk-guide'))).toBe(true);
});
