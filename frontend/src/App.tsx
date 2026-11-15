import { useEffect, useRef, useState } from 'react';
import { api, message } from './api';
import type {
  CheckInResult,
  Evidence,
  FictionalCheckInInput,
  ScenarioId,
  Snapshot,
  Timeline,
} from './contracts';
import { CsvUpload } from './components/CsvUpload';
import { FictionalCheckIn } from './components/FictionalCheckIn';
import { SpaceRiskExplorer } from './components/SpaceRiskExplorer';
import { MissionCommandBar } from './console/MissionCommandBar';
import { TelemetryCard } from './console/TelemetryCard';
import { BodyViewer } from './console/BodyViewer';
import { MetricPanel } from './console/MetricPanel';
import { ContextDock, type DockTab } from './console/ContextDock';
import { metrics, type MetricKey } from './console/metrics';
import { Activity, ArrowUpRight, FileUp, Radio, ShieldCheck } from 'lucide-react';
import type { CopilotContext } from './copilot-contract';
import { useMissionCopilot } from './copilot/useMissionCopilot';
import { CopilotPanel } from './copilot/CopilotPanel';
import { ReviewWorkflow } from './copilot/ReviewWorkflow';
import { TimelineView } from './components/TimelineView';
type Mission = {
  source: 'builtin' | 'csv' | 'checkin';
  snapshot: Snapshot;
  timeline: Timeline | null;
  checkIn?: CheckInResult['check_in'];
  decisionSupport?: CheckInResult['decision_support'];
  key: number;
  copilotContext: CopilotContext;
};
export default function App() {
  const [selectedMetric, setSelectedMetric] = useState<MetricKey>('resting_hr_bpm');
  const [dockTab, setDockTab] = useState<DockTab>('checkin');
  const [dockOpen, setDockOpen] = useState(true);
  function toggleWorkspace() {
    setDockOpen(!dockOpen);
    if (dockOpen)
      requestAnimationFrame(() => {
        window.scrollTo({ top: 0, behavior: 'instant' });
        document
          .querySelector<HTMLButtonElement>('.copilot-launch')
          ?.focus({ preventScroll: true });
      });
  }
  function openDock(tab: DockTab) {
    setDockTab(tab);
    setDockOpen(true);
  }
  function launchCopilot() {
    openDock('copilot');
    requestAnimationFrame(() => {
      const tab = document.getElementById('tab-copilot');
      tab?.closest('.context-dock')?.scrollIntoView({ block: 'start', behavior: 'instant' });
      tab?.focus({ preventScroll: true });
    });
  }
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
          setMission({
            source: 'builtin',
            snapshot,
            timeline,
            key,
            copilotContext: { kind: 'scenario', scenario, seed: 2026, days: 21 },
          });
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
      const csv = new TextDecoder('utf-8', { fatal: true }).decode(await file.arrayBuffer());
      if (!controller.signal.aborted && key === sequence.current)
        setMission({
          source: 'csv',
          snapshot,
          timeline: snapshot.mission_timeline,
          key,
          copilotContext: { kind: 'synthetic_csv', fictional_attestation: true, csv },
        });
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
          snapshot: result,
          timeline: result.mission_timeline,
          key,
          checkIn: result.check_in,
          decisionSupport: result.decision_support,
          copilotContext: {
            kind: 'scenario',
            scenario: payload.scenario,
            seed: payload.seed,
            days: payload.days,
            check_in: {
              fictional_attestation: true,
              resting_hr_bpm: payload.resting_hr_bpm,
              sleep_hours: payload.sleep_hours,
              activity_minutes: payload.activity_minutes,
              concerns: payload.concerns,
            },
          },
        });
    } catch (cause) {
      if (!controller.signal.aborted && key === sequence.current) setError(message(cause));
    } finally {
      if (!controller.signal.aborted && key === sequence.current) setBusy(false);
    }
  }
  const copilot = useMissionCopilot(mission?.copilotContext, mission?.key);
  const snapshot = mission?.snapshot;
  const source =
    mission?.source === 'csv'
      ? 'Uploaded synthetic CSV'
      : mission?.source === 'checkin'
        ? 'Attested fictional crew check-in'
        : 'Built-in synthetic scenario';
  const blocked = snapshot?.assessment === 'DATA_QUALITY_BLOCKED';
  const changed = snapshot?.assessment === 'CHANGE_FOR_REVIEW';
  return (
    <main className={`console-app ${!dockOpen ? 'dock-closed' : ''}`}>
      <MissionCommandBar
        scenarios={scenarios}
        scenario={scenario}
        snapshot={snapshot}
        source={source}
        busy={busy}
        onScenario={(value) => {
          setScenario(value);
          setRevision((value) => value + 1);
        }}
        onReload={() => setRevision((value) => value + 1)}
      />
      <div className="console-title-row">
        <div>
          <p className="eyebrow">ARES / CREW SYSTEMS INTELLIGENCE</p>
          <h1>
            Biomedical mission control<span>01</span>
          </h1>
        </div>
        <button className="copilot-launch" onClick={launchCopilot}>
          ARES Copilot ·{' '}
          {copilot.loading
            ? 'briefing…'
            : copilot.briefing
              ? 'briefing ready'
              : 'offline explanations'}
        </button>
        <div className={`assessment-chip ${blocked ? 'blocked' : changed ? 'change' : ''}`}>
          <Radio size={13} />
          <strong>{snapshot?.assessment ?? (busy ? 'LOADING MISSION' : 'AWAITING DATA')}</strong>
        </div>
      </div>
      {(catalogError || error) && (
        <div className="console-error" role="alert">
          {catalogError || error}
          <button
            onClick={() => {
              setCatalogRetry((value) => value + 1);
              setRevision((value) => value + 1);
            }}
          >
            Retry API connection
          </button>
        </div>
      )}
      {catalogBusy && (
        <span role="status" className="load-note">
          Loading scenarios…
        </span>
      )}
      {busy && (
        <span role="status" className="load-note">
          Loading mission data…
        </span>
      )}
      {!catalogBusy && !catalogError && !scenarios.length && (
        <p>No scenarios available from the API.</p>
      )}
      <div className="command-grid">
        <aside className="telemetry-rail" aria-label="Mission telemetry">
          <div className="rail-title">
            <h2>{snapshot ? 'Mission overview' : 'Mission telemetry'}</h2>
            <span>3 INDICATORS</span>
          </div>
          {snapshot ? (
            <>
              {metrics.map((metric) => (
                <TelemetryCard
                  key={metric.key}
                  snapshot={snapshot}
                  metric={metric}
                  selected={selectedMetric === metric.key}
                  onSelect={() => setSelectedMetric(metric.key)}
                />
              ))}
              <div className="rail-integrity">
                <ShieldCheck size={13} />
                {snapshot.summary.completeness_pct}% COMPLETE{' '}
                <span>{snapshot.summary.quality_findings} QUALITY FINDINGS</span>
              </div>
            </>
          ) : (
            <div className="awaiting-data">
              <Activity size={30} />
              <p>
                {error || catalogError ? 'Mission data unavailable' : 'Awaiting API observations'}
              </p>
              <p>No substitute readings are generated.</p>
            </div>
          )}
        </aside>
        <BodyViewer
          selected={selectedMetric}
          onSelect={setSelectedMetric}
          crewId={snapshot?.summary.crew_id}
        />
        {snapshot ? (
          <MetricPanel
            snapshot={snapshot}
            selected={selectedMetric}
            onSelect={setSelectedMetric}
            onReview={() => openDock('review')}
            onQualityInspect={() => openDock('timeline')}
          />
        ) : (
          <section className="metric-panel awaiting-data">
            <Activity size={30} />
            <h2>Signal analysis</h2>
            <p>{busy ? 'Loading actual API observations…' : 'No analysis available.'}</p>
          </section>
        )}
      </div>
      <ContextDock
        active={dockTab}
        open={dockOpen}
        onSelect={openDock}
        onToggle={toggleWorkspace}
        panels={{
          copilot: mission ? (
            <CopilotPanel
              key={mission.key}
              session={copilot}
              snapshot={mission.snapshot}
              onReview={() => openDock('review')}
            />
          ) : (
            <p>Load a fictional mission for a grounded offline briefing.</p>
          ),
          checkin: (
            <div className="drawer-split">
              <div>
                <FictionalCheckIn
                  scenario={scenario || undefined}
                  busy={busy}
                  onSubmit={submitCheckIn}
                  compact
                />
                {mission?.checkIn && (
                  <div className="checkin-result" aria-label="Check-in outcome">
                    <h3>Check-in applied to fictional mission</h3>
                    <p>{mission.checkIn.notice}</p>
                    <p>{mission.decisionSupport?.review_action}</p>
                    <button onClick={() => openDock('timeline')}>
                      Inspect updated timeline <ArrowUpRight size={13} />
                    </button>
                    <button onClick={() => openDock('review')}>Export updated review</button>
                  </div>
                )}
              </div>
              <CsvUpload onUpload={upload} busy={busy} />
            </div>
          ),
          timeline: mission ? (
            <TimelineView key={mission.key} timeline={mission.timeline} blocked={!!blocked} />
          ) : (
            <p>Load a mission to inspect its timeline.</p>
          ),
          review: mission ? (
            <ReviewWorkflow key={mission.key} session={copilot} />
          ) : (
            <p>Load a mission to create a review.</p>
          ),
          risks: <SpaceRiskExplorer />,
          sources: (
            <section id="scientific-evidence">
              <h2>Scientific context</h2>
              <p>
                Research references are background, not NASA/CSA telemetry or clinical validation of
                this prototype.
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
                    <ul className="evidence-grid">
                      {evidence.references.map((item) => (
                        <li key={item.url}>
                          <a href={item.url} target="_blank" rel="noreferrer">
                            {item.title} <ArrowUpRight size={12} />
                          </a>
                          <small>{item.organization}</small>
                          <p>{item.summary}</p>
                          <p>{item.limitation}</p>
                        </li>
                      ))}
                    </ul>
                  )}
                </>
              )}
            </section>
          ),
        }}
      />
      <footer className="console-footer">
        <span>
          <span className="live-dot" /> SYNTHETIC DATA / NOT A MEDICAL DEVICE
        </span>
        <span>Active data source: {source}</span>
        <span>PYTHON DOMAIN ENGINE · v1.5 COPILOT</span>
      </footer>
    </main>
  );
}
