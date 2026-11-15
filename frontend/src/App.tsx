import { useEffect, useRef, useState } from 'react';
import { api, message } from './api';
import type { CheckInResult, Evidence, FictionalCheckInInput, ScenarioId, Snapshot, Timeline } from './contracts';
import { CsvUpload } from './components/CsvUpload';
import { FictionalCheckIn } from './components/FictionalCheckIn';
import { SpaceRiskExplorer } from './components/SpaceRiskExplorer';
import { Overview } from './components/Overview';
import { Review } from './components/Review';
import { TimelineView } from './components/TimelineView';
type Mission = {
  source: 'builtin' | 'csv' | 'checkin';
  snapshot: Snapshot;
  timeline: Timeline | null;
  checkIn?: CheckInResult['check_in'];
  decisionSupport?: CheckInResult['decision_support'];
  key: number;
};
export default function App() {
  const [scenarios, setScenarios] = useState<{ id: ScenarioId; label: string }[]>([]);
  const [scenario, setScenario] = useState<ScenarioId | ''>('');
  const [evidence, setEvidence] = useState<Evidence>();
  const [catalogError, setCatalogError] = useState('');
  const [evidenceError, setEvidenceError] = useState('');
  const [catalogBusy, setCatalogBusy] = useState(true);
  const [catalogRetry, setCatalogRetry] = useState(0);
  const [revision, setRevision] = useState(0);
  const [mission, setMission] = useState<Mission>();
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState('');
  const active = useRef<AbortController | null>(null);
  const sequence = useRef(0);
  useEffect(() => {
    const controller = new AbortController();
    setCatalogBusy(true);
    setCatalogError('');
    setEvidenceError('');
    api
      .scenarios(controller.signal)
      .then((result) => {
        if (!controller.signal.aborted) {
          setScenarios(result.scenarios);
          setScenario((current) => current || result.scenarios[0]?.id || '');
        }
      })
      .catch((error) => {
        if (!controller.signal.aborted) setCatalogError(message(error));
      })
      .finally(() => {
        if (!controller.signal.aborted) setCatalogBusy(false);
      });
    api
      .evidence(controller.signal)
      .then((result) => {
        if (!controller.signal.aborted) setEvidence(result);
      })
      .catch((error) => {
        if (!controller.signal.aborted) setEvidenceError(message(error));
      });
    return () => controller.abort();
  }, [catalogRetry]);
  function start() {
    active.current?.abort();
    const controller = new AbortController();
    active.current = controller;
    const key = ++sequence.current;
    setBusy(true);
    setError('');
    setMission(undefined);
    return { controller, key };
  }
  useEffect(() => {
    if (!scenario) return;
    const { controller, key } = start();
    Promise.all([api.demo(scenario, controller.signal), api.timeline(scenario, controller.signal)])
      .then(([snapshot, timeline]) => {
        if (!controller.signal.aborted && key === sequence.current)
          setMission({ source: 'builtin', snapshot, timeline, key });
      })
      .catch((error) => {
        if (!controller.signal.aborted && key === sequence.current) setError(message(error));
      })
      .finally(() => {
        if (!controller.signal.aborted && key === sequence.current) setBusy(false);
      });
    return () => controller.abort();
  }, [scenario, revision]);
  useEffect(() => () => active.current?.abort(), []);
  async function upload(file: File) {
    const { controller, key } = start();
    try {
      const snapshot = await api.upload(file, true, controller.signal);
      if (!controller.signal.aborted && key === sequence.current)
        setMission({ source: 'csv', snapshot, timeline: snapshot.mission_timeline, key });
    } catch (error) {
      if (!controller.signal.aborted && key === sequence.current) setError(message(error));
    } finally {
      if (!controller.signal.aborted && key === sequence.current) setBusy(false);
    }
  }
  async function submitCheckIn(payload: FictionalCheckInInput) {
    const { controller, key } = start();
    try {
      const result = await api.fictionalCheckIn(payload, controller.signal);
      if (!controller.signal.aborted && key === sequence.current)
        setMission({
          source: 'checkin',
          snapshot: result, timeline: result.mission_timeline, key,
          checkIn: result.check_in, decisionSupport: result.decision_support,
        });
    } catch (cause) {
      if (!controller.signal.aborted && key === sequence.current) setError(message(cause));
    } finally {
      if (!controller.signal.aborted && key === sequence.current) setBusy(false);
    }
  }
  return (
    <main>
      <header>
        <p className="eyebrow">MISSION HEALTH CONSOLE / END-TO-END FICTIONAL DEMONSTRATION</p>
        <h1>ARES Health AI v1.3</h1>
        <p role="note">
          <strong>SYNTHETIC DATA / NOT A MEDICAL DEVICE</strong>
        </p>
        <p>
          Local fictional-data demonstration. No diagnosis, NASA telemetry, or clinical validation.
          Do not enter real health data.
        </p>
      </header>
      <section>
        <p className="eyebrow">01 / SELECT SCENARIO</p>
        <h2>Mission simulation</h2>
        {catalogBusy && <p role="status">Loading scenarios…</p>}
        {catalogError && <p role="alert">{catalogError}</p>}
        {!catalogBusy && !catalogError && !scenarios.length && (
          <p>No scenarios available from the API.</p>
        )}
        <label>
          Demo scenario
          <select
            value={scenario}
            disabled={!scenarios.length}
            onChange={(e) => {
              setScenario(e.target.value as ScenarioId);
              setRevision((value) => value + 1);
            }}
          >
            <option value="" disabled>
              Choose a scenario
            </option>
            {scenarios.map((item) => (
              <option key={item.id} value={item.id}>
                {item.label}
              </option>
            ))}
          </select>
        </label>
        <p>Seed 2026 · 21 days · values and rules supplied by FastAPI.</p>
        <button disabled={!scenario || busy} onClick={() => setRevision((value) => value + 1)}>
          Reload selected scenario
        </button>
        {catalogError && (
          <button onClick={() => setCatalogRetry((value) => value + 1)}>
            Retry API connection
          </button>
        )}
      </section>
      {busy && <p role="status">Loading mission data…</p>}
      {error && (
        <p role="alert">{error} Retry with a scenario or upload a corrected fictional CSV.</p>
      )}
      <FictionalCheckIn
        scenario={scenario || undefined}
        busy={busy}
        onSubmit={submitCheckIn}
      />
            <CsvUpload onUpload={upload} busy={busy} />
      {mission && (
        <div key={mission.key}>
          <p className="source-banner">
            Active data source:{' '}
            {mission.source === 'csv'
              ? 'Uploaded synthetic CSV'
              : mission.source === 'checkin'
                ? 'Attested fictional crew check-in'
                : 'Built-in synthetic scenario'}
          </p>
          {mission.checkIn && (
            <section className="mission-card" aria-label="Check-in outcome">
              <p className="eyebrow">03 / REVIEW CURRENT MISSION</p>
              <h2>Check-in applied to fictional mission</h2>
              <p>Evaluation date (UTC): {mission.checkIn.timestamp_utc}</p>
              <p>{mission.checkIn.notice}</p>
              {mission.decisionSupport && (
                <>
                  <h3>Procedure-oriented review</h3>
                  <p>{mission.decisionSupport.review_action}</p>
                  <p>{mission.decisionSupport.concerns_notice}</p>
                  <p className="notice-neutral">{mission.decisionSupport.mission_procedures}</p>
                </>
              )}
            </section>
          )}
          <Overview snapshot={mission.snapshot} />
          <TimelineView
            timeline={mission.timeline}
            blocked={mission.snapshot.assessment === 'DATA_QUALITY_BLOCKED'}
          />
          <Review
            scenario={mission.source === 'builtin' ? (scenario as ScenarioId) : undefined}
            embedded={mission.snapshot.review_report}
          />
        </div>
      )}
      <SpaceRiskExplorer />
      <section id="scientific-evidence">
        <p className="eyebrow">05 / SCIENTIFIC REFERENCES</p>
        <h2>Scientific context</h2>
        <p>
          Research references are background, not NASA/CSA telemetry or clinical validation of this
          prototype.
        </p>
        {evidenceError ? (
          <>
            <p role="alert">{evidenceError}</p>
            <button onClick={() => setCatalogRetry((value) => value + 1)}>
              Retry scientific references
            </button>
          </>
        ) : !evidence ? (
          <p role="status">Loading scientific references…</p>
        ) : (
          <>
            <p>{evidence.usage}</p>
            {!evidence.references.length ? (
              <p>No references available.</p>
            ) : (
              <ul>
                {evidence.references.map((item) => (
                  <li key={item.url}>
                    <a href={item.url} target="_blank" rel="noreferrer">
                      {item.title}
                    </a>{' '}
                    — {item.organization}
                    <p>{item.summary}</p>
                    <p>{item.limitation}</p>
                  </li>
                ))}
              </ul>
            )}
          </>
        )}
      </section>
    </main>
  );
}
