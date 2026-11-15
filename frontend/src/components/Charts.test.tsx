import { render, screen } from '@testing-library/react';
import { expect, it } from 'vitest';
import { Charts } from './Charts';
import { snapshotSchema } from '../contracts';
import fixtures from '../test/fixtures.json';
it('does not connect a line across an interior missing observation', () => {
  const observations = snapshotSchema.parse(fixtures.stable.demo).observations.slice(0, 4);
  observations[2].sleep_hours = null;
  render(<Charts observations={observations} />);
  const chart = screen.getByRole('img', { name: /Sleep duration/ });
  const lines = chart.querySelectorAll('polyline');
  expect(lines).toHaveLength(2);
  expect(chart.querySelectorAll('circle')).toHaveLength(3);
  expect(lines[0].getAttribute('points')?.trim().split(' ')).toHaveLength(2);
  expect(lines[1].getAttribute('points')?.trim().split(' ')).toHaveLength(1);
});
it('shows an explicit empty observation state', () => {
  render(<Charts observations={[]} />);
  expect(screen.getByText('No observations returned by the API.')).toBeVisible();
  expect(screen.queryByRole('img')).not.toBeInTheDocument();
});
it('does not invent a curve when every measurement is missing', () => {
  const observations = snapshotSchema.parse(fixtures.incomplete.demo).observations.slice(-1);
  render(<Charts observations={observations} />);
  expect(screen.getByText('No available sleep duration measurements.')).toBeVisible();
  expect(screen.queryByRole('img', { name: /Sleep duration/ })).not.toBeInTheDocument();
});
