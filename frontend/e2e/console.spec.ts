import { expect, test } from '@playwright/test';
import path from 'node:path';
const screenshots = path.resolve('screenshots/issue-17-regression');
async function loaded(page: import('@playwright/test').Page) {
  await page.goto('/');
  await expect(page.getByRole('heading', { name: 'Mission overview' })).toBeVisible();
  await expect(page.locator('.body-frame img')).toHaveJSProperty('complete', true);
}
test('real one-server mission workflow and desktop capture', async ({ page }) => {
  const errors: string[] = [];
  page.on('pageerror', (error) => errors.push(error.message));
  await page.setViewportSize({ width: 1440, height: 900 });
  await loaded(page);
  await expect(page.locator('.command-grid')).toBeInViewport();
  await expect(page.getByRole('tab', { name: 'Check-in', exact: true })).toBeInViewport();
  await expect(page.getByTestId('latest-resting_hr_bpm')).not.toContainText('—');
  expect(await page.evaluate(() => document.documentElement.scrollWidth <= innerWidth)).toBe(true);
  await page.screenshot({
    path: path.join(screenshots, 'mission-v15-desktop.png'),
    fullPage: true,
  });
  await page.getByRole('button', { name: 'Explore Sleep / neurobehavioral: Sleep' }).click();
  await expect(page.getByRole('heading', { name: 'Sleep duration', exact: true })).toBeVisible();
  await page.getByLabel('Demo scenario').selectOption('heart_rate_shift');
  await expect(page.locator('.assessment-chip')).toContainText('CHANGE_FOR_REVIEW');
  await page.getByRole('button', { name: /^Resting heart rate/ }).click();
  await expect(page.locator('.finding')).toContainText('Resting heart rate: recent');
  await page.screenshot({ path: path.join(screenshots, 'mission-v15-change.png'), fullPage: true });
  await page.getByLabel('Demo scenario').selectOption('incomplete');
  await expect(page.locator('.assessment-chip')).toContainText('DATA_QUALITY_BLOCKED');
  await expect(page.locator('.finding')).toContainText('INTERPRETATION WITHHELD');
  await expect(page.locator('.comparison-grid')).toHaveCount(0);
  await page.getByRole('button', { name: 'Inspect quality events' }).click();
  await expect(page.getByRole('tabpanel')).toContainText('data_quality');
  await page.screenshot({
    path: path.join(screenshots, 'mission-v15-blocked.png'),
    fullPage: true,
  });
  await page.getByLabel('Demo scenario').selectOption('stable');
  await expect(page.locator('.assessment-chip')).toContainText('NO_DEMO_RULE_TRIGGERED');
  await page.getByRole('tab', { name: 'Check-in', exact: true }).click();
  await page.getByLabel('Fictional resting heart rate', { exact: true }).fill('140');
  await page.getByLabel('Fictional sleep duration', { exact: true }).fill('7');
  await page.getByLabel('Fictional activity minutes', { exact: true }).fill('45');
  await page.getByRole('checkbox', { name: /I confirm this check-in/ }).check();
  await page.getByRole('button', { name: 'Analyze fictional check-in' }).click();
  await expect(page.getByTestId('latest-resting_hr_bpm')).toContainText('140');
  await expect(page.getByTestId('latest-sleep_hours')).toContainText('7');
  await expect(page.getByTestId('latest-activity_minutes')).toContainText('45');
  await expect(page.locator('.console-footer')).toContainText('Attested fictional crew check-in');
  await page.getByRole('tab', { name: 'Mission Timeline' }).click();
  await expect(page.getByRole('tabpanel')).toContainText('event-000001');
  await page.getByRole('tab', { name: 'Review & Export' }).click();
  await page.getByRole('checkbox', { name: /I confirm these review actions/ }).check();
  await page.getByRole('button', { name: 'Build comprehensive JSON report' }).click();
  const download = page.waitForEvent('download');
  await page.getByRole('button', { name: 'Download comprehensive JSON' }).click();
  const reportFile = await (await download).path();
  const fs = await import('node:fs/promises');
  const report = JSON.parse(await fs.readFile(reportFile!, 'utf8'));
  expect(report.scenario).toContain('fictional_checkin');
  await page.getByRole('tab', { name: 'Check-in', exact: true }).click();
  await page.getByLabel('Synthetic CSV file').setInputFiles('public/synthetic-template.csv');
  await page.getByRole('checkbox', { name: /I attest/ }).check();
  await page.getByRole('button', { name: 'Upload synthetic CSV' }).click();
  await expect(page.locator('.console-footer')).toContainText('Uploaded synthetic CSV');
  await page.getByRole('tab', { name: 'Mission Timeline' }).click();
  await expect(page.getByRole('tabpanel')).toContainText('event-000001');
  await page.getByRole('tab', { name: 'Spaceflight Risks' }).click();
  await page.getByRole('button', { name: 'Space radiation', exact: true }).click();
  await expect(page.getByRole('tabpanel')).toContainText('NASA');
  await page.getByRole('button', { name: 'Optional research lab' }).click();
  await expect(page.getByRole('heading', { name: /Biomedical Research Lab/ })).toBeVisible();
  await page.getByRole('button', { name: 'NASA space biology' }).click();
  await expect(page.getByRole('heading', { name: /NASA|OSDR/ }).first()).toBeVisible();
  await page.getByRole('button', { name: 'Synthetic mission demo' }).click();
  expect(errors).toEqual([]);
});
test('mobile composition, keyboard navigation and real capture', async ({ page }) => {
  await page.setViewportSize({ width: 390, height: 844 });
  await loaded(page);
  expect(await page.evaluate(() => document.documentElement.scrollWidth <= innerWidth)).toBe(true);
  await page.screenshot({
    path: path.join(screenshots, 'mission-v15-mobile.png'),
    fullPage: false,
  });
  await page.screenshot({
    path: path.join(screenshots, 'mission-v15-mobile-full.png'),
    fullPage: true,
  });
  await page.getByRole('tab', { name: 'Check-in', exact: true }).focus();
  await page.keyboard.press('ArrowRight');
  await expect(page.getByRole('tab', { name: 'Mission Timeline' })).toBeFocused();
  await expect(page.getByRole('tabpanel')).toContainText('Mission timeline');
  await page.getByRole('button', { name: 'Other body regions: not monitored' }).click();
  await expect(page.locator('.body-context')).toContainText('NOT MONITORED');
});

