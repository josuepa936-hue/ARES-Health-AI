import { expect, test, type Page } from '@playwright/test';
import path from 'node:path';

// Geometry is tested with actual compiled React + FastAPI, not jsdom estimates.
async function cockpitGeometry(page: Page, mobile: boolean) {
  await page.evaluate(() => scrollTo(0, 0));
  const cards = page.locator('.telemetry-card');
  await expect(cards).toHaveCount(3);
  for (const card of await cards.all()) {
    await expect(card).toBeInViewport({ ratio: 0.95 });
    const measurements = await card.evaluate((element) => {
      const bounds = element.getBoundingClientRect();
      const rows = [
        '.telemetry-title',
        '.telemetry-value',
        '.mini-chart',
        '.telemetry-foot',
        '.last-valid',
      ].map((selector) => element.querySelector(selector)!.getBoundingClientRect());
      return {
        height: bounds.height,
        contained: rows.every(
          (row) =>
            row.top >= bounds.top &&
            row.bottom <= bounds.bottom + 1 &&
            row.right <= bounds.right + 1,
        ),
        separated: rows.every((row, index) => index === 0 || rows[index - 1].bottom <= row.top + 1),
      };
    });
    expect(measurements.height).toBeGreaterThanOrEqual(mobile ? 200 : 156);
    expect(measurements.contained).toBe(true);
    expect(measurements.separated).toBe(true);
    await expect(card.locator('.mini-chart')).toBeVisible();
    await expect(card.locator('.last-valid')).toContainText('UTC');
  }
  const image = page.locator('.body-frame img');
  if (mobile) await image.scrollIntoViewIfNeeded();
  await expect(image).toHaveJSProperty('complete', true);
  await expect(image).toBeInViewport({ ratio: 0.95 });
  expect((await image.boundingBox())!.height).toBeGreaterThanOrEqual(300);
  const chart = page.locator('.primary-chart');
  if (mobile) await chart.scrollIntoViewIfNeeded();
  await expect(chart).toBeInViewport({ ratio: 0.95 });
  expect((await chart.boundingBox())!.height).toBeGreaterThanOrEqual(170);
  await expect(chart.locator('.recharts-xAxis-tick-labels text').first()).toBeInViewport();
  await expect(chart.locator('.recharts-yAxis-tick-labels text').first()).toBeInViewport();
  const command = (await page.locator('.command-grid').boundingBox())!;
  const dock = (await page.locator('.context-dock').boundingBox())!;
  expect(command.y + command.height).toBeLessThanOrEqual(dock.y);
  expect(await page.evaluate(() => document.documentElement.scrollWidth <= innerWidth)).toBe(true);
  // Docked reading is document flow, not a nested vertical scroller.
  for (const selector of ['.context-dock', '#panel-copilot', '.copilot-dialog', '.copilot-history'])
    await expect(page.locator(selector)).toHaveCSS('overflow-y', 'visible');
}

