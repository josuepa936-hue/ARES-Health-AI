import { lazy, Suspense, useState } from 'react';
import App from './App';
import { PUBLIC_DEMO } from './publicDemo';
const ResearchLab = lazy(() => import('./components/ResearchLab'));
const NasaResearch = lazy(() => import('./components/NasaResearch'));

/** Research is never fetched until explicitly opened; mission state stays separate. */
export default function Workspace() {
  const [mode, setMode] = useState<'mission' | 'research' | 'nasa'>('mission');
  return (
    <div className="mission-shell">
      <div className="global-header">
        <div className="brand-lockup">
          <span className="brand-mark">ARES</span>
          <span className="brand-subtitle">HEALTH AI / MISSION SYSTEMS</span>
        </div>
        <span className="global-status">INDEPENDENT DEMONSTRATION</span>
      </div>
      {PUBLIC_DEMO && (
        <p className="public-demo-notice" role="note">
          Experimental public demo · Fictional data only. Not a medical device or a NASA-authorized
          system. Never enter real health or personal information. Requests are processed
          transiently; reports download to your device.
        </p>
      )}
      <nav className="workspace-nav" aria-label="Workspace mode">
        <button aria-pressed={mode === 'mission'} onClick={() => setMode('mission')}>
          Synthetic mission demo
        </button>
        {!PUBLIC_DEMO && (
          <>
            <button aria-pressed={mode === 'research'} onClick={() => setMode('research')}>
              Optional research lab
            </button>
            <button aria-pressed={mode === 'nasa'} onClick={() => setMode('nasa')}>
              NASA space biology
            </button>
          </>
        )}
      </nav>
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