test('API failure recovery and late request cancellation in the browser', async ({ page }) => {
  let fail = true;
  await page.route('**/api/scenarios', async (route) => {
    if (fail) {
      fail = false;
      await route.fulfill({
        status: 503,
        contentType: 'application/json',
        body: JSON.stringify({ detail: 'Catalog temporarily unavailable' }),
      });
    } else await route.continue();
  });
  await page.goto('/');
  await expect(page.getByRole('alert')).toContainText('Catalog temporarily unavailable');
  await page.getByRole('button', { name: 'Retry API connection' }).click();
  await expect(page.getByRole('heading', { name: 'Mission overview' })).toBeVisible();
  let release: () => void = () => {};
  const wait = new Promise<void>((resolve) => {
    release = resolve;
  });
  await page.route('**/api/demo?scenario=heart_rate_shift&**', async (route) => {
    await wait;
    try {
      await route.continue();
    } catch {
      /* aborted request */
    }
  });
  await page.getByLabel('Demo scenario').selectOption('heart_rate_shift');
  await expect(page.getByText('Loading mission data…')).toBeVisible();
  await page.getByLabel('Demo scenario').selectOption('sleep_shift');
  await expect(page.getByRole('heading', { name: 'Mission overview' })).toBeVisible();
  release();
  await expect(page.getByLabel('Demo scenario')).toHaveValue('sleep_shift');
  const expected = await (
    await page.request.get('/api/demo?scenario=sleep_shift&seed=2026&days=21')
  ).json();
  await expect(page.getByTestId('latest-sleep_hours')).toContainText(
    String(expected.observations.at(-1).sleep_hours),
  );
});

test('WCAG AA automated check on desktop console', async ({ page }) => {
  await page.setViewportSize({ width: 1440, height: 900 });
  await loaded(page);
  const AxeBuilder = (await import('@axe-core/playwright')).default;
  const result = await new AxeBuilder({ page })
    .withTags(['wcag2a', 'wcag2aa', 'wcag21a', 'wcag21aa'])
    .analyze();
  expect(result.violations).toEqual([]);
  await expect(page.locator('.copilot-launch')).toContainText('briefing ready');
  for (const name of ['ARES Copilot', 'Review & Export']) {
    await page.getByRole('tab', { name, exact: true }).click();
    const audited = await new AxeBuilder({ page })
      .withTags(['wcag2a', 'wcag2aa', 'wcag21a', 'wcag21aa'])
      .analyze();
    expect(audited.violations).toEqual([]);
  }
});
