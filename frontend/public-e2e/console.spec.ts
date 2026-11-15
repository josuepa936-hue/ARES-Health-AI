import { expect, test } from '@playwright/test';

for (const width of [1440, 390]) {
  test(`public mission, check-in, Wellness and report at ${width}px`, async ({ page }) => {
    const errors: string[] = [];
    const violations: string[] = [];
    page.on('pageerror', (error) => errors.push(error.message));
    page.on('console', (message) => {
      if (message.type() === 'error' && /Content Security Policy/i.test(message.text()))
        violations.push(message.text());
    });
    await page.setViewportSize({ width, height: width === 390 ? 844 : 1000 });
    await page.goto('/');
    await expect(page.getByRole('note')).toContainText(
      'Not a medical device or a NASA-authorized system',
    );
    await expect(page.getByRole('heading', { name: 'Mission overview' })).toBeVisible();
    await expect(page.getByRole('button', { name: 'Optional research lab' })).toHaveCount(0);
    await expect(page.getByLabel('Synthetic CSV file')).toHaveCount(0);
    await expect(page.locator('.assessment-chip')).toContainText('NO_DEMO_RULE_TRIGGERED');
    await page.getByLabel('Demo scenario').selectOption('heart_rate_shift');
    await expect(page.locator('.assessment-chip')).toContainText('CHANGE_FOR_REVIEW');
    await page.getByRole('tab', { name: 'Check-in', exact: true }).click();
    await page.getByLabel('Fictional resting heart rate', { exact: true }).fill('140');
    await page.getByLabel('Fictional sleep duration', { exact: true }).fill('7');
    await page.getByLabel('Fictional activity minutes', { exact: true }).fill('45');
    await page.getByRole('checkbox', { name: /I confirm this check-in/ }).check();
    await page.getByRole('button', { name: 'Analyze fictional check-in' }).click();
    await expect(page.getByTestId('latest-resting_hr_bpm')).toContainText('140');
    await page.getByRole('tab', { name: 'Mission Timeline', exact: true }).click();
    await expect(page.getByRole('tabpanel')).toContainText('event-000001');
    await page.getByRole('tab', { name: 'ARES Copilot', exact: true }).click();
    await expect(page.locator('.copilot-launch')).toContainText('briefing ready');
    await page.locator('.copilot-suggestions > summary').click();
    await page.getByRole('button', { name: 'What changed?', exact: true }).click();
    await expect(page.getByRole('log')).toContainText('reference');
    await page.getByText('Mission Wellness & Procedures', { exact: true }).click();
    const wellness = page.getByLabel('Mission Wellness and Procedures');
    await expect(wellness.getByText('Sleep and schedule', { exact: true })).toBeVisible();
    await expect(
      wellness.getByRole('link', { name: /NASA research: Risk from Inadequate Sleep/ }),
    ).toBeVisible();
    await page.getByRole('tab', { name: 'Review & Export', exact: true }).click();
    await page.getByLabel('Fictional review state').selectOption('DOCUMENTED');
    await page.getByRole('checkbox', { name: /I confirm these review actions/ }).check();
    await page.getByRole('button', { name: 'Build comprehensive JSON report' }).click();
    const downloaded = page.waitForEvent('download');
    await page.getByRole('button', { name: 'Download comprehensive JSON' }).click();
    const fs = await import('node:fs/promises');
    const report = JSON.parse(await fs.readFile((await (await downloaded).path())!, 'utf8'));
    expect(report.fictional_review.clinical_authorization).toBe(false);
    expect(report.fictional_review.review_state).toBe('DOCUMENTED');
    expect(report.evaluated_observations).toHaveLength(21);
    await page.getByLabel('Demo scenario').selectOption('incomplete');
    await expect(page.locator('.assessment-chip')).toContainText('DATA_QUALITY_BLOCKED');
    await page.getByRole('tab', { name: 'ARES Copilot', exact: true }).click();
    await expect(page.locator('.copilot-briefing')).toContainText(
      'Trend interpretation is withheld',
    );
    if (!(await wellness.evaluate((element) => (element as HTMLDetailsElement).open)))
      await wellness.locator('summary').click();
    await expect(wellness.getByText('Comparison withheld', { exact: true })).toHaveCount(3);
    await expect(wellness.getByText('Comparison withheld', { exact: true }).first()).toBeVisible();
    expect(await page.evaluate(() => document.documentElement.scrollWidth <= innerWidth)).toBe(
      true,
    );
    await page.screenshot({ path: `test-results/public/mission-${width}.png`, fullPage: true });
    expect(errors).toEqual([]);
    expect(violations).toEqual([]);
  });
}

test('public errors and private paths do not expose data', async ({ request }) => {
  for (const path of [
    '/docs',
    '/openapi.json',
    '/.env',
    '/.git/config',
    '/src/ares_health/api.py',
    '/api/research/nasa/study',
    '/synthetic-template.csv',
  ])
    expect((await request.get(path)).status()).toBe(404);
  const error = await request.post('/api/mission/fictional-check-in', {
    data: { private: 'DO_NOT_ECHO' },
  });
  expect(error.status()).toBe(422);
  expect(await error.text()).not.toContain('DO_NOT_ECHO');
});

test('evaluators can enter through a link on another site', async ({ page, baseURL }) => {
  // A fulfilled local page provides a different site, without external accounts
  // or network dependency. The actual navigation targets the running service.
  const project = 'http://localhost:18080/project-link';
  await page.route(project, (route) =>
    route.fulfill({
      contentType: 'text/html',
      body: `<a href="${baseURL}/">Open the synthetic ARES demo</a>`,
    }),
  );
  await page.goto(project);
  await page.getByRole('link', { name: 'Open the synthetic ARES demo' }).click();
  await expect(page.getByRole('heading', { name: 'Mission overview' })).toBeVisible();
  await expect(page.getByRole('note')).toContainText('Experimental public demo');
});
