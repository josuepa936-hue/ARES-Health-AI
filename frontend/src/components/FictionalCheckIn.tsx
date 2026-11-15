import { useState, type FormEvent } from 'react';
import type { FictionalCheckInInput, FictionalConcern, ScenarioId } from '../contracts';

const concerns: { id: FictionalConcern; label: string }[] = [
  { id: 'fatigue', label: 'Fatigue (hypothetical)' },
  { id: 'headache', label: 'Headache (hypothetical)' },
  { id: 'dizziness', label: 'Dizziness (hypothetical)' },
  { id: 'sleepiness', label: 'Sleepiness (hypothetical)' },
];

/** All entries are expressly fictional, ephemeral, and checked in Python. */
export function FictionalCheckIn({
  scenario, busy, onSubmit,
}: {
  scenario?: ScenarioId;
  busy: boolean;
  onSubmit: (data: FictionalCheckInInput) => void;
}) {
  const [heartRate, setHeartRate] = useState('64');
  const [sleep, setSleep] = useState('7.5');
  const [activity, setActivity] = useState('42');
  const [selectedConcerns, setSelectedConcerns] = useState<FictionalConcern[]>([]);
  const [attested, setAttested] = useState(false);
  const [error, setError] = useState('');

  function handleSubmit(event: FormEvent) {
    event.preventDefault();
    setError('');
    if (!scenario) return setError('Select a fictional scenario first.');
    if (!attested) return setError('Confirm that every entry is fictional.');
    const hr = Number(heartRate);
    const hours = Number(sleep);
    const minutes = Number(activity);
    if (
      !heartRate.trim() || !sleep.trim() || !activity.trim() ||
      !Number.isFinite(hr) || hr <= 0 || hr > 250 ||
      !Number.isFinite(hours) || hours < 0 || hours > 24 ||
      !Number.isInteger(minutes) || minutes < 0 || minutes > 1440
    ) {
      return setError('Check fictional measurement units and valid input ranges.');
    }
    onSubmit({
      fictional_attestation: true,
      scenario,
      seed: 2026, days: 21,
      resting_hr_bpm: hr, sleep_hours: hours,
      activity_minutes: minutes,
      concerns: selectedConcerns,
    });
  }

  return (
    <section id="crew-checkin" aria-labelledby="crew-checkin-heading" className="mission-card">
      <p className="eyebrow">02 / CREW INTERACTION</p>
      <h2 id="crew-checkin-heading">Fictional astronaut check-in</h2>
      <p>
        Enter a <strong>hypothetical</strong> last-day observation to re-run ARES end to end:
        quality checks, transparent change rules, mission timeline, procedural guidance and
        downloadable review. The previous 20 days remain seeded simulation data.
      </p>
      <p className="notice-neutral">
        This demo cannot accept personal or real astronaut health measurements. It does not
        diagnose conditions or choose treatments.
      </p>
      <form onSubmit={handleSubmit}>
        <div className="form-grid">
          <label>
            Resting heart rate (bpm) — fictional
            <input aria-label="Fictional resting heart rate" type="number" required min="1" max="250" step="0.1"
              value={heartRate} onChange={(e) => setHeartRate(e.target.value)} />
          </label>
          <label>
            Sleep duration (hours) — fictional
            <input aria-label="Fictional sleep duration" type="number" required min="0" max="24" step="0.1"
              value={sleep} onChange={(e) => setSleep(e.target.value)} />
          </label>
          <label>
            Daily activity (minutes) — fictional
            <input aria-label="Fictional activity minutes" type="number" required min="0" max="1440" step="1"
              value={activity} onChange={(e) => setActivity(e.target.value)} />
          </label>
        </div>
        <fieldset>
          <legend>Hypothetical concerns (not automated triage)</legend>
          <div className="check-grid">
            {concerns.map((entry) => (
              <label key={entry.id}>
                <input type="checkbox" checked={selectedConcerns.includes(entry.id)}
                  onChange={(event) => setSelectedConcerns((current) => event.target.checked
                    ? [...current, entry.id] : current.filter((item) => item !== entry.id))} />
                {entry.label}
              </label>
            ))}
          </div>
        </fieldset>
        <label className="attestation">
          <input type="checkbox" checked={attested} onChange={(e) => setAttested(e.target.checked)}/>
          I confirm this check-in contains fictional values and concerns only.
        </label>
        <button type="submit" disabled={busy || !scenario || !attested}>
          Analyze fictional check-in
        </button>
        {error && <p role="alert">{error}</p>}
      </form>
    </section>
  );
}
