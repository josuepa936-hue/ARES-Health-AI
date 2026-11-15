import { expect, test } from '@playwright/test';
import { readdirSync } from 'node:fs';

test.beforeAll(() => {
  expect(
    readdirSync('/sys/class/net'),
    'Run in the prepared Docker --network none harness',
  ).toEqual(['lo']);
});

for (const width of [1440, 390]) {
  test(`disconnected local mission and research recovery at ${width}px`, async ({
    page,
    context,
  }) => {
    const remoteAttempts: string[] = [];
    const pageErrors: string[] = [];
    const localResponses: number[] = [];
    // Defense in depth. Docker --network none also blocks backend/Chromium
    // traffic outside this browser routing hook; only loopback exists.
    await context.route('**/*', (route) => {
      const url = new URL(route.request().url());
      if (url.origin === 'http://127.0.0.1:8000') return route.continue();
      remoteAttempts.push(`${url.protocol}//${url.host}`);
      return route.abort('internetdisconnected');
    });
    page.on('pageerror', (error) => pageErrors.push(error.message));
    page.on('response', (response) => {
      if (response.url().includes('/api/')) localResponses.push(response.status());
    });
    await page.setViewportSize({ width, height: width === 390 ? 844 : 1000 });
    await page.goto('/');
    await expect(page.getByRole('heading', { name: 'Mission overview' })).toBeVisible();
    await expect(page.locator('.assessment-chip')).toContainText('NO_DEMO_RULE_TRIGGERED');
    expect(await page.locator('.recharts-surface').count()).toBeGreaterThan(0);
    await expect(page.locator('.body-frame img')).toHaveJSProperty('complete', true);
    await expect(page.getByRole('button', { name: 'Optional research lab' })).toBeVisible();
    for (const [scenario, assessment] of [
      ['heart_rate_shift', 'CHANGE_FOR_REVIEW'],
      ['incomplete', 'DATA_QUALITY_BLOCKED'],
      ['stable', 'NO_DEMO_RULE_TRIGGERED'],
    ]) {
      await page.getByLabel('Demo scenario').selectOption(scenario);
      await expect(page.locator('.assessment-chip')).toContainText(assessment);
    }
    await page.getByRole('tab', { name: 'Check-in', exact: true }).click();
    await page.getByLabel('Fictional resting heart rate', { exact: true }).fill('140');
    await page.getByLabel('Fictional sleep duration', { exact: true }).fill('7');
    await page.getByLabel('Fictional activity minutes', { exact: true }).fill('45');
    await page.getByRole('checkbox', { name: /I confirm this check-in/ }).check();
    await page.getByRole('button', { name: 'Analyze fictional check-in' }).click();
    await expect(page.getByTestId('latest-resting_hr_bpm')).toContainText('140');
    await expect(page.getByTestId('latest-sleep_hours')).toContainText('7');
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
    await page.screenshot({ path: `/results/mission-wellness-${width}.png`, fullPage: true });
    // Before optional research is opened, all essential HTTP calls succeeded,
    // and not even an attempted external CDN/font/AI/cloud request was needed.
    expect(remoteAttempts).toEqual([]);
    expect(localResponses.every((status) => status === 200)).toBe(true);
    await page.getByRole('tab', { name: 'Review & Export', exact: true }).click();
    await page.getByLabel('Fictional review state').selectOption('DOCUMENTED');
    await page.getByRole('checkbox', { name: /I confirm these review actions/ }).check();
    await page.getByRole('button', { name: 'Build comprehensive JSON report' }).click();
    const download = page.waitForEvent('download');
    await page.getByRole('button', { name: 'Download comprehensive JSON' }).click();
    const file = `/results/fictional-browser-report-${width}.json`;
    await (await download).saveAs(file);
    const fs = await import('node:fs/promises');
    const report = JSON.parse(await fs.readFile(file, 'utf8'));
    expect(report.evaluated_observations).toHaveLength(21);
    expect(report.fictional_review.review_state).toBe('DOCUMENTED');
    expect(report.fictional_review.clinical_authorization).toBe(false);
    await page.getByRole('button', { name: 'NASA space biology', exact: true }).click();
    await expect(page.getByRole('alert')).toContainText('No research results were substituted');
    await expect(page.getByRole('table')).toHaveCount(0);
    await page.getByRole('button', { name: 'Optional research lab', exact: true }).click();
    await expect(page.getByRole('alert')).toContainText(/missing|invalid|unavailable/i);
    await expect(
      page.getByRole('heading', { name: 'MIT-BIH record 100', exact: true }),
    ).toHaveCount(0);
    await page.getByRole('button', { name: 'Synthetic mission demo', exact: true }).click();
    await expect(page.getByTestId('latest-resting_hr_bpm')).toContainText('140');
    await expect(page.getByLabel('Fictional review state')).toHaveValue('DOCUMENTED');
    expect(await page.evaluate(() => document.documentElement.scrollWidth <= innerWidth)).toBe(
      true,
    );
    await page.screenshot({
      path: `/results/mission-research-recovery-${width}.png`,
      fullPage: true,
    });
    await page.reload();
    await expect(page.getByRole('heading', { name: 'Mission overview' })).toBeVisible();
    await expect(page.locator('.assessment-chip')).toContainText('NO_DEMO_RULE_TRIGGERED');
    expect(remoteAttempts).toEqual([]);
    expect(pageErrors).toEqual([]);
    await fs.writeFile(
      `/results/browser-network-${width}.json`,
      JSON.stringify(
        {
          remoteAttempts,
          pageErrors,
          coreLocalResponses: localResponses.filter((s) => s === 200).length,
          researchUnavailableResponses: localResponses.filter((s) => s === 503).length,
          width,
          browserReloadWorked: true,
        },
        null,
        2,
      ),
    );
  });
}
