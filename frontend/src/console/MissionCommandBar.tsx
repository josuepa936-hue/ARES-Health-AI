import { Info, RefreshCw, ShieldCheck } from 'lucide-react';
import { useState } from 'react';
import type { ScenarioId, Snapshot } from '../contracts';
export function MissionCommandBar({
  scenarios,
  scenario,
  snapshot,
  source,
  busy,
  onScenario,
  onReload,
}: {
  scenarios: { id: ScenarioId; label: string }[];
  scenario: ScenarioId | '';
  snapshot?: Snapshot;
  source: string;
  busy: boolean;
  onScenario: (value: ScenarioId) => void;
  onReload: () => void;
}) {
  const [info, setInfo] = useState(false);
  return (
    <>
      <div className="mission-command-bar">
        <span className="command-id">
          <span className="live-dot" /> MISSION / {snapshot?.summary.crew_id ?? 'SIM-001'}
        </span>
        <label className="scenario-control">
          <span>SCENARIO</span>
          <select
            aria-label="Demo scenario"
            value={scenario}
            disabled={!scenarios.length}
            onChange={(e) => onScenario(e.target.value as ScenarioId)}
          >
            <option value="" disabled>
              Awaiting catalog
            </option>
            {scenarios.map((item) => (
              <option key={item.id} value={item.id}>
                {item.label}
              </option>
            ))}
          </select>
        </label>
        <button
          className="icon-button"
          aria-label="Reload selected scenario"
          disabled={!scenario || busy}
          onClick={onReload}
        >
          <RefreshCw size={14} className={busy ? 'loading-icon' : ''} />
        </button>
        <span className="command-source">{source}</span>
        <time>
          {snapshot?.observations.at(-1)?.timestamp_utc?.replace('T', ' ').replace('Z', ' UTC') ??
            'AWAITING OBSERVATIONS'}
        </time>
        <button
          className="icon-button"
          aria-label="Demo information and asset attribution"
          aria-expanded={info}
          onClick={() => setInfo((value) => !value)}
        >
          <Info size={17} />
        </button>
      </div>
      {info && (
        <aside className="info-popover">
          <div>
            <ShieldCheck size={18} />
            <strong>SYNTHETIC DATA / NOT A MEDICAL DEVICE</strong>
            <button onClick={() => setInfo(false)}>Close</button>
          </div>
          <p>
            No diagnosis, clinical validation, real crew telemetry or NASA endorsement. Do not enter
            personal health data. Values, comparisons and explanations come from the Python API.
          </p>
          <p>
            Original AI-generated illustrative human: OpenAI image generation, 2026. Output rights
            assigned to the user under OpenAI Terms. It is a clothed, anatomical navigation
            illustration, not a licensed clinical anatomy model, patient image or diagnostic
            reference. No third-party anatomical asset was borrowed.
          </p>
        </aside>
      )}
    </>
  );
}
