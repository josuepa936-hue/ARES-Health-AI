import { lazy, Suspense, useState } from 'react';
import App from './App';
const ResearchLab = lazy(() => import('./components/ResearchLab'));
const NasaResearch = lazy(() => import('./components/NasaResearch'));

/** Research is never fetched until explicitly opened; mission state stays separate. */
export default function Workspace() {
  const [mode, setMode] = useState<'mission' | 'research' | 'nasa'>('mission');
  return (
    <>
      <nav aria-label="Workspace mode">
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
    </>
  );
}
