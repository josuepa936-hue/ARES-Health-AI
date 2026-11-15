import type { Snapshot } from '../contracts';
import { Charts } from './Charts';
export function Overview({ snapshot }: { snapshot: Snapshot }) {
  const blocked = snapshot.assessment === 'DATA_QUALITY_BLOCKED';
  const available = !blocked && snapshot.assessment !== 'INSUFFICIENT_DATA';
  return (
    <section>
      <h2>Mission overview</h2>
      <p>
        API assessment: <strong>{snapshot.assessment}</strong>
      </p>
      <dl>
        <dt>Synthetic crew</dt>
        <dd>{snapshot.summary.crew_id}</dd>
        <dt>Recorded days</dt>
        <dd>{snapshot.summary.recorded_days}</dd>
        <dt>Data completeness</dt>
        <dd>{snapshot.summary.completeness_pct}%</dd>
        <dt>Quality findings</dt>
        <dd>{snapshot.summary.quality_findings}</dd>
      </dl>
      {blocked && (
        <div role="alert">
          <strong>Data quality blocks interpretation.</strong>
          <ul>
            {snapshot.quality_issues.map((issue) => (
              <li key={issue}>{issue}</li>
            ))}
          </ul>
          <p>Missing values remain gaps; no normality or trend interpretation is inferred.</p>
        </div>
      )}
      <ul>
        {snapshot.analysis_limitations.map((issue) => (
          <li key={issue}>{issue}</li>
        ))}
      </ul>
      <h3>{snapshot.guidance.heading}</h3>
      <p>{snapshot.guidance.meaning}</p>
      <ol>
        {snapshot.guidance.review_steps.map((step) => (
          <li key={step}>{step}</li>
        ))}
      </ol>
      {available && (
        <section aria-label="Explainable findings">
          <h3>Explainable findings</h3>
          <p>Review flags: {snapshot.summary.review_flags}</p>
          {snapshot.review_flags.length ? (
            <ul>
              {snapshot.review_flags.map((flag) => (
                <li key={flag.metric}>{flag.explanation}</li>
              ))}
            </ul>
          ) : (
            <p>No demonstration rule triggered. This is not medical clearance.</p>
          )}
          <details>
            <summary>API descriptive statistics</summary>
            <p>{snapshot.descriptive_statistics_notice}</p>
            {snapshot.descriptive_signals.length ? (
              <ul>
                {snapshot.descriptive_signals.map((signal) => (
                  <li key={signal.metric}>
                    {signal.label}: reference mean {signal.baseline_mean} {signal.unit}; recent mean{' '}
                    {signal.recent_mean} {signal.unit}; difference {signal.delta} {signal.unit};
                    median {signal.full_median}; robust variability {signal.robust_variability};
                    slope/day {signal.theil_sen_slope_per_day}. All values supplied by Python.
                  </li>
                ))}
              </ul>
            ) : (
              <p>No descriptive statistics available.</p>
            )}
          </details>
        </section>
      )}
      <Charts observations={snapshot.observations} />
      <p>{snapshot.disclaimer}</p>
    </section>
  );
}
