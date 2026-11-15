import { useState, type FormEvent } from 'react';
import { MAX_CSV_BYTES } from '../api';
export function CsvUpload({ onUpload, busy }: { onUpload: (file: File) => void; busy: boolean }) {
  const [file, setFile] = useState<File>();
  const [attested, setAttested] = useState(false);
  const [error, setError] = useState('');
  function submit(e: FormEvent) {
    e.preventDefault();
    setError('');
    if (!attested) {
      setError('Confirm fictional synthetic data only before uploading.');
      return;
    }
    if (!file) {
      setError('Choose a synthetic CSV file.');
      return;
    }
    if (file.size > MAX_CSV_BYTES) {
      setError('Synthetic CSV must be at most 1,000,000 bytes.');
      return;
    }
    onUpload(file);
  }
  return (
    <section id="synthetic-csv">
      <h2>Synthetic CSV import</h2>
      <p>
        Never upload real health records. Validation occurs in Python; an attestation is not
        independent proof of provenance. Files stay in memory.
      </p>
      <a href="/synthetic-template.csv" download>
        Download local synthetic CSV template
      </a>
      <form onSubmit={submit}>
        <label>
          Synthetic CSV file
          <input
            type="file"
            accept=".csv,text/csv"
            onChange={(e) => {
              setFile(e.target.files?.[0]);
              setAttested(false);
              setError('');
            }}
          />
        </label>
        <label>
          <input
            type="checkbox"
            checked={attested}
            onChange={(e) => setAttested(e.target.checked)}
          />
          I attest this file contains fictional synthetic data only, with no real health records.
        </label>
        <button disabled={busy}>Upload synthetic CSV</button>
      </form>
      {error && <p role="alert">{error}</p>}
    </section>
  );
}
