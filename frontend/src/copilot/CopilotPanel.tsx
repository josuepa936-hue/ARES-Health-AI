import { useState, useLayoutEffect, useRef, type FormEvent } from 'react';
import { Send, MessagesSquare, ArrowRight, Maximize2, Minimize2 } from 'lucide-react';
import type { CopilotSession } from './useMissionCopilot';
import type { Snapshot } from '../contracts';
import type { CopilotContext } from '../copilot-contract';
import { MissionWellness } from './MissionWellness';
import { EvidenceView } from './EvidenceView';
export function CopilotPanel({
  session,
  onReview,
  snapshot,
  context,
}: {
  session: CopilotSession;
  onReview: () => void;
  snapshot?: Snapshot;
  context: CopilotContext;
}) {
  const [question, setQuestion] = useState('');
  const [focused, setFocused] = useState(false);
  const [dockedHeight, setDockedHeight] = useState(0);
  const [briefOpen, setBriefOpen] = useState(true);
  const [announcement, setAnnouncement] = useState('');
  const dialog = useRef<HTMLDialogElement>(null);
  const history = useRef<HTMLDivElement>(null);
  const expandButton = useRef<HTMLButtonElement>(null);
  const turnNodes = useRef(new Map<number, HTMLElement>());
  const previousCount = useRef(session.turns.length);
  const pendingTurn = useRef<number | null>(null);
  // Reuse one dialog subtree so changing reading modes preserves drafts and history.
  // Native modal behavior traps focus and makes the background console inert.
  useLayoutEffect(() => {
    const element = dialog.current;
    if (!element) return;
    if (element.open) {
      if (element.close) element.close();
      else element.removeAttribute('open');
    }
    if (focused) {
      if (element.showModal) element.showModal();
      else element.setAttribute('open', '');
    } else {
      if (element.show) element.show();
      else element.setAttribute('open', '');
    }
    const previousOverflow = document.body.style.overflow;
    if (focused) document.body.style.overflow = 'hidden';
    if (focused) expandButton.current?.focus({ preventScroll: true });
    return () => {
      document.body.style.overflow = previousOverflow;
      if (element.open) {
        if (element.close) element.close();
        else element.removeAttribute('open');
      }
    };
  }, [focused]);
  useLayoutEffect(() => {
    const reader = history.current;
    if (!reader) return;
    // Give a short new turn room to align at the top after a long previous answer.
    // Docked document flow must not grow itself in a resize feedback loop.
    const measure = () =>
      reader.style.setProperty(
        '--answer-min-height',
        `${!focused ? 0 : Math.max(0, reader.clientHeight - 20)}px`,
      );
    measure();
    if (typeof ResizeObserver === 'undefined') return;
    const observer = new ResizeObserver(measure);
    observer.observe(reader);
    return () => observer.disconnect();
  }, [focused]);
  useLayoutEffect(() => {
    if (session.turns.length > previousCount.current) {
      const latest = session.turns.at(-1)!;
      pendingTurn.current = latest.turn;
      setBriefOpen(false);
      setAnnouncement(
        `Answer ${latest.turn} is ready. Focus is at the start of your question and response.`,
      );
    }
    previousCount.current = session.turns.length;
  }, [session.turns.length]);
  useLayoutEffect(() => {
    if (pendingTurn.current === null) return;
    // Only new answers and entering focus move the reader; evidence disclosure does not.
    const frame = requestAnimationFrame(() => {
      const node = turnNodes.current.get(pendingTurn.current!);
      const reader = history.current;
      if (node && reader) {
        if (!focused) node.scrollIntoView({ block: 'start', behavior: 'instant' });
        else
          reader.scrollTop = Math.max(
            0,
            node.getBoundingClientRect().top -
              reader.getBoundingClientRect().top +
              reader.scrollTop -
              12,
          );
        node.querySelector<HTMLElement>('[data-turn-heading]')?.focus({ preventScroll: true });
      }
      pendingTurn.current = null;
    });
    return () => cancelAnimationFrame(frame);
  }, [session.turns.length, briefOpen, focused]);
  function toggleFocus() {
    // Hold the document's reading position while its dialog moves into the top layer.
    if (!focused) setDockedHeight(dialog.current?.getBoundingClientRect().height ?? 0);
    pendingTurn.current = focused ? null : (session.turns.at(-1)?.turn ?? null);
    setFocused((value) => !value);
    if (focused) requestAnimationFrame(() => expandButton.current?.focus({ preventScroll: true }));
  }
  function review() {
    setFocused(false);
    onReview();
    requestAnimationFrame(() => document.getElementById('tab-review')?.focus());
  }
  async function submit(event: FormEvent) {
    event.preventDefault();
    if (!question.trim()) return;
    await session.ask(question);
    setQuestion('');
  }
  const prompts = session.briefing?.suggested_questions ?? [];
  return (
    <div style={{ minHeight: focused ? dockedHeight : undefined }}>
      <dialog
        ref={dialog}
        className={`copilot-dialog ${focused ? 'copilot-focus-mode' : ''}`}
        aria-label={
          focused ? 'Expanded ARES Copilot conversation' : 'Docked ARES Copilot conversation'
        }
        aria-modal={focused}
        onCancel={(event) => {
          event.preventDefault();
          setFocused(false);
          requestAnimationFrame(() => expandButton.current?.focus({ preventScroll: true }));
        }}
      >
        <section className="copilot-panel" aria-label="ARES mission copilot">
          <header className="copilot-title">
            <div>
              <h2>
                <MessagesSquare size={17} /> ARES Copilot
              </h2>
              <p>Deterministic · offline · not an LLM</p>
              <p>
                {focused
                  ? 'Focused reading · cockpit is behind this dialog'
                  : 'Full-size cockpit above · read below or expand the conversation'}
              </p>
            </div>
            <div className="copilot-reader-controls">
              <button onClick={review}>
                Review workflow <ArrowRight size={14} />
              </button>
              <button ref={expandButton} aria-expanded={focused} onClick={toggleFocus}>
                {focused ? <Minimize2 size={15} /> : <Maximize2 size={15} />}{' '}
                {focused ? 'Restore docked conversation' : 'Focus / expand conversation'}
              </button>
            </div>
          </header>
          <p className="copilot-assessment">
            <span>Current mission assessment</span>
            <strong>{session.briefing?.assessment ?? 'Awaiting Python briefing'}</strong>
          </p>
          <span role="status" className="sr-only">
            {announcement}
          </span>
          <div
            className="copilot-history"
            ref={history}
            tabIndex={0}
            role="region"
            aria-label="Conversation reading area"
          >
            {session.error && (
              <div role="alert">
                {session.error}
                <button onClick={session.retry}>Reset and retry copilot</button>
              </div>
            )}

            {!session.briefing && session.loading && (
              <p role="status">Recalculating grounded mission briefing…</p>
            )}
            {session.briefing && (
              <>
                <details
                  className="copilot-briefing"
                  open={briefOpen}
                  onToggle={(event) => setBriefOpen(event.currentTarget.open)}
                >
                  <summary>
                    Current mission briefing <span>· Python analysis</span>
                  </summary>
                  <p>{session.briefing.answer}</p>
                  <EvidenceView response={session.briefing} snapshot={snapshot} />
                </details>
                <MissionWellness
                  context={context}
                  contextRef={session.briefing.context_ref}
                  onReview={review}
                />
                <details className="copilot-suggestions">
                  <summary>
                    Suggested questions <span>· {prompts.length} supported topics</span>
                  </summary>
                  <div>
                    {prompts.map((item) => (
                      <button
                        key={item}
                        disabled={session.loading || session.turns.length >= 20}
                        onClick={() => session.ask(item)}
                      >
                        {item}
                        <ArrowRight size={13} />
                      </button>
                    ))}
                  </div>
                </details>
                <div
                  className="copilot-transcript"
                  role="log"
                  aria-label="Current mission conversation"
                  aria-live="off"
                >
                  {session.turns.map((turn) => (
                    <article
                      key={turn.turn}
                      data-testid={`copilot-turn-${turn.turn}`}
                      ref={(node) => {
                        if (node) turnNodes.current.set(turn.turn, node);
                        else turnNodes.current.delete(turn.turn);
                      }}
                    >
                      <h3 data-turn-heading tabIndex={-1}>
                        Conversation turn {turn.turn}
                      </h3>
                      <div className="copilot-question">
                        <span>Your fictional question</span>
                        <p>{turn.question}</p>
                      </div>
                      <div className="copilot-answer">
                        <h4>
                          ARES response <span>· {turn.response.intent.replaceAll('_', ' ')}</span>
                        </h4>
                        <p>{turn.response.answer}</p>
                      </div>
                      <EvidenceView response={turn.response} snapshot={snapshot} />
                    </article>
                  ))}
                </div>
                {!session.turns.length && (
                  <p className="copilot-empty">
                    Ask a mission question below, or open Suggested questions. Expand the
                    conversation for uninterrupted reading.
                  </p>
                )}
                {session.loading && <p role="status">Checking current Python evidence…</p>}
              </>
            )}
          </div>
          {session.briefing && (
            <form className="copilot-compose" onSubmit={submit}>
              <label htmlFor="copilot-question">Fictional mission question</label>
              <div>
                <input
                  id="copilot-question"
                  value={question}
                  onChange={(event) => setQuestion(event.target.value)}
                  maxLength={240}
                  placeholder="Ask what changed, about the baseline, or why data are blocked"
                  disabled={session.loading || session.turns.length >= 20}
                />
                <button
                  disabled={session.loading || !question.trim() || session.turns.length >= 20}
                >
                  <Send size={15} /> Ask
                </button>
              </div>
              <small>
                {session.turns.length}/20 turns · Fictional data only · Review states do not grant
                medical authorization.
              </small>
            </form>
          )}
        </section>
      </dialog>
    </div>
  );
}
