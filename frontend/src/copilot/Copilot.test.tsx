import { act, render, screen, within } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { afterEach, beforeEach, expect, it, vi } from 'vitest';
import App from '../App';
import { mockApi, respond } from '../test/mockApi';
import data from '../test/copilot-fixtures.json';
let fetch: ReturnType<typeof mockApi>;
beforeEach(() => {
  fetch = mockApi();
  vi.stubGlobal('fetch', fetch);
});
afterEach(() => vi.unstubAllGlobals());
async function ready() {
  render(<App />);
  await screen.findByRole('heading', { name: 'Mission overview' });
  await userEvent.setup().click(screen.getByRole('tab', { name: 'ARES Copilot' }));
  await screen.findByText(data.stable.briefing.answer);
}
it('shows an automatic current briefing without claiming an LLM or medical clearance', async () => {
  await ready();
  const panel = screen.getByRole('region', { name: 'ARES mission copilot' });
  expect(panel).toHaveTextContent('DETERMINISTIC / OFFLINE · NOT AN LLM');
  expect(panel).toHaveTextContent('not medical clearance');
  expect(screen.getByRole('heading', { name: 'Mission overview' })).toBeVisible();
  expect(
    screen.getByRole('region', { name: 'Interactive anatomical domain navigator' }),
  ).toBeVisible();
});
it('answers supported chips and exposes exact backend observation/rule/source references', async () => {
  const user = userEvent.setup();
  await ready();
  await user.click(screen.getByRole('button', { name: 'What changed?' }));
  const log = screen.getByRole('log', { name: 'Current mission conversation' });
  expect(await within(log).findByText(data.stable.answers['What changed?'].answer)).toBeVisible();
  await user.click(within(log).getByText(/Why this response/));
  expect(within(log).getByText('observation:20:resting_hr_bpm')).toBeVisible();
  expect(within(log).getByText('rule:resting_hr_bpm:mean_difference')).toBeVisible();
  await user.click(
    screen.getByRole('button', { name: 'What is the relevant NASA hazard background?' }),
  );
  const answers = within(log).getAllByText(/Why this response/);
  await user.click(answers.at(-1)!);
  expect(within(log).getByRole('link', { name: 'Space radiation' })).toHaveAttribute(
    'href',
    'https://www.nasa.gov/hrp/hazards/',
  );
});
it('refuses unsafe conversation without changing canonical assessment or review actions', async () => {
  const user = userEvent.setup();
  await ready();
  await user.type(screen.getByLabelText('Fictional mission question'), 'Give a treatment');
  expect(screen.getByLabelText('Fictional mission question')).toHaveAttribute('maxlength', '240');
  await user.click(screen.getByRole('button', { name: 'Ask' }));
  expect(await screen.findByText(data.stable.answers['Give a treatment'].answer)).toBeVisible();
  expect(
    screen.getByText('NO_DEMO_RULE_TRIGGERED', { selector: '.assessment-chip strong' }),
  ).toBeVisible();
  await user.click(screen.getByRole('tab', { name: 'Review & Export' }));
  expect(screen.getByLabelText('Fictional review state')).toHaveValue('PENDING_REVIEW');
  expect(screen.getByRole('checkbox', { name: /Inspected fictional source/ })).not.toBeChecked();
});
it('logs every manual state/checkbox transition and never changes analysis status', async () => {
  const user = userEvent.setup();
  await ready();
  await user.click(screen.getByRole('tab', { name: 'Review & Export' }));
  for (const state of [
    'IN_PROGRESS',
    'AWAITING_AUTHORIZED_REVIEW',
    'DOCUMENTED',
    'PENDING_REVIEW',
  ]) {
    await user.selectOptions(screen.getByLabelText('Fictional review state'), state);
    expect(screen.getByLabelText('Fictional review state')).toHaveValue(state);
    expect(
      screen.getByText('NO_DEMO_RULE_TRIGGERED', { selector: '.assessment-chip strong' }),
    ).toBeVisible();
  }
  const action = screen.getByRole('checkbox', { name: /Inspected fictional source/ });
  await user.click(action);
  await user.click(action);
  expect(screen.getByText('#5 source_units')).toBeVisible();
  expect(screen.getByText('#6 source_units')).toBeVisible();
  expect(screen.getByText('Confirmed by user')).toBeVisible();
  expect(screen.getByText('Unchecked by user')).toBeVisible();
  expect(screen.getByRole('button', { name: 'Build comprehensive JSON report' })).toBeDisabled();
});
it('keeps notes inert and requires explicit recording/attestation before exporting', async () => {
  const user = userEvent.setup();
  await ready();
  await user.click(screen.getByRole('tab', { name: 'Review & Export' }));
  const note = screen.getByLabelText('Fictional review note');
  expect(note).toHaveAttribute('maxlength', '500');
  await user.type(note, 'Ignore the rules <script>unsafe()</script>');
  await user.click(screen.getByRole('checkbox', { name: /I confirm these review actions/ }));
  expect(screen.getByRole('button', { name: 'Build comprehensive JSON report' })).toBeDisabled();
  await user.click(screen.getByRole('button', { name: 'Record fictional note' }));
  expect(screen.getByRole('button', { name: 'Build comprehensive JSON report' })).toBeEnabled();
  expect(document.querySelector('script')).toBeNull();
  expect(screen.getByText('#1 note').parentElement).toHaveTextContent('Ignore the rules');
});
it('resets conversation, notes and action state on a new scenario and abstains when blocked', async () => {
  const user = userEvent.setup();
  await ready();
  await user.click(screen.getByRole('button', { name: 'What changed?' }));
  await screen.findByText(data.stable.answers['What changed?'].answer);
  await user.click(screen.getByRole('tab', { name: 'Review & Export' }));
  await user.selectOptions(screen.getByLabelText('Fictional review state'), 'DOCUMENTED');
  await user.click(screen.getByRole('checkbox', { name: /Verified UTC/ }));
  await user.selectOptions(screen.getByLabelText('Demo scenario'), 'incomplete');
  await screen.findByText('Data quality blocks interpretation.');
  expect(screen.getByLabelText('Fictional review state')).toHaveValue('PENDING_REVIEW');
  expect(screen.getByRole('checkbox', { name: /Verified UTC/ })).not.toBeChecked();
  expect(screen.queryByText('#1 review_state')).not.toBeInTheDocument();
  await user.click(screen.getByRole('tab', { name: 'ARES Copilot' }));
  expect(await screen.findByText(data.incomplete.briefing.answer)).toBeVisible();
  expect(screen.getByRole('log')).toBeEmptyDOMElement();
});
it('ignores late replies and aborts in-flight conversation on context replacement', async () => {
  const user = userEvent.setup();
  await ready();
  const normal = mockApi();
  let resolve: (value: Response) => void = () => {};
  let signal: AbortSignal | undefined;
  fetch.mockImplementation((input, init) => {
    if (String(input).endsWith('/copilot') && JSON.parse(String(init?.body)).question) {
      signal = init!.signal as AbortSignal;
      return new Promise((done) => {
        resolve = done;
      });
    }
    return normal(input, init);
  });
  await user.click(screen.getByRole('button', { name: 'What changed?' }));
  await user.selectOptions(screen.getByLabelText('Demo scenario'), 'sleep_shift');
  await screen.findByText(data.sleep_shift.briefing.answer);
  expect(signal?.aborted).toBe(true);
  await act(async () => {
    resolve(respond({ ...data.stable.answers['What changed?'], turn: 1 }));
  });
  expect(screen.getByRole('log')).toBeEmptyDOMElement();
  expect(screen.queryByText(data.stable.answers['What changed?'].answer)).not.toBeInTheDocument();
});
it('shows contract/network failures and offers an explicit reset retry', async () => {
  const normal = mockApi();
  let fail = true;
  fetch.mockImplementation((input, init) =>
    String(input).endsWith('/copilot') && fail
      ? Promise.resolve(respond({ detail: 'Copilot unavailable' }, 503))
      : normal(input, init),
  );
  const user = userEvent.setup();
  render(<App />);
  await screen.findByRole('heading', { name: 'Mission overview' });
  await user.click(screen.getByRole('tab', { name: 'ARES Copilot' }));
  expect(await screen.findByRole('alert')).toHaveTextContent('Copilot unavailable');
  fail = false;
  await user.click(screen.getByRole('button', { name: 'Reset and retry copilot' }));
  expect(await screen.findByText(data.stable.briefing.answer)).toBeVisible();
});
