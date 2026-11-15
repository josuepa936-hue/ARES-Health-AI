import { useState } from 'react';
import { reviewActions, workflowStates, type WorkflowState } from '../copilot-contract';
import { downloadReport } from '../download';
import type { CopilotSession } from './useMissionCopilot';
export function ReviewWorkflow({ session }: { session: CopilotSession }) {
  const [draft, setDraft] = useState('');
  const [attested, setAttested] = useState(false);
  const full = session.audit.length >= 64;
  return (
    <section className="review-workflow" aria-label="Fictional review workflow">
      <h2>Fictional review & integrated export</h2>
      <p>
        Manual demonstration actions only. No institutional case is persisted and no person is
        contacted. States never change the analysis or grant medical authorization.
      </p>
      <div className="review-workflow-grid">
        <div>
          <label>
            Fictional review state
            <select
              value={session.state}
              disabled={full}
              onChange={(event) => session.setReviewState(event.target.value as WorkflowState)}
            >
              {workflowStates.map((state) => (
                <option key={state}>{state}</option>
              ))}
            </select>
          </label>
          <fieldset>
            <legend>Record actions manually — no automated confirmation</legend>
            {reviewActions.map((action) => (
              <label key={action.id}>
                <input
                  type="checkbox"
                  checked={session.actions[action.id]}
                  disabled={full}
                  onChange={(event) => session.setAction(action.id, event.target.checked)}
                />
                {action.label}
              </label>
            ))}
          </fieldset>
          <label>
            Fictional review note
            <textarea
              maxLength={500}
              value={draft}
              onChange={(event) => setDraft(event.target.value)}
              placeholder="Fictional engineering review only; no personal data"
            />
          </label>
          <button
            disabled={full || draft === session.note}
            onClick={() => session.recordNote(draft)}
          >
            Record fictional note
          </button>
          <small>
            {draft.length}/500 characters
            {draft !== session.note ? ' · unrecorded changes are not exported' : ''}
          </small>
          <label className="review-attestation">
            <input
              type="checkbox"
              checked={attested}
              onChange={(event) => setAttested(event.target.checked)}
            />
            I confirm these review actions and notes are fictional.
          </label>
          <button
            disabled={
              !attested ||
              !session.briefing ||
              session.loading ||
              session.exporting ||
              draft !== session.note
            }
            onClick={session.buildReport}
          >
            Build comprehensive JSON report
          </button>
          {session.exporting && <p role="status">Revalidating integrated report in Python…</p>}
          {session.error && <p role="alert">{session.error}</p>}
          {session.report && (
            <div className="integrated-report">
              <p>
                Report: {session.report.assessment} · review{' '}
                {session.report.fictional_review.review_state}
              </p>
              <button
                disabled={
                  !attested || draft !== session.note || session.loading || session.exporting
                }
                onClick={() => downloadReport(session.report!)}
              >
                Download comprehensive JSON
              </button>
              <p>
                Canonical legacy report fields retained; transcript answers were recomputed against
                this context. Unsafe/unsupported turns omitted:{' '}
                {session.report.copilot.omitted_unsupported_or_unsafe_turns}.
              </p>
            </div>
          )}
        </div>
        <aside>
          <h3>User-recorded audit log</h3>
          <p>{session.audit.length}/64 events · browser memory only; page reload resets.</p>
          {full && (
            <p role="alert">Audit limit reached. Export this review or reset with a new mission.</p>
          )}
          <ol>
            {session.audit.map((event) => (
              <li key={event.sequence}>
                <code>
                  #{event.sequence} {event.action}
                </code>
                <span>
                  {event.recorded_at_utc && (
                    <time dateTime={event.recorded_at_utc}>
                      {event.recorded_at_utc} ·{' '}
                    </time>
                  )}
                  {'checked' in event
                    ? event.checked
                      ? 'Confirmed by user'
                      : 'Unchecked by user'
                    : 'review_state' in event
                      ? event.review_state
                      : event.note}
                </span>
              </li>
            ))}
          </ol>
          {!session.audit.length && <p>Pending review. No action has been confirmed.</p>}
        </aside>
      </div>
    </section>
  );
}
