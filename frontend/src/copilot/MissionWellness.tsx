import { useEffect, useState } from 'react';
import { ArrowRight, BookOpen, HeartPulse } from 'lucide-react';
import { api, message } from '../api';
import type { CopilotContext, MissionWellness } from '../copilot-contract';

export function MissionWellness({
  context,
  contextRef,
  onReview,
}: {
  context: CopilotContext;
  contextRef?: string;
  onReview: () => void;
}) {
  const [guide, setGuide] = useState<MissionWellness>();
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  useEffect(() => {
    setGuide(undefined);
    setError('');
    if (!contextRef) return;
    const controller = new AbortController();
    setLoading(true);
    api.wellness(context, contextRef, controller.signal)
      .then((result) => {
        if (!controller.signal.aborted) {
          if (result.context_ref !== contextRef) {
            setError('Mission context changed. Reload the current briefing.');
          } else {
            setGuide(result);
          }
        }
      })
      .catch((reason) => {
        if (!controller.signal.aborted) setError(message(reason));
      })
      .finally(() => {
        if (!controller.signal.aborted) setLoading(false);
      });
    return () => controller.abort();
  }, [context, contextRef]);

  return (
    <details className="mission-wellness" aria-label="Mission Wellness and Procedures">
      <summary>
        <HeartPulse size={16} aria-hidden="true" />
        <strong>Mission Wellness &amp; Procedures</strong>
        <span>3 educational topics · NASA research context</span>
      </summary>
      {loading && <p role="status">Loading evidence-linked wellness guidance…</p>}
      {error && <p role="alert">{error}</p>}
      {guide && (
        <div className="mission-wellness-content">
          <p className="wellness-state">
            <strong>{guide.assessment}</strong> — {guide.summary}
          </p>
          <div className="wellness-topics">
            {guide.topics.map((topic) => (
              <article key={topic.id}>
                <header>
                  <h4>{topic.title}</h4>
                  <span>
                    {topic.comparison === 'withheld'
                      ? 'Comparison withheld'
                      : topic.illustrative_flag
                        ? 'Illustrative change to review'
                        : 'Educational context'}
                  </span>
                </header>
                <p>{topic.research_context}</p>
                <h5>What can be reviewed?</h5>
                <p>{topic.review_step}</p>
                <h5>Fictional routine example</h5>
                <p>{topic.routine_example}</p>
                <p className="wellness-limitation">{topic.limitation}</p>
                <a href={topic.source_url} target="_blank" rel="noopener noreferrer">
                  <BookOpen size={14} aria-hidden="true" />
                  NASA research: {topic.source_title}
                </a>
              </article>
            ))}
          </div>
          <p className="wellness-safety">{guide.disclaimer}</p>
          <p className="wellness-safety">
            These are examples for a fictional review, not scheduled reminders or
            authorized medical procedures. Nothing has been recorded automatically.
          </p>
          <button type="button" onClick={onReview}>
            Document a fictional review <ArrowRight size={14} aria-hidden="true" />
          </button>
        </div>
      )}
    </details>
  );
}
