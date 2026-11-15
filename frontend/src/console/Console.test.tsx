import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { expect, it } from 'vitest';
import { BodyViewer } from './BodyViewer';
import { TelemetryCard } from './TelemetryCard';
import { metrics } from './metrics';
import { snapshotSchema } from '../contracts';
import fixtures from '../test/fixtures.json';
import { vi } from 'vitest';
it('links the three monitored anatomy domains and explicitly labels other regions', async () => {
  const selected = vi.fn();
  const user = userEvent.setup();
  render(<BodyViewer selected="resting_hr_bpm" onSelect={selected} />);
  await user.click(screen.getByRole('button', { name: 'Explore Sleep / neurobehavioral: Sleep' }));
  expect(selected).toHaveBeenCalledWith('sleep_hours');
  await user.click(screen.getByRole('button', { name: 'Other body regions: not monitored' }));
  expect(screen.getByRole('status')).toHaveTextContent('NOT MONITORED');
  expect(screen.getByRole('status')).toHaveTextContent(
    'No respiratory, organ, radiation or diagnostic measurements',
  );
});
it('never replaces a missing latest measurement with an older valid value', () => {
  render(
    <TelemetryCard
      snapshot={snapshotSchema.parse(fixtures.incomplete.demo)}
      metric={metrics[0]}
      selected
      onSelect={() => {}}
    />,
  );
  expect(screen.getByTestId('latest-resting_hr_bpm')).toHaveTextContent('—');
  expect(screen.getByText('Comparison withheld')).toBeVisible();
  expect(screen.getByText(/Last valid/)).toHaveTextContent('2026-11-18');
});
