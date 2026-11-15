import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { beforeEach, afterEach, expect, it, vi } from 'vitest';
import App from '../App';
import { mockApi } from '../test/mockApi';

beforeEach(() => vi.stubGlobal('fetch', mockApi()));
afterEach(() => vi.unstubAllGlobals());

async function openCopilot() {
  const user = userEvent.setup();
  render(<App />);
  await screen.findByRole('heading', { name: 'Mission overview' });
  await user.click(screen.getByRole('tab', { name: 'ARES Copilot' }));
  await screen.findByText('Mission Wellness & Procedures');
  await user.click(screen.getByText('Mission Wellness & Procedures'));
  return user;
}

it('shows three NASA-linked educational topics and opens existing review workflow', async () => {
  const user = await openCopilot();
  expect(await screen.findByText('Sleep and schedule')).toBeVisible();
  expect(screen.getByText('Cardiovascular observation')).toBeVisible();
  expect(screen.getByText('Movement and exercise context')).toBeVisible();
  const reference = screen.getByRole('link', {
    name: /NASA research: Risk from Inadequate Sleep and Irregular Schedules/,
  });
  expect(reference).toHaveAttribute(
    'href',
    'https://www.nasa.gov/reference/risk-from-inadequate-sleep-and-irregular-schedules/',
  );
  expect(screen.getByText(/not scheduled reminders or/)).toBeVisible();
  await user.click(screen.getByRole('button', { name: /Document a fictional review/ }));
  expect(screen.getByLabelText('Fictional review state')).toHaveValue('PENDING_REVIEW');
});

it('shows comparison withheld for quality-blocked mission and never invents trends', async () => {
  const user = userEvent.setup();
  render(<App />);
  await screen.findByRole('heading', { name: 'Mission overview' });
  await user.selectOptions(screen.getByLabelText('Demo scenario'), 'incomplete');
  await screen.findByText('Data quality blocks interpretation.');
  await user.click(screen.getByRole('tab', { name: 'ARES Copilot' }));
  await screen.findByText('Mission Wellness & Procedures');
  await user.click(screen.getByText('Mission Wellness & Procedures'));
  const withheld = await screen.findAllByText('Comparison withheld');
  expect(withheld).toHaveLength(3);
  expect(screen.getAllByText(/no trend can be inferred/i)).toHaveLength(3);
});
