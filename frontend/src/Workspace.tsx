import { lazy, Suspense, useEffect, useState } from 'react';
import aresBrand from './assets/ares-brand.webp';
import App from './App';
import { PUBLIC_DEMO } from './publicDemo';
const ResearchLab = lazy(() => import('./components/ResearchLab'));
const NasaResearch = lazy(() => import('./components/NasaResearch'));

/** Research is never fetched until explicitly opened; mission state stays separate. */
export default function Workspace() {
  const [mode, setMode] = useState<'mission' | 'research' | 'nasa'>('mission');
  // Vite fingerprints the local brand asset, so it is available through FastAPI /assets
  // in both Render and the standalone offline build.
  useEffect(() => {
    const favicon = document.createElement('link');
    favicon.rel = 'icon';
    favicon.type = 'image/webp';
    favicon.href = aresBrand;
    favicon.setAttribute('data-ares-brand', 'true');
    document.head.appendChild(favicon);
    return () => favicon.remove();
  }, []);
  return (
    <div className="mission-shell">
      <div className="global-header">
        <div className="brand-lockup">
          <span className="brand-logo-tile">
            <img className="brand-logo-image" src={aresBrand} alt="ARES letter A with orbital satellite and ARES wordmark" width="67" height="46" />
          </span>
          <span className="brand-wordmark">
            <span className="brand-mark">ARES</span>
            <span className="brand-subtitle">HEALTH AI / MISSION SYSTEMS</span>
            <span className="brand-ai-disclosure">AI-GENERATED IMAGE</span>
          </span>
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
