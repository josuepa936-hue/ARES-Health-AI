import { useEffect, useRef, useState } from 'react';
import { api, message } from '../api';
import type { NasaSamples, NasaStudy } from '../nasa-contract';

/** Opt-in public mouse-spaceflight research view; isolated from crew telemetry. */
export default function NasaResearch() {
  const [study, setStudy] = useState<NasaStudy>();
  const [samples, setSamples] = useState<NasaSamples>();
  const [error, setError] = useState('');
  const [sampleError, setSampleError] = useState('');
  const [loading, setLoading] = useState(true);
  const [sampleLoading, setSampleLoading] = useState(false);
  const [retry, setRetry] = useState(0);
  const sampleController = useRef<AbortController | null>(null);

  useEffect(() => {
    const controller = new AbortController();
    setLoading(true);
    setError('');
    setSampleError('');
    setSamples(undefined);
    setStudy(undefined);
    api.nasaStudy(controller.signal)
      .then((data) => {
        if (!controller.signal.aborted) setStudy(data);
      })
      .catch((cause) => {
        if (!controller.signal.aborted) setError(message(cause));
      })
      .finally(() => {
        if (!controller.signal.aborted) setLoading(false);
      });
    return () => controller.abort();
  }, [retry]);

  useEffect(() => {
    // This aborts a pending sample request when leaving NASA mode.
    return () => sampleController.current?.abort();
  }, []);

  async function showSamples() {
    sampleController.current?.abort();
    const controller = new AbortController();
    sampleController.current = controller;
    setSampleLoading(true);
    setSamples(undefined);
    setSampleError('');
    try {
      const result = await api.nasaSamples(controller.signal);
      if (!controller.signal.aborted) setSamples(result);
    } catch (cause) {
      if (!controller.signal.aborted) setSampleError(message(cause));
    } finally {
      if (!controller.signal.aborted) setSampleLoading(false);
    }
  }

  return (
    <main>
      <h1>NASA Space Biology Research — OSD-87</h1>
      <p><strong>PUBLIC MOUSE RESEARCH / NOT ASTRONAUT HEALTH TELEMETRY</strong></p>
      <p>
        This is an opt-in NASA OSDR experiment explorer, completely separate from MIT-BIH
        terrestrial ECG and fictional crew monitoring. No diagnosis, astronaut risk
        scoring, or direct clinical inference is performed.
      </p>
      <p>
        <a href="https://osdr.nasa.gov/bio/repo/data/studies/OSD-87"
          target="_blank" rel="noreferrer">Open official OSD-87 study</a>
      </p>
      <button disabled={loading} onClick={() => setRetry((value) => value + 1)}>
        Refresh NASA public catalog
      </button>
      {loading && <p role="status">Requesting NASA's public file catalog…</p>}
      {error && (
        <p role="alert">
          {error} The NASA source could be unreachable or research mode disabled.
          No research results were substituted.
        </p>
      )}
      {study && (
        <section>
          <h2>{study.study_title}</h2>
          <p><strong>Source:</strong> {study.source_organization} · {study.accession}</p>
          <dl>
            <dt>Study organism</dt><dd>{study.organism}</dd>
            <dt>Studied tissue</dt><dd>{study.tissue}</dd>
            <dt>Mission context</dt><dd>{study.mission_context}</dd>
            <dt>Catalogued research files</dt><dd>{study.file_catalog_count}</dd>
            <dt>Visible public files returned</dt><dd>{study.visible_public_files}</dd>
          </dl>
          <p>{study.disclaimer}</p>
          <h3>Published file categories</h3>
          <p>Counts describe research files, not astronauts, diagnoses or dose measurements.</p>
          <ul>
            {study.file_categories.map((category) => (
              <li key={category.category}>{category.category}: {category.count} files</li>
            ))}
          </ul>
          <details>
            <summary>Explore the official public file catalog</summary>
            <ul>
              {study.files.map((file) => (
                <li key={file.file_name}>
                  <a href={file.file_url} target="_blank" rel="noreferrer">
                    {file.file_name}
                  </a> — {file.category}, {file.size_bytes.toLocaleString()} bytes
                </li>
              ))}
            </ul>
            <p>Large omics datasets are linked, never automatically downloaded into ARES.</p>
          </details>
          <h3>Research sample table</h3>
          <p>
            Only a vetted small public CSV can be previewed. Original experimental
            columns and values are shown without interpreting them as physiological readings.
          </p>
          {study.sample_preview_available ? (
            <button disabled={sampleLoading} onClick={showSamples}>Load NASA mouse sample table</button>
          ) : (
            <p>Small sample table is not publicly available in this catalog.</p>
          )}
          {sampleLoading && <p role="status">Fetching the small official NASA CSV…</p>}
          {sampleError && <p role="alert">{sampleError}</p>}
          {samples && (
            <>
              <p>Published rows: {samples.sample_count}. Provenance: {samples.data_provenance}.</p>
              <div className="table-scroll">
                <table>
                  <thead>
                    <tr>{samples.column_names.map((name) => <th key={name}>{name}</th>)}</tr>
                  </thead>
                  <tbody>
                    {samples.rows.map((row, i) => (
                      <tr key={i}>
                        {samples.column_names.map((name) => <td key={name}>{row[name] ?? ''}</td>)}
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
              <p>{samples.disclaimer}</p>
            </>
          )}
        </section>
      )}
    </main>
  );
}
