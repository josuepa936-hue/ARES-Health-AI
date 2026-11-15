import { z } from 'zod';
import { assessment, reportSchema, timelineSchema, type FictionalCheckInInput, type ScenarioId } from './contracts';
export type CopilotContext =
  | {
      kind: 'scenario';
      scenario: ScenarioId;
      seed: number;
      days: number;
      check_in?: Omit<FictionalCheckInInput, 'scenario' | 'seed' | 'days'>;
    }
  | { kind: 'synthetic_csv'; csv: string; fictional_attestation: true };
export const workflowStates = [
  'PENDING_REVIEW',
  'IN_PROGRESS',
  'AWAITING_AUTHORIZED_REVIEW',
  'DOCUMENTED',
] as const;
export type WorkflowState = (typeof workflowStates)[number];
export const reviewActions = [
  { id: 'source_units', label: 'Inspected fictional source and units' },
  { id: 'timestamp_context', label: 'Verified UTC timestamp and observation context' },
  { id: 'mission_protocol', label: 'Read the approved mission protocol (fictional action)' },
  {
    id: 'authorized_review',
    label: 'Requested authorized clinical review (fictional record only)',
  },
] as const;
export type ActionId = (typeof reviewActions)[number]['id'];
export type AuditEvent =
  | { sequence: number; recorded_at_utc?: string; action: ActionId; checked: boolean }
  | { sequence: number; recorded_at_utc?: string; action: 'review_state'; review_state: WorkflowState }
  | { sequence: number; recorded_at_utc?: string; action: 'note'; note: string };
export type Question = { turn: number; question: string };
export const responseSchema = z.object({
  answer: z.string(),
  intent: z.enum([
    'briefing',
    'changes',
    'baseline',
    'observations',
    'quality',
    'next_review',
    'hazards',
    'document_review',
    'unmonitored',
    'refusal',
    'unsupported',
  ]),
  context_ref: z.string().regex(/^ctx-[0-9a-f]{64}$/),
  scenario: z.string(),
  assessment,
  turn: z.number().int().min(0).max(20),
  engine: z.literal('deterministic-offline'),
  generative_model: z.literal(false),
  demo_only: z.literal(true),
  provenance: z.literal('synthetic'),
  evidence_refs: z
    .array(
      z
        .object({
          id: z.string(),
          kind: z.enum(['observation', 'rule', 'quality', 'source']),
          timestamp_utc: z.string().nullable().optional(),
          metric: z.string().optional(),
          value: z.number().finite().nullable().optional(),
          unit: z.string().optional(),
          text: z.string().optional(),
          window: z.string().optional(),
          timeline_id: z.string().optional(),
          absolute_difference: z.number().finite().optional(),
          title: z.string().optional(),
          url: z
            .string()
            .url()
            .refine((value) => value.startsWith('https://'))
            .optional(),
        })
        .passthrough(),
    )
    .max(100),
  limitations: z.array(z.string()),
  supported_actions: z.array(
    z.enum(['source_units', 'timestamp_context', 'mission_protocol', 'authorized_review']),
  ),
  suggested_questions: z.array(z.string()),
});
export type CopilotResponse = z.infer<typeof responseSchema>;
export const comprehensiveSchema = reportSchema
  .extend({
    // Comprehensive v1.5 reports use a single canonical four-state status.
    // Old standalone reports retain reportSchema's binary status contract.
    review_state: z.enum(workflowStates),
    legacy_review_state: z.enum(['Pending review', 'Reviewed in demo']),
    legacy_review_state_semantics: z.string(),
    application_version: z.literal('1.5'),
    context_ref: z.string(),
    copilot_schema_version: z.literal('1.5-demo'),
    copilot_application_version: z.literal('1.5'),
    // Reuse the verified timeline schema and keep its app version explicit.
    mission_timeline: timelineSchema.extend({ application_version: z.literal('1.5') }),
    copilot: z.object({
      engine: z.literal('deterministic-offline'),
      generative_model: z.literal(false),
      briefing: responseSchema,
      transcript: z.array(
        z.object({ turn: z.number(), question: z.string(), response: responseSchema }),
      ),
      omitted_unsupported_or_unsafe_turns: z.number(),
    }),
    fictional_review: z.object({
      review_state: z.enum(workflowStates),
      note: z.string(),
      actions: z.record(z.boolean()),
      audit_log: z.array(z.object({
        sequence: z.number().int().min(1).max(64),
        action: z.enum(['source_units', 'timestamp_context', 'mission_protocol', 'authorized_review', 'review_state', 'note']),
        checked: z.boolean().optional(),
        note: z.string().optional(),
        review_state: z.enum(workflowStates).optional(),
        recorded_at_utc: z.string().datetime({ offset: true }).optional(),
      }).passthrough()),
      audit_timestamp_source: z.string(),
      audit_timestamps_complete: z.boolean(),
      fictional_attestation: z.literal(true),
      clinical_authorization: z.literal(false),
      storage: z.string(),
      notice: z.string(),
    }),
  })
  .passthrough()
  .refine((report) => report.review_state === report.fictional_review.review_state,
    'Root review status and fictional workflow status must agree.')
  .refine((report) => report.application_version === report.copilot_application_version,
    'Report and copilot app versions must agree.');
export type ComprehensiveReport = z.infer<typeof comprehensiveSchema>;
