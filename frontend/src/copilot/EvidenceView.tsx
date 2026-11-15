import { BookOpen } from 'lucide-react';
import type { CopilotResponse } from '../copilot-contract';
import type { Snapshot } from '../contracts';
type Reference = CopilotResponse['evidence_refs'][number];
function References({ refs }: { refs: Reference[] }) {
  return (
    <ul className="reference-list">
      {refs.map((ref) => (
        <li key={ref.id}>
          <code>{ref.id}</code>
          {ref.timestamp_utc && <time>{ref.timestamp_utc}</time>}
          {ref.metric && (
            <span>
              {ref.metric} ·{' '}
              {ref.value ??
                (ref.absolute_difference === undefined
                  ? ''
                  : `rule ≥ ${ref.absolute_difference}`)}{' '}
              {ref.unit}
            </span>
          )}
          {ref.window && <span>{ref.window} window</span>}
          {ref.timeline_id && <span>Timeline: {ref.timeline_id}</span>}
          {ref.text && <p>{ref.text}</p>}
          {ref.url && (
            <a href={ref.url} target="_blank" rel="noreferrer">
              {ref.title ?? 'Official source'}
            </a>
          )}
        </li>
      ))}
    </ul>
  );
}
/** Display canonical API means only; do not derive biomedical statistics from refs. */
export function EvidenceView({
  response,
  snapshot,
}: {
  response: CopilotResponse;
  snapshot?: Snapshot;
}) {
  const observations = response.evidence_refs.filter((ref) => ref.kind === 'observation');
  const rules = response.evidence_refs.filter((ref) => ref.kind === 'rule');
  const quality = response.evidence_refs.filter((ref) => ref.kind === 'quality');
  const sources = response.evidence_refs.filter((ref) => ref.kind === 'source');
  const blocked = ['DATA_QUALITY_BLOCKED', 'INSUFFICIENT_DATA'].includes(response.assessment);
  const comparable =
    !blocked &&
    snapshot?.scenario === response.scenario &&
    snapshot?.assessment === response.assessment &&
    observations.length > 0;
  const dates = (window: string) => [
    ...new Set(
      observations
        .filter((ref) => ref.window === window && ref.timestamp_utc)
        .map((ref) => ref.timestamp_utc!),
    ),
  ];
  const referenceDates = dates('reference'),
    recentDates = dates('recent');
  const signals = comparable
    ? snapshot!.descriptive_signals.filter((signal) =>
        observations.some((ref) => ref.metric === signal.metric),
      )
    : [];
  return (
    <details className="grounded-evidence" data-testid="response-evidence">
      <summary>
        <BookOpen size={15} /> View evidence{' '}
        <span>· {response.evidence_refs.length} references</span>
      </summary>
      <div className="evidence-digest">
        <h4>Evidence summary</h4>
        {blocked ? (
          <p>
            Interpretation withheld. No numerical averages are shown for blocked or insufficient
            data.
          </p>
        ) : signals.length > 0 ? (
          <>
            <p>
              Reference and recent values below are supplied by Python. No averages or differences
              are calculated in this view.
            </p>
            <dl className="evidence-windows">
              <div>
                <dt>Reference window (UTC)</dt>
                <dd>
                  {referenceDates[0]}
                  <br />
                  to {referenceDates.at(-1)}
                </dd>
              </div>
              <div>
                <dt>Recent window (UTC)</dt>
                <dd>
                  {recentDates[0]}
                  <br />
                  to {recentDates.at(-1)}
                </dd>
              </div>
            </dl>
            <div className="evidence-comparisons" aria-label="Canonical Python comparisons">
              {signals.map((signal) => (
                <article key={signal.metric}>
                  <h5>
                    {signal.label} <span>({signal.unit})</span>
                  </h5>
                  <dl>
                    <div>
                      <dt>Baseline</dt>
                      <dd data-testid={`evidence-baseline-${signal.metric}`}>
                        {signal.baseline_mean.toFixed(3)}
                      </dd>
                    </div>
                    <div>
                      <dt>Recent</dt>
                      <dd data-testid={`evidence-recent-${signal.metric}`}>
                        {signal.recent_mean.toFixed(3)}
                      </dd>
                    </div>
                    <div>
                      <dt>Difference</dt>
                      <dd data-testid={`evidence-delta-${signal.metric}`}>
                        {signal.delta > 0 ? '+' : ''}
                        {signal.delta.toFixed(3)}
                      </dd>
                    </div>
                  </dl>
                </article>
              ))}
            </div>
          </>
        ) : observations.length > 0 ? (
          <p>
            Exact evaluated observations and window membership are available below; comparison
            values remain in the unchanged Python answer.
          </p>
        ) : null}
        {quality.length > 0 && <References refs={quality} />}
        {sources.length > 0 && (
          <>
            <h5>Scientific background sources</h5>
            <References refs={sources} />
          </>
        )}
        {rules.length > 0 && (
          <>
            <h5>Illustrative rules, not clinical thresholds</h5>
            <References refs={rules} />
          </>
        )}
        {observations.length > 0 && (
          <details className="evidence-observations">
            <summary>
              Detailed observations, UTC dates and timeline IDs ({observations.length})
            </summary>
            <References refs={observations} />
          </details>
        )}
        {!response.evidence_refs.length && (
          <p>
            This answer explains a review-policy limitation; no physiological conclusion or
            scientific citation was invented.
          </p>
        )}
        <details className="evidence-limitations">
          <summary>Medical limitations and context reference</summary>
          <p>
            Context <code>{response.context_ref}</code>
          </p>
          <ul>
            {response.limitations.map((item) => (
              <li key={item}>{item}</li>
            ))}
          </ul>
        </details>
      </div>
    </details>
  );
}
