import type { Observation } from '../contracts';
const metrics = [
  ['resting_hr_bpm', 'Resting heart rate', 'bpm'],
  ['sleep_hours', 'Sleep duration', 'hours'],
  ['activity_minutes', 'Daily activity', 'min/day'],
] as const;
/** Presentation-only coordinates. No imputation, smoothing or biomedical rules. */
export function Charts({ observations }: { observations: Observation[] }) {
  if (!observations.length) return <p>No observations returned by the API.</p>;
  return (
    <section aria-label="Physiological charts">
      <h2>Physiological observations</h2>
      <p>
        Fictional daily values, UTC. Gaps represent missing values; no interpolation is performed.
      </p>
      {metrics.map(([key, label, unit]) => {
        const values = observations
          .map((row) => row[key])
          .filter((value): value is number => value !== null);
        const low = Math.min(...values),
          high = Math.max(...values);
        const segments: string[][] = [[]];
        observations.forEach((row, index) => {
          const value = row[key];
          if (value === null) {
            segments.push([]);
            return;
          }
          const x = 40 + (index * 510) / Math.max(1, observations.length - 1);
          const y = high === low ? 95 : 160 - ((value - low) * 130) / (high - low);
          segments[segments.length - 1].push(`${x},${y}`);
        });
        return (
          <figure key={key}>
            <figcaption>
              {label} ({unit})
            </figcaption>
            {values.length ? (
              <svg
                viewBox="0 0 580 210"
                role="img"
                aria-label={`${label} in ${unit}; UTC dates; missing records are gaps`}
              >
                <text x="0" y="25">
                  {high}
                </text>
                <text x="0" y="175">
                  {low}
                </text>
                {segments.map((points, index) => (
                  <g key={index}>
                    <polyline
                      fill="none"
                      stroke="currentColor"
                      strokeWidth="2"
                      points={points.join(' ')}
                    />
                    {points.map((point, n) => (
                      <circle key={n} cx={point.split(',')[0]} cy={point.split(',')[1]} r="3" />
                    ))}
                  </g>
                ))}
                <text x="40" y="200">
                  {observations[0].timestamp_utc?.slice(0, 10) ?? 'Unknown date'}
                </text>
                <text x="430" y="200">
                  {observations.at(-1)?.timestamp_utc?.slice(0, 10) ?? 'Unknown date'}
                </text>
              </svg>
            ) : (
              <p>No available {label.toLowerCase()} measurements.</p>
            )}
          </figure>
        );
      })}
      <details>
        <summary>Observation values and UTC dates</summary>
        <div className="table-scroll">
          <table>
            <thead>
              <tr>
                <th>UTC timestamp</th>
                {metrics.map(([key, label, unit]) => (
                  <th key={key}>
                    {label} ({unit})
                  </th>
                ))}
              </tr>
            </thead>
            <tbody>
              {observations.map((row, index) => (
                <tr key={index}>
                  <th>{row.timestamp_utc ?? 'Unknown timestamp'}</th>
                  {metrics.map(([key]) => (
                    <td key={key}>{row[key] ?? 'Missing'}</td>
                  ))}
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </details>
    </section>
  );
}
