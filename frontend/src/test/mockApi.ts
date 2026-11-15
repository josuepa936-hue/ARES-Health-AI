import { vi } from 'vitest';
import fixtures from './fixtures.json';
import copilotFixtures from './copilot-fixtures.json';
import type { WorkflowState } from '../copilot-contract';
export { fixtures };
export function respond(body: unknown, status = 200) {
  return new Response(JSON.stringify(body), {
    status,
    headers: { 'Content-Type': 'application/json' },
  });
}
export function mockApi() {
  return vi.fn(async (input: string | URL | Request, init?: RequestInit) => {
    const url = new URL(String(input), 'http://localhost');
    const scenario = (url.searchParams.get('scenario') || 'stable') as 'stable';
    switch (url.pathname) {
      case '/api/mission/copilot': {
        const body = JSON.parse(String(init?.body));
        const key = (
          body.context.kind === 'synthetic_csv'
            ? 'csv'
            : body.context.check_in
              ? 'checkin'
              : body.context.scenario
        ) as keyof typeof copilotFixtures;
        const fixture = copilotFixtures[key];
        const response = body.question
          ? (fixture.answers[body.question as keyof typeof fixture.answers] ??
            fixture.answers['Tell a story'])
          : fixture.briefing;
        return respond({ ...response, turn: body.turn });
      }
      case '/api/mission/comprehensive-report': {
        const body = JSON.parse(String(init?.body));
        const key = (
          body.context.kind === 'synthetic_csv'
            ? 'csv'
            : body.context.check_in
              ? 'checkin'
              : body.context.scenario
        ) as keyof typeof copilotFixtures;
        const state = ([...body.audit_log]
          .reverse()
          .find((event) => event.action === 'review_state')?.review_state ??
          'PENDING_REVIEW') as WorkflowState;
        const fixture = { ...copilotFixtures[key].report, ...copilotFixtures[key].reports[state] };
        return respond({
          ...fixture,
          application_version: '1.5',
          copilot_application_version: '1.5',
          mission_timeline: { ...fixture.mission_timeline, application_version: '1.5' },
          review_state: state,
          legacy_review_state: state === 'DOCUMENTED' ? 'Reviewed in demo' : 'Pending review',
          legacy_review_state_semantics: 'Compatibility-only; use review_state for current status.',
          fictional_review: {
            ...fixture.fictional_review,
            review_state: state,
            audit_log: body.audit_log,
            audit_timestamp_source: 'User device UTC at action time; not independently authenticated.',
            audit_timestamps_complete: body.audit_log.every(
              (event: { recorded_at_utc?: string }) => !!event.recorded_at_utc
            ),
          },
        });
      }
      case '/api/scenarios':
        return respond(fixtures.scenarios);
      case '/api/evidence':
        return respond(fixtures.evidence);
      case '/api/mission/risk-guide':
        return respond({
          source: 'NASA Human Research Program — Five Hazards of Human Spaceflight',
          reference_url: 'https://www.nasa.gov/hrp/hazards/',
          disclaimer:
            'Educational hazard context, not NASA operational health guidance or patient-specific recommendations.',
          risks: [
            { id: 'radiation', title: 'Space radiation', body_region: 'whole_body' },
            { id: 'gravity', title: 'Altered gravity', body_region: 'musculoskeletal' },
            { id: 'isolation', title: 'Isolation and confinement', body_region: 'head' },
            { id: 'distance', title: 'Distance from Earth', body_region: 'whole_body' },
            {
              id: 'environment',
              title: 'Hostile or closed environments',
              body_region: 'cardiovascular',
            },
          ].map((item) => ({
            ...item,
            spaceflight_context: 'NASA research background.',
            candidate_observations: ['Research indicators'],
            ares_current_coverage: 'Fictional or unavailable.',
            crew_review: 'Review approved mission procedures.',
            reference_url: 'https://www.nasa.gov/hrp/hazards/',
          })),
        });
      case '/api/mission/fictional-check-in': {
        const input = JSON.parse(String(init?.body));
        const id = input.scenario as 'stable';
        const scenario = id + '_fictional_checkin';
        const snapshot = fixtures[id].demo;
        const observations = snapshot.observations.map((row, index) =>
          index === snapshot.observations.length - 1
            ? {
                ...row,
                resting_hr_bpm: input.resting_hr_bpm,
                sleep_hours: input.sleep_hours,
                activity_minutes: input.activity_minutes,
              }
            : row,
        );
        return respond({
          ...snapshot,
          scenario,
          observations,
          mission_timeline: { ...fixtures[id].timeline, scenario },
          review_report: { ...fixtures[id].report, scenario },
          check_in: {
            timestamp_utc: observations.at(-1)?.timestamp_utc,
            fictional_attestation: true,
            mode: 'fictional_latest_day_override',
            reported_concerns: input.concerns,
            notice: 'Only the latest fictional observation was replaced.',
          },
          decision_support: {
            assessment: snapshot.assessment,
            review_action: 'Review the observations and approved procedures.',
            reported_concerns: input.concerns,
            concerns_notice: 'No clinical triage is performed.',
            mission_procedures: 'Consult authorized flight-medical personnel.',
            clinical_decision_support: false,
          },
        });
      }
      case '/api/demo':
        return respond(fixtures[scenario].demo);
      case '/api/timeline':
        return respond(fixtures[scenario].timeline);
      case '/api/review': {
        const request = JSON.parse(String(init?.body));
        return respond({
          ...fixtures[request.scenario as 'stable'].report,
          review_state: request.review_state,
          reviewer_note: request.reviewer_note,
        });
      }
      case '/api/synthetic-csv':
        return respond({
          ...fixtures.stable.demo,
          scenario: 'uploaded_synthetic_csv',
          review_report: { ...fixtures.stable.report, scenario: 'uploaded_synthetic_csv' },
          mission_timeline: {
            ...fixtures.stable.timeline,
            scenario: 'uploaded_synthetic_csv',
          },
        });
      default:
        throw new Error(`Unexpected request ${url}`);
    }
  });
}
