import { useEffect, useState } from 'react';
import { api, message } from '../api';
import type { RiskGuide } from '../contracts';

/** Interactive NASA hazard context, not calibrated risk prediction. */
export function SpaceRiskExplorer() {
  const [guide, setGuide] = useState<RiskGuide>();
  const [selected, setSelected] = useState('gravity');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(true);
  const [reload, setReload] = useState(0);

  useEffect(() => {
    const controller = new AbortController();
    setLoading(true);
    setError('');
    api.riskGuide(controller.signal).then((data) => {
      if (!controller.signal.aborted) setGuide(data);
    }).catch((cause) => {
      if (!controller.signal.aborted) setError(message(cause));
    }).finally(() => {
      if (!controller.signal.aborted) setLoading(false);
    });
    return () => controller.abort();
  }, [reload]);

  const risk = guide?.risks.find((item) => item.id === selected) ?? guide?.risks[0];

  return (
    <section id="space-risks" className="mission-card" aria-label="NASA spaceflight risk explorer">
      <p className="eyebrow">04 / RESEARCH-BASED CONTEXT</p>
      <h2>Five hazards of human spaceflight</h2>
      <p>
        Choose a NASA research hazard to understand what ARES can and <strong>cannot</strong>
        measure. The hazard buttons do not indicate medical status or risk severity.
      </p>
      {loading && <p role="status">Loading NASA hazard context from ARES API…</p>}
      {error && (
        <>
          <p role="alert">{error}</p>
          <button onClick={() => setReload((value) => value + 1)}>Retry spaceflight risk guide</button>
        </>
      )}
      {guide && risk && (
        <>
          <div className="risk-selector" role="group" aria-label="Select spaceflight hazard">
            {guide.risks.map((item) => (
              <button key={item.id} aria-pressed={item.id === risk.id}
                onClick={() => setSelected(item.id)}>
                {item.title}
              </button>
            ))}
          </div>
          <article className="hazard-detail">
            <p className="eyebrow">SELECTED NASA HAZARD / {risk.id.toUpperCase()}</p>
            <h3>{risk.title}</h3>
            <p>{risk.spaceflight_context}</p>
            <h4>Relevant observations to consider</h4>
            <ul>{risk.candidate_observations.map((item) => <li key={item}>{item}</li>)}</ul>
            <h4>What ARES currently measures</h4>
            <p>{risk.ares_current_coverage}</p>
            <h4>Suggested review of approved procedures</h4>
            <p>{risk.crew_review}</p>
            <a href={risk.reference_url} target="_blank" rel="noreferrer">
              Read NASA Human Research Program source
            </a>
          </article>
          <p className="notice-neutral">{guide.disclaimer}</p>
        </>
      )}
    </section>
  );
}
