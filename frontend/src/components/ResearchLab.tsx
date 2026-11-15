import { useEffect, useState } from 'react';
import { api, message } from '../api';
import type { ResearchResult } from '../research-contract';
export default function ResearchLab() {
  const [result, setResult] = useState<ResearchResult>();
  const [error, setError] = useState('');
  const [busy, setBusy] = useState(true);
  const [retry, setRetry] = useState(0);
  useEffect(() => {
    const controller = new AbortController();
    setResult(undefined);
    setError('');
    setBusy(true);
    api
      .research(controller.signal)
      .then((data) => {
        if (!controller.signal.aborted) setResult(data);
      })
      .catch((error) => {
        if (!controller.signal.aborted) setError(message(error));
      })
      .finally(() => {
        if (!controller.signal.aborted) setBusy(false);
      });
    return () => controller.abort();
  }, [retry]);
  return (
    <main>
      <h1>Biomedical Research Lab — future research</h1>
      <p>
        <strong>PUBLIC TERRESTRIAL RESEARCH ECG / NOT A MEDICAL DEVICE</strong>
      </p>
      <p>
        This opt-in benchmark is separate from synthetic mission data. No diagnosis, arrhythmia
        classification, astronaut risk scoring or treatment recommendations. No ECG uploads.
      </p>
      {busy && <p role="status">Loading the locally prepared benchmark…</p>}
      {error && (
        <p role="alert">
          {error} Research may be disabled, unprepared, or unavailable. The synthetic mission demo
          remains the submission fallback.
        </p>
      )}
      <button disabled={busy} onClick={() => setRetry((value) => value + 1)}>
        Reload research benchmark
      </button>
      {result && (
        <>
          <h2>MIT-BIH record 100</h2>
          <p>
            <a href={result.source.url} target="_blank" rel="noreferrer">
              {result.source.dataset} {result.source.version}
            </a>{' '}
            · <a href={result.source.doi}>Dataset citation</a>
          </p>
          <p>
            Provenance: {result.data_provenance}. {result.source.context}
          </p>
          <p>Signal quality: {result.quality.status}</p>
          <ul>
            {result.quality.checks.map((check) => (
              <li key={check}>{check}</li>
            ))}
          </ul>
          {result.status === 'abstained' ? (
            <div role="alert">
              <h2>Benchmark abstained</h2>
              <ul>
                {result.reasons.map((reason) => (
                  <li key={reason}>{reason}</li>
                ))}
              </ul>
              <p>No benchmark scores or reassuring interpretations are available.</p>
            </div>
          ) : (
            <Benchmark result={result} />
          )}
          <details>
            <summary>Exact processing versions and provenance manifest</summary>
            <pre>
              {JSON.stringify(
                {
                  versions: result.processing_versions,
                  acquisition: result.acquisition,
                  protocol: result.protocol,
                },
                null,
                2,
              )}
            </pre>
          </details>
          <p>{result.disclaimer}</p>
        </>
      )}
    </main>
  );
}
function Benchmark({ result }: { result: ResearchResult }) {
  if (!result.metrics) return null;
  const low = Math.min(...result.waveform.map((point) => point.mv));
  const high = Math.max(...result.waveform.map((point) => point.mv));
  const x = (sample: number) => 30 + (sample * 740) / 21600;
  const y = (mv: number) => (high === low ? 110 : 200 - ((mv - low) * 175) / (high - low));
  return (
    <>
      <h2>Beat-detection benchmark (not medical accuracy)</h2>
      <p>
        360 Hz MLII; first 60 seconds. Scoring samples [360, 21240), excluding the first/last
        second. Inclusive ±150 ms matching tolerance is an engineering choice, not a clinical
        standard.
      </p>
      <p>
        {result.protocol.matching}. Metrics use full-resolution samples; the display takes every
        12th sample and is not used for scoring.
      </p>
      <dl>
        {Object.entries(result.metrics).map(([key, value]) => (
          <div key={key}>
            <dt>{key.replaceAll('_', ' ')}</dt>
            <dd>{value ?? 'Undefined (no supporting matched/scored beats)'}</dd>
          </div>
        ))}
      </dl>
      <h3>Raw ECG (mV) and heartbeat markers</h3>
      <p>
        Blue line: raw signal. Orange circles: detected R-peaks. Green squares: expert-reviewed
        heartbeat references. Markers retain exact full-resolution sample times.
      </p>
      <svg
        viewBox="0 0 800 250"
        role="img"
        aria-label="Public research ECG in mV, time 0–60 seconds, detected peaks and expert-reviewed heartbeat markers"
      >
        <text x="0" y="20">
          {high.toFixed(2)} mV
        </text>
        <text x="0" y="225">
          {low.toFixed(2)} mV
        </text>
        <polyline
          fill="none"
          stroke="#17599b"
          points={result.waveform.map((point) => `${x(point.sample)},${y(point.mv)}`).join(' ')}
        />
        {result.reference_peaks.map((point) => (
          <rect
            key={point.sample}
            x={x(point.sample) - 3}
            y={y(point.mv) - 3}
            width="6"
            height="6"
            fill="none"
            stroke="green"
          />
        ))}
        {result.detected_peaks.map((point, index) => (
          <circle
            key={index}
            cx={x(point.sample)}
            cy={y(point.mv)}
            r="5"
            fill="none"
            stroke="#a34a00"
          />
        ))}
        <text x="30" y="245">
          0 s
        </text>
        <text x="720" y="245">
          60 s
        </text>
      </svg>
      <h3>Annotation accounting</h3>
      <dl>
        {Object.entries(result.annotation_counts ?? {}).map(([key, value]) => (
          <div key={key}>
            <dt>{key.replaceAll('_', ' ')}</dt>
            <dd>{value}</dd>
          </div>
        ))}
      </dl>
      <h3>Discrepancies</h3>
      <p>
        FP = unmatched detector candidate; FN = unmatched reference heartbeat. These are evaluation
        outcomes, not clinical labels.
      </p>
      {result.discrepancies.length ? (
        <div className="table-scroll">
          <table>
            <thead>
              <tr>
                <th>Outcome</th>
                <th>Original sample</th>
                <th>Seconds from record start</th>
              </tr>
            </thead>
            <tbody>
              {result.discrepancies.map((item, index) => (
                <tr key={index}>
                  <td>{item.type}</td>
                  <td>{item.sample}</td>
                  <td>{(item.sample / 360).toFixed(4)}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      ) : (
        <p>No unmatched beats in this scored window. This does not establish clinical validity.</p>
      )}
    </>
  );
}
