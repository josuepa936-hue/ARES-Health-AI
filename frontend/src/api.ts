import { z } from 'zod';
import { researchSchema } from './research-contract';
import { nasaStudySchema, nasaSamplesSchema } from './nasa-contract';
import {
  evidenceSchema,
  csvSnapshotSchema,
  reportSchema,
  scenariosSchema,
  snapshotSchema,
  timelineSchema,
  checkInSchema,
  riskGuideSchema,
  type FictionalCheckInInput,
  type ScenarioId,
  type ReviewReport,
} from './contracts';
export const MAX_CSV_BYTES = 1_000_000;
export class ApiError extends Error {
  constructor(
    message: string,
    public status?: number,
  ) {
    super(message);
    this.name = 'ApiError';
  }
}
function errorDetail(body: unknown): string | undefined {
  if (!body || typeof body !== 'object' || !('detail' in body)) return;
  const detail = body.detail;
  if (typeof detail === 'string') return detail;
  const csv = z.object({ errors: z.array(z.string()) }).safeParse(detail);
  if (csv.success) return csv.data.errors.join('; ');
  const validation = z
    .array(z.object({ loc: z.array(z.union([z.string(), z.number()])), msg: z.string() }))
    .safeParse(detail);
  if (validation.success)
    return validation.data.map((item) => `${item.loc.join('.')}: ${item.msg}`).join('; ');
}
export function createApi(baseUrl = import.meta.env.VITE_API_BASE_URL ?? '') {
  const base = baseUrl.replace(/\/$/, '');
  async function request<T>(
    path: string,
    schema: z.ZodType<T>,
    signal: AbortSignal,
    init?: RequestInit,
  ): Promise<T> {
    let response: Response;
    try {
      response = await fetch(`${base}/api${path}`, { ...init, signal });
    } catch (error) {
      if (signal.aborted) throw error;
      throw new ApiError('Cannot reach the local API. Start FastAPI on 127.0.0.1:8000 and retry.');
    }
    let body: unknown;
    try {
      body = await response.json();
    } catch {
      throw new ApiError(
        response.ok
          ? 'The API returned invalid JSON.'
          : `API request failed (HTTP ${response.status}).`,
        response.status,
      );
    }
    if (!response.ok)
      throw new ApiError(
        errorDetail(body) || `API request failed (HTTP ${response.status}).`,
        response.status,
      );
    const parsed = schema.safeParse(body);
    if (!parsed.success)
      throw new ApiError(
        'The API response does not match the expected contract. No results were displayed.',
      );
    return parsed.data;
  }
  const query = (scenario: ScenarioId) =>
    `?scenario=${encodeURIComponent(scenario)}&seed=2026&days=21`;
  return {
    nasaStudy: (signal: AbortSignal) =>
      request('/research/nasa/study', nasaStudySchema, signal),
    nasaSamples: (signal: AbortSignal) =>
      request('/research/nasa/sample-table', nasaSamplesSchema, signal),
    research: (signal: AbortSignal) =>
      request('/research/ecg/demo?record=100', researchSchema, signal),
    scenarios: (signal: AbortSignal) => request('/scenarios', scenariosSchema, signal),
    evidence: (signal: AbortSignal) => request('/evidence', evidenceSchema, signal),
    riskGuide: (signal: AbortSignal) => request('/mission/risk-guide', riskGuideSchema, signal),
    fictionalCheckIn: (payload: FictionalCheckInInput, signal: AbortSignal) =>
      request('/mission/fictional-check-in', checkInSchema, signal, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload),
      }),
    demo: (scenario: ScenarioId, signal: AbortSignal) =>
      request(`/demo${query(scenario)}`, snapshotSchema, signal),
    timeline: (scenario: ScenarioId, signal: AbortSignal) =>
      request(`/timeline${query(scenario)}`, timelineSchema, signal),
    review: (
      scenario: ScenarioId,
      state: ReviewReport['review_state'],
      note: string,
      signal: AbortSignal,
    ) =>
      request('/review', reportSchema, signal, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          scenario,
          seed: 2026,
          days: 21,
          review_state: state,
          reviewer_note: note,
        }),
      }),
    async upload(file: File, attested: boolean, signal: AbortSignal) {
      if (!attested)
        throw new ApiError('Confirm that the file contains fictional synthetic data only.');
      if (file.size > MAX_CSV_BYTES)
        throw new ApiError('Synthetic CSV must be at most 1,000,000 bytes.');
      const bytes = await file.arrayBuffer();
      signal.throwIfAborted();
      return request('/synthetic-csv', csvSnapshotSchema, signal, {
        method: 'POST',
        headers: { 'Content-Type': 'text/csv', 'X-Synthetic-Attestation': 'true' },
        body: bytes,
      });
    },
  };
}
export const api = createApi();
export function message(error: unknown): string {
  return error instanceof Error
    ? error.message
    : 'An unexpected error occurred. Retry the request.';
}
