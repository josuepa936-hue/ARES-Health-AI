import { useEffect, useRef, useState } from 'react';
import { api, message } from '../api';
import {
  reviewActions,
  type ActionId,
  type AuditEvent,
  type ComprehensiveReport,
  type CopilotContext,
  type CopilotResponse,
  type Question,
  type WorkflowState,
} from '../copilot-contract';
type Turn = Question & { response: CopilotResponse };
type Session = {
  scope?: number;
  briefing?: CopilotResponse;
  turns: Turn[];
  audit: AuditEvent[];
  state: WorkflowState;
  note: string;
  report?: ComprehensiveReport;
  error: string;
  loading: boolean;
  exporting: boolean;
};
const initial = (scope?: number): Session => ({
  scope,
  turns: [],
  audit: [],
  state: 'PENDING_REVIEW',
  note: '',
  error: '',
  loading: false,
  exporting: false,
});
export function useMissionCopilot(context: CopilotContext | undefined, scope: number | undefined) {
  const [session, setSession] = useState<Session>(initial());
  const [retry, setRetry] = useState(0);
  const chat = useRef<AbortController | null>(null);
  const exporting = useRef<AbortController | null>(null);
  useEffect(() => {
    chat.current?.abort();
    exporting.current?.abort();
    setSession({ ...initial(scope), loading: !!context });
    if (!context) return;
    const controller = new AbortController();
    chat.current = controller;
    api
      .copilot(context, '', 0, undefined, controller.signal)
      .then((briefing) => {
        if (!controller.signal.aborted)
          setSession((current) => ({ ...current, briefing, loading: false }));
      })
      .catch((error) => {
        if (!controller.signal.aborted)
          setSession((current) => ({ ...current, error: message(error), loading: false }));
      });
    return () => {
      controller.abort();
      chat.current?.abort();
      exporting.current?.abort();
    };
  }, [context, scope, retry]);
  const current = session.scope === scope ? session : initial(scope);
  function invalidateExport() {
    exporting.current?.abort();
    setSession((state) => ({ ...state, report: undefined, exporting: false, error: '' }));
  }
  async function ask(question: string) {
    if (
      !context ||
      !current.briefing ||
      current.loading ||
      current.turns.length >= 20 ||
      !question.trim()
    )
      return;
    chat.current?.abort();
    const controller = new AbortController();
    chat.current = controller;
    invalidateExport();
    setSession((state) => ({ ...state, loading: true }));
    const turn = current.turns.length + 1;
    try {
      const response = await api.copilot(
        context,
        question.trim(),
        turn,
        current.briefing.context_ref,
        controller.signal,
      );
      if (!controller.signal.aborted)
        setSession((state) => ({
          ...state,
          turns: [...state.turns, { turn, question: question.trim(), response }],
          loading: false,
        }));
    } catch (error) {
      if (!controller.signal.aborted)
        setSession((state) => ({ ...state, error: message(error), loading: false }));
    }
  }
  function append(
    event:
      | Omit<Extract<AuditEvent, { action: ActionId }>, 'sequence'>
      | Omit<Extract<AuditEvent, { action: 'review_state' }>, 'sequence'>
      | Omit<Extract<AuditEvent, { action: 'note' }>, 'sequence'>,
  ) {
    if (current.audit.length >= 64) return;
    invalidateExport();
    setSession((state) => ({
      ...state,
      audit: [
        ...state.audit,
        {
          ...event,
          sequence: state.audit.length + 1,
          // Capture the user's real click-time UTC, not the synthetic
          // observation clock or an unverified server timestamp.
          recorded_at_utc: new Date().toISOString(),
        } as AuditEvent,
      ],
      state: event.action === 'review_state' ? event.review_state : state.state,
      note: event.action === 'note' ? event.note : state.note,
    }));
  }
  async function buildReport() {
    if (!context || !current.briefing || current.loading) return;
    exporting.current?.abort();
    const controller = new AbortController();
    exporting.current = controller;
    setSession((state) => ({ ...state, exporting: true, error: '', report: undefined }));
    try {
      const report = await api.comprehensiveReport(
        context,
        current.briefing.context_ref,
        current.turns.map(({ turn, question }) => ({ turn, question })),
        current.audit,
        controller.signal,
      );
      if (!controller.signal.aborted)
        setSession((state) => ({ ...state, exporting: false, report }));
    } catch (error) {
      if (!controller.signal.aborted)
        setSession((state) => ({ ...state, exporting: false, error: message(error) }));
    }
  }
  const actions = Object.fromEntries(reviewActions.map((action) => [action.id, false]));
  current.audit.forEach((event) => {
    if ('checked' in event) actions[event.action] = event.checked;
  });
  return {
    ...current,
    actions,
    ask,
    buildReport,
    setAction: (action: ActionId, checked: boolean) => append({ action, checked }),
    setReviewState: (review_state: WorkflowState) =>
      append({ action: 'review_state', review_state }),
    recordNote: (note: string) => append({ action: 'note', note }),
    retry: () => setRetry((value) => value + 1),
  };
}
export type CopilotSession = ReturnType<typeof useMissionCopilot>;
