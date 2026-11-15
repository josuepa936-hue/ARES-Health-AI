import { useEffect, useRef, useState, type FormEvent } from 'react';
import { api, message } from '../api';
import type { ReviewReport, ScenarioId } from '../contracts';
import { downloadReport } from '../download';
export function Review({ scenario, embedded }: { scenario?: ScenarioId; embedded?: ReviewReport }) {
  const [state, setState] = useState<ReviewReport['review_state']>('Pending review');
  const [note, setNote] = useState('');
  const [report, setReport] = useState(embedded);
  const [error, setError] = useState('');
  const [busy, setBusy] = useState(false);
  const controller = useRef<AbortController | null>(null);
  useEffect(() => () => controller.current?.abort(), []);
  function invalidate() {
    controller.current?.abort();
    setBusy(false);
    setReport(undefined);
    setError('');
  }
  async function submit(e: FormEvent) {
    e.preventDefault();
    if (!scenario) return;
    controller.current?.abort();
    const current = new AbortController();
    controller.current = current;
    setBusy(true);
    setReport(undefined);
    setError('');
    try {
      const result = await api.review(scenario, state, note, current.signal);
      if (!current.signal.aborted) setReport(result);
    } catch (error) {
      if (!current.signal.aborted) setError(message(error));
    } finally {
      if (!current.signal.aborted) setBusy(false);
    }
  }
  return (
    <section id="mission-review">
      <h2>Mission Review Center</h2>
      <p>Fictional notes only. Do not enter personal or medical information.</p>
      {scenario ? (
        <form onSubmit={submit}>
          <label>
            Review state
            <select
              value={state}
              onChange={(e) => {
                invalidate();
                setState(e.target.value as ReviewReport['review_state']);
              }}
            >
              <option>Pending review</option>
              <option>Reviewed in demo</option>
            </select>
          </label>
          <label>
            Reviewer note
            <textarea
              value={note}
              maxLength={500}
              onChange={(e) => {
                invalidate();
                setNote(e.target.value);
              }}
            />
          </label>
          <span>{note.length}/500 characters</span>{' '}
          <button disabled={busy}>Request review JSON</button>
        </form>
      ) : (
        <p>
          CSV uploads and fictional check-ins export the API's embedded review report. Built-in
          scenario review submission is unavailable for these derived datasets.
        </p>
      )}
      {busy && <p role="status">Preparing review…</p>}
      {error && <p role="alert">{error}</p>}
      {report && (
        <>
          <p>Report assessment: {report.assessment}</p>
          <button onClick={() => downloadReport(report)}>Download review JSON</button>
        </>
      )}
    </section>
  );
}
