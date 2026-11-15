import { Crosshair, Maximize2 } from 'lucide-react';
import { useState } from 'react';
import anatomy from './crew-anatomy.png';
import { metrics, type MetricKey } from './metrics';
export function BodyViewer({
  selected,
  onSelect,
  crewId = 'SIM-001',
}: {
  crewId?: string;
  selected: MetricKey;
  onSelect: (key: MetricKey) => void;
}) {
  const [unmonitored, setUnmonitored] = useState(false);
  const [zoom, setZoom] = useState(false);
  const active = metrics.find((item) => item.key === selected)!;
  return (
    <section className="body-viewer" aria-label="Interactive anatomical domain navigator">
      <div className="panel-heading">
        <span>
          <Crosshair size={15} /> ANATOMICAL OVERVIEW
        </span>
        <button
          className="icon-button"
          aria-label={zoom ? 'Reset anatomy view' : 'Enlarge anatomy view'}
          aria-pressed={zoom}
          onClick={() => setZoom((value) => !value)}
        >
          <Maximize2 size={14} />
        </button>
      </div>
      <div className={`body-stage ${zoom ? 'zoomed' : ''}`}>
        <div className="body-orbit orbit-one" />
        <div className="body-orbit orbit-two" />
        <div className="body-frame">
          <img
            src={anatomy}
            alt="Original AI-generated clothed human with anatomical overlays; illustrative domain navigation, not clinical anatomy"
            draggable={false}
          />
          {metrics.map((metric, index) => (
            <button
              key={metric.key}
              className={`body-hotspot hotspot-${index} ${!unmonitored && selected === metric.key ? 'active' : ''}`}
              aria-pressed={!unmonitored && selected === metric.key}
              aria-label={`Explore ${metric.domain}: ${metric.short}`}
              onClick={() => {
                setUnmonitored(false);
                onSelect(metric.key);
              }}
            >
              <span />
              <b>{metric.short}</b>
            </button>
          ))}
          <button
            className="body-hotspot hotspot-unmonitored"
            aria-label="Other body regions: not monitored"
            onClick={() => setUnmonitored(true)}
          >
            <span />
            <b>Not monitored</b>
          </button>
        </div>
        <span className="anatomy-ai-watermark" aria-label="AI-generated anatomical illustration">AI-GENERATED IMAGE</span>
        <span className="body-coordinate">ANTERIOR / ILLUSTRATIVE</span>
        <span className="body-coordinate right">{crewId}</span>
      </div>
      <div className="body-context" role="status">
        <span className="live-dot" />
        <div>
          <strong>{unmonitored ? 'NOT MONITORED' : active.domain}</strong>
          <p>
            {unmonitored
              ? 'No respiratory, organ, radiation or diagnostic measurements are available.'
              : `${active.name} is a fictional observation, not a measurement of organ health.`}
          </p>
        </div>
      </div>
      <p className="anatomy-caption">
        Original generated illustration · decorative overlays, not sensor coverage or a clinical
        model.
      </p>
    </section>
  );
}
