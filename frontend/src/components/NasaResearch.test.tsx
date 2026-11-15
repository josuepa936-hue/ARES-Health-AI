import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { afterEach, expect, it, vi } from 'vitest';
import NasaResearch from './NasaResearch';
import Workspace from '../Workspace';
import { mockApi, respond } from '../test/mockApi';

afterEach(() => vi.unstubAllGlobals());
const study = {
  schema_version: '1.2-osdr',
  accession: 'OSD-87',
  study_title: 'Spaceflight effects on the mouse retina',
  source_organization: 'NASA Open Science Data Repository',
  study_url: 'https://osdr.nasa.gov/bio/repo/data/studies/OSD-87',
  api_url: 'https://osdr.nasa.gov/osdr/data/osd/files/87',
  organism: 'Mus musculus (mouse)',
  tissue: 'retina',
  mission_context: 'STS-135',
  data_provenance: 'public_space_biology_research',
  file_catalog_count: 2,
  visible_public_files: 1,
  file_categories: [{ category: 'Microarray Data', count: 1 }],
  files: [{
    file_name: 'GLDS-87_array_SampleTable_GLmicroarray.csv',
    category: 'Microarray Data',
    size_bytes: 290,
    file_url: 'https://osdr.nasa.gov/geode-py/ws/studies/OSD-87/download?source=datamanager&file=GLDS-87_array_SampleTable_GLmicroarray.csv',
  }],
  sample_preview_available: true,
  disclaimer: 'Mouse biological research, not astronaut health data.',
};
const samples = {
  schema_version: '1.2-osdr-samples',
  accession: 'OSD-87',
  file_name: 'GLDS-87_array_SampleTable_GLmicroarray.csv',
  data_provenance: 'public_space_biology_research',
  sample_count: 2,
  column_names: ['Sample', 'Condition'],
  rows: [{ Sample: 'MOUSE_R1', Condition: 'flight' }, { Sample: 'MOUSE_R2', Condition: 'control' }],
  reference_url: study.study_url,
  disclaimer: 'Original published mouse experimental rows, not astronaut data.',
};

it('renders official mouse study metadata and loads the sample table only on click', async () => {
  const fetch = vi.fn((url: string) =>
    Promise.resolve(respond(String(url).includes('sample-table') ? samples : study)),
  );
  vi.stubGlobal('fetch', fetch);
  const user = userEvent.setup();
  render(<NasaResearch />);
  expect(await screen.findByText('Spaceflight effects on the mouse retina')).toBeVisible();
  expect(screen.getByText(/NOT ASTRONAUT HEALTH TELEMETRY/)).toBeVisible();
  expect(fetch).toHaveBeenCalledTimes(1);
  expect(screen.queryByText('MOUSE_R1')).not.toBeInTheDocument();
  await user.click(screen.getByRole('button', { name: 'Load NASA mouse sample table' }));
  expect(await screen.findByText('MOUSE_R1')).toBeVisible();
  expect(screen.getByText('MOUSE_R2')).toBeVisible();
  expect(fetch).toHaveBeenCalledTimes(2);
});

it('never substitutes a synthetic NASA study when the network is unavailable', async () => {
  vi.stubGlobal('fetch', vi.fn().mockResolvedValue(respond({
    detail: 'Official NASA OSDR public dataset is currently inaccessible',
  }, 503)));
  render(<NasaResearch />);
  expect(await screen.findByRole('alert')).toHaveTextContent('currently inaccessible');
  expect(screen.queryByText('Spaceflight effects on the mouse retina')).not.toBeInTheDocument();
});

it('keeps NASA research inactive until explicitly selected and leaves synthetic mission intact', async () => {
  const normal = mockApi();
  const fetch = vi.fn((input: string | URL | Request, init?: RequestInit) =>
    String(input).includes('/research/nasa/')
      ? Promise.resolve(respond(study))
      : normal(input, init),
  );
  vi.stubGlobal('fetch', fetch);
  const user = userEvent.setup();
  render(<Workspace />);
  await screen.findByRole('heading', { name: 'Mission overview' });
  expect(fetch.mock.calls.some(([url]) => String(url).includes('/research/nasa/'))).toBe(false);
  await user.click(screen.getByRole('button', { name: 'NASA space biology' }));
  expect(await screen.findByText('Spaceflight effects on the mouse retina')).toBeVisible();
  expect(screen.getByText('SYNTHETIC DATA / NOT A MEDICAL DEVICE')).not.toBeVisible();
  await user.click(screen.getByRole('button', { name: 'Synthetic mission demo' }));
  expect(screen.getByRole('heading', { name: 'Mission overview' })).toBeVisible();
});

it('aborts an unresolved catalog request when leaving the NASA view', () => {
  let signal: AbortSignal | undefined;
  vi.stubGlobal('fetch', vi.fn((_input, init) => {
    signal = init.signal;
    return new Promise(() => {});
  }));
  const view = render(<NasaResearch />);
  view.unmount();
  expect(signal?.aborted).toBe(true);
});
