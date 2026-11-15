import { lazy, Suspense, useState } from 'react';
import App from './App';
const ResearchLab = lazy(() => import('./components/ResearchLab'));
const NasaResearch = lazy(() => import('./components/NasaResearch'));

/** Research is never fetched until explicitly opened; mission state stays separate. */
export default function Workspace() {
  const [mode, setMode] = useState<'mission' | 'research' | 'nasa'>('mission');
  return (
    <div className="mission-shell">
      <div className="global-header">
        <div className="brand-lockup">
          <span className="brand-mark">ARES / HEALTH AI</span>
          <span className="brand-subtitle">Astronaut Risk Evaluation System · Demonstration Console</span>
        </div>
        <span className="global-status">INDEPENDENT RESEARCH PROTOTYPE · SYNTHETIC CREW</span>
      </div>
      <nav className="workspace-nav" aria-label="Workspace mode">
        <button aria-pressed={mode === 'mission'} onClick={() => setMode('mission')}>
          Synthetic mission demo
        </button>
        <button aria-pressed={mode === 'research'} onClick={() => setMode('research')}>
          Optional research lab
        </button>
        <button aria-pressed={mode === 'nasa'} onClick={() => setMode('nasa')}>
          NASA space biology
        </button>
      </nav>
      {mode === 'mission' && (
        <nav className="quick-nav" aria-label="Mission workflow navigation">
          <a href="#crew-checkin">Crew check-in</a>
          <a href="#mission-results">Mission assessment</a>
          <a href="#mission-timeline">Timeline</a>
          <a href="#mission-review">Review report</a>
          <a href="#space-risks">Spaceflight hazards</a>
          <a href="#scientific-evidence">Evidence</a>
        </nav>
      )}
      <div hidden={mode !== 'mission'}>
        <App />
      </div>
      {mode === 'research' && (
        <Suspense fallback={<p role="status">Opening optional research view…</p>}>
          <ResearchLab />
        </Suspense>
      )}
      {mode === 'nasa' && (
        <Suspense fallback={<p role="status">Opening NASA OSDR research view…</p>}>
          <NasaResearch />
        </Suspense>
      )}
    </div>
  );
}
