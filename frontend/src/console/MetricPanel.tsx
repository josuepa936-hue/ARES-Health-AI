import { useState } from 'react';
import {
  Area,
  AreaChart,
  CartesianGrid,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from 'recharts';
import { ArrowUpRight, ChartNoAxesCombined, Download } from 'lucide-react';
import type { Snapshot } from '../contracts';
import { metrics, analysisAvailable, type MetricKey } from './metrics';
export function MetricPanel({
  snapshot,
  selected,
  onSelect,
  onReview,
  onQualityInspect,
}: {
  snapshot: Snapshot;
  selected: MetricKey;
  onSelect: (key: MetricKey) => void;
  onReview: () => void;
  onQualityInspect?: () => void;
}) {
  const [details, setDetails] = useState(false);
  const metric = metrics.find((item) => item.key === selected)!;
  const available = analysisAvailable(snapshot);
  const signal = available
    ? snapshot.descriptive_signals.find((item) => item.metric === selected)
    : undefined;
  const flags = available ? snapshot.review_flags.filter((flag) => flag.metric === selected) : [];
  return (
    <section className="metric-panel" aria-label="Selected physiological analysis">
      <div className="panel-heading">
        <span>
          <ChartNoAxesCombined size={15} /> SIGNAL ANALYSIS
        </span>
        <span>UTC / DAILY</span>
      </div>
      <div className="metric-selector" role="group" aria-label="Select physiological metric">
        {metrics.map((item) => (
          <button
            key={item.key}
            aria-pressed={item.key === selected}
            onClick={() => onSelect(item.key)}
          >
            {item.short}
          </button>
        ))}
      </div>
      <div className="chart-title">
        <div>
          <p className="eyebrow">{metric.domain}</p>
          <h2>{metric.name}</h2>
        </div>
        <span className="unit-badge">{metric.unit}</span>
      </div>
      <div
        className="primary-chart"
        role="img"
        aria-label={`${metric.name} in ${metric.unit}; actual API observations, UTC; missing values remain gaps`}
      >
        <ResponsiveContainer width="100%" height="100%">
          <AreaChart
            data={snapshot.observations}
            margin={{ top: 10, right: 8, bottom: 0, left: -20 }}
          >
            <defs>
              <linearGradient id="metricFill" x1="0" y1="0" x2="0" y2="1">
                <stop offset="0%" stopColor="#45e4d0" stopOpacity={0.23} />
                <stop offset="100%" stopColor="#45e4d0" stopOpacity={0} />
              </linearGradient>
            </defs>
            <CartesianGrid stroke="#173542" strokeDasharray="3 6" vertical={false} />
            <XAxis
              dataKey="timestamp_utc"
              tickFormatter={(value) => String(value).slice(5, 10)}
              minTickGap={38}
              axisLine={false}
              tickLine={false}
              tick={{ fill: '#94b7bf', fontSize: 10 }}
            />
            <YAxis
              domain={['auto', 'auto']}
              tick={{ fill: '#94b7bf', fontSize: 10 }}
              tickLine={false}
              axisLine={false}
              width={52}
            />
            <Tooltip
              contentStyle={{
                background: '#0b2330',
                border: '1px solid #35717b',
                borderRadius: 6,
                color: '#ecffff',
              }}
              labelFormatter={(label) => `${label} · UTC`}
              formatter={(value) => [`${value} ${metric.unit}`, metric.name]}
            />
            <Area
              type="linear"
              dataKey={selected}
              stroke="#4ce0d0"
              fill="url(#metricFill)"
              strokeWidth={2}
              dot={{ r: 2, fill: '#54e8d5', strokeWidth: 0 }}
              activeDot={{ r: 5 }}
              connectNulls={false}
              isAnimationActive={false}
            />
          </AreaChart>
        </ResponsiveContainer>
      </div>
      {available && (
        <div className="comparison-grid">
          <div>
            <span>REFERENCE / FIRST 7 DAYS</span>
            <strong>
              {signal?.baseline_mean.toFixed(2) ?? '—'} <small>{metric.unit}</small>
            </strong>
          </div>
          <div>
            <span>RECENT / LAST 4 DAYS</span>
            <strong>
              {signal?.recent_mean.toFixed(2) ?? '—'} <small>{metric.unit}</small>
            </strong>
          </div>
        </div>
      )}
      <div className={`finding ${!available ? 'blocked' : flags.length ? 'change' : ''}`}>
        <span className="eyebrow">
          {!available
            ? 'INTERPRETATION WITHHELD'
            : flags.length
              ? 'ILLUSTRATIVE CHANGE'
              : 'OBSERVATION / DEMO RULE'}
        </span>
        {snapshot.assessment === 'DATA_QUALITY_BLOCKED' && (
          <div role="alert" className="quality-inline">
            <strong>Data quality blocks interpretation.</strong>
            <p>{snapshot.quality_issues.join(' ')}</p>
            <button onClick={onQualityInspect}>Inspect quality events</button>
          </div>
        )}
        {snapshot.assessment !== 'DATA_QUALITY_BLOCKED' && (
          <p>
            {!available
              ? 'Missing or invalid records prevent a meaningful comparison. No health interpretation is available.'
              : (flags[0]?.explanation ??
                'No illustrative rule triggered for this indicator. This does not establish medical safety.')}
          </p>
        )}
      </div>
      <div className="panel-actions">
        <button onClick={() => setDetails((value) => !value)} aria-expanded={details}>
          <ArrowUpRight size={14} /> Observation values and UTC dates
        </button>
        <button onClick={onReview}>
          <Download size={14} /> Review & export
        </button>
      </div>
      {details && (
        <div className="signal-detail">
          <table>
            <thead>
              <tr>
                <th>UTC timestamp</th>
                {metrics.map((item) => (
                  <th key={item.key}>
                    {item.name} ({item.unit})
                  </th>
                ))}
              </tr>
            </thead>
            <tbody>
              {snapshot.observations.map((row, index) => (
                <tr key={index}>
                  <th>{row.timestamp_utc}</th>
                  {metrics.map((item) => (
                    <td key={item.key}>{row[item.key] ?? 'Missing'}</td>
                  ))}
                </tr>
              ))}
            </tbody>
          </table>
          {available && (
            <details>
              <summary>API descriptive statistics</summary>
              <p>{snapshot.descriptive_statistics_notice}</p>
              <pre>{JSON.stringify(snapshot.descriptive_signals, null, 2)}</pre>
            </details>
          )}
        </div>
      )}
    </section>
  );
}
