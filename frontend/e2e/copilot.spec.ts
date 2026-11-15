import { expect, test } from '@playwright/test';
import path from 'node:path';
const captures = path.resolve('screenshots');
test('offline copilot questions, manual four-state audit and canonical integrated export', async ({
  page,
}) => {
  const remoteRequests: string[] = [];
  page.on('request', (request) => {
    if (request.url().startsWith('https://')) remoteRequests.push(request.url());
  });
  await page.route('https://**/*', (route) => route.abort());
  await page.setViewportSize({ width: 1440, height: 900 });
  await page.goto('/');
  await expect(page.getByRole('heading', { name: 'Mission overview' })).toBeVisible();
  await page.getByRole('tab', { name: 'ARES Copilot', exact: true }).click();
  await expect(page.getByRole('region', { name: 'ARES mission copilot' })).toContainText(
    'not medical clearance',
  );
  await expect(page.locator('.copilot-launch')).toContainText('briefing ready');
  await page.screenshot({ path: path.join(captures, 'copilot-v15-desktop.png'), fullPage: true });
  await page.getByRole('button', { name: 'What changed?', exact: true }).click();
  await expect(page.getByRole('log')).toContainText('reference');
  await page.getByRole('tab', { name: 'Review & Export' }).click();
  await page.getByLabel('Fictional review state').selectOption('DOCUMENTED');
  await page.getByLabel('Demo scenario').selectOption('heart_rate_shift');
  await expect(page.locator('.assessment-chip')).toContainText('CHANGE_FOR_REVIEW');
  await expect(page.getByLabel('Fictional review state')).toHaveValue('PENDING_REVIEW');
  await page.getByRole('tab', { name: 'ARES Copilot', exact: true }).click();
  await expect(page.getByRole('log')).toBeEmpty();
  await page.getByRole('button', { name: 'What changed?', exact: true }).click();
  await expect(page.getByRole('log')).toContainText('difference');
  const log = page.getByRole('log');
  await log.getByText(/Why this response/).click();
  await expect(log).toContainText('rule:resting_hr_bpm:mean_difference');
  await expect(log).toContainText('Timeline:');
  await page.getByLabel('Fictional mission question').fill('Give a treatment');
  await page.getByRole('button', { name: 'Ask', exact: true }).click();
  await expect(log).toContainText('I cannot provide diagnosis');
  const assessment = await page.locator('.assessment-chip strong').innerText();
  await page.getByRole('tab', { name: 'Review & Export' }).click();
  for (const state of ['IN_PROGRESS', 'AWAITING_AUTHORIZED_REVIEW', 'DOCUMENTED']) {
    await page.getByLabel('Fictional review state').selectOption(state);
    await expect(page.locator('.assessment-chip strong')).toHaveText(assessment);
  }
  await page.getByRole('checkbox', { name: /Inspected fictional source/ }).check();
  await page.getByRole('checkbox', { name: /Verified UTC/ }).check();
  await page
    .getByLabel('Fictional review note')
    .fill('Fictional engineering review. No clinical authorization.');
  await page.getByRole('button', { name: 'Record fictional note' }).click();
  await page.getByRole('checkbox', { name: /I confirm these review actions/ }).check();
  await page.getByRole('button', { name: 'Build comprehensive JSON report' }).click();
  await expect(page.getByRole('button', { name: 'Download comprehensive JSON' })).toBeEnabled();
  await page.screenshot({ path: path.join(captures, 'copilot-v15-review.png'), fullPage: true });
  const downloaded = page.waitForEvent('download');
  await page.getByRole('button', { name: 'Download comprehensive JSON' }).click();
  await page.screenshot({path:path.join(captures,'copilot-v15-export.png'),fullPage:true});
  const fs = await import('node:fs/promises');
  const report = JSON.parse(await fs.readFile((await (await downloaded).path())!, 'utf8'));
  expect(report.assessment).toBe(assessment);
  expect(report.fictional_review.review_state).toBe('DOCUMENTED');
  expect(report.fictional_review.clinical_authorization).toBe(false);
  expect(report.fictional_review.audit_log).toHaveLength(6);
  expect(report.copilot.omitted_unsupported_or_unsafe_turns).toBe(1);
  expect(report.copilot.transcript).toHaveLength(1);
  expect(report.evaluated_observations).toHaveLength(21);
  expect(report.copilot.transcript[0].response.context_ref).toBe(report.context_ref);
  expect(report.mission_timeline.events.length).toBeGreaterThan(21);
  expect(report.risk_context.risks).toHaveLength(5);
  await page.getByLabel('Demo scenario').selectOption('incomplete');
  await expect(page.locator('.assessment-chip')).toContainText('DATA_QUALITY_BLOCKED');
  await page.getByRole('tab', { name: 'ARES Copilot', exact: true }).click();
  await expect(page.locator('.copilot-briefing')).toContainText('Trend interpretation is withheld');
  await page.screenshot({ path: path.join(captures, 'copilot-v15-blocked.png'), fullPage: true });
  expect(remoteRequests).toEqual([]);
});
test('mobile copilot remains functional and review is reset on page reload', async ({ page }) => {
  await page.setViewportSize({ width: 390, height: 844 });
  await page.goto('/');
  await expect(page.getByRole('heading', { name: 'Mission overview' })).toBeVisible();
  await page.getByRole('tab', { name: 'ARES Copilot', exact: true }).click();
  await expect(page.locator('.copilot-briefing')).toContainText('No demonstration rule triggered');
  await page.getByRole('button', { name: 'What is still not monitored?', exact: true }).click();
  await expect(page.getByRole('log')).toContainText('not monitored');
  expect(await page.evaluate(() => document.documentElement.scrollWidth <= innerWidth)).toBe(true);
  await page.screenshot({
    path: path.join(captures, 'copilot-v15-mobile-full.png'),
    fullPage: true,
  });
  await page.locator('.context-dock').scrollIntoViewIfNeeded();
  await page.screenshot({ path: path.join(captures, 'copilot-v15-mobile.png') });
  await page.getByRole('tab', { name: 'Review & Export' }).click();
  await page.getByLabel('Fictional review state').selectOption('IN_PROGRESS');
  await page.reload();
  await expect(page.getByRole('heading', { name: 'Mission overview' })).toBeVisible();
  await page.getByRole('tab', { name: 'Review & Export' }).click();
  await expect(page.getByLabel('Fictional review state')).toHaveValue('PENDING_REVIEW');
  await expect(page.getByText('Pending review. No action has been confirmed.')).toBeVisible();
});
