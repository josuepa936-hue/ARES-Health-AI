import type { Snapshot } from '../contracts';
export const metrics = [
  {
    key: 'resting_hr_bpm',
    name: 'Resting heart rate',
    short: 'Heart rate',
    unit: 'bpm',
    domain: 'Cardiovascular',
    icon: 'heart',
  },
  {
    key: 'sleep_hours',
    name: 'Sleep duration',
    short: 'Sleep',
    unit: 'h',
    domain: 'Sleep / neurobehavioral',
    icon: 'moon',
  },
  {
    key: 'activity_minutes',
    name: 'Daily activity',
    short: 'Activity',
    unit: 'min',
    domain: 'Musculoskeletal',
    icon: 'activity',
  },
] as const;
export type MetricKey = (typeof metrics)[number]['key'];
export type Metric = (typeof metrics)[number];
export function latestObservation(snapshot: Snapshot, key: MetricKey) {
  const latest = snapshot.observations.at(-1);
  const lastValid = [...snapshot.observations].reverse().find((row) => row[key] !== null);
  return { latest, lastValid };
}
export function analysisAvailable(snapshot: Snapshot) {
  return (
    snapshot.assessment !== 'DATA_QUALITY_BLOCKED' && snapshot.assessment !== 'INSUFFICIENT_DATA'
  );
}
