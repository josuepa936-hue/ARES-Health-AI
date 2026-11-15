import { afterEach, describe, expect, it, vi } from 'vitest';
import { createApi } from './api';
import { fixtures, mockApi, respond } from './test/mockApi';
afterEach(() => vi.unstubAllGlobals());
const signal = () => new AbortController().signal;
describe('typed HTTP adapter', () => {
  it('uses a configurable base URL, query, and cancellation signal', async () => {
    const fetch = mockApi();
    vi.stubGlobal('fetch', fetch);
    const s = signal();
    await createApi('http://127.0.0.1:8000/').demo('heart_rate_shift', s);
    expect(fetch).toHaveBeenCalledWith(
      'http://127.0.0.1:8000/api/demo?scenario=heart_rate_shift&seed=2026&days=21',
      expect.objectContaining({ signal: s }),
    );
  });
  it.each([
    [400, { detail: 'Attestation required' }, 'Attestation required'],
    [
      422,
      { detail: { status: 'CSV_REJECTED', errors: ['Duplicate timestamps', 'Invalid sleep'] } },
      'Duplicate timestamps; Invalid sleep',
    ],
    [
      422,
      { detail: [{ loc: ['query', 'days'], msg: 'Invalid days' }] },
      'query.days: Invalid days',
    ],
    [500, { detail: { unexpected: 7 } }, 'HTTP 500'],
  ])('validates error shapes for HTTP %s', async (status, body, expected) => {
    vi.stubGlobal('fetch', vi.fn().mockResolvedValue(respond(body, status)));
    await expect(createApi().scenarios(signal())).rejects.toThrow(expected);
  });
  it('handles non-JSON server errors', async () => {
    vi.stubGlobal(
      'fetch',
      vi.fn().mockResolvedValue(new Response('upstream failure', { status: 502 })),
    );
    await expect(createApi().scenarios(signal())).rejects.toThrow('HTTP 502');
  });
  it('rejects malformed successful responses', async () => {
    vi.stubGlobal('fetch', vi.fn().mockResolvedValue(respond({ assessment: 'healthy' })));
    await expect(createApi().demo('stable', signal())).rejects.toThrow('expected contract');
  });
  it('rejects non-finite observations in otherwise valid data', async () => {
    const body = structuredClone(fixtures.stable.demo);
    body.observations[0].sleep_hours = Infinity;
    // Response.json below preserves the deliberately malformed non-finite number.
    vi.stubGlobal('fetch', vi.fn().mockResolvedValue({ ok: true, json: async () => body }));
    await expect(createApi().demo('stable', signal())).rejects.toThrow('expected contract');
  });
  it('reports connection failures without fabricating data', async () => {
    vi.stubGlobal('fetch', vi.fn().mockRejectedValue(new TypeError('Failed to fetch')));
    await expect(createApi().scenarios(signal())).rejects.toThrow('Cannot reach the local API');
  });
  it('preserves abort errors', async () => {
    const controller = new AbortController();
    controller.abort();
    vi.stubGlobal('fetch', vi.fn().mockRejectedValue(new DOMException('Aborted', 'AbortError')));
    await expect(createApi().scenarios(controller.signal)).rejects.toMatchObject({
      name: 'AbortError',
    });
  });
  it('requires attestation and enforces byte size before sending', async () => {
    const fetch = mockApi();
    vi.stubGlobal('fetch', fetch);
    await expect(
      createApi().upload(new File(['abc'], 'fixture.csv'), false, signal()),
    ).rejects.toThrow('fictional');
    await expect(
      createApi().upload(new File(['x'.repeat(1_000_001)], 'large.csv'), true, signal()),
    ).rejects.toThrow('1,000,000');
    expect(fetch).not.toHaveBeenCalled();
  });
  it('sends raw CSV bytes and required headers, without multipart', async () => {
    const fetch = mockApi();
    vi.stubGlobal('fetch', fetch);
    const file = new File(['fictional,csv\n'], 'fixture.csv');
    await createApi().upload(file, true, signal());
    const init = fetch.mock.calls[0][1]!;
    expect(init.headers).toEqual({ 'Content-Type': 'text/csv', 'X-Synthetic-Attestation': 'true' });
    expect(init.body).toBeInstanceOf(ArrayBuffer);
    expect(new TextDecoder().decode(init.body as ArrayBuffer)).toBe('fictional,csv\n');
  });
});

it('rejects inconsistent assessment/guidance rather than showing reassuring stale text', async () => {
  vi.stubGlobal(
    'fetch',
    vi.fn().mockResolvedValue(
      respond({
        ...fixtures.stable.demo,
        assessment: 'DATA_QUALITY_BLOCKED',
      }),
    ),
  );
  await expect(createApi().demo('stable', signal())).rejects.toThrow('expected contract');
});
it('rejects a CSV report attached to the wrong dataset', async () => {
  vi.stubGlobal(
    'fetch',
    vi.fn().mockResolvedValue(
      respond({
        ...fixtures.stable.demo,
        scenario: 'uploaded_synthetic_csv',
        review_report: fixtures.stable.report,
      }),
    ),
  );
  await expect(
    createApi().upload(new File(['synthetic'], 'fixture.csv'), true, signal()),
  ).rejects.toThrow('expected contract');
});
