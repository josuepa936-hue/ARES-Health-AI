/** Runtime-checked API shapes. Python owns all biomedical rules and statistics. */
import { z } from 'zod';
const number = z.number().finite();
const strings = z.array(z.string());
export const assessment = z.enum([
  'NO_DEMO_RULE_TRIGGERED',
  'CHANGE_FOR_REVIEW',
  'DATA_QUALITY_BLOCKED',
  'INSUFFICIENT_DATA',
]);
export const scenarioId = z.enum(['stable', 'heart_rate_shift', 'sleep_shift', 'incomplete']);
export type ScenarioId = z.infer<typeof scenarioId>;
export const scenariosSchema = z.object({
  scenarios: z.array(z.object({ id: scenarioId, label: z.string() })),
  data_provenance: z.literal('synthetic'),
  simulation_only: z.literal(true),
});
export const observationSchema = z.object({
  timestamp_utc: z.string().nullable(),
  crew_id: z.string().nullable(),
  source_type: z.string().nullable(),
  resting_hr_bpm: number.nullable(),
  sleep_hours: number.nullable(),
  activity_minutes: number.nullable(),
});
export type Observation = z.infer<typeof observationSchema>;
export const flagSchema = z.object({
  metric: z.string(),
  baseline_mean: number,
  recent_mean: number,
  difference: number,
  unit: z.string(),
  explanation: z.string(),
});
export const reportSchema = z
  .object({
    schema_version: z.string(),
    application: z.string(),
    scenario: z.string(),
    data_provenance: z.literal('synthetic'),
    assessment,
    observation_count: number,
    review_flags: z.array(flagSchema),
    data_quality_issues: strings,
    analysis_limitations: strings,
    review_state: z.enum(['Pending review', 'Reviewed in demo']),
    reviewer_note: z.string(),
    disclaimer: z.string(),
  })
  .passthrough();
export type ReviewReport = z.infer<typeof reportSchema>;
const snapshotBase = z.object({
  schema_version: z.string(),
  scenario: z.string(),
  data_provenance: z.literal('synthetic'),
  simulation_only: z.literal(true),
  assessment,
  summary: z.object({
    recorded_days: number,
    completeness_pct: number,
    quality_findings: number,
    review_flags: number,
    crew_id: z.string(),
  }),
  observations: z.array(observationSchema),
  quality_issues: strings,
  analysis_limitations: strings,
  review_flags: z.array(flagSchema),
  descriptive_signals: z.array(
    z.object({
      metric: z.string(),
      label: z.string(),
      unit: z.string(),
      baseline_mean: number,
      recent_mean: number,
      delta: number,
      full_median: number,
      robust_variability: number,
      theil_sen_slope_per_day: number,
      n: number,
    }),
  ),
  descriptive_statistics_notice: z.string(),
  guidance: z.object({
    state: assessment,
    heading: z.string(),
    meaning: z.string(),
    review_steps: strings,
  }),
  disclaimer: z.string(),
  review_report: reportSchema.optional(),
});
// This is response consistency checking, not a second biomedical rule engine.
const consistentGuidance = (snapshot: z.infer<typeof snapshotBase>) =>
  snapshot.assessment === snapshot.guidance.state;
export const snapshotSchema = snapshotBase.refine(consistentGuidance);
export const csvSnapshotSchema = snapshotBase
  .extend({ review_report: reportSchema })
  .refine(consistentGuidance)
  .refine(
    (snapshot) =>
      snapshot.review_report.scenario === snapshot.scenario &&
      snapshot.review_report.assessment === snapshot.assessment,
  );
export type Snapshot = z.infer<typeof snapshotSchema>;
export const eventTypes = [
  'observation',
  'analysis_status',
  'trend_change',
  'data_quality',
] as const;
export type EventType = (typeof eventTypes)[number];
export const timelineSchema = z.object({
  schema_version: z.string(),
  assessment,
  scenario: z.string(),
  data_provenance: z.literal('synthetic'),
  simulation_only: z.literal(true),
  events: z.array(
    z.object({
      id: z.string(),
      type: z.enum(eventTypes),
      timestamp_utc: z.string().nullable(),
      observation_index: number.nullable(),
      explanation: z.string(),
      details: z.record(z.unknown()),
    }),
  ),
  disclaimer: z.string(),
});
export type Timeline = z.infer<typeof timelineSchema>;
export const evidenceSchema = z.object({
  usage: z.string(),
  references: z.array(
    z.object({
      indicator: z.string(),
      title: z.string(),
      organization: z.string(),
      url: z
        .string()
        .url()
        .refine((url) => url.startsWith('https://')),
      summary: z.string(),
      limitation: z.string(),
    }),
  ),
});
export type Evidence = z.infer<typeof evidenceSchema>;
