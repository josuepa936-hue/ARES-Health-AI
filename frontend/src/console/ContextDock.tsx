import {
  ChevronDown,
  ChevronUp,
  ClipboardCheck,
  Clock3,
  FileDown,
  Orbit,
  BookOpen,
} from 'lucide-react';
import type { ReactNode } from 'react';
export const dockTabs = [
  { id: 'checkin', label: 'Check-in', Icon: ClipboardCheck },
  { id: 'timeline', label: 'Mission Timeline', Icon: Clock3 },
  { id: 'review', label: 'Review & Export', Icon: FileDown },
  { id: 'risks', label: 'Spaceflight Risks', Icon: Orbit },
  { id: 'sources', label: 'Research Sources', Icon: BookOpen },
] as const;
export type DockTab = (typeof dockTabs)[number]['id'];
export function ContextDock({
  active,
  open,
  onSelect,
  onToggle,
  panels,
}: {
  active: DockTab;
  open: boolean;
  onSelect: (tab: DockTab) => void;
  onToggle: () => void;
  panels: Record<DockTab, ReactNode>;
}) {
  return (
    <section
      className={`context-dock ${open ? '' : 'collapsed'}`}
      aria-label="Mission contextual workspace"
    >
      <div className="dock-toolbar">
        <div role="tablist" aria-label="Mission workflow">
          {dockTabs.map(({ id, label, Icon }, index) => (
            <button
              id={`tab-${id}`}
              key={id}
              role="tab"
              aria-selected={active === id}
              aria-controls={`panel-${id}`}
              tabIndex={active === id ? 0 : -1}
              onClick={() => onSelect(id)}
              onKeyDown={(e) => {
                let next = index;
                if (e.key === 'ArrowRight') next = (index + 1) % dockTabs.length;
                else if (e.key === 'ArrowLeft')
                  next = (index + dockTabs.length - 1) % dockTabs.length;
                else if (e.key === 'Home') next = 0;
                else if (e.key === 'End') next = dockTabs.length - 1;
                else return;
                e.preventDefault();
                onSelect(dockTabs[next].id);
                document.getElementById(`tab-${dockTabs[next].id}`)?.focus();
              }}
            >
              <Icon size={14} />
              <span>{label}</span>
            </button>
          ))}
        </div>
        <button
          className="icon-button dock-collapse"
          aria-label={open ? 'Collapse contextual workspace' : 'Expand contextual workspace'}
          aria-expanded={open}
          onClick={onToggle}
        >
          {open ? <ChevronDown size={16} /> : <ChevronUp size={16} />}
        </button>
      </div>
      {dockTabs.map(({ id }) => (
        <div
          key={id}
          id={`panel-${id}`}
          role="tabpanel"
          aria-labelledby={`tab-${id}`}
          hidden={!open || active !== id}
          tabIndex={0}
          className="dock-content"
        >
          {panels[id]}
        </div>
      ))}
    </section>
  );
}