for (const [width, height] of [
  [1920, 820],
  [1440, 900],
  [1366, 768],
  [390, 844],
]) {
  test(`Issue 19 full cockpit and readable conversation at ${width}x${height}`, async ({
    page,
  }) => {
    const errors: string[] = [];
    const requests: string[] = [];
    page.on('pageerror', (error) => errors.push(error.message));
    page.on('request', (request) => {
      if (request.url().includes('/api/')) requests.push(request.url());
    });
    await page.setViewportSize({ width, height });
    await page.goto('/');
    await expect(page.getByRole('heading', { name: 'Mission overview' })).toBeVisible();
    await expect(page.locator('.copilot-launch')).toContainText('briefing ready');
    await page.getByRole('tab', { name: 'ARES Copilot', exact: true }).click();
    await expect(page.locator('.copilot-assessment')).toContainText('NO_DEMO_RULE_TRIGGERED');
    await cockpitGeometry(page, width < 761);
    await page.evaluate(() => scrollTo(0, 0));
    await page.screenshot({ path: path.resolve(`screenshots/issue-19-after-${width}.png`) });

    const canonical = await (
      await page.request.get('/api/demo?scenario=stable&seed=2026&days=21')
    ).json();
    for (const metric of ['resting_hr_bpm', 'sleep_hours', 'activity_minutes'])
      await expect(page.getByTestId(`latest-${metric}`)).toContainText(
        String(canonical.observations.at(-1)[metric]),
      );
    await page.getByLabel('Fictional mission question').fill('What changed?');
    await page.getByRole('button', { name: 'Ask', exact: true }).click();
    const turn = page.getByTestId('copilot-turn-1');
    await expect(turn.getByRole('heading', { name: 'Conversation turn 1' })).toBeFocused();
    await expect(turn.locator('.copilot-answer h4')).toBeInViewport();
    const comparison = canonical.descriptive_signals.find(
      (item: { metric: string }) => item.metric === 'resting_hr_bpm',
    );
    await expect(turn.locator('.copilot-answer')).toContainText(comparison.delta.toFixed(3));
    await expect(turn.locator('.copilot-answer p')).toHaveCSS('font-size', '14px');
    await page.getByLabel('Fictional mission question').fill('What dates are used?');
    await page.screenshot({
      path: path.resolve(`screenshots/issue-19-conversation-${width}.png`),
      fullPage: true,
    });
    const requestCount = requests.length;
    const focus = page.getByRole('button', { name: 'Focus / expand conversation', exact: true });
    await focus.scrollIntoViewIfNeeded();
    const readingPosition = await page.evaluate(() => scrollY);
    await focus.click();
    const dialog = page.getByRole('dialog', { name: 'Expanded ARES Copilot conversation' });
    await expect(dialog).toContainText('cockpit is behind this dialog');
    await expect(turn.getByRole('heading', { name: 'Conversation turn 1' })).toBeInViewport();
    await page.screenshot({ path: path.resolve(`screenshots/issue-19-focus-${width}.png`) });
    await page.keyboard.press('Escape');
    await expect(focus).toBeFocused();
    expect(Math.abs((await page.evaluate(() => scrollY)) - readingPosition)).toBeLessThan(2);
    await expect(page.getByLabel('Fictional mission question')).toHaveValue('What dates are used?');
    await page.getByRole('button', { name: /Full cockpit/ }).click();
    await expect(page.locator('.console-app')).toHaveClass(/dock-closed/);
    await expect(page.locator('.copilot-launch')).toBeFocused();
    await expect(page.getByLabel('Demo scenario')).toHaveValue('stable');
    expect(await page.evaluate(() => scrollY)).toBe(0);
    await page.screenshot({ path: path.resolve(`screenshots/issue-19-full-cockpit-${width}.png`) });
    await page.locator('.copilot-launch').click();
    await expect(page.getByRole('tab', { name: 'ARES Copilot', exact: true })).toBeFocused();
    await expect(page.getByLabel('Fictional mission question')).toHaveValue('What dates are used?');
    await expect(turn).toContainText(comparison.delta.toFixed(3));
    expect(requests.length).toBe(requestCount);
    await cockpitGeometry(page, width < 761);

    // Check the previously unreviewed changed and blocked states with the same layout.
    for (const scenario of ['heart_rate_shift', 'incomplete']) {
      await page.getByLabel('Demo scenario').selectOption(scenario);
      const assessment = scenario === 'incomplete' ? 'DATA_QUALITY_BLOCKED' : 'CHANGE_FOR_REVIEW';
      await expect(page.locator('.copilot-assessment')).toContainText(assessment);
      await cockpitGeometry(page, width < 761);
      await page.getByLabel('Fictional mission question').fill('What changed?');
      await page.getByRole('button', { name: 'Ask', exact: true }).click();
      await expect(turn.getByRole('heading', { name: 'Conversation turn 1' })).toBeFocused();
      await focus.click();
      await expect(dialog).toBeVisible();
      await turn.getByTestId('response-evidence').locator('summary').first().click();
      if (scenario === 'incomplete') {
        await expect(turn).toContainText('Trend interpretation is withheld');
        await expect(turn).toContainText('No numerical averages');
        await expect(turn.locator('.evidence-comparisons')).toHaveCount(0);
      } else {
        const changed = await (
          await page.request.get('/api/demo?scenario=heart_rate_shift&seed=2026&days=21')
        ).json();
        const signal = changed.descriptive_signals.find(
          (item: { metric: string }) => item.metric === 'resting_hr_bpm',
        );
        await expect(turn.getByTestId('evidence-recent-resting_hr_bpm')).toHaveText(
          signal.recent_mean.toFixed(3),
        );
      }
      if (width === 1440 || width === 390)
        await page.screenshot({
          path: path.resolve(`screenshots/issue-19-${scenario}-${width}.png`),
        });
      await page.keyboard.press('Escape');
      await expect(page.getByLabel('Demo scenario')).toHaveValue(scenario);
    }
    expect(errors).toEqual([]);
  });
}
