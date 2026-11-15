import { waitFor } from '@testing-library/react';
import { expect, it, vi } from 'vitest';
import { downloadReport } from './download';
import { reportSchema } from './contracts';
import fixtures from './test/fixtures.json';
it('downloads the complete server report as JSON and releases its object URL', async () => {
  const report = reportSchema.parse(fixtures.stable.report);
  const create = vi.fn((_blob: Blob) => 'blob:fictional');
  const revoke = vi.fn();
  vi.stubGlobal('URL', Object.assign(URL, { createObjectURL: create, revokeObjectURL: revoke }));
  const click = vi.spyOn(HTMLAnchorElement.prototype, 'click').mockImplementation(() => {});
  downloadReport(report);
  expect(click).toHaveBeenCalledOnce();
  expect(create.mock.calls[0][0]).toBeInstanceOf(Blob);
  const blob = create.mock.calls[0][0] as Blob;
  expect(blob.type).toBe('application/json');
  expect(JSON.parse(new TextDecoder().decode(await blob.arrayBuffer()))).toEqual(
    fixtures.stable.report,
  );
  expect(document.querySelector('a')).toBeNull();
  await waitFor(() => expect(revoke).toHaveBeenCalledWith('blob:fictional'));
  vi.unstubAllGlobals();
});
