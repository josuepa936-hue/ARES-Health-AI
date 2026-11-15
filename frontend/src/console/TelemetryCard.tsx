import { Activity, Heart, Moon, ArrowUpRight } from 'lucide-react';
import { ResponsiveContainer, LineChart, Line, YAxis } from 'recharts';
import type { Snapshot } from '../contracts';
import { analysisAvailable, latestObservation, type Metric } from './metrics';
export function TelemetryCard({
  snapshot,
  metric,
  selected,
  onSelect,
}: {
  snapshot: Snapshot;
  metric: Metric;
  selected: boolean;
  onSelect: () => void;
}) {
  const { latest, lastValid } = latestObservation(snapshot, metric.key);
  const signal = analysisAvailable(snapshot)
    ? snapshot.descriptive_signals.find((item) => item.metric === metric.key)
    : undefined;
  const Icon = metric.icon === 'heart' ? Heart : metric.icon === 'moon' ? Moon : Activity;
  return (
    <button
      className={`telemetry-card ${selected ? 'selected' : ''}`}
      aria-pressed={selected}
      onClick={onSelect}
    >
      <div className="telemetry-title">
        <Icon size={16} />
        <span>{metric.name}</span>
        <ArrowUpRight size={13} />
      </div>
      <div className="telemetry-value" data-testid={`latest-${metric.key}`}>
        {latest?.[metric.key] ?? '—'} <span>{metric.unit}</span>
        {latest?.[metric.key] === null && <small>MISSING OBSERVATION</small>}
      </div>
      <div className="mini-chart" aria-hidden="true">
        <ResponsiveContainer width="100%" height="100%">
          <LineChart accessibilityLayer={false} data={snapshot.observations}>
            <YAxis hide domain={['auto','auto']}/>
            <Line
              type="linear"
              dataKey={metric.key}
              stroke="var(--cyan)"
              strokeWidth={1.6}
              dot={false}
              connectNulls={false}
              isAnimationActive={false}
            />
          </LineChart>
        </ResponsiveContainer>
      </div>
      <div className="telemetry-foot">
        <span>
          {signal
            ? `Δ ${signal.delta > 0 ? '+' : ''}${signal.delta.toFixed(2)} ${metric.unit}`
            : 'Comparison withheld'}
        </span>
        <span>{snapshot.observations.length}-DAY VIEW</span>
      </div>
      <div className="last-valid">
        Last valid ·{' '}
        {lastValid?.timestamp_utc?.replace('T', ' ').replace('Z', ' UTC') ?? 'Unavailable'}
      </div>
    </button>
  );
}
