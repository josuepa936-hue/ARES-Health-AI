import { vi } from 'vitest';
import fixtures from './fixtures.json';
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
      case '/api/scenarios':
        return respond(fixtures.scenarios);
      case '/api/evidence':
        return respond(fixtures.evidence);
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
        });
      default:
        throw new Error(`Unexpected request ${url}`);
    }
  });
}
