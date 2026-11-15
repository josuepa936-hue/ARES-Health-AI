import { z } from 'zod';
const finite = z.number().finite();
const point = z.object({ sample: z.number().int().min(0).max(21599), mv: finite });
export const researchSchema = z
  .object({
    schema_version: z.literal('1.2-research'),
    record: z.literal('100'),
    data_provenance: z.literal('public_research_ecg'),
    status: z.enum(['benchmarked', 'abstained']),
    reasons: z.array(z.string()),
    source: z.object({
      dataset: z.literal('MIT-BIH Arrhythmia Database'),
      version: z.literal('1.0.0'),
      url: z.literal('https://physionet.org/content/mitdb/1.0.0/'),
      doi: z.literal('https://doi.org/10.13026/C2F305'),
      context: z.string(),
    }),
    protocol: z.object({
      sampling_rate_hz: z.literal(360),
      tolerance_ms: z.literal(150),
      scoring_start_sample: z.literal(360),
      scoring_end_sample_exclusive: z.literal(21240),
      segment_end_sample_exclusive: z.literal(21600),
      matching: z.string(),
      display_stride: z.literal(12),
    }),
    processing_versions: z.record(z.string()),
    quality: z.object({ status: z.string(), checks: z.array(z.string()) }),
    metrics: z
      .object({
        tp: z.number().int(),
        fp: z.number().int(),
        fn: z.number().int(),
        precision: finite.nullable(),
        recall: finite.nullable(),
        f1: finite.nullable(),
        mean_absolute_timing_error_ms: finite.nullable(),
      })
      .nullable(),
    waveform: z.array(point).max(1800),
    detected_peaks: z.array(point).max(500),
    reference_peaks: z.array(point).max(500),
    matches: z
      .array(
        z.object({
          reference_sample: z.number().int(),
          detected_sample: z.number().int(),
          absolute_error_ms: finite,
        }),
      )
      .max(500),
    discrepancies: z
      .array(z.object({ type: z.enum(['FP', 'FN']), sample: z.number().int() }))
      .max(1000),
    annotation_counts: z.record(z.number().int().nonnegative()).nullable(),
    acquisition: z.record(z.unknown()).nullable().optional(),
    disclaimer: z.string(),
  })
  .refine((data) =>
    data.status === 'benchmarked'
      ? data.metrics !== null && data.waveform.length > 0
      : data.metrics === null && data.waveform.length === 0,
  );
export type ResearchResult = z.infer<typeof researchSchema>;
