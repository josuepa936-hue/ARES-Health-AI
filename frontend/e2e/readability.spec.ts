import { test, expect } from '@playwright/test';
import path from 'node:path';
import AxeBuilder from '@axe-core/playwright';
for (const [width, height] of [
  [1440, 900],
  [1366, 768],
  [390, 844],
]) {
  test(`Issue 17 readable focused answer and progressive evidence at ${width}x${height}`, async ({
    page,
  }) => {
    const errors: string[] = [];
    page.on('pageerror', (error) => errors.push(error.message));
    await page.emulateMedia({ reducedMotion: 'reduce' });
    await page.setViewportSize({ width, height });
    await page.goto('/');
    await expect(page.getByRole('heading', { name: 'Mission overview' })).toBeVisible();
    await page.getByLabel('Demo scenario').selectOption('heart_rate_shift');
    await expect(page.locator('.assessment-chip')).toContainText('CHANGE_FOR_REVIEW');
    await page.getByRole('tab', { name: 'ARES Copilot', exact: true }).click();
    await expect(page.locator('.copilot-launch')).toContainText('briefing ready');
    expect(await page.evaluate(() => document.documentElement.scrollWidth <= innerWidth)).toBe(
      true,
    );
    await page.getByLabel('Fictional mission question').fill('What changed?');
    await page.getByRole('button', { name: 'Ask', exact: true }).click();
    const compactTurn = page.getByTestId('copilot-turn-1');
    await expect(compactTurn.getByRole('heading', { name: 'Conversation turn 1' })).toBeFocused();
    await expect(compactTurn.locator('.copilot-question')).toBeInViewport();
    await expect(compactTurn.locator('.copilot-answer h4')).toBeInViewport();
    if (width > 760) {
      expect(
        await page.evaluate(() => document.documentElement.scrollHeight <= innerHeight + 1),
      ).toBe(true);
      expect(
        await page.locator('.copilot-history').evaluate((element) => element.clientHeight),
      ).toBeGreaterThanOrEqual(140);
      const panel = await page.locator('.metric-panel').boundingBox();
      const dock = await page.locator('.context-dock').boundingBox();
      expect(panel!.y + panel!.height).toBeLessThanOrEqual(dock!.y);
      await page.screenshot({ path: path.resolve(`screenshots/issue-17-docked-${width}.png`) });
    }
    await page.getByRole('button', { name: 'Focus / expand conversation', exact: true }).click();
    const dialog = page.getByRole('dialog', { name: 'Expanded ARES Copilot conversation' });
    await expect(dialog).toBeVisible();
    await expect(page.locator('body')).toHaveCSS('overflow', 'hidden');

    const turn = dialog.getByTestId('copilot-turn-1');
    const heading = turn.getByRole('heading', { name: 'Conversation turn 1' });
    await expect(heading).toBeFocused();
    await expect(heading).toBeInViewport();
    await expect(turn.locator('.copilot-question')).toBeInViewport();
    await expect(turn.locator('.copilot-answer h4')).toBeInViewport();
    await page.keyboard.press('Tab');
    expect(await dialog.evaluate((element) => element.contains(document.activeElement))).toBe(true);
    await expect(turn).toContainText('What changed?');
    const api = await (
      await page.request.get('/api/demo?scenario=heart_rate_shift&seed=2026&days=21')
    ).json();
    const expected = api.descriptive_signals.find(
      (signal: { metric: string }) => signal.metric === 'resting_hr_bpm',
    );
    await expect(turn.locator('.copilot-answer')).toContainText(expected.delta.toFixed(3));
    expect(
      await turn
        .locator('.copilot-answer p')
        .evaluate((element) => parseFloat(getComputedStyle(element).fontSize)),
    ).toBeGreaterThanOrEqual(14);
    expect(
      await turn
        .locator('.copilot-answer p')
        .evaluate((element) => element.scrollHeight <= element.clientHeight + 1),
    ).toBe(true);
    const evidence = turn.getByTestId('response-evidence');
    await evidence.locator('summary').first().scrollIntoViewIfNeeded();
    const reader = dialog.getByRole('region', { name: 'Conversation reading area' });
    const before = await reader.evaluate((element) => element.scrollTop);
    await evidence.locator('summary').first().click();
    await expect(turn.getByTestId('evidence-baseline-resting_hr_bpm')).toHaveText(
      expected.baseline_mean.toFixed(3),
    );
    await expect(turn.getByTestId('evidence-recent-resting_hr_bpm')).toHaveText(
      expected.recent_mean.toFixed(3),
    );
    await expect(turn.getByTestId('evidence-delta-resting_hr_bpm')).toHaveText(
      `+${expected.delta.toFixed(3)}`,
    );
    expect(Math.abs((await reader.evaluate((element) => element.scrollTop)) - before)).toBeLessThan(
      2,
    );
    await expect(evidence).toContainText('2026-11-01T00:00:00Z');
    await expect(evidence).toContainText('2026-11-21T00:00:00Z');
    // One scroll owner; individual evidence/prompts, the dock and dialog do not scroll.
    const owners = await dialog.evaluate((element) =>
      [element, ...element.querySelectorAll('*')]
        .filter((node) => {
          const style = getComputedStyle(node);
          return (
            ['auto', 'scroll'].includes(style.overflowY) &&
            node.scrollHeight > node.clientHeight + 1
          );
        })
        .map((node) => node.className),
    );
    expect(owners).toEqual(['copilot-history']);
    await reader.evaluate((element) => {
      const digest = element.querySelector('[data-testid="copilot-turn-1"] .evidence-digest')!;
      element.scrollTop =
        digest.getBoundingClientRect().top -
        element.getBoundingClientRect().top +
        element.scrollTop -
        12;
    });
    await page.screenshot({ path: path.resolve(`screenshots/issue-17-evidence-${width}.png`) });
    await reader.evaluate(
      (element) =>
        (element.scrollTop =
          element.querySelector('[data-testid="copilot-turn-1"]')!.getBoundingClientRect().top -
          element.getBoundingClientRect().top +
          element.scrollTop -
          12),
    );
    await expect(heading).toBeInViewport();
    await page.screenshot({ path: path.resolve(`screenshots/issue-17-after-${width}.png`) });
    if (width === 1440)
      expect(
        (
          await new AxeBuilder({ page })
            .withTags(['wcag2a', 'wcag2aa', 'wcag21a', 'wcag21aa'])
            .analyze()
        ).violations,
      ).toEqual([]);
    await evidence.getByText(/Detailed observations, UTC dates and timeline IDs/).click();
    await expect(evidence).toContainText('observation:20:resting_hr_bpm');
    await expect(evidence).toContainText('Timeline:');
    // Expanded old evidence must never make a new response start at its tail.
    await dialog
      .getByLabel('Fictional mission question')
      .fill('What is the relevant NASA hazard background?');
    await dialog.getByRole('button', { name: 'Ask', exact: true }).click();
    const next = dialog.getByTestId('copilot-turn-2');
    await expect(next.getByRole('heading', { name: 'Conversation turn 2' })).toBeFocused();
    await expect(next.getByRole('heading', { name: 'Conversation turn 2' })).toBeInViewport();
    await next.getByTestId('response-evidence').locator('summary').first().click();
    await expect(next.getByRole('link', { name: 'Space radiation' })).toHaveAttribute(
      'href',
      'https://www.nasa.gov/hrp/hazards/',
    );
    await page.keyboard.press('Escape');
    await expect(
      page.getByRole('button', { name: 'Focus / expand conversation', exact: true }),
    ).toBeFocused();
    await expect(page.getByRole('heading', { name: 'Mission overview' })).toBeVisible();
    await page.getByLabel('Demo scenario').selectOption('incomplete');
    await expect(page.locator('.assessment-chip')).toContainText('DATA_QUALITY_BLOCKED');
    await page.getByRole('button', { name: 'Focus / expand conversation', exact: true }).click();
    await dialog.getByLabel('Fictional mission question').fill('What changed?');
    await dialog.getByRole('button', { name: 'Ask', exact: true }).click();
    const blocked = dialog.getByTestId('copilot-turn-1');
    await expect(blocked).toContainText('Trend interpretation is withheld');
    await blocked.getByTestId('response-evidence').locator('summary').first().click();
    await expect(blocked.getByTestId('response-evidence')).toContainText('No numerical averages');
    await expect(blocked.locator('.evidence-comparisons')).toHaveCount(0);
    await page.screenshot({ path: path.resolve(`screenshots/issue-17-blocked-${width}.png`) });
    expect(errors).toEqual([]);
  });
}
