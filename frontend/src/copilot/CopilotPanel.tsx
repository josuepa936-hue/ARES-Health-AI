import { useState, useEffect, useRef, type FormEvent } from 'react';
import { BookOpen, Send, MessagesSquare, ArrowRight } from 'lucide-react';
import type { CopilotResponse } from '../copilot-contract';
import type { CopilotSession } from './useMissionCopilot';
export function WhyResponse({ response }: { response: CopilotResponse }) {
  return (
    <details className="copilot-evidence">
      <summary>
        <BookOpen size={12} /> Why this response · {response.evidence_refs.length} evidence
        references
      </summary>
      <p>
        Context {response.context_ref} · {response.assessment}
      </p>
      {response.evidence_refs.length ? (
        <ul>
          {response.evidence_refs.map((ref) => (
            <li key={ref.id}>
              <code>{ref.id}</code>
              {ref.timestamp_utc && <time>{ref.timestamp_utc}</time>}
              {ref.metric && (
                <span>
                  {ref.metric} ·{' '}
                  {ref.value ??
                    (ref.absolute_difference === undefined
                      ? ''
                      : `rule ≥ ${ref.absolute_difference}`)}{' '}
                  {ref.unit}
                </span>
              )}
              {ref.window && <span>{ref.window} window</span>}
              {ref.timeline_id && <span>Timeline: {ref.timeline_id}</span>}
              {ref.text && <p>{ref.text}</p>}
              {ref.url && (
                <a href={ref.url} target="_blank" rel="noreferrer">
                  {ref.title ?? 'Official source'}
                </a>
              )}
            </li>
          ))}
        </ul>
      ) : (
        <p>
          This response states a supported review-policy limitation; no physiological inference or
          source fact was added.
        </p>
      )}
      <ul>
        {response.limitations.map((item) => (
          <li key={item}>{item}</li>
        ))}
      </ul>
    </details>
  );
}
export function CopilotPanel({
  session,
  onReview,
}: {
  session: CopilotSession;
  onReview: () => void;
}) {
  const [question, setQuestion] = useState('');
  const history = useRef<HTMLDivElement>(null);
  useEffect(() => {
    if (history.current) history.current.scrollTop = history.current.scrollHeight;
  }, [session.turns.length]);
  async function submit(event: FormEvent) {
    event.preventDefault();
    if (!question.trim()) return;
    await session.ask(question);
    setQuestion('');
  }
  return (
    <section className="copilot-panel" aria-label="ARES mission copilot">
      <div className="copilot-title">
        <h2>
          <MessagesSquare size={15} /> ARES Copilot
        </h2>
        <span>DETERMINISTIC / OFFLINE · NOT AN LLM</span>
        <button onClick={onReview}>
          Review workflow <ArrowRight size={12} />
        </button>
      </div>
      {session.loading && !session.briefing && (
        <p role="status">Recalculating grounded mission briefing…</p>
      )}
      {session.error && (
        <div role="alert">
          {session.error}
          <button onClick={session.retry}>Reset and retry copilot</button>
        </div>
      )}
      {session.briefing && (
        <div className="copilot-grid">
          <div className="copilot-conversation">
            <div className="copilot-history" ref={history}>
              <article className="copilot-briefing">
                <span className="eyebrow">
                  CURRENT MISSION BRIEFING · {session.briefing.assessment}
                </span>
                <p>{session.briefing.answer}</p>
                <WhyResponse response={session.briefing} />
              </article>
              <div
                className="copilot-transcript"
                role="log"
                aria-label="Current mission conversation"
                aria-live="polite"
              >
                {session.turns.map((turn) => (
                  <article key={turn.turn}>
                    <p className="copilot-question">{turn.question}</p>
                    <p>{turn.response.answer}</p>
                    <WhyResponse response={turn.response} />
                  </article>
                ))}
              </div>
              {session.loading && <p role="status">Checking current Python evidence…</p>}
            </div>
            <form className="copilot-compose" onSubmit={submit}>
              <label htmlFor="copilot-question">Fictional mission question</label>
              <div>
                <input
                  id="copilot-question"
                  value={question}
                  onChange={(event) => setQuestion(event.target.value)}
                  maxLength={240}
                  placeholder="Ask what changed or which evidence supports it"
                  disabled={session.loading || session.turns.length >= 20}
                />
                <button
                  disabled={session.loading || !question.trim() || session.turns.length >= 20}
                >
                  <Send size={13} /> Ask
                </button>
              </div>
              <small>
                {session.turns.length}/20 turns · no personal health information · bounded supported
                intents
              </small>
            </form>
          </div>
          <aside className="copilot-prompts">
            <span className="eyebrow">EVIDENCE-GROUNDED QUESTIONS</span>
            {session.briefing.suggested_questions.map((item) => (
              <button
                key={item}
                disabled={session.loading || session.turns.length >= 20}
                onClick={() => session.ask(item)}
              >
                {item}
                <ArrowRight size={11} />
              </button>
            ))}
            <p>
              Conversation and review actions reset with each new mission snapshot or page reload.
              No server case storage.
            </p>
          </aside>
        </div>
      )}
    </section>
  );
}
