import { useState } from 'react';
import { eventTypes, type EventType, type Timeline } from '../contracts';
export function TimelineView({
  timeline,
  blocked,
}: {
  timeline: Timeline | null;
  blocked: boolean;
}) {
  const [filters, setFilters] = useState<EventType[]>([...eventTypes]);
  if (!timeline)
    return (
      <section id="mission-timeline">
        <h2>Mission timeline</h2>
        <p>
          The API does not provide timelines for CSV uploads. No built-in scenario timeline is shown
          for this dataset.
        </p>
      </section>
    );
  const events = timeline.events.filter(
    (event) =>
      filters.includes(event.type) &&
      !(blocked && (event.type === 'trend_change' || event.type === 'analysis_status')),
  );
  return (
    <section id="mission-timeline">
      <h2>Mission timeline</h2>
      <p>
        Repeated trends are overlapping window evaluations, not onset of a medical event. Event IDs
        apply to this response only.
      </p>
      <fieldset>
        <legend>Filter timeline event types</legend>
        {eventTypes.map((type) => (
          <label key={type}>
            <input
              type="checkbox"
              checked={filters.includes(type)}
              onChange={(e) =>
                setFilters((current) =>
                  e.target.checked ? [...current, type] : current.filter((item) => item !== type),
                )
              }
            />
            {type}
          </label>
        ))}
      </fieldset>
      {!events.length ? (
        <p>No events match the selected filters.</p>
      ) : (
        <ol>
          {events.map((event) => (
            <li key={event.id}>
              <strong>{event.type}</strong> ·{' '}
              {event.timestamp_utc ?? 'Dataset-wide (no attributed time)'} · <code>{event.id}</code>
              <p>{event.explanation}</p>
              {typeof event.details.effect === 'string' && <p>{event.details.effect}</p>}
            </li>
          ))}
        </ol>
      )}
    </section>
  );
}
